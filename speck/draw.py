__all__ = ['Streaks']

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from itertools import cycle
from typing import Union, Iterable, Generator
import logging

from speck.noise import Noise
from speck.colour import Colour

logger = logging.getLogger('speck')


class Streaks:
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
        return cls(Image.open(path).convert('L'))

    @property
    def x(self):
        return np.linspace(0, self.w, self.w * self.inter)

    @property
    def y(self):
        if self.y_noise is not None:
            return [
                (y[0] + yn[0], y[1] + yn[1]) for y, yn in zip(self._y, self.y_noise)
            ]
        else:
            return self._y

    def _set_param(self, param: str, value) -> bool:
        if getattr(self, param) == value:
            return False
        setattr(self, param, value)
        return True

    def _create_fig(self, short_edge):
        scale = short_edge / min((self.w, self.h))
        self.fig, self.ax = plt.subplots(figsize=[x * scale for x in (self.w, self.h)])
        self.ax.invert_yaxis()
        self.ax.spines['left'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['bottom'].set_visible(False)
        self.ax.set_xticks([])
        self.ax.set_yticks([])

    @staticmethod
    def _repeat_head_tail(arr, n):
        return np.insert(
            np.insert(arr, 0, np.ones(n) * arr[0]), -1, np.ones(n) * arr[-1]
        )

    def _set_data(self):
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

            y_top = i + (L / (1 + np.exp(-self.k * (self.x - x0)))) + y_offset
            y_bot = 2 * i + 1 - y_top

            self._y.append((y_top, y_bot))

        self._apply_noise()

    def _apply_noise(self):
        if self.noise is not None:
            self.y_noise = self.noise(self.h, self.w * self.inter)
        else:
            self.y_noise = None

        self._apply_colour()

    @staticmethod
    def cycle_to_n(it: Iterable, n: int) -> Generator:
        if isinstance(it, str):
            it = [it]
        return (i for i, _ in zip(cycle(it), range(n)))

    def _apply_colour(self):
        if isinstance(self.colour, (str, Iterable)):
            self.y_colour = self.cycle_to_n(self.colour, self.h)
        else:
            self.y_colour = self.cycle_to_n(self.colour(self.h), self.h)

    def draw(
        self,
        y_range: tuple = (0, 1),
        noise: Noise = None,
        colour: Union[str, Iterable, Colour] = 'black',
        k: int = 10,
        inter: int = 100,
        short_edge: float = 10.0,
        seed=None,
    ):
        if seed is not None:
            np.random.seed(seed)

        # set where to start cascading updates from based on which parameters changed
        # "lower" starting points for the function cascade are set earlier
        cascade_func = None

        # if colour param changed (independent of changes in noise and data)
        if self._set_param('colour', colour):
            cascade_func = self._apply_colour

        # if noise param changed (independent of changes in data)
        if self._set_param('noise', noise):
            cascade_func = self._apply_noise

        # if data params changed
        if (
            self._set_param('k', k)
            | self._set_param('inter', inter)
            | self._set_param('y_range', y_range)
        ):
            cascade_func = self._set_data

        # run cascade
        if cascade_func is not None:
            logger.info(f'Cascading from {cascade_func.__name__}')
            cascade_func()

        # plot data
        self._create_fig(short_edge)

        for y, c in zip(self.y, self.y_colour):
            self.ax.fill_between(self.x, *y, color=c, lw=0)
