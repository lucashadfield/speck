__all__ = ['RandomNoise', 'SineNoise']

import numpy as np
from typing import List, Tuple, Union


class Noise:
    def __init__(self, profile: str, *args, **kwargs):
        if profile not in ['parallel', 'reflect', 'independent']:
            raise ValueError(
                'Invalid noise profile. Supported profiles are: parallel, reflect, independent'
            )

        self.profile = profile

    def __repr__(self):
        """
        Auto __repr__ based on instance __dict__
        Parameters with a leading _ are omitted from the repr and thus from the hash
        """

        d = [f'{k}={v}' for k, v in self.__dict__.items() if not k.startswith('_')]
        return f'{self.__class__.__name__}({", ".join(d)})'

    def __hash__(self):
        return hash(
            tuple([v for k, v in self.__dict__.items() if not k.startswith('_')])
        )

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __call__(self, m: int, n: int) -> List[Tuple]:
        # m = number of rows (lines)
        # n = number of points per line

        noise_a = []
        for _ in range(m):
            noise_a.append(self._generate(n))

        if self.profile == 'parallel':
            return [(yn, yn) for yn in noise_a]
        if self.profile == 'reflect':
            return [(yn, -yn) for yn in noise_a]
        if self.profile == 'independent':
            noise_b = []
            for _ in range(m):
                noise_b.append(self._generate(n))
            return [(a, b) for a, b in zip(noise_a, noise_b)]

    def _generate(self, n: int) -> np.ndarray:
        raise NotImplementedError


class RandomNoise(Noise):
    def __init__(
        self,
        profile: str = 'parallel',
        scale: float = 0.5,
        pull: float = 0.1,
        mean_n: int = 100,
    ):
        """
        Create RandomNoise object to be passed to SpeckPlot.draw method
        :param profile: noise profile to apply to each line
                'parallel': apply the same noise profile to the top and bottom edge of each line so they remain parallel
                'reflect': apply opposite noise profiles to the top and bottom edge of each line
                'independent': apply independently generated noise profiles to the top and bottom edge of each line
        :param scale: magnitude of the noise generated
        :param pull: affects magnitude of subsequent noise offsets to avoid out of control noise
        :param mean_n: number of random noise values that are averaged together - smoother noise
        """

        self.scale = scale
        self.pull = pull
        self.mean_n = mean_n

        super().__init__(profile)

    def _generate(self, n: int) -> np.ndarray:
        res = np.array([0.0])
        for _ in range(n):
            r = np.random.normal(-res.sum() * self.pull, self.scale)
            res = np.insert(res, -1, r)

        return np.convolve(res, np.ones((self.mean_n,)) / self.mean_n)[
            (self.mean_n - 1) : -1
        ]


class SineNoise(Noise):
    def __init__(
        self,
        profile: str = 'parallel',
        scale: Union[float, tuple] = 0.5,
        wave_count: int = 3,
        base_freq: float = 3.0,
        freq_factor: Tuple[float, float] = (1.0, 3.0),
        phase_offset_range: Tuple[float, float] = (0, 360),
    ):
        """
        Create SineNoise object to be passed to SpeckPlot.draw method
        :param profile: noise profile to apply to each line
                'parallel': apply the same noise profile to the top and bottom edge of each line so they remain parallel
                'reflect': apply opposite noise profiles to the top and bottom edge of each line
                'independent': apply independently generated noise profiles to the top and bottom edge of each line
        :param scale: magnitude of the noise generated.
                Either constant noise as a float or a tuple of length SpeckPlot.w * SpeckPlot * h, eg:
                scale = tuple(np.linspace(0.5, 1.5, speck_plot.w * speck_plot.h))
        :param wave_count: number of sine waves that are combined to create the noise profile
        :param base_freq: base number of wavelengths that fit in the width of the image
        :param freq_factor: range of random multipliers that are applied to the base frequency for each wave
        :param phase_offset_range: range of random offsets that are applied to each wave
        """

        self.scale = scale
        self.wave_count = wave_count
        self.base_freq = base_freq
        self.freq_factor = freq_factor
        self.phase_offset_range = phase_offset_range

        super().__init__(profile)

    def _generate(self, n: int) -> np.ndarray:
        return np.array(
            [
                self.scale
                * np.sin(
                    np.linspace(0, self.base_freq * 2 * np.pi, n) * factor + offset
                )
                for factor, offset in zip(
                    np.random.uniform(*self.freq_factor, self.wave_count),
                    np.random.uniform(
                        np.deg2rad(self.phase_offset_range[0]),
                        np.deg2rad(self.phase_offset_range[1]),
                        self.wave_count,
                    ),
                )
            ]
        ).prod(axis=0)
