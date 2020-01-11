__all__ = ['GradientColour', 'CmapColour', 'KMeansColour', 'GreyscaleMeanColour']

import numpy as np
import matplotlib as mpl
from typing import Union, Iterable, List, Tuple
import cv2


class Colour:
    def __repr__(self):
        """
        Auto __repr__ based on instance __dict__
        Parameters with a leading _ are omitted from the repr and thus from the hash
        """

        d = [f'{k}={v}' for k, v in self.__dict__.items() if not k.startswith('_')]
        return f'{self.__class__.__name__}({", ".join(d)})'

    def __hash__(self):
        h = []
        for k, v in self.__dict__.items():
            if not k.startswith('_'):
                h.append(tuple(v) if isinstance(v, list) else v)

        return hash(tuple(h))

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __call__(self, m: int) -> Iterable[Tuple]:
        raise NotImplementedError


class GradientColour(Colour):
    def __init__(self, colour_list: Tuple):
        """
        Create GradientColour object to be passed to SpeckPlot.draw method.
        Colours each line according to a generated colour between the provided checkpoint colours.
        :param colour_list: colours between which colour gradients are generated to colour each line
        """

        if len(colour_list) == 1:
            colour_list = [colour_list[0], colour_list[0]]
        self.colour_list = colour_list
        self._cmap = mpl.colors.LinearSegmentedColormap.from_list("", colour_list)

    def __call__(self, m: int) -> Iterable[Tuple]:
        return [self._cmap(x) for x in np.linspace(0, 1, m, endpoint=False)]


class CmapColour(Colour):
    def __init__(self, cmap: Union[str, mpl.colors.Colormap]):
        """
        Create CmapColour object to be passed to SpeckPlot.draw method.
        Colour each line according to pre-defined matplotlib cmap.
        :param cmap: matplotlib cmap object or name to generate line colours according to
        """

        self.cmap = mpl.cm.get_cmap(cmap) if isinstance(cmap, str) else cmap

    def __call__(self, m: int) -> Iterable[Tuple]:
        return [self.cmap(x) for x in np.linspace(0, 1, m, endpoint=False)]


class KMeansColour(Colour):
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.1)
    flags = cv2.KMEANS_RANDOM_CENTERS

    def __init__(self, speck_plot, k: int = 5):
        """
        Create KMeansColour object to be passed to SpeckPlot.draw method.
        Clusters each horizontal line of pixel colour values into k groups using k-means to determine
        the dominant colour of that row, and then sets the line colour to that.
        :param speck_plot: SpeckPlot object to base colours on
        :param k: number of groups for k-means
        """

        if speck_plot.image.mode != 'RGB':
            raise AssertionError('KMeansColour requires RGB image mode')

        self.k = k
        self.im = np.array(speck_plot.image)

    def _kmeans_colour(self, row: np.ndarray) -> Tuple:
        _, labels, palette = cv2.kmeans(
            row, self.k, None, self.criteria, 10, self.flags
        )
        _, counts = np.unique(labels, return_counts=True)

        return palette[np.argmax(counts)] / 255

    def __call__(self, m: int) -> Iterable[Tuple]:
        return np.squeeze(
            np.apply_along_axis(self._kmeans_colour, 1, np.float32(self.im))
        )


class GreyscaleMeanColour(Colour):
    def __init__(self, speck_plot):
        """
        Create GreyScacleMeanColour objrect to be passed to SpeckPlot.draw method.
        Takes the mean greyscale colour of each row of pixels and makes the line that colour.
        :param speck_plot: SpeckPlot object to base colours on
        """

        self.im = speck_plot.im

    def __call__(self, m: int) -> Iterable[Tuple]:
        return [(c, c, c) for c in np.array(self.im).mean(1) / 255.0]
