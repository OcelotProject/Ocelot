# -*- coding: utf-8 -*-
from .errors import InvalidTransformationFunction
from collections.abc import Iterable
import functools


def get_function_meta(function):
    if isinstance(function, functools.partial):
        return {
            'name': function.func.__name__,
            'description': function.func.__doc__,
            'table': getattr(function.func, "__table__", None),
        }
    else:
        return {
            'name': function.__name__,
            'description': function.__doc__,
            'table': getattr(function, "__table__", None),
        }


def validate_configuration(config):
    unroll = lambda x: x if isinstance(x, Iterable) else [x]
    as_iterable = (elem for function in config for elem in unroll(function))
    for function in as_iterable:
        try:
            assert get_function_meta(function)
        except:
            message = "Transformation function {} has no metadata"
            raise InvalidTransformationFunction(message.format(function))
    return config
