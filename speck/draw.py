__all__ = ['SpeckPlot']

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import figure
from PIL import Image
from itertools import cycle
from typing import Union, Iterable, Optional, List, Tuple
import logging
from functools import lru_cache

from speck.noise import Noise
from speck.colour import Colour
from speck.modifier import Modifier

logger = logging.getLogger('speck')


class SpeckPlot:
    k = 10
    inter = 100

    def __init__(self, image: Image, fig_short_edge: float = 10.0):
        self.image = image
        self.fig_short_edge = fig_short_edge
        self.im = np.array(image.convert('L'))
        self.h, self.w = self.im.shape

        self.fig, self.ax = plt.subplots(
            figsize=[
                x * fig_short_edge / min((self.w, self.h)) for x in (self.w, self.h)
            ]
        )
        plt.close(self.fig)

    @classmethod
    def from_path(
        cls, path: str, resize: Optional[Tuple] = None, fig_short_edge: float = 10.0
    ):
        image = Image.open(path)
        if resize is not None:
            image = image.resize(resize)
        return cls(image, fig_short_edge)

    @classmethod
    def from_url(
        cls, url: str, resize: Optional[Tuple] = None, fig_short_edge: float = 10.0
    ):
        import requests
        from io import BytesIO

        image = Image.open(BytesIO(requests.get(url).content))
        if resize is not None:
            image = image.resize(resize)
        return cls(image, fig_short_edge)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.image}, {self.fig_short_edge})'

    def _clear_ax(self, background) -> None:
        self.ax.clear()
        self.ax.set_facecolor(background)
        self.ax.invert_yaxis()
        self.ax.spines['left'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['bottom'].set_visible(False)
        self.ax.set_xticks([])
        self.ax.set_yticks([])

    def cache_clear(self, method: Optional[str] = None) -> None:
        if method is not None:
            getattr(self, method).cache_clear()
        else:
            self.x.cache_clear()
            self.y.cache_clear()
            self.noise.cache_clear()
            self.colour.cache_clear()

    @lru_cache()
    def x(self) -> np.ndarray:
        return np.linspace(0, self.w, self.w * self.inter)

    @lru_cache()
    def y(self, y_range: Tuple[float, float]) -> List[Tuple[np.ndarray, np.ndarray]]:
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
    def noise(
        self, noise: Optional[Noise]
    ) -> List[Tuple[Union[np.ndarray, int], Union[np.ndarray, int]]]:
        if noise is not None:
            return noise(self.h, self.w * self.inter)
        else:
            return [(0, 0) for _ in self.h]

    @lru_cache()
    def colour(
        self, colour: Union[str, Iterable, Colour]
    ) -> Union[Iterable, Iterable[Tuple]]:
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

        self._clear_ax(background)
        for y_, n_, c_ in zip(y, cycle(n), cycle(c)):
            y_top = y_[0] + n_[0]
            y_bot = y_[1] + n_[1]

            self.ax.fill_between(x, y_top, y_bot, color=c_, lw=0)

        return self.fig
