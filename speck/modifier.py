__all__ = ['LineThicknessModifier']

import numpy as np
from typing import List, Iterable, Tuple, Union, Callable
from functools import partial

from speck.types import XData, YData, NoiseData, ColourData


class Modifier:
    def __call__(
        self, x: XData, y: YData, n: NoiseData, c: ColourData,
    ) -> Tuple[
        XData, YData, NoiseData, ColourData,
    ]:
        raise NotImplementedError


class LineThicknessModifier(Modifier):
    def __init__(
        self, thicknesses: Iterable[int], aggregation: Union[str, Callable] = 'sum'
    ):
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

    def __call__(self, x, y, n, c):
        if sum(self.thicknesses) != len(y):
            raise AssertionError('sum(thicknesses) != number of lines')

        pos = 0
        y_ = []
        for t in self.thicknesses:
            y_top = (
                self.aggregation([y[pos + i][0] - pos + i - 0.5 for i in range(t)])
                + pos
                + t / 2
            )
            y_bot = (
                self.aggregation([y[pos + i][1] - pos + i - 0.5 for i in range(t)])
                + pos
                + t / 2
            )

            y_.append((y_top, y_bot))
            pos += t

        return x, y_, n, c
