# -*- coding: utf-8 -*-
from .ecospold2_meta import *
from lxml import objectify
from time import time
import multiprocessing
import os
import pprint
import pyprind
import signal


def _(string):
    return string.replace("{http://www.EcoInvent.org/EcoSpold02}", "")


def is_combined_production(dataset):
    """"Combined production datasets have multiple reference products.

    Returns a boolean."""
    return len([1 for exc in dataset['exchanges']
                if exc['type'] == "reference product"]) > 1


def parameterize(elem, data):
    parameters = [
        obj for obj in elem.flowData.iterchildren()
        if 'parameter' in obj.tag
    ]
    if not parameters:
        return
    else:
        data['parameters'] = []
    for param in parameters:
        obj = {
            'variable': param.get('variableName'),
            'name': param.name.text,
        }
        if hasattr(param, "uncertainty"):
            obj['uncertainty'] = extract_uncertainty(param.uncertainty)
        formula = param.get('mathematicalRelation')
        if formula:
            obj['formula'] = formula
        data['parameters'].append(obj)


def extract_pedigree_matrix(elem):
    try:
        return tuple([
            int(elem.pedigreeMatrix.get(label))
            for label in PEDIGREE_LABELS
        ])
    except:
        pass


def extract_uncertainty(unc):
    distribution_labels = ['lognormal', 'normal', 'triangular',
                           'uniform', 'undefined']
    distribution = next((getattr(unc, label)
                         for label in distribution_labels
                         if hasattr(unc, label)))
    data = {UNCERTAINTY_MAPPING.get(key, key): float(distribution.get(key)) for key in distribution.keys()}
    data.update({
        'type': _(distribution.tag),
    })
    pm = extract_pedigree_matrix(unc)
    if pm:
        data['pedigree matrix'] = pm
    return data


def extract_compartments(exc):
    try:
        return (
            exc.compartment.compartment.text,
            exc.compartment.subcompartment.text,
        )
    except:
        pass


def extract_production_volume(exc):
    pv = exc.get('productionVolumeAmount')
    if not pv:
        return
    data = {'amount': float(pv)}
    if hasattr(exc, "productionVolumeUncertainty"):
        data['uncertainty'] = extract_uncertainty(exc.productionVolumeUncertainty)
    formula = exc.get('productionVolumeMathematicalRelation')
    if formula:
        data['formula'] = formula
    variable = exc.get('productionVolumeVariableName')
    if variable:
        data['variable'] = variable
    return data


def extract_property(prop):
    data = {
        'id': prop.get('propertyId'),
        'amount': float(prop.get('amount')),
        'name': prop.name.text,
    }
    if hasattr(prop, "uncertainty"):
        data['uncertainty'] = extract_uncertainty(prop.uncertainty)
    if prop.get("variableName"):
        data['variable'] = prop.get("variableName")
    if prop.get("mathematicalRelation"):
        data['formula'] = prop.get("mathematicalRelation")
    return data


def extract_minimal_exchange(exc):
    # Basic data
    data = {
        'id': exc.get('id'),
        'tag': _(exc.tag),
        'name': exc.name.text,
        'unit': exc.unitName.text,
        'amount': float(exc.get('amount')),
        'type': (INPUT_GROUPS[exc.inputGroup.text]
                 if hasattr(exc, "inputGroup")
                 else OUTPUT_GROUPS[exc.outputGroup.text]),
    }

    # Variable and formula will be deleted if dataset is not multioutput
    if exc.get("variableName"):
        data['variable'] = exc.get("variableName")
    if exc.get("mathematicalRelation"):
        data['formula'] = exc.get("mathematicalRelation")

    properties = [extract_property(obj)
                  for obj in exc.iterchildren()
                  if _(obj.tag) == 'property']
    if properties:
        data['properties'] = properties

    # Biosphere compartments
    compartments = extract_compartments(exc)
    if compartments:
        data['compartments'] = compartments

    # Production volume & uncertainty
    pv = extract_production_volume(exc)
    if pv:
        data['production volume'] = pv

    # Uncertainty
    if hasattr(exc, "uncertainty"):
        data['uncertainty'] = extract_uncertainty(exc.uncertainty)

    return data


def extract_minimal_ecospold2_info(elem, filepath):
    data = {
        'filepath': filepath,
        'name': elem.activityDescription.activity.activityName.text,
        'location': elem.activityDescription.geography.shortname.text,
        'type': SPECIAL_ACTIVITY_TYPE[elem.activityDescription.activity.get('specialActivityType')],
        'technology level': TECHNOLOGY_LEVEL[elem.activityDescription.technology.get('technologyLevel')],
        'temporal': (
            elem.activityDescription.timePeriod.get("startDate"),
            elem.activityDescription.timePeriod.get("endDate")
        ),
        'economic': elem.activityDescription.macroEconomicScenario.name.text,
        'exchanges': [extract_minimal_exchange(exc)
                      for exc in elem.flowData.iterchildren()
                      if 'Exchange' in exc.tag]
    }
    if is_combined_production(data):
         # Dataset will require recalculation, so variableName
         # and mathematicalRelation are necessary
        data['combined production'] = True
        parameterize(elem, data)
    else:
        # Don't need parameter or property data because no allocation
        for exc in data['exchanges']:
            if 'formula' in exc:
                del exc['formula']
            if 'properties' in exc:
                del exc['properties']
    return data


def generic_extractor(filepath):
    with open(filepath, encoding='utf8') as f:
        try:
            root = objectify.parse(f).getroot()
            data = [extract_minimal_ecospold2_info(child, filepath)
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
                ]

    print("Extracting {} undefined datasets".format(len(filelist)))

    if use_mp:
        start = time()
        # With code from
        # http://jtushman.github.io/blog/2014/01/14/python-%7C-multiprocessing-and-interrupts/
        with multiprocessing.Pool(
                processes=multiprocessing.cpu_count(),
                initializer=lambda : signal.signal(signal.SIGINT, signal.SIG_IGN)
            ) as pool:
            try:
                data = pool.map(generic_extractor, filelist)
            except KeyboardInterrupt:
                pool.terminate()
                raise KeyboardInterrupt
        print("Extracted {} undefined datasets in {:.1f} seconds".format(len(data), time() - start))
    else:
        data = [generic_extractor(fp)
                for fp in pyprind.prog_bar(filelist)]

    # Unroll lists of lists
    return [y for x in data for y in x]
