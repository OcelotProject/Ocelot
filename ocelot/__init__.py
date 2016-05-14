# -*- coding: utf-8 -*-
__all__ = (
    "Configuration",
    "data_dir",
    "SystemModel",
    "Report",
)


CYTOOLZ = """Functional programming library cytoolz not found.

Please consider installing the cytoolz library using a package manager
or http://www.lfd.uci.edu/~gohlke/pythonlibs/ (for Windows). There
are significant speedups versus the pure-python library toolz.

See https://github.com/pytoolz/cytoolz for more information."""

try:
    import cytoolz as toolz
except ImportError:
    import warnings
    import toolz
    warnings.warn(CYTOOLZ)

from .data import data_dir
from .io import *
from .configuration import Configuration, default_configuration
from .model import SystemModel
from .report import Report
