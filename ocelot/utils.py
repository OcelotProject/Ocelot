# -*- coding: utf-8 -*-
import os
import functools
import pandas as pd
from copy import copy
import numpy as np

def extract_products_as_tuple(dataset):
    return tuple(sorted([exc['name']
                  for exc in dataset['exchanges']
                  if exc['type'] == 'reference product']))


def activity_grouper(dataset):
    return (dataset['name'], extract_products_as_tuple(dataset))


def iterate_exchanges(datasets):
    for ds in datasets:
        for exc in ds['exchanges']:
            yield exc


def iterate_outouts_to_technosphere(ds):
    for exc in ds['exchanges']:
        if exc['type'] in ['reference product', 'byproduct']:
            yield exc


def get_function_meta(function):
    try:
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
    except:
        raise
        return {
            'name': "callable of unknown type",
            'description': "none provided",
            'table': None,
        }


def get_reference_product(ds):
    for exc in ds['exchanges']:
        if exc['type'] == 'reference exchange' and exc['amount'] != 0.:
            break
    return exc

def uncertainty_to_df(u):
    """used by the function internal_to_df"""
    
    to_add = {}
    for field in u:
        if field == 'pedigree matrix':
            to_add.update(dict(zip(PEDIGREE_LABELS, u['pedigree matrix'])))
        elif field == 'type':
            to_add['uncertainty type'] = u['type']
        else:
            to_add[field] = u[field]
    
    return to_add
    

def uncertainty_to_internal(s):
    u = ''
    return u


def internal_to_df(dataset_internal):
    """Takes a dataset and change its representation to a convenient dataframe format"""
    
    df = {}
    for exc in dataset_internal['exchanges']:
        to_add = {'data type': 'exchange'}
        for field in exc:
            if field == 'uncertainty':
                to_add.update(uncertainty_to_df(exc['uncertainty']))
            elif field not in ['production volume', 'properties']:
                to_add[field] = exc[field]
        to_add['Ref'] = 'Ref({})'.format(exc['id'])
        df[len(df)] = copy(to_add)
        if 'production volume' in exc:
            to_add = {'data type': 'production volume'}
            for field in exc['production volume']:
                if field == 'uncertainty':
                    to_add.update(uncertainty_to_df(exc['production volume']['uncertainty']))
                else:
                    to_add[field] = exc['production volume'][field]
            to_add['Ref'] = "Ref({}, 'ProductionVolume')".format(exc['id'])
            df[len(df)] = copy(to_add)
        if 'properties' in exc:
            to_add = {'data type': 'property'}
            for field in exc['property']:
                if field == 'uncertainty':
                    to_add.update(uncertainty_to_df(exc['property']['uncertainty']))
                else:
                    to_add[field] = exc['property'][field]
            to_add['Ref'] = "Ref({}, {})".format(exc['id'], exc['property']['id'])
            df[len(df)] = copy(to_add)
    
    if 'parameters' in dataset_internal:
        for p in dataset_internal['parameters']:
            to_add = {'data type': 'parameter'}
            for field in p:
                if field == 'uncertainty':
                    to_add.update(uncertainty_to_df(p['uncertainty']))
                else:
                    to_add[field] = p[field]
            to_add['Ref'] = 'Ref({})'.format(exc['id'])
            df[len(df)] = copy(to_add)
    df = pd.DataFrame(df).transpose()
    del df['id']
    
    return df


def df_to_internal(df, dataset_internal):
    parameters = df[df['data type'] == 'parameter']
    if len(parameters) > 0:
        dataset_internal['parameters'] = []
        for index in parameters.index:
            to_add = {}
            parameters.loc[index]