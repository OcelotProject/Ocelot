# -*- coding: utf-8 -*-
from .ecospold2_meta import (
    ACCESS_RESTRICTED,
    BYPRODUCT_CLASSIFICATION,
    INPUT_GROUPS,
    OUTPUT_GROUPS,
    PEDIGREE_LABELS,
    SPECIAL_ACTIVITY_TYPE,
    TECHNOLOGY_LEVEL,
    UNCERTAINTY_MAPPING,
)
from lxml import objectify
from time import time
import multiprocessing
import os
import pyprind
import signal


def _(string):
    return string.replace("{http://www.EcoInvent.org/EcoSpold02}", "")


def is_combined_production(dataset):
    """"Combined production datasets have multiple reference products.

    Returns a boolean."""
    return len([1 for exc in dataset['exchanges']
                if exc['type'] == "reference product"]) > 1


def extract_parameter(obj):
    param = {'name': obj.name.text,
         'id': obj.get('parameterId'),
         'amount': float(obj.get('amount')),
         'unit': obj.unitName.text if hasattr(obj, 'unitName') else "dimensionless"
    }
    if hasattr(obj, "uncertainty"):
        param['uncertainty'] = extract_uncertainty(obj.uncertainty)
    if obj.get('variableName'):
        param['variable'] = obj.get('variableName').strip()
    if obj.get('mathematicalRelation'):
        param['formula'] = obj.get('mathematicalRelation').strip()
    return param


def extract_pedigree_matrix(elem):
    if not hasattr(elem, "pedigreeMatrix"):
        return {}
    else:
        return {value: int(elem.pedigreeMatrix.get(key))
                for key, value in PEDIGREE_LABELS.items()}


def extract_uncertainty(unc):
    """Extract uncertainty and pedigree matrix data.

    Rather ugly code is needed to extract the uncertainty data because of the way it is nested. For example:

    .. code-block:: xml

        <uncertainty>
            <lognormal meanValue="1" mu="-0.46" variance="0" varianceWithPedigreeUncertainty="0.0034" />
            <pedigreeMatrix reliability="2" completeness="3" temporalCorrelation="2" geographicalCorrelation="5" furtherTechnologyCorrelation="1" />
        </uncertainty>

    """
    distribution_labels = ['lognormal', 'normal', 'triangular', 'beta',
                           'uniform', 'undefined', 'binomial', 'gamma']
    distribution = next((getattr(unc, label)
                         for label in distribution_labels
                         if hasattr(unc, label)))
    data = {UNCERTAINTY_MAPPING.get(key, key): float(distribution.get(key))
            for key in distribution.keys()}
    data.update({
        'type': _(distribution.tag),
        'pedigree matrix': extract_pedigree_matrix(unc)
    })
    # TODO: Why is this necessary? Should be in undefined datasets...
    if not data['pedigree matrix'] and data['type'] in ('lognormal', 'normal'):
        data['pedigree matrix'] = {x: 5 for x in PEDIGREE_LABELS.values()}
    return data


def extract_production_volume(exc):
    data = {'amount': float(exc.get('productionVolumeAmount') or 0)}
    if hasattr(exc, "productionVolumeUncertainty"):
        data['uncertainty'] = extract_uncertainty(exc.productionVolumeUncertainty)
    formula = exc.get('productionVolumeMathematicalRelation')
    if formula:
        data['formula'] = formula.strip()
    variable = exc.get('productionVolumeVariableName')
    if variable:
        data['variable'] = variable.strip()
    return data


def extract_property(prop):
    data = {
        'id': prop.get('propertyId'),
        'amount': float(prop.get('amount')),
        'name': prop.name.text,
        "unit": prop.unitName.text if hasattr(prop, 'unitName') else "dimensionless",
    }
    if hasattr(prop, "uncertainty"):
        data['uncertainty'] = extract_uncertainty(prop.uncertainty)
    if prop.get("variableName"):
        data['variable'] = prop.get("variableName")
    if prop.get("mathematicalRelation"):
        data['formula'] = prop.get("mathematicalRelation").strip()
    return data


def extract_exchange(dataset, exc):
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

    # Activity link, optional field
    if exc.get('activityLinkId'):
        data['activity link'] = exc.get("activityLinkId")

    # Byproduct classification, optional field
    byproduct = [obj.classificationValue.text
                 for obj in exc.iterchildren()
                 if (_(obj.tag) == 'classification'
                 and obj.classificationSystem.text == 'By-product classification')]
    assert len(set(byproduct)) < 2
    if byproduct:
        data['byproduct classification'] = BYPRODUCT_CLASSIFICATION[
                byproduct[0]]

    # Variable name and mathematical relation extraction
    if exc.get("variableName"):
        data['variable'] = exc.get("variableName").strip()
    if exc.get("mathematicalRelation"):
        data['formula'] = exc.get("mathematicalRelation").strip()

    data['properties'] = [extract_property(obj)
                          for obj in exc.iterchildren()
                          if _(obj.tag) == 'property']

    # Biosphere compartments
    if 'environment' in data['type']:
        data['compartment'] = exc.compartment.compartment.text
        data['subcompartment'] = exc.compartment.subcompartment.text

    # Production volume; only extracted when needed
    if data['type'] in ('reference product', 'byproduct'):
        data['production volume'] = extract_production_volume(exc)

    # Uncertainty
    if hasattr(exc, "uncertainty"):
        data['uncertainty'] = extract_uncertainty(exc.uncertainty)

    # Conditional exchange
    if 'environment' not in data['type']:
        data['conditional exchange'] = (
            'activity link' in data
            and dataset['type'] == 'market activity'
            and data['type'] == 'byproduct'
            and data['amount'] < 0
        )

    return data


def extract_ecospold2_dataset(elem, filepath):
    data = {
        'filepath': filepath,
        'id': elem.activityDescription.activity.get('id'),
        'name': elem.activityDescription.activity.activityName.text,
        'location': elem.activityDescription.geography.shortname.text,
        'type': SPECIAL_ACTIVITY_TYPE[elem.activityDescription.activity.get('specialActivityType')],
        'technology level': TECHNOLOGY_LEVEL[elem.activityDescription.technology.get('technologyLevel')],
        'start date': elem.activityDescription.timePeriod.get("startDate"),
        'end date': elem.activityDescription.timePeriod.get("endDate"),
        'economic scenario': elem.activityDescription.macroEconomicScenario.name.text,
        'access restricted': ACCESS_RESTRICTED[elem.administrativeInformation.\
            dataGeneratorAndPublication.get('accessRestrictedTo')],
        'parameters': [extract_parameter(exc)
                       for exc in elem.flowData.iterchildren()
                       if 'parameter' in _(exc.tag)],
    }
    data['exchanges'] = [extract_exchange(data, exc)
                         for exc in elem.flowData.iterchildren()
                         if 'Exchange' in _(exc.tag)]
    data['combined production'] = is_combined_production(data)
    return data


def generic_extractor(filepath):
    with open(filepath, encoding='utf8') as f:
        try:
            root = objectify.parse(f).getroot()
            data = [extract_ecospold2_dataset(child, filepath)
                    for child in root.iterchildren()]
        except:
            print(filepath)
            raise
    return data


def extract_ecospold2_directory(dirpath, use_mp=True):
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
