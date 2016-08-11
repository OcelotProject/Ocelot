# -*- coding: utf-8 -*-
from ..collection import Collection
import logging


def fix_formulas(data):
    """Fix some special cases in formulas needed for correct parsing.

    * ``ABS`` -> ``abs``
    * ``%`` -> ``e-2``
    * ``^`` -> ``**``

    """
    _ = lambda x: x.replace("ABS(", "abs(").replace('%', "e-2").replace("^", "**")

    for dataset in data:
        for exc in dataset['exchanges']:
            if 'formula' in exc:
                exc['formula'] = _(exc['formula'])
            if 'formula' in exc.get('production volume', {}):
                exc['production volume']['formula'] = \
                    _(exc['production volume']['formula'])
            for p in exc.get('properties', []):
                if 'formula' in p:
                    p['formula'] = _(p['formula'])
        for p in dataset['parameters']:
            if 'formula' in p:
                p['formula'] = _(p['formula'])
    return data


def fix_clinker_pv_variable_name(data):
    """Change ``clinker_PV`` to ``clinker_pv`` in variable names and formulas.

    Both ``clinker_PV`` and ``clinker_pv`` are used in the dataset. Needed for consistency in case-sensitive formula parsing."""
    for dataset in data:
        if dataset['name'] == 'clinker production':
            for exc in dataset['exchanges']:
                if 'production volume' in exc:
                    if 'clinker_PV' in exc['production volume'].get('formula', ''):
                        exc['production volume']['formula'] = \
                            exc['production volume']['formula'].\
                            replace('clinker_PV', 'clinker_pv')
                        message = ("{} ({}): Changed `clinker_PV` to "
                                   "`clinker_pv` in formula `{}`")
                        logging.info({
                            'type': 'list element',
                            'data': message.format(
                                dataset['name'],
                                dataset['location'],
                                exc['production volume']['formula']
                            )
                        })
                    if exc['production volume'].get('variable') == 'clinker_PV':
                        exc['production volume']['variable'] = 'clinker_pv'
                        message = "{} ({}): Changed variable `clinker_PV` to `clinker_pv`"
                        logging.info({
                            'type': 'list element',
                            'data': message.format(dataset['name'], dataset['location'])
                        })
    return data


def fix_cement_production_variable_name(data):
    """Change ``ggbfs`` to ``GGBFS`` in variable names and formulas.

    Needed for consistency in case-sensitive formula parsing."""
    for dataset in data:
        if dataset['name'] == 'cement production, alternative constituents 6-20%':
            for exc in dataset['exchanges']:
                if 'ggbfs' in exc.get('formula', ''):
                    exc['formula'] = exc['formula'].replace('ggbfs', 'GGBFS')
                    message = "{} ({}): Changed `ggbfs` to `GGBFS` in formula `{}`"
                    logging.info({
                        'type': 'list element',
                        'data': message.format(
                            dataset['name'],
                            dataset['location'],
                            exc['formula']
                        )
                    })
                if exc.get('variable') == 'ggbfs':
                    message = "{} ({}): Changed variable `ggbfs` to `GGBFS`"
                    logging.info({
                        'type': 'list element',
                        'data': message.format(dataset['name'], dataset['location'])
                    })
                    exc['variable'] = 'GGBFS'
    return data


def fix_ethylene_glycol_uses_yield(data):
    """Change ``yield`` to ``Yield`` to avoid Python reserved word."""
    for dataset in data:
        if dataset['name'] == 'ethylene glycol production':
            for p in dataset['parameters']:
                if p.get('variable') == 'yield':
                    p['variable'] = 'Yield'
                    message = "{} ({}): Changed variable `yield` to `Yield`"
                    logging.info({
                        'type': 'list element',
                        'data': message.format(dataset['name'], dataset['location'])
                    })
            for exc in dataset['exchanges']:
                if 'yield' in exc.get('formula', ''):
                    exc['formula'] = exc['formula'].replace('yield', 'Yield')
                    message = "{} ({}): Changed `yield` to `Yield` in formula `{}`"
                    logging.info({
                        'type': 'list element',
                        'data': message.format(
                            dataset['name'],
                            dataset['location'],
                            exc['formula']
                        )
                    })

    return data


def fix_offshore_petroleum_variable_name(data):
    """Change ``petroleum_APV`` to ``petroleum_apv`` in variable names and formulas.

    Needed for consistency in case-sensitive formula parsing."""
    for dataset in data:
        if dataset['name'] == 'petroleum and gas production, off-shore':
            for exc in dataset['exchanges']:
                if 'petroleum_APV' in exc.get('formula', ''):
                    exc['formula'] = exc['formula'].replace('petroleum_APV', 'petroleum_apv')
                    message = "{} ({}): Changed `petroleum_APV` to `petroleum_apv` in formula `{}`"
                    logging.info({
                        'type': 'list element',
                        'data': message.format(
                            dataset['name'],
                            dataset['location'],
                            exc['formula']
                        )
                    })
                if '\r\n' in exc.get('formula', ''):
                    exc['formula'] = exc['formula'].replace('\r\n', '')
    return data


def fix_benzene_chlorination_unit(data):
    """Change units in benzene chlorination to kilograms."""
    message = ("{} ({}): Changed `UnitConversion(152000000, "
               "'pound avoirdupois', 'kg')` to `68949040.24` in formula `{}`")

    for dataset in data:
        if dataset['name'] == 'benzene chlorination':
            for exc in dataset['exchanges']:
                if 'avoirdupois' in exc.get('production volume', {}).get('formula', ''):
                    exc['production volume']['formula'] = \
                        exc['production volume']['formula'].replace(
                            "UnitConversion(152000000, 'pound avoirdupois', 'kg')",
                            '68949040.24'
                        )
                    logging.info({
                        'type': 'list element',
                        'data': message.format(
                            dataset['name'],
                            dataset['location'],
                            exc['production volume']['formula']
                        )
                    })
    return data


fix_known_ecoinvent_issues = Collection(
    fix_formulas,
    fix_clinker_pv_variable_name,
    fix_cement_production_variable_name,
    fix_ethylene_glycol_uses_yield,
    fix_offshore_petroleum_variable_name,
    fix_benzene_chlorination_unit,
)
