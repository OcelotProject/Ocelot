# -*- coding: utf-8 -*-
import imp
from . import ecospold2_meta as meta
imp.reload(meta)
from lxml import objectify
from time import time
import multiprocessing
import os
import pprint
import pyprind
import signal

from .. import utils
imp.reload(utils)


def _(string):
    return string.replace("{http://www.EcoInvent.org/EcoSpold02}", "")


def extract_parameters(elem):
    parameters = []
    for obj in elem.flowData.iterchildren():
        if 'parameter' in obj.tag:
            p = {'name': obj.name.text, 
                 'id': obj.get('parameterId')}
            if hasattr(obj, "uncertainty"):
                p['uncertainty'] = extract_uncertainty(obj.uncertainty)
            formula = obj.get('mathematicalRelation')
            if obj.get('variableName'):
                p['variable'] = obj.get('variableName').strip()
            if formula:
                p['mathematical relation'] = formula.strip()
            parameters.append(p)
    return parameters

def extract_pedigree_matrix(elem):
    pm = {}
    if hasattr(elem, 'pedigreeMatrix'):
        for field in meta.PEDIGREE_LABELS:
            pm[meta.PEDIGREE_LABELS[field]] = int(elem.pedigreeMatrix.get(field))
    return pm


def extract_uncertainty(unc):
    distribution_labels = ['lognormal', 'normal', 'triangular',
                           'uniform', 'undefined']
    distribution = next((getattr(unc, label)
                         for label in distribution_labels
                         if hasattr(unc, label)))
    data = {meta.UNCERTAINTY_MAPPING.get(key, key): float(distribution.get(key)) for key in distribution.keys()}
    data.update({'type': _(distribution.tag)})
    data.update(extract_pedigree_matrix(unc))
    
    return data


def extract_production_volume(exc, exc_data):
    pv = exc.get('productionVolumeAmount')
    if not pv:
        if exc_data['type'] in ['reference product', 'byproduct']:
            data = {'amount': 0.}
        else:
            data = False
    else:
        data = {'amount': float(pv)}
        if hasattr(exc, "productionVolumeUncertainty"):
            data['uncertainty'] = extract_uncertainty(exc.productionVolumeUncertainty)
        if exc.get('productionVolumeMathematicalRelation'):
            data['mathematical relation'] = exc.get(
                'productionVolumeMathematicalRelation').strip()
        if exc.get('productionVolumeVariableName'):
            data['variable'] = exc.get('productionVolumeVariableName')
    
    return data


def extract_property(exc):
    properties = []
    for prop in exc.iterchildren():
        if _(prop.tag) == 'property':
            p = {
                'name': prop.name.text, 
                'id': prop.get('propertyId'),
                'amount': float(prop.get('amount'))
                }
            if hasattr(prop, 'unitName'):
                p['unit'] = prop.unitName.text
            else:
                p['unit'] = 'dimensionless'
            if hasattr(prop, "uncertainty"):
                p['uncertainty'] = extract_uncertainty(prop.uncertainty)
            if prop.get("variableName"):
                p['variable'] = prop.get("variableName")
            if prop.get("mathematicalRelation"):
                p['mathematical relation'] = prop.get("mathematicalRelation").strip()
            properties.append(p)
    
    return properties


def extract_minimal_exchange(exc):
    # Basic data
    data = {
        'id': exc.get('id'),
        'tag': _(exc.tag),
        'name': exc.name.text,
        'unit': exc.unitName.text,
        'amount': float(exc.get('amount')),
        'type': (meta.INPUT_GROUPS[exc.inputGroup.text]
                 if hasattr(exc, "inputGroup")
                 else meta.OUTPUT_GROUPS[exc.outputGroup.text])
    }
    
    # Activity link, optional field
    if exc.get('activityLinkId'):
        data['activity link'] = exc.get("activityLinkId")
    
    # Byproduct classification, optional field
    for obj in exc.iterchildren():
        if (_(obj.tag) == 'classification' and 
                obj.classificationSystem.text == 'By-product classification'):
            data['byproduct classification'] = meta.BYPRODUCT_CLASSIFICATION[
                obj.classificationValue.text]
            break
    
    #Variable name and mathematical relation extraction
    if exc.get("variableName"):
        data['variable'] = exc.get("variableName")
    if exc.get("mathematicalRelation"):
        data['mathematical relation'] = exc.get("mathematicalRelation").strip()
    
    # Property extraction
    properties = extract_property(exc)
    if len(properties) > 0:
        data['properties'] = properties

    # Biosphere compartments
    if 'environment' in data['type']:
        data['compartment'] = exc.compartment.compartment.text
        data['subcompartment'] = exc.compartment.subcompartment.text
    
    # Production volume & uncertainty
    pv = extract_production_volume(exc, data)
    if pv:
        data['production volume'] = pv
    
    # Uncertainty
    if hasattr(exc, "uncertainty"):
        data['uncertainty'] = extract_uncertainty(exc.uncertainty)

    return data


def extract_minimal_ecospold2_info(elem, filepath):
    data = {
        'filepath': filepath,
        'id': elem.activityDescription.activity.get('id'), 
        'name': elem.activityDescription.activity.activityName.text,
        'location': elem.activityDescription.geography.shortname.text,
        'type': meta.SPECIAL_ACTIVITY_TYPE[elem.activityDescription.activity.get('specialActivityType')],
        'technology level': meta.TECHNOLOGY_LEVEL[elem.activityDescription.technology.get('technologyLevel')],
        'start date': elem.activityDescription.timePeriod.get("startDate"), 
        'end date': elem.activityDescription.timePeriod.get("endDate"), 
        'economic scenario': elem.activityDescription.macroEconomicScenario.name.text,
        'exchanges': [extract_minimal_exchange(exc)
                      for exc in elem.flowData.iterchildren()
                      if 'Exchange' in exc.tag], 
        'access restricted': meta.ACCESS_RESTRICTED[elem.administrativeInformation.dataGeneratorAndPublication.get(
                            'accessRestrictedTo')], 
        'last operation': 'extract_minimal_ecospold2_info', 
        'allocation method': '(not known at this point)'
        }
    data['main reference product'] = utils.find_main_reference_product(data)
    parameters = extract_parameters(elem)
    if len(parameters) > 0:
        data['parameters'] = parameters
    
    return data


def generic_extractor(filepath):
    #print(filepath)
    with open(filepath, encoding='utf8') as f:
        try:
            root = objectify.parse(f).getroot()
            data = [extract_minimal_ecospold2_info(child, filepath)
                    for child in root.iterchildren()]
        except:
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