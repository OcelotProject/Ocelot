CYTOOLZ = """Funciontal programming library cytoolz not found.

Please consider installing the cytoolz library using a package manager
or http://www.lfd.uci.edu/~gohlke/pythonlibs/ (for Windows). There
are significant speedups.

See https://github.com/pytoolz/cytoolz for more information."""

try:
    import cytoolz
except ImportError:
    import warnings
    warnings.warn(CYTOOLZ)

from .data import data_dir
from .io import extract_directory, xmlify_directory, validate_directory
