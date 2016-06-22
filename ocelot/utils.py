# -*- coding: utf-8 -*-
import os
import functools
import pandas as pd
from copy import copy
import numpy as np
from pickle import dump, load

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

def uncertainty_to_df(u, data_format):
    """used by the function internal_to_df"""

    to_add = {}
    for field in u:
        to_add[data_format.loc[('uncertainty', field), 'in dataframe']] = u[field]

    return to_add


def is_empty(e):
    return type(e) in ['', None, np.nan, np.NaN, np.nan, []]


def uncertainty_to_internal(s):
    if 'uncertainty type' in s and not is_empty(s['uncertainty type']):
        pass
    return ''


def add_line_to_df(df, data_format, parent, element):
    to_add = {'data type': parent}
    for field in element:
        if field in ['production volume', 'property']:
            df = add_line_to_df(df, data_format, field, element[field])
        elif field == 'uncertainty':
            for field2 in element[field]:
                to_add[data_format.loc[(field, field2), 'in dataframe']] = element[field][field2]
        else:
            to_add[data_format.loc[(parent, field), 'in dataframe']] = element[field]
    to_add = add_Ref(to_add)
    df[len(df)] = copy(to_add)
    return df


def add_Ref(to_add):
    if to_add['data type'] == 'exchange':
        to_add['Ref'] = "Ref('{}')".format(to_add['exchange id'])
    elif to_add['data type'] == 'production volume':
        to_add['Ref'] = "Ref('{}', 'ProductionVolume')".format(to_add['exchange id'])
    elif to_add['data type'] == 'parameter':
        to_add['Ref'] = "Ref('{}')".format(to_add['id'])
    elif to_add['data type'] == 'property':
        to_add['Ref'] = "Ref('{}', '{}')".format(to_add['exchange id'], to_add['property id'])
    else:
        1/0
    return to_add


def internal_to_df(dataset, data_format):
    """Takes a dataset and change its representation to a convenient dataframe format"""
    data_format = data_format.set_index(['parent', 'field']).sortlevel(level=0)
    df = {}
    for parent in ['exchanges', 'parameters']:
        if parent in dataset:
            df = add_line_to_df(df, data_format, parent[:-1], dataset[parent])
    df = pd.DataFrame(df).transpose()
    del df['id']

    return df


def df_to_internal(df, dataset_internal):
    parameters = df[df['data type'] == 'parameter']
    if len(parameters) > 0:
        dataset_internal['parameters'] = []
        for index in parameters.index:
            s = parameters.loc[index]
            to_add = {}
            for field in parameters:
                if not is_empty(s[field]) and field != 'Ref':
                    to_add[field] = s[field]
                elif field == 'Ref':
                    to_add['id'] = s[field].replace('Ref(', '').replace('(', '')

            dataset_internal['parameters'].append(copy(to_add))


def read_format_definition():
    return pd.read_excel(os.path.join(os.path.dirname(__file__), "data", "format.xlsx"))


def save_file(obj, folder, filename):
    f = open(os.path.join(folder, filename) + '.pkl', mode = 'wb')
    dump(obj, f, protocol = -1)
    f.close()


def open_file(folder, filename):
    f = open(os.path.join(folder, filename) + '.pkl', mode = 'rb')
    obj = load(f)
    return obj


def print_dataset_to_excel(dataset, folder, data_format):
    filename = '{} - {}.xlsx'.format(dataset['name'], dataset['main reference product'])
    writer = pd.ExcelWriter(os.path.join(folder, filename))
    fields = ['activity name', 'location', 
              'start date', 'end date', 'activity type', 'technology level', 
              'access restricted', 'allocation method']
    data_format = data_format.set_index('in dataframe').loc[fields][['field']]
    data_format = data_format['field'].apply(lambda key: dataset[key])
    df = pd.DataFrame()
    
    if 'data frame' not in dataset:
        dataset['data frame'] = internal_to_df(dataset, data_format)
    
    return ''


def datasets_to_dict(datasets, fields):
    if type(fields) == str or len(fields) == 1:
        if type(fields) in (list, tuple):
            fields = fields[0]
        new_datasets = {dataset[fields]: dataset for dataset in datasets}
    else:
        new_datasets = {tuple([dataset[field] for field in fields]):
            dataset for dataset in datasets}
    return new_datasets


def find_main_reference_product(exchanges):
    amount = 0.
    for exc in exchanges:
        if abs(exc['amount']) > amount:
            amount = exc['amount']
            name = exc['name']
    return name