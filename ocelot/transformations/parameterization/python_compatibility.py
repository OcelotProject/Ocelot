# -*- coding: utf-8 -*-
from ...errors import UnparsableFormula
from ..utils import iterate_all_parameters
from copy import deepcopy
import ast
import logging
import re


KNOWN_MATH_SUBSTITUTIONS = (
    # bad string, replacement
    ("%", "e-2"),
    ("^", "**"),
    ("\r\n", ""),
)

RESERVED_WORDS = {
    "and", "as", "assert", "break", "class", "continue", "def", "del",
    "elif", "else", "except", "False", "finally", "for", "from", "global",
    "if", "import", "in", "is", "lambda", "None", "nonlocal", "not", "or",
    "pass", "raise", "return", "True", "try", "while", "with", "yield"
}

RESERVED_WORDS_RE = [(word, re.compile("(^|[^a-zA-Z_]){}($|[^a-zA-Z_])".format(word)))
                     for word in RESERVED_WORDS]

RESERVED_WORDS_STARTING = [(word, re.compile("{}[^a-zA-Z_]".format(word)))
                           for word in RESERVED_WORDS]

IF_RE = re.compile("if\((?P<condition>[^;]+);(?P<if_yes>[^;]+);(?P<if_no>[^;)]+)\)")

POWER_RE = re.compile("power\((?P<base>[^;]+);(?P<exponent>[^;]+)\)")


def find_if_clause(ds, string):
    while IF_RE.search(string):
        match = IF_RE.search(string)
        match_string = match.group(0)
        condition, if_true, if_false = match.groups()
        if if_true == if_false:
            replacement = "({})".format(if_true.strip())
        else:
            replacement = "(({}) if ({}) else ({}))".format(
                if_true, condition, if_false
            )
        logging.info({
            'type': 'table element',
            'data': (ds['name'], '', match_string, replacement)
        })
        string = string.replace(match_string, replacement)
    return string


def find_power_clause(ds, string):
    while POWER_RE.search(string):
        match = POWER_RE.search(string)
        match_string = match.group(0)
        replacement = "(({})**({}))".format(*match.groups())
        logging.info({
            'type': 'table element',
            'data': (ds['name'], '', match_string, replacement)
        })
        string = string.replace(match_string, replacement)
    return string


def fix_math_formulas(data):
    """Fix some special cases in formulas needed for correct parsing."""
    for ds in data:
        for exc in iterate_all_parameters(ds):
            if 'formula' not in exc:
                continue
            for bad, good in KNOWN_MATH_SUBSTITUTIONS:
                if bad in exc['formula']:
                    logging.info({
                        'type': 'table element',
                        'data': (ds['name'], exc['formula'], bad, good)
                    })
                    exc['formula'] = exc['formula'].replace(bad, good)
            exc['formula'] = find_if_clause(ds, exc['formula'])
            exc['formula'] = find_power_clause(ds, exc['formula'])
    return data

fix_math_formulas.__table__ = {
    'title': 'Replace unparsable math elements with their python equivalents',
    'columns': ["Activity name", "Formula", "Old element", "New element"]
}


def lowercase_all_parameters(data):
    """Convert all formulas and parameters to lower case.

    Ecoinvent formulas and variables names are case-insensitive, and often provided in many variants, e.g. ``clinker_PV`` and ``clinker_pv``. There are too many of these to fix manually, so we use a sledgehammer."""
    for ds in data:
        for exc in iterate_all_parameters(ds):
            if 'formula' in exc:
                exc['formula'] = exc['formula'].lower()
            if 'variable' in exc:
                exc['variable'] = exc['variable'].lower()
    return data


class NameFinder(ast.NodeVisitor):
    """Find all symbol names used by a parsed node.

    Code for this class and subsequent function from asteval (https://newville.github.io/asteval/)."""
    def __init__(self):
        self.names = []
        ast.NodeVisitor.__init__(self)

    def generic_visit(self, node):
        if node.__class__.__name__ == 'Name':
            if node.ctx.__class__ == ast.Load and node.id not in self.names:
                self.names.append(node.id)
        ast.NodeVisitor.generic_visit(self, node)


def get_ast_names(string):
    """Returns symbol names from an AST node"""
    finder = NameFinder()
    try:
        finder.generic_visit(ast.parse(string))
    except:
        raise UnparsableFormula
    return finder.names


def check_and_fix_formula(ds, string):
    """Check if the formula is usable in ``asteval``.

    First, check to make sure that the formula doesn't start with a reserved word that would be valid python but wouldn't produce meaningful results. For example, ``yield - fair * knight`` will be parsable, but yield is treated as a command instead of a variable.

    Next, we check if the formula is parsable. If it isn't, we search for reserved words in the formula, using a regular expression like ``[^a-zA-Z_]?yield[^a-zA-Z_]?``. The regular expression is necessary to avoid find reserved words inside longer variable names like ``yield_management``, which are valid and should be left alone.

    In either case, if reserved words are found, they are replaced with their uppercase equivalents.

    If the formula can't be repaired, it is returned in its original form; otherwise the new formula is returned."""
    updated = deepcopy(string)
    for word, reg_exp in RESERVED_WORDS_STARTING:
        if reg_exp.match(updated):
            updated = updated.replace(word, word.upper())
            logging.info({
                'type': 'table element',
                'data': (ds['name'], word, string)
            })

    try:
        get_ast_names(updated)
        return updated
    except UnparsableFormula:
        found = []
        for word, reg_exp in RESERVED_WORDS_RE:
            if reg_exp.search(updated):
                updated = updated.replace(word, word.upper())
                found.append(word)
        try:
            get_ast_names(updated)
            logging.info({
                'type': 'table element',
                'data': (ds['name'], ";".join(found), string)
            })
            return updated
        except UnparsableFormula:
            return string


def replace_reserved_words(data):
    """Replace python reserved words in variable names and formulas.

    For variable names, this is relatively simple - we just and see of the variable name is a python reserved word. For formulas, we use the ``check_and_fix_formula`` function.

    Changes datasets in place."""
    for ds in data:
        for exc in iterate_all_parameters(ds):
            if 'variable' in exc and exc['variable'] in RESERVED_WORDS:
                logging.info({
                    'type': 'table element',
                    'data': (ds['name'], exc['variable'], exc['variable'])
                })
                exc['variable'] = exc['variable'].upper()
            if 'formula' in exc:
                exc['formula'] = check_and_fix_formula(ds, exc['formula'])
    return data

replace_reserved_words.__table__ = {
    'title': 'Uppercase reserved python words like `yield` to avoid parsing errors.',
    'columns': ["Activity name", "Reserved word(s)", "Problem element"]
}


def delete_unparsable_formulas(data):
    """Uses AST parser to find unparsable formulas, which are deleted"""
    # Introduce breaks in formulas for nicer displays
    _ = lambda s: " ".join([s[i:i+40] for i in range(0, len(s), 40)])

    for ds in data:
        for exc in iterate_all_parameters(ds):
            if 'formula' in exc:
                try:
                    elements = get_ast_names(exc['formula'])
                except UnparsableFormula:
                    logging.info({
                        'type': 'table element',
                        'data': (ds['name'], _(exc['formula']))
                    })
                    del exc['formula']
    return data

delete_unparsable_formulas.__table__ = {
    'title': 'Delete unparsable formulas.',
    'columns': ["Activity name", "Formula"]
}
