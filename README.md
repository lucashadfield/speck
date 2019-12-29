# speck
### render images as a set of parallel lines

[![Python 3.6](https://img.shields.io/badge/python-3.6+-blue.svg)](#)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Example:

```python
from speck.draw import SpeckPlot
from speck.noise import SineNoise
from speck.colour import CmapColour

s = SpeckPlot.from_path(path_str)

s.draw(
    noise=SineNoise(scale=0.7, profile='parallel'),
    y_range=(0.2, 0.6),
    short_edge=12,
    colour=CmapColour('Oranges')
)
```

![Example](https://i.imgur.com/SHUMebO.png)
