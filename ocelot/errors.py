# -*- coding: utf-8 -*-

class OcelotError(Exception):
    """Base for custom ocelot errors"""
    pass


class ZeroProduction(OcelotError):
    """Reference production exchange has amount of zero"""
    pass


class IdenticalVariables(OcelotError):
    """The same variable name is used twice"""
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


class MultipleGlobalDatasets(OcelotError):
    """Multiple global datasets for the same activity name and reference product are not allowed"""
    pass


class UnparsableFormula(OcelotError):
    """Formula contains elements that can't be parsed"""
    pass


class InvalidMarketExchange(Exception):
    """Markets aren't allowed to consume their own reference product"""
    pass


class InvalidMarket(Exception):
    """Markets can only have one reference product"""
    pass


class UnresolvableActivityLink(OcelotError):
    """Activity link can't be uniquely resolved to an exchange"""
    pass


class MissingMandatoryProperty(Exception):
    """Exchange is missing a mandatory property"""
    pass


class OverlappingMarkets(OcelotError):
    """Markets overlap, preventing correct linking"""
    pass


class IdenticalDatasets(OcelotError):
    """Multiple datasets with the same identifying attributes were found"""
    pass


class InvalidTransformationFunction(OcelotError):
    """Metadata could not be retrieved for this function"""
    pass
