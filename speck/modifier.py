import numpy as np
from typing import Tuple


class Modifier:
    def __call__(
        self, x: np.ndarray, y_top: np.ndarray, y_bot: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        raise NotImplementedError
