![speck](https://i.imgur.com/MFWe4EW.png)
======

[![Python 3.6](https://img.shields.io/badge/python-3.6+-blue.svg)](#)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


Render images as a set of continuous lines representing each horizontal (or vertical) line of pixels:
- Line weights vary with greyscale pixel darkness.
- Set line weight range and clipping.
- Add noise profiles to introduce randomness.
- Add colour profiles to vary line colours.
- Use ipywidget to tweak outputs interactively

## Basic Example:

```python
from speck import SpeckPlot, SineNoise, CmapColour

s = SpeckPlot.from_path(path='...')

s.draw(
    weights=(0.2, 0.6),
    noise=SineNoise(scale=0.7),
    colour=CmapColour('Oranges')
)

s.save(path='...')
```

![Example](https://i.imgur.com/SHUMebO.png)


## Interactive Widget
```python
from speck import SpeckPlot, SpeckWidget
s = SpeckPlot.from_path('...', resize=(100, 100), scale_factor=10)
SpeckWidget(s).interact()
```
