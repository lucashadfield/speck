import numpy as np
from typing import List, Iterable, Tuple, Union


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
    def __init__(self, thicknesses: Iterable[int]):
        if 0 in thicknesses:
            raise AssertionError('Invalid thickness: 0')
        self.thicknesses = thicknesses

    def __call__(self, x, y, n, c):
        if sum(self.thicknesses) != len(y):
            raise AssertionError('sum(thicknesses) != number of lines')

        pos = 0
        y_ = []
        for t in self.thicknesses:
            new_t = sum([abs(y[pos + i][0] - y[pos + i][1]) for i in range(t)])
            y_.append((pos + t / 2 + new_t / 2, pos + t / 2 - new_t / 2))
            pos += t

        return x, y_, n, c
