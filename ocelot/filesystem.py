# -*- coding: utf-8 -*-
import hashlib
import os
import re
import unicodedata
import appdirs

re_slugify = re.compile('[^\w\s-]', re.UNICODE)


def safe_filename(string):
    """Convert arbitrary strings to make them safe for filenames. Substitutes strange characters, and uses unicode normalization.

    Appends hash of `string` to avoid name collisions.

    From http://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename-in-python"""
    safe = re.sub(
        '[-\s]+',
        '-',
        str(
            re_slugify.sub(
                '',
                unicodedata.normalize('NFKD', str(string))
            ).strip()
        )
    )
    if isinstance(string, str):
        string = string.encode("utf8")
    return safe + "." + hashlib.md5(string).hexdigest()


def create_dir(dirpath):
    """Create directory tree to `dirpath`; ignore if already exists"""
    if not os.path.isdir(dirpath):
        os.makedirs(dirpath)
    return dirpath


def check_dir(directory):
    """Returns ``True`` if given path is a directory and writeable, ``False`` otherwise."""
    return os.path.isdir(directory) and os.access(directory, os.W_OK)


def get_base_output_directory():
    """Get base directory for model run.

    Try the environment variable OCELOT_OUTPUT first, fall back to `appdirs <https://pypi.python.org/pypi/appdirs>`__"""
    try:
        return create_dir(os.environ['OCELOT_OUTPUT'])
    except KeyError:
        return create_dir(appdirs.user_data_dir("Ocelot", "ocelot_runs"))
