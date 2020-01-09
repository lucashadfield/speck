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
    k = 10  # logistic growth rate on pixel boundaries
    inter = 100  # x-axis points generated between each input image pixel
    dpi = 100  # figure dpi used for plotting and saving

    def __init__(
        self, image: Image, scale_factor: float = 5.0, horizontal: bool = True
    ):
        """
        Create a SpeckPlot from a PIL Image
        :param image: PIL image
        :param scale_factor: the pixel scaling factor, each input pixel maps to scale_factor output pixels
        :param horizontal: use horizontal lines to render the image
        """

        self.image = image
        self.scale_factor = scale_factor
        self.horizontal = horizontal
        if self.horizontal:
            self.im = np.array(image.convert('L'))
        else:
            self.im = np.array(image.convert('L').rotate(-90, expand=1))

        self.h, self.w = self.im.shape
        figsize = self.w * scale_factor / self.dpi, self.h * scale_factor / self.dpi
        self.fig = plt.figure(figsize=figsize if self.horizontal else figsize[::-1])
        self.ax = self.fig.add_axes([0.0, 0.0, 1.0, 1.0], xticks=[], yticks=[])
        plt.close(self.fig)

    @classmethod
    def from_path(
        cls,
        path: str,
        scale_factor: float = 3.0,
        resize: Optional[Tuple] = None,
        horizontal: bool = True,
    ):
        """
        Create a SpeckPlot from an image path
        :param path: path to image file
        :param scale_factor: the pixel scaling factor, each input pixel maps to scale_factor output pixels
        :param resize: dimensions to resize to
        :param horizontal: use horizontal lines to render the image
        """

        image = Image.open(path)
        if resize is not None:
            image = image.resize(resize)
        return cls(image, scale_factor, horizontal)

    @classmethod
    def from_url(
        cls,
        url: str,
        scale_factor: float = 3.0,
        resize: Optional[Tuple] = None,
        horizontal: bool = False,
    ):
        """
        Create SpeckPlot from image URL
        :param url: url string
        :param scale_factor: the pixel scaling factor, each input pixel maps to scale_factor output pixels
        :param resize: dimensions to resize to
        :param horizontal: use horizontal lines to render the image
        """

        import requests
        from io import BytesIO

        image = Image.open(BytesIO(requests.get(url).content))
        if resize is not None:
            image = image.resize(resize)
        return cls(image, scale_factor, horizontal)

    def __repr__(self):
        d = [f'{k}={v}' for k, v in self.__dict__.items() if not k.startswith('_')]
        return f'{self.__class__.__name__}({", ".join(d)})'

    def _clear_ax(self, background: Union[str, Tuple]) -> None:
        self.ax.clear()
        self.ax.set_facecolor(background)
        if self.horizontal:
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
            self._x.cache_clear()
            self._y.cache_clear()
            self._noise.cache_clear()
            self._colour.cache_clear()

    def cache_info(self) -> dict:
        return {
            'x': self._x.cache_info(),
            'y': self._y.cache_info(),
            'noise': self._noise.cache_info(),
            'colour': self._colour.cache_info(),
        }

    @lru_cache()
    def _x(self) -> XData:
        return np.linspace(0, self.w, self.w * self.inter)

    @lru_cache()
    def _y(
        self,
        weights: Tuple[float, float],
        weight_clipping: Tuple[float, float],
        skip: int,
    ) -> YData:
        y_min = weights[0] / 2 + 0.5
        y_max = weights[1] / 2 + 0.5
        clip_min = (1 - weight_clipping[1]) * 255.0
        clip_max = (1 - weight_clipping[0]) * 255.0

        def repeat_head_tail(arr: np.ndarray, n: int) -> np.ndarray:
            return np.insert(
                np.insert(arr, 0, np.ones(n) * arr[0]), -1, np.ones(n) * arr[-1]
            )

        y = []

        for i, line in enumerate(self.im):
            if i % (skip + 1):
                continue

            # apply clipping
            line = (
                (line.clip(clip_min, clip_max) - clip_min) * 255 / (clip_max - clip_min)
            )

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
                L / (1 + np.exp(-self.k * (self._x() - x0)))
            ) + y_offset
            y_bot: np.ndarray = 2 * i + 1 - y_top

            y.append((y_top, y_bot))

        return y

    @lru_cache()
    def _noise(self, noise: Optional[Noise]) -> NoiseData:
        if noise is not None:
            return noise(self.h, self.w * self.inter)
        else:
            return [(0, 0) for _ in range(self.h)]

    @lru_cache()
    def _colour(self, colour: Union[str, Iterable, Colour]) -> ColourData:
        if isinstance(colour, str):
            return [colour]
        if isinstance(colour, Iterable):
            return colour
        if isinstance(colour, Colour):
            return colour(self.h)

    def draw(
        self,
        weights: Tuple[float, float] = (0, 1),
        weight_clipping: Tuple[float, float] = (0, 1),
        noise: Optional[Noise] = None,
        colour: Union[str, Iterable, Colour] = 'black',
        skip: int = 0,
        background: Union[str, Tuple] = 'white',
        modifiers: Optional[Iterable[Modifier]] = None,
        seed: Optional[int] = None,
        ax: Optional[Axis] = None,
    ) -> figure:
        """
        Render the input image to produce a matplotlib figure

        :param weights: min and max line widths
                eg. weights = (0.2, 0.9) =
                    0.2 units of line weight mapped from <= min darkness offset
                    0.9 units of line weight mapped from >= max darkness offset
        :param weight_clipping: proportion of greys that map to min and max thicknesses.
                eg. shade_limits = (0.1, 0.8) =
                    <=10% grey maps to min weight
                    >=80% grey maps to max weight
        :param noise: Noise object that is called and added onto thickness values
        :param colour: Colour object that is called and applied to lines
        :param skip: number of lines of pixels to skip for each plotted line
        :param background: background colour of output plot
        :param modifiers: list of Modifier objects that are iteratively applied to the output x, y, noise and colour data
        :param seed: random seed value
        :param ax: optional Axis object to plot on to
        :return: matplotlib figure object containing the plot
        """

        if seed is not None:
            np.random.seed(seed)

        x = self._x()
        y = self._y(weights, weight_clipping, skip)
        n = self._noise(noise)
        c = self._colour(colour)

        # run modifiers if necessary
        if modifiers is not None:
            for m in modifiers:
                x, y, n, c = m(x, y, n, c)

        # create plot elements
        if ax is not None:
            self.ax = ax
        self._clear_ax(background)
        for y_, n_, c_ in zip(y, cycle(n), cycle(c)):
            y_top = y_[0] + n_[0]
            y_bot = y_[1] + n_[1]

            if self.horizontal:
                self.ax.fill_between(x, y_top, y_bot, color=c_, lw=0)
            else:
                self.ax.fill_betweenx(x, y_top, y_bot, color=c_, lw=0)

        return self.fig

    def save(self, path: str, transparent: bool = False) -> None:
        """
        Save rendered figure to disk. Call this after the draw method
        :param path: path to save location
        :param transparent: whether to save with a transparent background (assuming .png extension)
        """

        self.fig.savefig(
            path,
            dpi=self.dpi,
            bbox_inches='tight',
            pad_inches=0,
            transparent=transparent,
        )
