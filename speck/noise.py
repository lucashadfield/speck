__all__ = ['RandomNoise', 'SineNoise']

import numpy as np
from typing import List, Tuple


class Noise:
    def __init__(self, profile: str, *args, **kwargs):
        if profile not in ['parallel', 'reflective', 'independent']:
            raise ValueError(
                'Invalid noise profile. Supported profiles are: parallel, reflective, independent'
            )

        self.profile = profile

    def _generate(self, n: int) -> np.ndarray:
        raise NotImplementedError

    def __call__(self, m: int, n: int) -> List[Tuple]:
        # m = number of rows (lines)
        # n = number of points per line

        noise_a = []
        for _ in range(m):
            noise_a.append(self._generate(n))

        if self.profile == 'parallel':
            return [(yn, yn) for yn in noise_a]
        if self.profile == 'reflective':
            return [(yn, -yn) for yn in noise_a]
        if self.profile == 'independent':
            noise_b = []
            for _ in range(m):
                noise_b.append(self._generate(n))
            return [(a, b) for a, b in zip(noise_a, noise_b)]


class RandomNoise(Noise):
    def __init__(
        self,
        profile: str = 'parralel',
        scale: float = 0.1,
        pull: float = 0.1,
        mean_n: int = 100,
    ):
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
        scale: float = 0.5,
        wave_count: int = 4,
        base_freq: int = 10,
        freq_factor: tuple = (1, 5),
    ):
        self.scale = scale
        self.wave_count = wave_count
        self.base_freq = base_freq
        self.freq_factor = freq_factor

        super().__init__(profile)

    def _generate(self, n: int) -> np.ndarray:
        return np.array(
            [
                np.sin(np.linspace(0, self.base_freq, n) * r) * self.scale
                for r in np.random.uniform(*self.freq_factor, self.wave_count)
            ]
        ).prod(axis=0)
