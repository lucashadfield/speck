import pytest
import os

from speck.draw import SpeckPlot
from speck.noise import SineNoise, RandomNoise
from speck.colour import GradientColour, CmapColour, KMeansColour, GreyscaleMeanColour

try:
    import argument_randomiser as ar
except ModuleNotFoundError as e:
    raise type(e)(
        "No module named 'argument_randomiser', install with: pip3 install git+https://github.com/lucashadfield/argument_randomiser.git"
    )


IMAGE_PATH = os.path.join(os.path.dirname(__file__), 'resources/speck.jpg')
SAVE_FIG = {'dpi': 100, 'bbox_inches': 'tight', 'pad_inches': 0}
COLOURS = (
    '#2e3440',
    '#3b4252',
    '#434c5e',
    '#4c566a',
    '#d8dee9',
    '#e5e9f0',
    '#eceff4',
    '#8fbcbb',
    '#88c0d0',
    '#81a1c1',
    '#5e81ac',
    '#bf616a',
    '#d08770',
    '#ebcb8b',
    '#a3be8c',
    '#b48ead',
)
CMAPS = (
    'viridis',
    'cividis',
    'Greys',
    'Oranges',
    'YlGn',
    'PuBuGn',
    'PiYG',
    'twilight',
    'Set2',
    'terrain',
)


@pytest.fixture('session')
def speck_plot():
    s = SpeckPlot.from_path(IMAGE_PATH, scale=3, resize=None, horizontal=True)
    s.draw = ar.randargs()(s.draw)
    return s


@pytest.fixture('session')
def sine_noise_cls():
    return ar.randargs()(SineNoise)


@pytest.fixture('session')
def colour_gradient_cls():
    return ar.randargs()(GradientColour)


@pytest.fixture('session')
def colour_cmap_cls():
    return ar.randargs()(CmapColour)


@pytest.mark.parametrize('seed', range(25))
@pytest.mark.mpl_image_compare(savefig_kwargs=SAVE_FIG)
def test_sine_colour_gradient(speck_plot, sine_noise_cls, colour_gradient_cls, seed):
    x = ar.IntRandomiser(1, 1000, seed=seed)

    return speck_plot.draw(
        weights=ar.FloatRandomiser(0, 1, 2, ordered=False, seed=x()),
        weight_clipping=ar.FloatRandomiser(0, 1, 2, ordered=True, seed=x()),
        noise=sine_noise_cls(
            scale=ar.FloatRandomiser(0, 2, seed=x()),
            wave_count=ar.IntRandomiser(1, 10, seed=x()),
            base_freq=ar.FloatRandomiser(1, 10, seed=x()),
            freq_factor=ar.FloatRandomiser(1, 10, size=2, seed=x()),
            phase_offset_range=(0, ar.FloatRandomiser(0, 360, seed=x())),
        ),
        colour=colour_gradient_cls(
            colour_list=ar.SelectionRandomiser(
                COLOURS,
                size=ar.IntRandomiser(2, 4, seed=x()),
                repalcement=True,
                seed=x(),
            )
        ),
        skip=ar.IntRandomiser(0, 3, seed=x()),
        background=ar.SelectionRandomiser(COLOURS, seed=x()),
        seed=x(),
    )


@pytest.mark.parametrize('seed', range(25))
@pytest.mark.mpl_image_compare(savefig_kwargs=SAVE_FIG)
def test_sine_colour_cmap(speck_plot, sine_noise_cls, colour_cmap_cls, seed):
    x = ar.IntRandomiser(1001, 2000, seed=seed)

    return speck_plot.draw(
        weights=ar.FloatRandomiser(0, 1, 2, ordered=False, seed=x()),
        weight_clipping=ar.FloatRandomiser(0, 1, 2, ordered=True, seed=x()),
        noise=sine_noise_cls(
            scale=ar.FloatRandomiser(0, 2, seed=x()),
            wave_count=ar.IntRandomiser(1, 10, seed=x()),
            base_freq=ar.FloatRandomiser(1, 10, seed=x()),
            freq_factor=ar.FloatRandomiser(1, 10, size=2, seed=x()),
            phase_offset_range=(0, ar.FloatRandomiser(0, 360, seed=x())),
        ),
        colour=colour_cmap_cls(ar.SelectionRandomiser(CMAPS, seed=x())),
        skip=ar.IntRandomiser(0, 3, seed=x()),
        background=ar.SelectionRandomiser(COLOURS, seed=x()),
        seed=x(),
    )
