# -*- coding: utf-8 -*-
from ..utils import iterate_all_parameters
import logging

logger = logging.getLogger('ocelot')

KNOWN_SUBSTITUTIONS = (
    (
        'thermoforming of plastic sheets',
        "1/014000000/50*0.946",
        "1.3514285714285711e-09"
    ), (
        'benzene chlorination',
        "UnitConversion(152000000, 'pound avoirdupois', 'kg')",
        "68949040.24"
    ), (
        'glued laminated timber production, for indoor use',
        'AVERAGE(3.08E04;4.00E04;3.39E04)*(AVERAGE(367561;433458;449963)' + \
        '/AVERAGE(1408383;1631979;1717500))',
        "9176.23"
    ), (
        "cement production, alternative constituents 6-20%",
        "ABS(blast_furnace_slag/ cement* APV_cement)",
        "(abs(blast_furnace_slag / cement * apv_cement) if cement else 0)"
    )
)


def fix_known_bad_formula_strings(data):
    """Change certain known bad text elements in formulas."""
    message = ("{} ({}): Changed {} to {}")

    for ds in data:
        for name, bad, good in KNOWN_SUBSTITUTIONS:
            if ds['name'] == name:
                for param in iterate_all_parameters(ds):
                    if bad in param.get('formula', ''):
                        logger.info({
                            'type': 'list element',
                            'data': message.format(
                                ds['name'], ds['location'], bad, good
                            )
                        })
                        param['formula'] = param['formula'].replace(bad, good)
    return data


def fix_specific_ecoinvent_issues(data):
    """A set of data manipulations for specific ecoinvent issues.

    Currently, this function does the following:

    * Delete the exchange for ``refinery gas`` from the activity ``petroleum refinery operation``, because "This flow has been cut off in accordance with the ecoinvent centre due to special circumstances."

    """
    for ds in data:
        if ds['name'] != "petroleum refinery operation":
            continue
        before = len(ds['exchanges'])
        ds['exchanges'] = [exc for exc in ds['exchanges']
                           if (exc['name'] != 'refinery gas' or exc['amount'])]
        after = len(ds['exchanges'])
        if before != after:
            logger.info({
                'type': 'table element',
                'data': (ds['name'], ds['location'], before, after)
            })
    return data

fix_specific_ecoinvent_issues.__table__ = {
    'title': 'Delete a specific non-functional exchange from petroleum refineries.',
    'columns': ["Activity name", "Locations", "Num. exchanges before", "Num. exchanges after"]
}
