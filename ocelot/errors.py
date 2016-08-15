# -*- coding: utf-8 -*-

class OcelotError(Exception):
    """Base for custom ocelot errors"""
    pass

class ZeroProduction(OcelotError):
    """Reference production exchange has amount of zero"""
    pass


class InvalidMultioutputDataset(OcelotError):
    pass


class OutputDirectoryError(OcelotError):
    pass


class ParameterizationError(OcelotError):
    pass


class UnsupportedDistribution(OcelotError):
    """Manipulation of this uncertainty type is not supported"""
    pass


class InvalidExchange(OcelotError):
    """This exchange in invalid in the given system model"""
    pass
