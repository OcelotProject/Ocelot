# -*- coding: utf-8 -*-
import os
import pandas as pd
import time
from .. import utils
from copy import copy
import numpy as np

def dummy():
    return ''


def dataset_from_excel(dirpath, filename, data_format):
    '''reads datasets defined in a standardized excel format.  Validation happens with the
    validator defined in utils'''
    
    #setting indexes in data_format for convenience
    data_format = data_format.set_index(['parent', 'in data frame']).sortlevel(level=0)
    
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
    
    return dataset


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

def dataset_to_excel(dataset, folder, data_format, activity_overview):
    
    #prepare writer
    dataset = copy(dataset)
    if tuple(data_format.index.names) != ('in data frame'):
        meta = data_format.set_index('in data frame')
    filename = '{} - {} - {}.xlsx'.format(dataset['name'], dataset['location'], 
        dataset['reference product'])
    writer = pd.ExcelWriter(os.path.join(folder, filename))
    
    #put meta information in a data frame
    fields = ['activity name', 'location', 'reference product', 
              'start date', 'end date', 'activity type', 'technology level', 
              'access restricted', 'allocation method']
    meta = meta.loc[fields][['field']]
    meta['value'] = meta['field'].apply(lambda key: dataset[key])
    del meta['field']
    meta = meta.reset_index().rename(columns = {'in data frame': 'field'})
    meta = pd.concat([meta, pd.DataFrame({len(meta): {'field': 'history', 'value': ''}})])
    hist = pd.DataFrame(dataset['history']).transpose().reset_index()
    hist = hist.rename(columns = {'': 'field', '': 'value'})
    meta = pd.concat([meta, hist])
    meta.to_excel(writer, 'meta', columns = ['field', 'value'], 
        index = False, merge_cells = False)
        
    #build a data frame with the quantitative information
    dataset = utils.internal_to_df(dataset, data_format)
    df = dataset['data frame']
    
    #add the activity name and geography of the activity links
    if 'activity link' in list(df.columns):
        with_AL = df[~df['activity link'].isin([np.nan])]
        if tuple(activity_overview.index.names) != ('activity id', 'exchange name'):
            activity_overview = activity_overview.set_index(
                ['activity id', 'exchange name']).sortlevel(level=0)
        for index in set(with_AL.index):
            try:
                sel = activity_overview.loc[tuple(with_AL.loc[index, 
                    ['activity link', 'exchange name']])]
                if type(sel) == pd.core.frame.DataFrame:
                    assert len(sel) == 1
                    sel = sel.iloc[0]
                with_AL.loc[index, 'activity link name'] = sel['activity name']
                with_AL.loc[index, 'activity link location'] = sel['location']
            except KeyError:
                pass
        df = pd.concat([with_AL, df[df['activity link'].isin([np.nan])]])
    
    #write the data frame in excel, in a specific order
    columns = ['data type', 'Ref', 'tag', 'exchange type', 'exchange name', 'parameter name', 
              'property name', 'compartment', 'subcompartment', 
              'activity link name', 'activity link location', 
              'amount', 'unit', 'mathematical relation', 'variable', 
              'uncertainty type', 'mean value', 'variance', 'reliability', 'completeness', 
              'temporal correlation', 'geographical correlation', 
              'further technology correlation']
    for field in set(columns).difference(set(df.columns)):
        columns.remove(field)
    
    #first fragment: exchanges
    fragment = df[df['data type'] == 'exchanges']
    types = ['reference product', 'byproduct', 'from technosphere', 
             'to environment', 'from environment']
    fragments = []
    for t in types:
        f = fragment[fragment['exchange type'] == t]
        if len(f) > 0:
            fragments.append(f.sort_values(by = 'exchange name'))
    
    #then, the other quantitative info
    for t in ['production volume', 'parameters', 'properties']:
        f = df[df['data type'] == t]
        if len(f) > 0:
            fragments.append(f.sort_values(by = 'exchange name'))
    df = pd.concat(fragments)
    df.to_excel(writer, 'quantitative', columns = columns, 
        index = False, merge_cells = False)
    
    #if allocation factors have been calculated, output them
    if 'allocation factors' in dataset:
        df = dataset['allocation factors'].reset_index()
        if 'TVR' in set(df.columns):
            columns = ['exchange name', 'amount', 'price', 'revenu', 'TVR', 
                'amount*TVR', 'amount*TVR/sum(amount*TVR)', 'TV', 'allocation factor']
        else:
            columns = ['exchange name', 'amount', 'price', 'revenu', 'allocation factor']
        df = df.sort_values(by = 'allocation factor')
        df.to_excel(writer, 'allocation factors', columns = columns, 
                    index = False, merge_cells = False)
    
    #save and close
    writer.save()
    writer.close()
    

def internal_to_df(dataset, data_format):
    """Takes a dataset and change its representation to a convenient data frame format"""
    
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
    dataset['data frame'] = df
    
    for field in ['exchanges', 'parameters']:
        if field in dataset:
            del dataset[field]
    
    return dataset


def add_line_to_df(df, data_format, parent, element, to_add = False):
    '''recursive function: checks if an exchange has also PV and properties to output in the dataframe'''
    
    if to_add == False:
        to_add = {'data type': parent}
    else:
        to_add_new = copy(to_add)
        for field in to_add:
            if field not in ['tag', 'exchange type', 'exchange name', 
                    'compartment', 'subcompartment', 'exchange id', 
                    'unit', 'byproduct classification']:
                del to_add_new[field]
        to_add_new['data type'] = parent
        to_add = copy(to_add_new)
        
    for field in element:
        if field == 'uncertainty':
            for field2 in element[field]:
                to_add[data_format.loc[(field, field2), 'in data frame']] = element[field][field2]
        elif field not in ['production volume', 'properties']:
            to_add[data_format.loc[(parent, field), 'in data frame']] = element[field]
    if 'properties' in element:
        for e in element['properties']:
            df = add_line_to_df(df, data_format, 'properties', e, to_add = copy(to_add))
    if 'production volume' in element:
        df = add_line_to_df(df, data_format, 'production volume', 
            element['production volume'], to_add = copy(to_add))
    
    df[len(df)] = copy(to_add)
    return df