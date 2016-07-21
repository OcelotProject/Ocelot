# -*- coding: utf-8 -*-
import os
import pandas as pd
import time
from .. import utils
from copy import copy

def dummy():
    return ''

def extract_excel(dirpath, data_format):
    data_format = data_format.set_index(['parent', 'in data frame']).sortlevel(level=0)
    assert os.path.isdir(dirpath), "Can't find directory {}".format(dirpath)
    filelist = [os.path.join(dirpath, filename)
                for filename in os.listdir(dirpath)
                if (filename.lower().endswith(".xlsx") and 
                    '~' not in filename)]
    datasets = []
    for filename in filelist:
        dataset = read_meta(dirpath, filename, data_format)
        df = pd.read_excel(os.path.join(dirpath, filename), 'quantitative')
        exchanges = df[df['data type'] == 'exchanges']
        PVs = df[df['data type'] == 'production volume'].set_index('exchange id')
        properties = df[df['data type'] == 'properties'].set_index('exchange id')
        for col in ['unit', 'byproduct classification', 'data type', 'name', 'exchange type']:
            del PVs[col]
        for col in ['unit', 'byproduct classification', 'data type', 'exchange type']:
            del properties[col]
        dataset = add_exchanges(dataset, exchanges, properties, PVs, data_format)
        parameters = df[df['data type'] == 'parameters']
        if len(parameters) > 0:
            dataset['parameters'] = []
            del parameters['data type']
            for index in parameters.index:
                sel = pd.DataFrame(parameters.loc[index])
                sel = sel[~sel[index].apply(utils.is_empty)]
                sel = sel.join(data_format.loc['parameters'][['in dataset']])
                dataset['parameters'].append(dict(zip(list(sel['in dataset']), 
                    list(sel[index]))))
        datasets.append(copy(dataset))
    return datasets
def add_PV(exc, PVs, data_format):
    if exc['id'] in PVs.index:
        sel = pd.DataFrame(PVs.loc[exc['id']])
        sel = sel[~sel[exc['id']].apply(utils.is_empty)]
        sel = sel.join(data_format.loc['production volume'][['in dataset']])
        exc['production volume'] = dict(zip(list(sel['in dataset']), 
            list(sel[exc['id']])))
    return exc
def add_properties(exc, properties, data_format):
    if exc['id'] in properties.index:
        exc['properties'] = []
        d = properties.loc[exc['id']]
        if type(d) != pd.core.frame.DataFrame:
            d = pd.DataFrame(d).transpose()
        for i in range(len(d)):
            sel = pd.DataFrame(d.iloc[i])
            sel = sel[~sel[exc['id']].apply(utils.is_empty)]
            sel = sel.join(data_format.loc['properties'][['in dataset']])
            exc['properties'].append(dict(zip(list(sel['in dataset']), 
                list(sel[exc['id']]))))
    return exc
def add_parameters(dataset, parameters, data_format):
    return dataset
def read_meta(dirpath, filename, data_format):
    df = pd.read_excel(os.path.join(dirpath, filename), 'meta').set_index('field')
    df = df.join(data_format.loc['dataset'][['in dataset']]).reset_index()
    dataset = dict(zip(list(df['in dataset']), list(df['value'])))
    dataset['history'] = {'extract_excel': time.ctime()}
    return dataset
def add_exchanges(dataset, exchanges, properties, PVs, data_format):
    dataset['exchanges'] = []
    for index in exchanges.index:
        sel = pd.DataFrame(exchanges.loc[index])
        sel = sel[~sel[index].apply(utils.is_empty)]
        sel = sel.join(data_format.loc['exchanges'][['in dataset']])
        exc = dict(zip(list(sel['in dataset']), list(sel[index])))
        exc = add_PV(exc, PVs, data_format)
        exc = add_properties(exc, properties, data_format)
        dataset['exchanges'].append(exc)
    return dataset
