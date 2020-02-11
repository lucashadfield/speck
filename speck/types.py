__all__ = ['XData', 'YData', 'NoiseData', 'ColourData']

from typing import Union, Iterable, List, Tuple

import numpy as np

XData = np.ndarray
YData = List[Tuple[np.ndarray, np.ndarray]]
NoiseData = List[Tuple[Union[np.ndarray, int], Union[np.ndarray, int]]]
ColourData = Union[Iterable, Iterable[Tuple]]
