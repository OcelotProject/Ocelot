# -*- coding: utf-8 -*-
from . import extract_directory
from .validate_internal import dataset_schema
from lxml import etree
from voluptuous import Invalid
import os
import pprint
import pyprind


def validate_directory_against_xsd(dirpath, schema):
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


def validate_directory(dirpath):
    data, errors = extract_directory(dirpath, False), {}
    print("Validating datasets:")
    for ds in pyprind.prog_bar(data):
        try:
            dataset_schema(ds)
        except Invalid as err:
            errors[err.msg] = {"path": err.path, "dataset": ds}
    if errors:
        logfile = "ocelot-validation-errors.log"
        errors = [(k, v['path'], v['dataset']) for k, v in errors.items()]
        print("{} errors found.\nSee error logfile {} for details.".format(
            len(errors), logfile)
        )
        with open(logfile, "w", encoding='utf-8') as f:
            f.write("Internal validation errors for extracted directory:\n{}\n".format(dirpath))
            f.write(pprint.pformat(errors, width=120, compact=True))
    else:
        print("No errors found")
