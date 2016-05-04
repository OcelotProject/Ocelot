# -*- coding: utf-8 -*-
from lxml import objectify
import multiprocessing
import os
import pyprind


def rewrite_file(fp):
    try:
        objectify.parse(f)
    except:
        with open(fp, encoding='utf8') as f:
            lines = [line.replace("< ", "&lt; ") for line in f]
        with open(fp, "w", encoding='utf8') as f:
            for line in lines:
                f.write(line)


def xmlify_directory(dirpath):
    """Fix invalid XML files which don't quote '<'.

    Grumble grumble...

    We use '< ' to find the offending elements, but this is suboptimal."""
    assert os.path.isdir(dirpath), "Can't find directory {}".format(dirpath)
    filelist = [os.path.join(dirpath, filename)
                for filename in os.listdir(dirpath)
                if filename.lower().endswith(".spold")
                ]
    for fp in pyprind.prog_bar(filelist):
        rewrite_file(fp)
