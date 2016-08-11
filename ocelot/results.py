# -*- coding: utf-8 -*-

class SaveStrategy(object):
    """This class tells the system model when to save intermediate results.

    Default strategy is to save after every five transformation functions.

    Can be initialized using any of the following:

    * ``None``: Use the default value (every five transformation functions).
    * ``a`` (where ``a`` is an integer): Save every ``a`` transformation functions.
    * ``a:b`` (a, b are integers): Save every intermediate result between transformation function number ``a`` and ``b`` (inclusive of ``a`` and ``b``).
    * ``a:b:c`` (a, b, c are integers): Save every ``c``th intermediate result between transformation function number ``a`` and ``b`` (inclusive of ``a`` and ``b``). For example, an input of ``2:8:3`` would save results after functions ``2``, ``5``, and ``8``.

    Usage:

    .. code-block:: python

        >>> strat = SaveStrategy()
        >>> strat(4)
        False
        >>> strat(5)
        True
        >>> strat = SaveStrategy("2:10:4")
        >>> strat(2)
        True
        >>> strat(3)
        False

    """
    DEFAULT = 5

    def __init__(self, arg=None):
        self.func = self.parse(arg)

    def __call__(self, index):
        return self.func(index)

    def parse(self, arg):
        if not arg:
            return lambda x: not x % self.DEFAULT
        elif ":" not in arg:
            try:
                int(arg)
            except:
                raise ValueError("Can't parse {} as integer".format(arg))
            if arg < 1:
                raise ValueError("Input value must be >= 1")
            return lambda x: not x % int(arg)
        else:
            try:
                arg = [int(x) for x in arg.split(":")]
            except:
                raise ValueError("Can't split and parse integers from {}".format(arg))
            arg[1] += 1  # We are inclusive of top value
            possibles = list(range(*arg))
            return lambda x: x in possibles
