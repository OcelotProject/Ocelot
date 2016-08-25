# -*- coding: utf-8 -*-
import logging
import uuid


def create_pv_parameters(dataset):
    """Remove all production volume parameterization.

    Production volumes are fixed, like reference production exchange amounts. This function will do one of three things:

    #. If there is no ``formula`` or ``variable`` in the production volume, do nothing.
    #. If there is only a ``formula``, delete the formula.
    #. If there is a ``variable``, move the variable to a new parameter.

    """
    for exc in dataset['exchanges']:
        pv = exc.get("production volume")
        if not pv:
            continue
        elif 'variable' in pv:
            new_parameter = {
                'unit': exc['unit'],
                'id': str(uuid.uuid4()),
                'name': "Shifted PV parameter: " + pv['variable'],
                'variable': pv['variable'],
                'amount': pv['amount']
            }
            logging.info({
                'type': 'table element',
                'data': (dataset['name'], new_parameter['name'], pv['amount'])
            })
            if 'formula' in pv:
                new_parameter['formula'] = pv['formula']
                del pv['formula']
            dataset['parameters'].append(new_parameter)
            del pv['variable']
        elif 'formula' in pv:
            del pv['formula']
    return dataset

create_pv_parameters.__table__ = {
    'title': 'Turn parameterized production volumes into parameters.',
    'columns': ["Activity name", "Variable name", "Amount"]
}
