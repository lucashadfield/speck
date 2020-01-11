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

### Install:
```
pip3 install git+https://github.com/lucashadfield/speck.git
```


### Basic Example:

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


### Interactive Widget
```python
from speck import SpeckPlot, SpeckWidget
s = SpeckPlot.from_path('...', resize=(100, 100), scale_factor=10)
SpeckWidget(s).interact()
```


### Configuration Parameters:
Output is configured based on the arguments passed to the `draw` method of `SpeckPlot`

**Basic options:**
- `weights`: min and max line widths
        
        eg. weights = (0.2, 0.9) =
            0.2 units of line weight mapped from <= min weight clipping 
                (if weight_clipping is (0, 1), white is 0.2 units thick)
            0.9 units of line weight mapped from >= max weight clipping 
                (if weight_clipping is (0, 1), black is 0.9 units thick)
- `weight_clipping`: proportion of greys that map to min and max thicknesses.
        
        eg. weight_clipping = (0.1, 0.8) =
            <=10% grey maps to min weight
            >=80% grey maps to max weight
- `noise`: Noise object that is called and added onto thickness values (see below)
- `colour`: Colour object that is called and applied to lines (see below)
- `skip`: number of lines of pixels to skip for each plotted line
- `background`: background colour of output plot
- `modifiers`: list of Modifier objects that are iteratively applied to the output x, y, noise and colour data (see below)
- `seed`: random seed value
- `ax`: optional Axis object to plot on to

**Colour Profile options:**
- `GradientColour`: Colours each line according to a generated colour between the provided checkpoint colours.
- `CmapColour`: Colour each line according to pre-defined matplotlib cmap.
- `KMeansColour`: Clusters each horizontal line of pixel colour values into k groups using k-means to determine the dominant colour of that row, and then sets the line colour to that.
- `GreyscaleMeanColour`: Takes the mean greyscale colour of each row of pixels and makes the line that colour.
- Create your own by inheriting from Colour.

**Noise Profile options:**
- `SineNoise`: Random smooth noise based on the product of multiple random sine waves.
- `RandomNoise`: Random static noise with some averaging. (slow)
- Create your own by inheriting from Noise.

**Modifier Profile options:**
- `LineUnionModifier`: Combines multiple rendered lines together to allow for building more complex line weight profiles.
- Create your own by inheriting from Modifier