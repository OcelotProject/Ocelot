# -*- coding: utf-8 -*-
from ..utils import iterate_all_parameters
from asteval import Interpreter
from bw2parameters import ParameterSet


def extract_named_parameters(dataset):
    """Extract named parameters from ``dataset``.

    Each named parameter must have a name, and should have either a numeric value (``amount``) or a ``formula`` string. Parameters without names (``variable``) are not extracted, as don't contribute to dataset recalculation; they only get updated afterwards.

    Returns a dictionary with form: ``{'name': {'amount': number, 'formula': string}}``.

    """
    return {exc['variable']: {key: exc[key]
                              for key in ('amount', 'formula')
                              if exc.get(key) is not None}
            for exc in iterate_all_parameters(dataset)
            if 'variable' in exc}


class TolerantParameterSet(ParameterSet):
    """Subclass of ParameterSet that sets flawed formulas to zero"""
    def evaluate(self):
        interpreter = Interpreter()
        result = {}
        for key in self.order:
            # No global params in Ocelot
            # if key in self.global_params:
            #     interpreter.symtable[key] = self.global_params[key]
            if self.params[key].get('formula'):
                try:
                    value = interpreter(self.params[key]['formula'])
                except ZeroDivisionError:
                    # Grumble grumble...
                    value = 0
                interpreter.symtable[key] = result[key] = value
            elif 'amount' in self.params[key]:
                interpreter.symtable[key] = result[key] = self.params[key]['amount']
            else:
                raise ValueError("No suitable formula or static amount found "
                                 "in {}".format(key))
        return result


def recalculate(dataset):
    """Recalculate parameterized relationships within a dataset.

    Modifies values in place.

    Creates a ``TolerantParameterSet``, populates it with named parameters with a dataset, and then gets the evaluation order the graph of parameter relationships. After reevaluating all named parameters, creates an ``Interpreter`` with named parameters and all of numpy in its namespace. This interpreter is used to evaluate all other formulas in the dataset.

    Formulas that divide by zero are evaluated to zero.

    Returns the modified dataset."""
    interpreter = Interpreter()
    parameter_set = TolerantParameterSet(extract_named_parameters(dataset))
    for key, value in parameter_set.evaluate().items():
        interpreter.symtable[key] = value

    for exc in iterate_all_parameters(dataset):
        if 'formula' in exc:
            try:
                exc['amount'] = interpreter(exc['formula'])
            except ZeroDivisionError:
                exc['amount'] = 0
        elif 'variable' in exc:
            exc['amount'] = interpreter.symtable[exc['variable']]
        else:
            raise ValueError
    return dataset
