# -*- coding: utf-8 -*-
from voluptuous import Schema, Any, Optional
from .ecospold2_meta import SPECIAL_ACTIVITY_TYPE, TECHNOLOGY_LEVEL, PEDIGREE_LABELS

# Schema which are just lists of valid values

valid_access_restriction = Any('public', 'licensees', 'results only', 'restricted')
valid_activity_types = Any(*list(SPECIAL_ACTIVITY_TYPE.values()))
valid_allocation_method = Any(
    'combined production with byproduct',
    'combined production without byproduct',
    'constrained market',
    'economic allocation',
    'no allocation',
    'recycling activity',
    'true value allocation',
    'waste treatment',
)
valid_byproducts = Any('allocatable product', 'waste', 'recyclable')
valid_technology_levels = Any(*list(TECHNOLOGY_LEVEL.values()))

# Uncertainty distribution schemas

valid_pedigree_matrix = Any({lbl: int for lbl in PEDIGREE_LABELS.values()}, {})

valid_lognormal = Schema({
    'mean': float,
    'pedigree matrix': valid_pedigree_matrix,
    'type': 'lognormal',
    'variance with pedigree uncertainty': float,
    Optional('mu'): float,  # Somehow this is optional (/missing) in some ecospold2 datasets
    Optional('variance'): float,
}, required=True)

valid_normal = Schema({
    'mean': float,
    'pedigree matrix': valid_pedigree_matrix,
    'type': 'normal',
    'variance with pedigree uncertainty': float,
    Optional('variance'): float,
}, required=True)

valid_uniform = Schema({
    'maximum': float,
    'minimum': float,
    'pedigree matrix': valid_pedigree_matrix,
    'type': 'uniform',
}, required=True)

valid_triangular = Schema({
    'maximum': float,
    'minimum': float,
    'mode': float,
    'pedigree matrix': valid_pedigree_matrix,
    'type': 'triangular',
}, required=True)

# Rarely-used distributions. Not supported by our pedigree-matrix implementation.

valid_binomial = Schema({
    'n': float,
    'p': float,
    'pedigree matrix': valid_pedigree_matrix,
    'type': 'binomial',
}, required=True)

valid_beta = Schema({
    'maximum': float,
    'minimum': float,
    'mode': float,
    'pedigree matrix': valid_pedigree_matrix,
    'type': 'beta',
}, required=True)

valid_gamma = Schema({
    'pedigree matrix': valid_pedigree_matrix,
    'scale': float,
    'shape': float,
    'type': 'gamma',
}, required=True)

valid_undefined = Schema({
    'maximum': float,
    'minimum': float,
    'pedigree matrix': valid_pedigree_matrix,
    'standard deviation 95%': float,
    'type': 'undefined',
}, required=True)

# Schema subcomponents

valid_uncertainty = Any(
    valid_beta,
    valid_binomial,
    valid_gamma,
    valid_lognormal,
    valid_normal,
    valid_triangular,
    valid_undefined,
    valid_uniform,
)

valid_production_volume = Schema({
    'amount': float, # ecospold2 field 1530: productionVolumeAmount
    Optional('formula'): str, # ecospold2 field 1534: productionVolumeMathematicalRelation
    Optional('uncertainty'): valid_uncertainty,  # ecospold2 field 1539: productionVolumeUncertainty
    Optional('variable'): str, # ecospold2 field 1532: productionVolumeVariableName
}, required=True)

valid_property = Schema({
    'amount': float, # ecospold2 field 2330: amount
    'id': str, # ecospold2 field 2300: propertyId
    'name': str,
    'unit': str, # ecospold2 field 2324: unitName
    'unit': str, # ecospold2 field 2324: unitName
    Optional('formula'): str, # field 2340: mathematicalRelation
    Optional('uncertainty'): valid_uncertainty,
    Optional('variable'): str, # ecospold2 field 2350: variableName
}, required=True)

valid_parameter = Schema({
    "unit": str,
    'amount': float, # ecospold2 field 1710: amount
    'id': str,
    'name': str, # ecospold2 field 1700: name
    Optional('formula'): str, # ecospold2 field 1720: mathematicalRelation
    Optional('uncertainty'): valid_uncertainty,
    Optional('variable'): str, # eocspold2 field 1715: variableName
})

# Exchange schemas

elementary_exchange_schema = Schema({
    'amount': float, # ecospold2 field 1020: amount
    'compartment': str,
    'id': str, # ecospold2 field 1005: id
    'name': str, # ecospold2 field 1000: flow name
    'subcompartment': str,
    'tag': 'elementaryExchange',
    'type': Any('from environment', 'to environment'),
    'unit': str, # ecospold2 field 1035: unitName
    Optional('formula'): str, # ecospold2 field 1060: mathematicalRelation
    Optional('properties'): [valid_property],
    Optional('uncertainty'): valid_uncertainty,
    Optional('variable'): str, # ecospold2_meta field 1040: variableName
}, required=True)

activity_exchange_schema = Schema({
    'amount': float, # ecospold2 field 1020: amount
    'id': str, # ecospold2 field 1005: id
    'name': str, # ecospold2 field 1000: flow name
    'tag': 'intermediateExchange',
    'type': Any('from technosphere', 'reference product', 'byproduct', 'dropped product'),
    'unit': str, # ecospold2 field 1035: unitName
    Optional('activity link'): str, # ecospold2 field 1520: activityLinkId
    Optional('byproduct classification'): valid_byproducts, # ecospold2 field 310: classificationValue, if classificationSystem is 'By-product classification'.
    Optional('conditional exchange'): bool,
    Optional('formula'): str, # ecospold2 field 1060: mathematicalRelation
    Optional('production volume'): valid_production_volume, # Only when needed for multioutput
    Optional('properties'): [valid_property],
    Optional('uncertainty'): valid_uncertainty,
    Optional('variable'): str, # ecospold2_meta field 1040: variableName
}, required=True)

# Dataset schema

dataset_schema = Schema({
    "combined production": bool, # More than one reference product
    "exchanges": [Any(elementary_exchange_schema, activity_exchange_schema)],
    "parameters": [valid_parameter],
    'access restricted': valid_access_restriction, # ecospold2 field 3550: accessRestrictedTo
    'economic scenario': str, # ecospold2 field 700: macroEconomicScenarioId
    'end date': str, # Starting and ending dates for dataset validity, in format '2015-12-31'
    'filepath': str,
    'id': str,
    'location': str, # ecospold2 field 410: shortname
    'name': str, # ecospold2 field 100: activityName
    'start date': str,
    'technology level': valid_technology_levels, # ecospold2 field 500
    'type': valid_activity_types, # ecospold2 field 115: specialActivityType
    Optional('allocation method'): valid_allocation_method,  # Allocation method used. Added by a transformation.
    Optional('reference product'): str, # Name of the reference product. Added by a transformation.
}, required=True)
