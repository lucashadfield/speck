__all__ = ['XData', 'YData', 'NoiseData', 'ColourData']

import numpy as np
from typing import Union, Iterable, Optional, List, Tuple

XData = np.ndarray
YData = List[Tuple[np.ndarray, np.ndarray]]
NoiseData = List[Tuple[Union[np.ndarray, int], Union[np.ndarray, int]]]
ColourData = Union[Iterable, Iterable[Tuple]]
