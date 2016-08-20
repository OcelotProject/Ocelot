# -*- coding: utf-8 -*-


class OutputDirectoryError(Exception):
    pass


class ParameterizationError(Exception):
    pass


class MultipleGlobalDatasets(Exception):
    pass


class InvalidMarketExchange(Exception):
    """Markets aren't allowed to consume their own reference product"""
    pass


class InvalidMarket(Exception):
    """Markets can only have one reference product"""
    pass
