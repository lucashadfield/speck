__all__ = ['LineUnionModifier']

from typing import Iterable, Tuple, Union, Callable
from functools import partial
from abc import ABC, abstractmethod

import numpy as np

from speck.types import XData, YData, NoiseData, ColourData


class Modifier(ABC):
    @abstractmethod
    def __call__(
        self, x: XData, y: YData, n: NoiseData, c: ColourData,
    ) -> Tuple[
        XData, YData, NoiseData, ColourData,
    ]:
        pass


class LineUnionModifier(Modifier):
    def __init__(
        self, thicknesses: Iterable[int], aggregation: Union[str, Callable] = 'sum'
    ):
        """
        Combines multiple rendered lines together to allow for building more complex line weight profiles
        :param thicknesses: list of number of lines to combine. sum(thicknesses) should equal speck_plot.h, eg.
                    thicknesses = [1, 2, 3, 4, 5] =>
                        - first line is 1 line thick
                        - second line is the union of second and third line
                        - third line is the union of the next 3 lines, etc...
                        - speck_plot.h should be 15 in this example
        :param aggregation: aggregation method to apply to sets of combined lines
        """

        if 0 in thicknesses:
            raise AssertionError('Invalid thickness: 0')
        self.thicknesses = thicknesses

        if isinstance(aggregation, str):
            if aggregation not in ['sum', 'mean']:
                raise ValueError(
                    'Unsupported aggregation: Supported aggregations are sum, mean or custom Callable'
                )
            aggregation = (
                partial(np.sum, axis=0)
                if aggregation == 'sum'
                else partial(np.mean, axis=0)
            )

        self.aggregation = aggregation

    def __call__(
        self, x: XData, y: YData, n: NoiseData, c: ColourData,
    ) -> Tuple[
        XData, YData, NoiseData, ColourData,
    ]:
        if sum(self.thicknesses) != len(y):
            raise AssertionError('sum(thicknesses) != number of lines')

        pos = 0
        y_ = []
        for t in self.thicknesses:
            y_top = (
                self.aggregation([y[pos + i][0] - pos - i - 0.5 for i in range(t)])
                + pos
                + t / 2
            )
            y_bot = (
                self.aggregation([y[pos + i][1] - pos - i - 0.5 for i in range(t)])
                + pos
                + t / 2
            )

            y_.append((y_top, y_bot))
            pos += t

        return x, y_, n, c
