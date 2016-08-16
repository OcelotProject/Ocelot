# -*- coding: utf-8 -*-
import re

SPECIAL_ACTIVITY_TYPE = {
    "0": "transforming activity",
    "1": "market activity",
    "10": "market group",
    "2": "IO activity",
    "3": "residual activity",
    "4": "production mix",
    "5": "import activity",
    "6": "supply mix",
    "7": "export activity",
    "8": "re-export activity",
    "9": "correction activity"
}

TECHNOLOGY_LEVEL = {
    "0": "undefined",
    "None": "undefined",
    "1": "new",
    "2": "modern",
    "3": "current",
    "4": "old",
    "5": "outdated"
}

INPUT_GROUPS = {
    "1": "materials/fuels",
    "2": "electricity/heat",
    "3": "services",
    "4": "from environment",
    "5": "from technosphere"
}

OUTPUT_GROUPS = {
    "0": "reference product",
    "2": "byproduct",
    "3": "material for treatment",
    "4": "to environment",
    "5": "stock addition"
}

PEDIGREE_LABELS = {
    "reliability": 'reliability',
    "completeness": 'completeness',
    "temporalCorrelation": 'temporal correlation',
    "geographicalCorrelation": 'geographical correlation',
    "furtherTechnologyCorrelation": 'further technology correlation'
}

UNCERTAINTY_MAPPING = {
    # Translate some ecoinvent terms to their actual names
    'maxValue': 'maximum',
    'meanValue': 'mean',
    'minValue': 'minimum',
    'mostLikelyValue': 'mode',
    'mostFrequentValue': 'mode',
    'varianceWithPedigreeUncertainty': 'variance with pedigree uncertainty',
    'standardDeviation95': 'standard deviation 95%'
}

ACCESS_RESTRICTED = {
    '0': 'public',
    '1': 'licensees',
    '2': 'results only',
    '3': 'restricted'
 }

BYPRODUCT_CLASSIFICATION = {
    'allocatable product': 'allocatable product',
    'Waste': 'waste',
    'Recyclable': 'recyclable'
}

UUID_REGULAR_EXPRESSION = '\w{8}-\w{4}-\w{4}-\w{4}-\w{12}'

REF_REGULAR_EXPRESSIONS = [
    # exchange amount and parameters
    re.compile("Ref\(\'%s\'\)" % UUID_REGULAR_EXPRESSION),
    # production volume
    re.compile("Ref\(\'%s\'[,]\s'ProductionVolume'\)" % (UUID_REGULAR_EXPRESSION)),
    # property
    re.compile("Ref\(\'%s\'[,]\s\'%s\'\)" % (UUID_REGULAR_EXPRESSION, UUID_REGULAR_EXPRESSION))
]
