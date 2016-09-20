# -*- coding: utf-8 -*-
from ...errors import UnparsableFormula
from ..utils import iterate_all_parameters
from copy import deepcopy
import ast
import logging
import re

logger = logging.getLogger('ocelot')

# TODO: A more elegant solution would probably use pyparsing
# for all this cleanup, etc., but this is a whole new and
# difficult domain of knowledge.


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
IF_BEGINNING = re.compile("if\(")
COMPLETE_IF = re.compile("^if\((?P<condition>[^;]+);(?P<if_yes>[^;]+);(?P<if_no>.+)\)$")

POWER_RE = re.compile("power\((?P<base>[^;]+);(?P<exponent>[^;]+)\)")


def find_if_boundaries(string):
    """Find beginning and end indices of an ``if(a;b;c)`` statement.

    Uses a manual count (``stack``) of opening and closing parentheses.

    Adapted from http://stackoverflow.com/questions/5454322/python-how-to-match-nested-parentheses-with-regex"""
    stack = []
    for m in re.finditer(r'[()]', string):
        pos = m.start()
        character = string[pos]

        # Skip escape sequence
        if string[pos-1] == '\\':
            # TODO: Think about what \( would actually mean in a formula.
            continue
        elif character == "(":
            stack.append(pos + 1)
        elif character == ")":
            # Unmatched closing parentheses can't happen because we return
            # as soon as we are balanced.
            prevpos = stack.pop()
            if not stack:
                return (prevpos, pos)

    message = "Unmatched opening parentheses at position {}:\n\t{}"
    raise ValueError(message.format(stack[0], string))


def replace_if_statement(substring):
    """Replace an ``if(a;b;c)`` clause. ``substring`` must contain the if clause exactly."""
    match = COMPLETE_IF.search(substring)
    match_string = match.group(0)
    condition, if_true, if_false = match.groups()
    if if_true == if_false:
        replacement = "({})".format(if_true.strip())
    else:
        replacement = "(({}) if ({}) else ({}))".format(
            if_true, condition, if_false
        )
    return substring.replace(match_string, replacement)


def find_replace_nested_if_statements(ds, line):
    """Iteratively find and replace nested if statements.

    In order to handle nesting correctly, replaces the smallest (by length) if statement each time."""
    original = deepcopy(line)
    while IF_BEGINNING.search(line):
        # Get start indices and length of all if statements
        match_positions = []
        for match in IF_BEGINNING.finditer(line):
            start = match.start()
            _, end = find_if_boundaries(line[start:])
            match_positions.append((start, end))

        # Sort by smallest length and replace this one
        match_positions.sort(key=lambda x: (x[1]))
        start, end = match_positions[0]
        line = line[:start] + replace_if_statement(line[start:start + end + 1]) + line[start + end + 1:]
    logger.info({
        'type': 'table element',
        'data': (ds['name'], '', original, line)
    })
    return line


def find_if_clause(ds, string):
    """Reformat clauses that use ``if(condition;if_true;if_false)`` syntax.

    Can handle nested if clauses. Will replace if statements if ``if_true`` is equal to ``if_false``."""
    if string.count("if("):
        return find_replace_nested_if_statements(ds, string)
    else:
        return string


def find_power_clause(ds, string):
    while POWER_RE.search(string):
        match = POWER_RE.search(string)
        match_string = match.group(0)
        as_numbers = [float(x) for x in match.groups()]
        replacement = "(({})**({}))".format(*as_numbers)
        logger.info({
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
                    logger.info({
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

    Ecoinvent formulas and variables names are case-insensitive, and often provided in many variants, e.g. ``clinker_PV`` and ``clinker_pv``. There are too many of these to fix manually, so we use a sledgehammer approach to guarantee consistency within datasets."""
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
            logger.info({
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
            logger.info({
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
                logger.info({
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
                    get_ast_names(exc['formula'])
                except UnparsableFormula:
                    logger.info({
                        'type': 'table element',
                        'data': (ds['name'], _(exc['formula']))
                    })
                    del exc['formula']
    return data

delete_unparsable_formulas.__table__ = {
    'title': 'Delete unparsable formulas.',
    'columns': ["Activity name", "Formula"]
}
