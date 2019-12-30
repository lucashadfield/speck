import numpy as np
from typing import List, Iterable, Tuple, Union, Callable
from functools import partial


class Modifier:
    def __call__(
        self,
        x: np.ndarray,
        y: List[Tuple[np.ndarray, np.ndarray]],
        n: List[Tuple[Union[np.ndarray, int], Union[np.ndarray, int]]],
        c: Union[Iterable, Iterable[Tuple]],
    ) -> Tuple[
        np.ndarray,
        List[Tuple[np.ndarray, np.ndarray]],
        List[Tuple[Union[np.ndarray, int], Union[np.ndarray, int]]],
        Union[Iterable, Iterable[Tuple]],
    ]:
        raise NotImplementedError


class LineThickness(Modifier):
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
