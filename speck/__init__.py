from .draw import SpeckPlot
from .noise import *
from .colour import *

from pkg_resources import get_distribution

__version__ = get_distribution('speck').version
