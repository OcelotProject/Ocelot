# -*- coding: utf-8 -*-
from ..utils import iterate_all_parameters
import logging

KNOWN_SUBSTITUTIONS = (
    ('thermoforming of plastic sheets', "1/014000000/50*0.946", "1.3514285714285711e-09"),
    ('benzene chlorination', "UnitConversion(152000000, 'pound avoirdupois', 'kg')", "68949040.24")
)


def fix_known_bad_formula_strings(data):
    """Change certain known bad text elements in formulas."""
    message = ("{} ({}): Changed {} to {}")

    for ds in data:
        for name, bad, good in KNOWN_SUBSTITUTIONS:
            if ds['name'] == name:
                for param in iterate_all_parameters(ds):
                    if bad in param.get('formula', ''):
                        logging.info({
                            'type': 'list element',
                            'data': message.format(
                                ds['name'], ds['location'], bad, good
                            )
                        })
                        param['formula'] = param['formula'].replace(bad, good)
    return data
