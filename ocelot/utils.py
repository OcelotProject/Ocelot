# -*- coding: utf-8 -*-
import os
import functools
import pandas as pd
from copy import copy
import numpy as np
import scipy as sp
from pickle import dump, load
import ocelot
import random

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
        to_add[data_format.loc[('uncertainty', field), 'in data frame']] = u[field]

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
    
    to_add = add_Ref(to_add)
    df[len(df)] = copy(to_add)
    return df


def add_dummy_variable(df):
    if 'variable' not in list(df.columns):
        df['variable'] = ''
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
    try:
        obj = load(f)
    except:
        obj = load(f, encoding = 'cp1252')
    f.close()
    return obj


def do_not_overwrite(folder, filename_to_save, filelist = []):
    if filelist == []:
        filelist = [os.path.join(folder, filename) for filename in os.listdir(folder)]
    if os.path.join(folder, filename_to_save) in filelist:
        extention = filename_to_save.split('.')[-1]
        filename_to_save = filename_to_save.replace('.'+extention, '')
        r = str(random.random()*1000).split('.')[0]
        filename_to_save = filename_to_save+r+'.'+extention
        if filename_to_save in filelist:
            filename_to_save = do_not_overwrite(folder, filename_to_save, filelist = filelist)
    return filename_to_save
    

def print_dataset_to_excel(dataset, folder, data_format, activity_overview):
    dataset = copy(dataset)
    if tuple(data_format.index.names) != ('in data frame'):
        meta = data_format.set_index('in data frame')
    filename = '{} - {} - {}.xlsx'.format(dataset['name'], dataset['location'], 
        dataset['main reference product'])
    filename = do_not_overwrite(folder, filename, filelist = [])
        
    writer = pd.ExcelWriter(os.path.join(folder, filename))
    fields = ['activity name', 'location', 'main reference product', 
              'start date', 'end date', 'activity type', 'technology level', 
              'access restricted', 'allocation method', 'last operation']
    meta = meta.loc[fields][['field']]
    meta['value'] = meta['field'].apply(lambda key: dataset[key])
    del meta['field']
    meta = meta.reset_index().rename(columns = {'in data frame': 'field'})
    meta.to_excel(writer, 'meta', columns = ['field', 'value'], 
        index = False, merge_cells = False)
    if 'data frame' not in dataset:
        dataset = internal_to_df(dataset, data_format)
    df = dataset['data frame']
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


def find_main_reference_product(dataset):
    amount = 0.
    for exc in dataset['exchanges']:
        if exc['type'] in ['reference product'] and abs(exc['amount']) > amount:
            amount = exc['amount']
            name = exc['name']
    return name


def select_exchanges_to_technosphere(df):
    '''selects only the lines of the data frame with an exchange amount to technosphere'''
    df = df.copy()
    sel = df[df['data type'] == 'exchanges']
    sel = sel[sel['exchange type'].isin(['byproduct', 'reference product'])]
	
    return sel


def make_reference_product(chosen_product_exchange_id, dataset):
    dataset_copy = copy(dataset)
    #find new reference product
    df = dataset_copy['data frame']
    exchanges_to_technosphere = select_exchanges_to_technosphere(df)
    sel = exchanges_to_technosphere[
        exchanges_to_technosphere['exchange id'] == chosen_product_exchange_id].iloc[0]
        
    #add new reference product to metainformation
    dataset_copy['main reference product'] = sel['exchange name']
    dataset_copy['main reference product index'] = sel.name
    
    #this assertion error will be caught and handle by calling function, do not remove!
    assert df.loc[dataset_copy['main reference product index'], 'amount'] != 0.
    
    #put to zero the amount of the other coproducts
    indexes = list(tuple(exchanges_to_technosphere.index))
    indexes.remove(sel.name)
    allocated_df = df.copy()
    allocated_df.loc[indexes, 'amount'] = 0.
    
    #make the selected coproduct the reference product
    indexes = allocated_df[allocated_df['exchange id'
        ] == chosen_product_exchange_id]
    indexes = indexes[indexes['exchange type'
        ].isin(['reference product', 'byproduct'])]
    indexes = list(indexes.index)
    allocated_df.loc[indexes, 'exchange type'] = 'reference product'
    
    #remove the production volume of the other outputs to technosphere
    conditions = ~((allocated_df['data type'] == 'production volume') & (
        allocated_df['exchange name'] != dataset_copy['main reference product']))
    allocated_df = allocated_df[conditions]
    
    dataset_copy['data frame'] = allocated_df.copy()
    
    return dataset_copy


def find_main_reference_product_index(dataset):
    df = dataset['data frame']
    sel = df[df['data type'] == 'exchanges']
    sel = sel[sel['exchange type'] == 'reference product']
    sel = sel[sel['exchange name'] == dataset['main reference product']]
    main_reference_product_index = list(sel.index)[0]
    return main_reference_product_index

def scale_exchanges(dataset):
    '''scales the amount of the exchanges to get a reference exchange amount of 1 or -1'''
    
    df = dataset['data frame']
    main_reference_product_index = find_main_reference_product_index(dataset)
    ref_amount = abs(df.loc[main_reference_product_index, 'amount'])
    assert ref_amount != 0.
    if ref_amount != 1.:
        indexes = list(df[df['data type'] == 'exchanges'].index)
        df.loc[indexes, 'amount'] = df.loc[indexes, 'amount'] / ref_amount
    dataset['data frame'] = df
    
    return dataset


def filter_datasets(datasets, activity_overview, criteria):
    datasets = datasets_to_dict(datasets, ['name', 'location'])
    for field in criteria:
        activity_overview = activity_overview[activity_overview[field].isin(criteria[field])]
    new_datasets = []
    activity_overview = activity_overview.set_index(['activity name', 'location']).sortlevel(level=0)
    for index in set(activity_overview.index):
        new_datasets.append(datasets[index])
    return new_datasets


def replace_Ref_by_variable(dataset):
    '''finds mathematical relations using Ref instead of variables.  
    The Refs are replaced by variables'''
    
    #find indexes where there are mathematical relations
    df = dataset['data frame']
    indexes = df[~df['mathematical relation'].apply(ocelot.utils.is_empty)]
    if len(indexes) > 0:
        #find indexes where the mathematical relation contains Refs
        indexes = list(indexes[indexes['mathematical relation'].apply(
            lambda x: 'Ref(' in x)].index)
    
    if len(indexes) > 0:
        #build how to go from Ref to variable
        Ref_to_variable = df[['Ref', 'variable']].set_index('Ref')
        
        #find and replace Refs by variables
        for index in indexes: #for each mathematical relation containing a Ref
            for reg in ocelot.io.ecospold2_meta.REF_REGURLAR_EXPRESSIONS: #for each kind of Ref
                founds = reg.findall(df.loc[index, 'mathematical relation'])
                for found in founds:
                    df.loc[index, 'mathematical relation'] = df.loc[index, 'mathematical relation'
                        ].replace(found, Ref_to_variable.loc[found, 'variable'])
    
    dataset['data frame'] = df.copy()
    
    return dataset


def build_graph(dataset, combined = False):
    '''builds a matrix of dependencies between each mathematical relation and other variables'''
    #Problem: if a mathematicalRelation1 = variable11*2, and the variableName variable1 exists, 
    #and we do "variable1 in mathematicalRelation1", we will get a false dependency of 
    #mathematicalRelation1 on variable1.  
    #Solution: check for the longest variableName first, and once found, remove
    #them from the mathematicalRelation.
    dataset = ocelot.utils.replace_Ref_by_variable(dataset)
    dataset = copy(dataset)
    df = dataset['data frame']
    
    df['length'] = df['variable'].apply(len)
    order = list(df.sort_values(by = 'length', ascending = False).index)
    if combined:
        #in the context of combined production, PVs and amounts of reference products 
        #are out of the equation
        indexes = list(df[df['data type'] == 'production volume'].index)
        df.loc[indexes, 'mathematical relation'] = ''
        indexes = df[df['data type'] == 'exchanges']
        indexes = list(indexes[indexes['exchange type'] == 'reference product'].index)
        df.loc[indexes, 'mathematical relation'] = ''
    df_with_formula = df[~df['mathematical relation'].apply(ocelot.utils.is_empty)]
    mathematical_relations = dict(zip(list(df_with_formula.index), 
        list(df_with_formula['mathematical relation'])))
    
    #gathering information for the graph matrix
    rows = []
    columns = []
    for i in mathematical_relations:
        for j in order:
            v = df.loc[j, 'variable']
            if v in mathematical_relations[i]:
                mathematical_relations[i] = mathematical_relations[i].replace(v, '')
                rows.append(j)
                columns.append(i)
    c = [1 for i in range(len(rows))]
    ij = np.vstack((rows, columns))
    graph = sp.sparse.csr_matrix((c,ij), shape = (len(df), len(df)))
    
    #graph contains a "1" in position (i,j) if the mathematical relation i depends on amount j
    dataset['graph'] = graph
    
    return dataset


def calculation_order(dataset):
    #for a given amount, find all the paths between it and the other amounts
    #the calculation order is based on the longest path: amounts with longest 
    #maximum length path are calculated last.
  
    dataset = copy(dataset)
    df = dataset['data frame']
    graph = dataset['graph']
    longestPath = {}
    for index in range(len(df)): #for each amount
        paths = [[index]] #the path starts with itself
        longest = 0
        while True:#iterate until there is no more path to find
            paths_to_check = []
            for i in range(len(paths)):
                path = copy(paths[i])
                rows, columns, c = sp.sparse.find(graph.getcol(path[-1]))
                if len(rows) == 0: #if the last amount of the path has no dependant
                    longest = max(longest, len(path))
                    #keep track of the longest path so far
                else:
                    for row in rows:
                        if row in path:
                            #if the amount to add in the path is already there, 
                            #it means there is a circular reference
                            raise NotImplementedError('circular reference')
                        #accumulate path at the end of the list of path
                        new_path = copy(path)
                        new_path.append(row)
                        paths_to_check.append(new_path)
            if len(paths_to_check) == 0:
                #no more path to check, out of the loop!
                break
            else:
                paths = copy(paths_to_check)
        longestPath[index] = copy(longest)
    df['calculation order'] = pd.Series(longestPath)
    df = df.sort_values(by = 'calculation order')
    
    dataset['data frame'] = df
    
    return dataset


def recalculate(dataset):
    dataset = copy(dataset)
    df = dataset['data frame']
    #the shortest paths do not depend on other variables, so they are "calculated" first
    minOrder = df['calculation order'].min()
    sel = df[df['calculation order'] == minOrder]
    calculatedAmount = dict(zip(list(sel['variable']), list(sel['amount'])))
    values = dict(zip(list(sel.index), list(sel['amount'])))
    
    #then, calculation of the other path, in increasing length of path
    for index in list(df[df['calculation order'] != minOrder].index):
        m = df.loc[index, 'mathematical relation']
        v = df.loc[index, 'variable']
        if m == '':
            calculatedAmount[v] = copy(df.loc[index, 'amount'])
        else:
            try:
                calculatedAmount[v] = eval(m, calculatedAmount)
            except:
                raise NotImplementedError('error in calculation of an amount')
        values[index] = copy(calculatedAmount[df.loc[index, 'variable']])
    df['calculated amount'] = pd.Series(values)
    
    dataset['data frame'] = df    
    
    return dataset


def reset_index_df(dataset):
    '''after some linking steps, the number of rows might have changed, and this
    creates errors in the recalculation algorithm.  This function resets the index of the
    dataframe to a continuous series from 0 to len(dataset['data frame']) - 1.  '''
    
    dataset = copy(dataset)
    df = dataset['data frame']
    df.index = range(len(df))
    sel = df[df['exchange type'] == 'reference product']
    sel = sel[sel['data type'] == 'exchanges']
    sel = sel[sel['exchange name'] == dataset['main reference product']]
    assert len(sel) == 1
    dataset['main reference product index'] = sel.iloc[0].name
    dataset['data frame'] = df
    
    return dataset


def validate_against_linking(datasets, system_model_folder, data_format, result_folder):
    folder = os.path.join(system_model_folder, 'excel and csv')
    filename = 'activity_overview_3.2_cut-off.xlsx'
    ao = pd.read_excel(os.path.join(folder, filename), 'activity overview')
    ao = ao.set_index(['activityName', 'Geography', 'Product']).sortlevel(level=0)
    folder = folder = os.path.join(system_model_folder, 'datasets')
    results = {}
    
    for dataset in datasets:
        print('validating', dataset['name'], dataset['location'], dataset['main reference product'])
        print(datasets.index(dataset), 'of', len(datasets))
        to_add = {'activity name': dataset['name'], 
                  'location': dataset['location'], 
                'reference product': dataset['main reference product']}
        index = dataset['name'], dataset['location'], dataset['main reference product']
        found = True
        if index in set(ao.index):
            linked_filename = ao.loc[index]['filename']
        elif index[1] == 'GLO':
            index = dataset['name'], 'RoW', dataset['main reference product']
            if index in set(ao.index):
                linked_filename = ao.loc[index]['filename']
            else:
                found = False
        else:
            found = False
        if found:
            df = dataset['data frame'].copy()
            sel = df[df['data type'] == 'exchanges']
            sel = sel[sel['tag'] == 'elementaryExchange']
            sel = sel[sel['amount'] != 0.]
            if len(sel) > 0:
                linked_filename = os.path.join(folder, linked_filename)
                linked_dataset = ocelot.io.extract_ecospold2.generic_extractor(linked_filename)[0]
                linked_dataset = ocelot.utils.internal_to_df(linked_dataset, data_format)
                df = linked_dataset['data frame'].copy()
                sel_linked = df[df['data type'] == 'exchanges']
                sel_linked = sel_linked[sel_linked['tag'] == 'elementaryExchange']
                sel_linked = sel_linked[sel_linked['amount'] != 0.]
                sel = sel.set_index(['exchange name', 'compartment', 'subcompartment'
                    ])[['amount']]
                sel_linked = sel_linked.set_index(['exchange name', 'compartment', 'subcompartment'
                    ])[['amount']]
                df = sel.join(sel_linked, how = 'outer', rsuffix = '_reference')
                df['test'] = abs(df['amount'].divide(df['amount_reference']))
                tolerance = .001
                if sum(df['test'] > 1. + tolerance) + sum(df['test'] < 1. - tolerance):
                    to_add['message'] = 'differences'
                else:
                    to_add['message'] = 'validation passed'
            else:
                to_add['message'] = 'no exchange to/from nature: nothing to validate against the reference'
        else:
            to_add['message'] = 'reference not found, (not necessarily an error)'
        results[len(results)] = copy(to_add)
        print(to_add['message'])
        print('')
    results = pd.DataFrame(results).transpose()
    filename = 'validation_results.xlsx'
    columns = ['activity name', 'location', 'reference product', 'message']
    results.to_excel(os.path.join(result_folder, filename), columns = columns, 
                     index = False, merge_cells = False)