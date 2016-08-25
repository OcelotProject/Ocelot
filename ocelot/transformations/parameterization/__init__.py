# -*- coding: utf-8 -*-
from ...collection import Collection
from .implicit_references import replace_implicit_references
from .known_ecoinvent_issues import fix_known_bad_formula_strings
from .production_volumes import create_pv_parameters
from .python_compatibility import (
    delete_unparsable_formulas,
    fix_math_formulas,
    lowercase_all_parameters,
    replace_reserved_words,
)
from .recalculation import recalculate
from .validation import variable_names_are_unique

fix_ecoinvent_parameters = Collection(
    replace_implicit_references,
    fix_known_bad_formula_strings,
    lowercase_all_parameters,
    fix_math_formulas,
    replace_reserved_words,
    delete_unparsable_formulas,
)
