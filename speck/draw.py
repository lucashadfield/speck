__all__ = ['SpeckPlot']

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from itertools import cycle
from typing import Union, Iterable, Optional, List, Tuple
import logging

from speck.noise import Noise
from speck.colour import Colour
from speck.modifier import Modifier

logger = logging.getLogger('speck')


class SpeckPlot:
    def __init__(self, image: Image):
        self.image = image
        self.im = np.array(image.convert('L'))
        self.h, self.w = self.im.shape

        self.k = None
        self.inter = None
        self.y_range = None
        self.noise = None
        self.colour = None

    @classmethod
    def from_path(cls, path: str):
        return cls(Image.open(path))

    @staticmethod
    def _repeat_head_tail(arr: np.ndarray, n: int) -> np.ndarray:
        return np.insert(
            np.insert(arr, 0, np.ones(n) * arr[0]), -1, np.ones(n) * arr[-1]
        )

    @staticmethod
    def _zip_cycle(a, b) -> zip:
        if isinstance(b, str):
            b = [b]
        elif len(b) > len(a):
            b = b[: len(a)]
        return zip(a, cycle(b))

    def _set_param(self, param: str, value) -> bool:
        if getattr(self, param) == value:
            return False
        setattr(self, param, value)
        return True

    @property
    def y(self) -> List[Tuple[np.ndarray, np.ndarray]]:
        if self._y_noise is not None:
            return [
                (y[0] + yn[0], y[1] + yn[1]) for y, yn in zip(self._y, self._y_noise)
            ]
        else:
            return self._y

    def _create_fig(self, short_edge) -> None:
        scale = short_edge / min((self.w, self.h))
        self.fig, self.ax = plt.subplots(figsize=[x * scale for x in (self.w, self.h)])
        self.ax.invert_yaxis()
        self.ax.spines['left'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['bottom'].set_visible(False)
        self.ax.set_xticks([])
        self.ax.set_yticks([])

    def _set_x_y(self) -> None:
        self.x = np.linspace(0, self.w, self.w * self.inter)

        y_min = self.y_range[0] / 2 + 0.5
        y_max = self.y_range[1] / 2 + 0.5

        self._y = []

        for i, line in enumerate(self.im):
            y_offset = np.repeat(y_max - line[:-1] * (y_max - y_min) / 255, self.inter)
            L = (
                np.repeat(y_max - line[1:] * (y_max - y_min) / 255, self.inter)
                - y_offset
            )
            x0 = np.repeat(np.arange(1, self.w), self.inter)

            y_offset = self._repeat_head_tail(y_offset, self.inter // 2)
            L = self._repeat_head_tail(L, self.inter // 2)
            x0 = self._repeat_head_tail(x0, self.inter // 2)

            y_top: np.ndarray = i + (
                L / (1 + np.exp(-self.k * (self.x - x0)))
            ) + y_offset
            y_bot: np.ndarray = 2 * i + 1 - y_top

            self._y.append((y_top, y_bot))

    def _apply_noise(self) -> None:
        if self.noise is not None:
            self._y_noise = self.noise(self.h, self.w * self.inter)
        else:
            self._y_noise = None

    def _apply_colour(self) -> None:
        if isinstance(self.colour, (str, Iterable)):
            self.y_colour = self.colour
        else:
            self.y_colour = self.colour(self.h)

    def _plot(self, short_edge, modifier) -> None:
        self._create_fig(short_edge)

        for (y_top, y_bot), c in self._zip_cycle(self.y, self.y_colour):
            x = self.x
            if modifier is not None:
                x, y_top, y_bot = modifier(x, y_top, y_bot)

            self.ax.fill_between(x, y_top, y_bot, color=c, lw=0)

    def draw(
        self,
        y_range: tuple = (0, 1),
        noise: Optional[Noise] = None,
        colour: Union[str, Iterable, Colour] = 'black',
        k: int = 10,
        inter: int = 100,
        short_edge: float = 10.0,
        modifier: Optional[Modifier] = None,
        seed: Optional[int] = None,
    ) -> None:
        if seed is not None:
            np.random.seed(seed)

        update_funcs = TaskList()
        if self._set_param('inter', inter):
            update_funcs.append([self._set_x_y, self._apply_noise])
        if self._set_param('k', k) | self._set_param('y_range', y_range):
            update_funcs.append([self._set_x_y])
        if self._set_param('noise', noise):
            update_funcs.append([self._apply_noise])
        if self._set_param('colour', colour):
            update_funcs.append([self._apply_colour])

        for func in update_funcs:
            func()

        # plot data
        self._plot(short_edge, modifier)


class TaskList(list):
    def append(self, items: list) -> None:
        for i in items:
            if i not in self:
                super().append(i)
