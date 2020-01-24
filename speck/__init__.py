from .draw import SpeckPlot
from .noise import *
from .colour import *
from .tools import SpeckWidget
from .modifier import LineUnionModifier

from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution('speck').version
except DistributionNotFound:
    pass
