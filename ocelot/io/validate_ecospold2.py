# -*- coding: utf-8 -*-
from lxml import etree
import os
import pprint
import pyprind


def validate_directory(dirpath, schema):
    """Extract all the ``.spold`` files in the directory ``dirpath``.

    Use a multiprocessing pool if ``use_mp``, which is the default."""
    assert os.path.isdir(dirpath), "Can't find data directory {}".format(dirpath)
    assert os.path.isfile(schema), "Can't find schema file {}".format(schema)

    filelist = [os.path.join(dirpath, filename)
                for filename in os.listdir(dirpath)
                if filename.lower().endswith(".spold")
                ]

    print("Validating {} undefined datasets".format(len(filelist)))

    errors = []
    ecospold2_schema = etree.XMLSchema(etree.parse(open(schema)))

    for fp in pyprind.prog_bar(filelist):
        file = etree.parse(open(fp))
        if not ecospold2_schema.validate(file):
            errors.append(os.path.basename(fp))

    if errors:
        print("The following files did not validate:")
        pprint.pprint(errors)
    else:
        print("All files valid")
