__all__ = ['SpeckPlot']

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import figure
from matplotlib.axis import Axis
from PIL import Image
from itertools import cycle
from typing import Union, Iterable, Optional, Tuple
import logging
from functools import lru_cache

from speck.noise import Noise
from speck.colour import Colour
from speck.modifier import Modifier
from speck.types import *

logger = logging.getLogger('speck')


class SpeckPlot:
    k = 10
    inter = 100
    dpi = 100

    def __init__(self, image: Image, scale_factor: float = 5.0):
        self.image = image
        self.scale_factor = scale_factor
        self.im = np.array(image.convert('L'))
        self.h, self.w = self.im.shape

        self.fig = plt.figure(
            figsize=(self.w * scale_factor / self.dpi, self.h * scale_factor / self.dpi)
        )
        self.ax = self.fig.add_axes([0.0, 0.0, 1.0, 1.0], xticks=[], yticks=[])
        plt.close(self.fig)

    @classmethod
    def from_path(
        cls, path: str, scale_factor: float = 3.0, resize: Optional[Tuple] = None
    ):
        image = Image.open(path)
        if resize is not None:
            image = image.resize(resize)
        return cls(image, scale_factor)

    @classmethod
    def from_url(
        cls, url: str, scale_factor: float = 3.0, resize: Optional[Tuple] = None
    ):
        import requests
        from io import BytesIO

        image = Image.open(BytesIO(requests.get(url).content))
        if resize is not None:
            image = image.resize(resize)
        return cls(image, scale_factor)

    def __repr__(self):
        d = [f'{k}={v}' for k, v in self.__dict__.items() if not k.startswith('_')]
        return f'{self.__class__.__name__}({", ".join(d)})'

    def _clear_ax(self, background: Union[str, Tuple]) -> None:
        self.ax.clear()
        self.ax.set_facecolor(background)
        self.ax.invert_yaxis()
        self.ax.spines['left'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['bottom'].set_visible(False)
        self.ax.set_xticks([])
        self.ax.set_yticks([])

    def cache_clear(self, parameter: Optional[str] = None) -> None:
        if parameter is not None:
            getattr(self, parameter).cache_clear()
        else:
            self.x.cache_clear()
            self.y.cache_clear()
            self.noise.cache_clear()
            self.colour.cache_clear()

    def cache_info(self) -> dict:
        return {
            'x': self.x.cache_info(),
            'y': self.y.cache_info(),
            'noise': self.noise.cache_info(),
            'colour': self.colour.cache_info(),
        }

    @lru_cache()
    def x(self) -> XData:
        return np.linspace(0, self.w, self.w * self.inter)

    @lru_cache()
    def y(self, y_range: Tuple[float, float]) -> YData:
        y_min = y_range[0] / 2 + 0.5
        y_max = y_range[1] / 2 + 0.5

        def repeat_head_tail(arr: np.ndarray, n: int) -> np.ndarray:
            return np.insert(
                np.insert(arr, 0, np.ones(n) * arr[0]), -1, np.ones(n) * arr[-1]
            )

        y = []

        for i, line in enumerate(self.im):
            y_offset = np.repeat(y_max - line[:-1] * (y_max - y_min) / 255, self.inter)
            L = (
                np.repeat(y_max - line[1:] * (y_max - y_min) / 255, self.inter)
                - y_offset
            )
            x0 = np.repeat(np.arange(1, self.w), self.inter)

            y_offset = repeat_head_tail(y_offset, self.inter // 2)
            L = repeat_head_tail(L, self.inter // 2)
            x0 = repeat_head_tail(x0, self.inter // 2)

            y_top: np.ndarray = i + (
                L / (1 + np.exp(-self.k * (self.x() - x0)))
            ) + y_offset
            y_bot: np.ndarray = 2 * i + 1 - y_top

            y.append((y_top, y_bot))

        return y

    @lru_cache()
    def noise(self, noise: Optional[Noise]) -> NoiseData:
        if noise is not None:
            return noise(self.h, self.w * self.inter)
        else:
            return [(0, 0) for _ in range(self.h)]

    @lru_cache()
    def colour(self, colour: Union[str, Iterable, Colour]) -> ColourData:
        if isinstance(colour, str):
            return [colour]
        if isinstance(colour, Iterable):
            return colour
        if isinstance(colour, Colour):
            return colour(self.h)

    def draw(
        self,
        y_range: Tuple[float, float] = (0, 1),
        noise: Optional[Noise] = None,
        colour: Union[str, Iterable, Colour] = 'black',
        modifiers: Optional[Iterable[Modifier]] = None,
        background: Union[str, Tuple] = 'white',
        seed: Optional[int] = None,
        ax: Optional[Axis] = None,
    ) -> figure:
        if seed is not None:
            np.random.seed(seed)

        x = self.x()
        y = self.y(y_range)
        n = self.noise(noise)
        c = self.colour(colour)

        if modifiers is not None:
            for m in modifiers:
                x, y, n, c = m(x, y, n, c)

        if ax is not None:
            self.ax = ax
        self._clear_ax(background)
        for y_, n_, c_ in zip(y, cycle(n), cycle(c)):
            y_top = y_[0] + n_[0]
            y_bot = y_[1] + n_[1]

            self.ax.fill_between(x, y_top, y_bot, color=c_, lw=0)

        return self.fig

    def save(self, path: str) -> None:
        self.fig.savefig(path, dpi=self.dpi, bbox_inches='tight', pad_inches=0)
