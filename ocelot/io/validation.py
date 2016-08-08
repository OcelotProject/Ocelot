# -*- coding: utf-8 -*-
from voluptuous import Schmea, Any, Optional
from .ecospold2_meta import SPECIAL_ACTIVITY_TYPE, TECHNOLOGY_LEVEL

# Schema which are just lists of valid values

valid_allocation_method = Any([
    'combined production with byproduct',
    'combined production without byproduct',
    'constrained market',
    'economic allocation',
    'no allocation',
    'recycling activity',
    'true value allocation',
    'waste treatment',
])
valid_technology_levels = Any(TECHNOLOGY_LEVEL.values())
valid_byproducts = Any(['allocatable', 'waste', 'recyclable'])
valid_activity_types = Any(SPECIAL_ACTIVITY_TYPE.values())
valid_access_restriction = Any(['public', 'licensees', 'results only', 'restricted'])

# Uncertainty distribution schemas

valid_pedigree_matrix = tuple([Any(range(1, 6))] * 5)

valid_lognormal = Schema({
    'type': 'lognormal',
    'mean': float,
    'mu', float,
    Optional('variance'): float,
    'varianceWithPedigreeUncertainty': float,
    'pedigree matrix': valid_pedigree_matrix,
}, required=True)

valid_normal = Schema({
    'type': 'normal',
    'mean': float,
    Optional('variance'): float,
    'varianceWithPedigreeUncertainty': float,
    'pedigree matrix': valid_pedigree_matrix,
}, required=True)

valid_uniform = Schema({
    'type': 'uniform',
    'minimum': float,
    'maximum': float,
    'pedigree matrix': valid_pedigree_matrix,
}, required=True)

valid_triangular = Schema({
    'type': 'triangular',
    'mode': float,
    'minimum': float,
    'maximum': float,
    'pedigree matrix': valid_pedigree_matrix,
}, required=True)

# Rarely-used distributions. Not supported by our pedigree-matrix implementation.

valid_binomial = Schema({
    'type': 'binomial',
    'n': float,
    'p': float,
    'pedigree matrix': valid_pedigree_matrix,
}, required=True)

valid_beta = Schema({
    'type': 'beta',
    'mode': float,
    'minimum': float,
    'maximum': float,
    'pedigree matrix': valid_pedigree_matrix,
}, required=True)

valid_gamma = Schema({
    'type': 'gamma',
    'shape': float,
    'scale': float,
    'pedigree matrix': valid_pedigree_matrix,
}, required=True)

valid_undefined = Schema({
    'type': 'undefined',
    'standardDeviation95': float,
    'minimum': float,
    'maximum': float,
    'pedigree matrix': valid_pedigree_matrix,
}, required=True)

# Schema subcomponents

valid_uncertainty = Any([
    valid_beta,
    valid_binomial,
    valid_gamma,
    valid_lognormal,
    valid_normal,
    valid_triangular,
    valid_undefined,
    valid_uniform,
])

valid_production_volume = Schema({
    'amount': float, # ecospold2 field 1530: productionVolumeAmount
    Optional('variable'): str, # ecospold2 field 1532: productionVolumeVariableName
    Optional('mathematical relation'): str, # ecospold2 field 1534: productionVolumeMathematicalRelation
    'uncertainty': valid_uncertainty,  # ecospold2 field 1539: productionVolumeUncertainty
}, required=True)

valid_property = Schema({
    'id': str, # ecospold2 field 2300: propertyId
    'amount': float, # ecospold2 field 2330: amount
    Optional('variable'): str, # ecospold2 field 2350: variableName
    Optional('mathematical relation'): str, # field 2340: mathematicalRelation
    'unit': str, # ecospold2 field 2324: unitName
    'uncertainty': valid_uncertainty,
}, required=True)

valid_parameter = Schema({
    'amount': float, # ecospold2 field 1710: amount
    'name': str, # ecospold2 field 1700: name
    'variable': str, # eocspold2 field 1715: variableName
    'mathematical relation': str, # ecospold2 field 1720: mathematicalRelation
    'uncertainty': valid_uncertainty,
})

# Exchange schemas

elementary_exchange_schema = Schema({
    'amount': float, # ecospold2 field 1020: amount
    'name': str, # ecospold2 field 1000: flow name
    'id': str, # ecospold2 field 1005: id
    'compartment': str,
    'subcompartment': str,
    Optional('variable'): str, # ecospold2_meta field 1040: variableName
    Optional('mathematical relation'): str, # ecospold2 field 1060: mathematicalRelation
    'tag': 'intermediateExchange',
    Optional('properties'): {str: valid_property},
    'type': Any(['from environment', 'to environment']),
    'unit': str, # ecospold2 field 1035: unitName
    'uncertainty': valid_uncertainty,
}, required=True)

activity_exchange_schema = Schema({
    'amount': float, # ecospold2 field 1020: amount
    'name': str, # ecospold2 field 1000: flow name
    'id': str, # ecospold2 field 1005: id
    Optional('production volume'): valid_production_volume,
    Optional('variable'): str, # ecospold2_meta field 1040: variableName
    Optional('mathematical relation'): str, # ecospold2 field 1060: mathematicalRelation
    Optional('properties'): {str: valid_property},
    Optional('activity link'): str # ecospold2 field 1520: activityLinkId
    Optional('byproduct classification'): valid_byproducts, # ecospold2 field 310: classificationValue, if classificationSystem is 'By-product classification'.
    'tag': 'elementaryExchange'
    'type': Any(['from technosphere', 'reference product', 'byproduct', ]),
    'unit': str, # ecospold2 field 1035: unitName
    'uncertainty': valid_uncertainty,
}, required=True)

# Dataset schema

dataset_schema = Schema({
    'id': str,
    'name': str, # ecospold2 field 100: activityName
    'filepath': str,
    'location': str, # ecospold2 field 410: shortname
    'technology level': valid_technology_levels, # ecospold2 field 500
    'economic scenario': str, # ecospold2 field 700: macroEconomicScenarioId
    'start date': str,
    'end date': str, # Starting and ending dates for dataset validity, in format '2015-12-31'
    'type': valid_activity_types, # ecospold2 field 115: specialActivityType
    'access restricted': valid_access_restriction, # ecospold2 field 3550: accessRestrictedTo
    "exchanges": [Any([elementary_exchange_schema, activity_exchange_schema])],
    "parameters": [valid_parameter],
    Optional('allocation method'): valid_allocation_method,  # Allocation method used. Added by a transformation.
    Optional('main reference product'): str, # Name of the reference product. Added by a transformation.
}, required=True)
