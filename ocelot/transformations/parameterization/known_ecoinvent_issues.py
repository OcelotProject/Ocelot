# -*- coding: utf-8 -*-
import logging


def fix_benzene_chlorination_unit(data):
    """Change units in benzene chlorination to kilograms.

    One dataset has a unit conversion in its formula that Ocelot can't understand. This text, ``UnitConversion(152000000, 'pound avoirdupois', 'kg')``, is replaced with its numeric value."""
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
