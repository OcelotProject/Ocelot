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
    return e in ['', None, np.nan, np.NaN, np.nan, []]


def uncertainty_to_internal(s):
    if 'uncertainty type' in s and not is_empty(s['uncertainty type']):
        pass
    return ''


def add_line_to_df(df, data_format, parent, element, to_add = False):
    if to_add == False:
        to_add = {'data type': parent}
    else:
        to_add_new = copy(to_add)
        for field in to_add:
            if field not in ['tag', 'exchange type', 'exchange name', 
                    'compartment', 'subcompartment', 'exchange id']:
                del to_add_new[field]
        to_add_new['data type'] = parent
        to_add = copy(to_add_new)
        
    for field in element:
        if field == 'uncertainty':
            for field2 in element[field]:
                to_add[data_format.loc[(field, field2), 'in dataframe']] = element[field][field2]
        elif field not in ['production volume', 'properties']:
            to_add[data_format.loc[(parent, field), 'in dataframe']] = element[field]
    if 'properties' in element:
        for e in element['properties']:
            df = add_line_to_df(df, data_format, 'properties', e, to_add = copy(to_add))
    if 'production volume' in element:
        df = add_line_to_df(df, data_format, 'production volume', 
            element['production volume'], to_add = copy(to_add))
    
    to_add = add_Ref(to_add)
    df[len(df)] = copy(to_add)
    return df


def add_dummy_variable(df):
    if 'variable' in list(df.columns):
        counter = 0
        for index in set(df.index):
            if is_empty(df.loc[index, 'variable']):
                df.loc[index, 'variable'] = 'dummy_variable_{}'.format(counter)
                counter += 1
    return df

def add_Ref(to_add):
    if to_add['data type'] == 'exchanges':
        to_add['Ref'] = "Ref('{}')".format(to_add['exchange id'])
    elif to_add['data type'] == 'production volume':
        to_add['Ref'] = "Ref('{}', 'ProductionVolume')".format(to_add['exchange id'])
    elif to_add['data type'] == 'parameters':
        to_add['Ref'] = "Ref('{}')".format(to_add['parameter id'])
    elif to_add['data type'] == 'properties':
        to_add['Ref'] = "Ref('{}', '{}')".format(to_add['exchange id'], to_add['property id'])
    else:
        1/0
    return to_add


def internal_to_df(dataset, data_format):
    """Takes a dataset and change its representation to a convenient dataframe format"""
    if tuple(data_format.index.names) != ('parent', 'field'):
        data_format = data_format.set_index(['parent', 'field']).sortlevel(level=0)
    df = {}
    for parent in ['exchanges', 'parameters']:
        if parent in dataset:
            for element in dataset[parent]:
                df = add_line_to_df(df, data_format, parent, element)
    df = pd.DataFrame(df).transpose()
    if np.NaN in df:
        del df[np.NaN]
    df = add_dummy_variable(df)
    dataset['data frame'] = df
    
    return dataset


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


def print_dataset_to_excel(dataset, folder, data_format, activity_overview):
    if tuple(data_format.index.names) != ('in dataframe'):
        meta = data_format.set_index('in dataframe')
    filename = '{} - {} - {}.xlsx'.format(dataset['name'], dataset['location'], 
        dataset['main reference product'])
    writer = pd.ExcelWriter(os.path.join(folder, filename))
    fields = ['activity name', 'location', 'main reference product', 
              'start date', 'end date', 'activity type', 'technology level', 
              'access restricted', 'allocation method']
    meta = meta.loc[fields][['field']]
    meta['value'] = meta['field'].apply(lambda key: dataset[key])
    del meta['field']
    meta = meta.reset_index().rename(columns = {'in dataframe': 'field'})
    meta.to_excel(writer, 'meta', columns = ['field', 'value'], 
        index = False, merge_cells = False)
    if 'data frame' not in dataset:
        dataset['data frame'] = internal_to_df(dataset, data_format)
    df = dataset['data frame']
    if 'activity link' in list(df.columns):
        with_AL = df[~df['activity link'].isin([np.nan])]
        if tuple(activity_overview.index.names) != ('activity id', 'exchange name'):
            activity_overview = activity_overview.set_index(
                ['activity id', 'exchange name']).sortlevel(level=0)
        for index in set(with_AL.index):
            sel = activity_overview.loc[tuple(with_AL.loc[index, 
                ['activity link', 'exchange name']])]
            if type(sel) == pd.core.frame.DataFrame:
                assert len(sel) == 1
                sel = sel.iloc[0]
            with_AL.loc[index, 'activity link name'] = sel['activity name']
            with_AL.loc[index, 'activity link location'] = sel['location']
        df = pd.concat([with_AL, df[df['activity link'].isin([np.nan])]])
    columns = ['data type', 'Ref', 'tag', 'exchange type', 'exchange name', 'parameter name', 
              'property name', 'compartment', 'subcompartment', 
              'activity link name', 'activity link location', 
              'amount', 'unit', 'mathematical relation', 'variable', 
              'uncertainty type', 'mean value', 'variance', 'reliability', 'completeness', 
              'temporal correlation', 'geographical correlation', 
              'further technology correlation']
    for field in set(columns).difference(set(df.columns)):
        columns.remove(field)
    fragment = df[df['data type'] == 'exchanges']
    types = ['reference product', 'byproduct', 'from technosphere', 
             'to environment', 'from environment']
    fragments = []
    for t in types:
        f = fragment[fragment['exchange type'] == t]
        if len(f) > 0:
            fragments.append(f.sort_values(by = 'exchange name'))
    for t in ['production volume', 'parameters', 'properties']:
        f = df[df['data type'] == t]
        if len(f) > 0:
            fragments.append(f.sort_values(by = 'exchange name'))
    df = pd.concat(fragments)
    df.to_excel(writer, 'quantitative', columns = columns, 
        index = False, merge_cells = False)
    writer.save()
    writer.close()

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