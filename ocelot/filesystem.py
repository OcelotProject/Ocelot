# -*- coding: utf-8 -*-
import appdirs
import hashlib
import os
import pickle
import re
import unicodedata
import uuid

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


def get_output_directory():
    """Get base directory for model run.

    Try the environment variable OCELOT_OUTPUT first, fall back to the base directory plus ``model-runs``."""
    try:
        env_var = create_dir(os.environ['OCELOT_OUTPUT'])
        assert env_var
        print("Using environment variable OCELOT_OUTPUT:\n", env_var)
        return env_var
    except:
        return create_dir(os.path.join(get_base_directory(), "model-runs"))


def get_cache_directory():
    """Return base directory where cache data (already extracted datasets) are saved.

    Creates directory if it is not already present."""
    dp = create_dir(os.path.join(get_base_directory(), "cache"))
    assert check_dir(dp), "Can't use cache directory:\n{}".format(dp)
    return dp


def get_base_directory():
    """Return base directory where cache and output data are saved.

    Creates directory if it is not already present."""
    return create_dir(appdirs.user_data_dir("Ocelot", "ocelot_project"))


def get_cache_filepath_for_data_path(data_path):
    """Return the cache directory for source directory ``data_path``.

    The cache filepath is in the directory returned by ``get_cache_directory``. The file name is the MD5 hash of the string ``data_path`` plus ``".pickle"``"""
    return os.path.join(
        get_cache_directory(),
        hashlib.md5(data_path.encode("utf-8")).hexdigest() + ".pickle"
    )


def check_cache_directory(data_path):
    """Check that the data in the cache directory for source directory ``data_path`` is still fresh.

    Returns a boolean."""
    assert os.path.isdir(data_path), "Invalid path for ``data_path``: {}".format(data_path)
    cache_fp = get_cache_filepath_for_data_path(data_path)
    cache_time = os.stat(cache_fp).st_mtime
    source_time = os.stat(data_path).st_mtime
    return cache_time > source_time


def get_from_cache(data_path):
    """Return cached extracted data from directory ``data_path``.

    This function only loads the pickled cache data; use ``check_cache_directory`` to make sure cache is not expired."""
    return pickle.load(open(get_cache_filepath_for_data_path(data_path), "rb"))


def cache_data(data, data_path):
    """Write extracted ``data`` from source directory ``data_path`` to cache directory for future use."""
    with open(get_cache_filepath_for_data_path(data_path), "wb") as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)


class OutputDir(object):
    """OutputDir is responsible for creating and managing a model run output directory."""
    def __init__(self, dir_path=None):
        """Create the job id and output directory"""
        self.report_id = uuid.uuid4().hex
        if dir_path is None:
            dir_path = get_output_directory()
        self.directory = os.path.join(dir_path, self.report_id)
        try:
            create_dir(self.directory)
            assert check_dir(self.directory)
        except:
            raise OutputDirectoryError(
                "Can't find or write to output directory:\n\t{}".format(
                self.directory)
            )
