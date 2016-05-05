# -*- coding: utf-8 -*-
from .ecospold2_meta import *
from lxml import objectify
from time import time
import multiprocessing
import os
import pprint
import pyprind


def extract_minimal_ecospold2_info(elem):
    data = {
        'name': elem.activityDescription.activity.activityName.text,
        'location': elem.activityDescription.geography.shortname.text,
        'type': SPECIAL_ACTIVITY_TYPE[elem.activityDescription.activity.get('specialActivityType')]
    }
    return data


def parse_element(elem):
    return {
        'tag': str(elem.tag),
        'attributes': dict(elem.attrib),
        'text': str(elem.text or ""),
        'children': [parse_element(child) for child in elem.iterchildren()]
    }


def generic_extractor(filepath):
    with open(filepath, encoding='utf8') as f:
        try:
            root = objectify.parse(f).getroot()
            data = [extract_minimal_ecospold2_info(child)
                    for child in root.iterchildren()]
        except:
            print(filepath)
            raise
    return data


def extract_directory(dirpath, use_mp=True):
    """Extract all the ``.spold`` files in the directory ``dirpath``.

    Use a multiprocessing pool if ``use_mp``, which is the default."""
    assert os.path.isdir(dirpath), "Can't find directory {}".format(dirpath)
    filelist = [os.path.join(dirpath, filename)
                for filename in os.listdir(dirpath)
                if filename.lower().endswith(".spold")
                ][:100]

    print("Extracting {} undefined datasets".format(len(filelist)))

    if use_mp:
        start = time()
        with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
            data = pool.map(generic_extractor, filelist)
        print("Extracted {} undefined datasets in {:.1f} seconds".format(len(data), time() - start))
    else:
        data = []
        for fp in pyprind.prog_bar(filelist):
            data.append(generic_extractor(fp))

    pprint.pprint(data)
