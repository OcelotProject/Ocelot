# -*- coding: utf-8 -*-
import os
import pandas as pd
import time
from .. import utils
from copy import copy

def dummy():
    return ''


def extract_excel(dirpath, data_format):
    '''reads datasets defined in a standardized excel format.  Validation happens with the
    validator defined in utils'''
    
    #setting indexes in data_format for convenience
    data_format = data_format.set_index(['parent', 'in data frame']).sortlevel(level=0)
    
    #making a filelist
    assert os.path.isdir(dirpath), "Can't find directory {}".format(dirpath)
    filelist = [os.path.join(dirpath, filename)
                for filename in os.listdir(dirpath)
                if (filename.lower().endswith(".xlsx") and 
                    '~' not in filename)]
    
    datasets = []
    for filename in filelist:
        #reading the meta data
        dataset = read_meta(dirpath, filename, data_format)
        
        #loading the quantitative and dispatching in different data frames for convenience
        df = pd.read_excel(os.path.join(dirpath, filename), 'quantitative')
        exchanges = df[df['data type'] == 'exchanges']
        del exchanges['data type']
        PVs = df[df['data type'] == 'production volume'].set_index('exchange id')
        properties = df[df['data type'] == 'properties'].set_index('exchange id')
        if len(PVs) > 0:
            for col in ['unit', 'byproduct classification', 'data type', 'name', 'exchange type']:
                del PVs[col]
        if len(properties) > 0:
            for col in ['byproduct classification', 'data type', 'exchange type']:
                del properties[col]
        parameters = df[df['data type'] == 'parameters']
        del parameters['data type']
        
        #adding exchanges
        dataset = add_exchanges(dataset, exchanges, properties, PVs, data_format)
        
        #adding parameters, if any
        dataset = add_parameters(dataset, parameters, data_format)
        
        #adding dataset to the list of datasets
        datasets.append(copy(dataset))
    
    return datasets


def add_PV(exc, PVs, data_format):
    if exc['id'] in PVs.index:
        #only if the exchange has a PV in the quantitative data frame
        sel = pd.DataFrame(PVs.loc[exc['id']])
        
        #getting rid of empty fields and mapping to field names in internal format
        sel = sel[~sel[exc['id']].apply(utils.is_empty)]
        sel = sel.join(data_format.loc['production volume'][['in dataset']])
        
        #adding to the exchange
        exc['production volume'] = dict(zip(list(sel['in dataset']), 
            list(sel[exc['id']])))
    
    return exc


def add_properties(exc, properties, data_format):
    if exc['id'] in properties.index:
        #only if the exchange has a properties in the quantitative data frame
        exc['properties'] = []
        
        #storing properties in a data frame
        d = properties.loc[exc['id']]
        if type(d) != pd.core.frame.DataFrame:
            d = pd.DataFrame(d).transpose()
        
        for i in range(len(d)):
            #getting rid of empty fields and mapping to field names in internal format
            sel = pd.DataFrame(d.iloc[i])
            sel = sel[~sel[exc['id']].apply(utils.is_empty)]
            sel = sel.join(data_format.loc['properties'][['in dataset']])
            
            #adding to the exchange
            exc['properties'].append(dict(zip(list(sel['in dataset']), 
                list(sel[exc['id']]))))
    
    return exc


def add_parameters(dataset, parameters, data_format):
    if len(parameters) > 0:
        #only if some parameters are in the quantitative data frame
        dataset['parameters'] = []
        
        for index in parameters.index:
            #getting rid of empty fields and mapping to field names in internal format
            sel = pd.DataFrame(parameters.loc[index])
            sel = sel[~sel[index].apply(utils.is_empty)]
            sel = sel.join(data_format.loc['parameters'][['in dataset']])
            
            #adding to the dataset
            dataset['parameters'].append(dict(zip(list(sel['in dataset']), 
                list(sel[index]))))
    
    return dataset


def read_meta(dirpath, filename, data_format):
    #loading the data frame
    df = pd.read_excel(os.path.join(dirpath, filename), 'meta').set_index('field')
    
    #mapping to field names in internal format
    df = df.join(data_format.loc['dataset'][['in dataset']]).reset_index()
    dataset = dict(zip(list(df['in dataset']), list(df['value'])))
    
    #adding history time stamp
    dataset['history'] = {'extract_excel': time.ctime()}
    
    return dataset


def add_exchanges(dataset, exchanges, properties, PVs, data_format):
    dataset['exchanges'] = []
    for index in exchanges.index:
        #getting rid of empty fields and mapping to field names in internal format
        sel = pd.DataFrame(exchanges.loc[index])
        sel = sel[~sel[index].apply(utils.is_empty)]
        sel = sel.join(data_format.loc['exchanges'][['in dataset']])
        exc = dict(zip(list(sel['in dataset']), list(sel[index])))
        if 'environment' in exc['type']:
            exc['tag'] = 'elementaryExchange'
        else:
            exc['tag'] = 'intermediateExchange'
        
        #adding PV, if any
        exc = add_PV(exc, PVs, data_format)
        
        #adding properties, if any
        exc = add_properties(exc, properties, data_format)
        
        #adding to the dataset
        dataset['exchanges'].append(exc)
    
    return dataset
