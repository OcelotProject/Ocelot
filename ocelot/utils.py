# -*- coding: utf-8 -*-
import os
import functools
import pandas as pd
from copy import copy, deepcopy
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


def is_empty(e):
    if type(e) in [float]:
        test = e in ['', None, np.nan, np.NaN, np.nan, []] or np.isnan(e)
    else:
        test = e in ['', None, np.nan, np.NaN, np.nan, []]
    return test


def uncertainty_to_internal(to_add, sel, data_format):
    uncertainty = {}
    for col in set(data_format.loc['uncertainty'].index):
        if col in sel.index and not ocelot.utils.is_empty(sel[col]):
            field = data_format.loc[('uncertainty', col), 'field']
            uncertainty[field] = sel[col]
    if len(uncertainty) > 0:
        to_add['uncertainty'] = uncertainty
    return to_add


def add_dummy_variable(dataset):
    counter = 0
    for exc in dataset['exchanges']:
        if 'variable' not in exc:
            exc['variable'] = 'dummy_variable_{}'.format(counter)
            counter += 1
        if 'production volume' in exc and 'variable' not in exc['production volume']:
            exc['production volume']['variable'] = 'dummy_variable_{}'.format(counter)
            counter += 1
        if 'properties' in exc:
            for p in exc['properties']:
                if 'variable' not in p:
                    p['variable'] = 'dummy_variable_{}'.format(counter)
                    counter += 1
    if 'parameters' in dataset:
        for p in dataset['parameters']:
            if 'variable' not in p:
                p['variable'] = 'dummy_variable_{}'.format(counter)
                counter += 1
    return dataset


def add_Ref(dataset):
    for exc in dataset['exchanges']:
        exc['Ref'] = "Ref('{}')".format(exc['id'])
        if 'production volume' in exc:
            exc['production volume']['Ref'] = "Ref('{}', 'ProductionVolume')".format(
                exc['id'])
        if 'properties' in exc:
            for p in exc['properties']:
                p['Ref'] = "Ref('{}', '{}')".format(exc['id'], p['id'])
    if 'parameters' in dataset:
        for p in dataset['parameters']:
            p['Ref'] = "Ref('{}')".format(p['id'])
    
    return dataset

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
    
    for field in ['exchanges', 'parameters']:
        if field in dataset:
            del dataset[field]
    
    return dataset


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
        dataset['reference product'])
    filename = do_not_overwrite(folder, filename, filelist = [])
        
    writer = pd.ExcelWriter(os.path.join(folder, filename))
    fields = ['activity name', 'location', 'reference product', 
              'start date', 'end date', 'activity type', 'technology level', 
              'access restricted', 'allocation method', 'last operation']
    meta = meta.loc[fields][['field']]
    meta['value'] = meta['field'].apply(lambda key: dataset[key])
    del meta['field']
    meta = meta.reset_index().rename(columns = {'in data frame': 'field'})
    meta = pd.concat([meta, pd.DataFrame({len(meta): {'field': 'history', 'value': ''}})])
    hist = pd.DataFrame(dataset['history']).transpose().reset_index()
    1/0
    #hist = hist.sort_values(by = )
    hist = hist.rename(columns = {'': 'field', '': 'value'})
    meta = pd.concat([meta, hist])
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


def make_reference_product(reference_product_name, dataset):
    new_dataset = deepcopy(dataset)
    
    #change type if necessary
    for exc in new_dataset['exchanges']:
        if exc['type'] in ['reference product', 'byproduct']:
            if exc['name'] == reference_product_name:
                assert exc['amount'] != 0.
                exc['type'] = 'reference product'
                new_dataset['reference product'] = exc['name']
            else:
                #put to zero the amount of the other coproducts
                exc['amount'] = 0.
                
                #remove the production volume of the other outputs to technosphere
                if 'production volume' in exc:
                    del exc['production volume']
    
    return new_dataset


def find_reference_product(dataset):
    for exc in dataset['exchanges']:
        if exc['name'] == dataset['reference product'] and exc['type'] == 'reference product':
            break
    return exc

def scale_exchanges(dataset):
    '''scales the amount of the exchanges to get a reference product amount of 1 or -1'''
    
    ref = find_reference_product(dataset)
    assert ref['amount'] != 0.
    if ref['amount'] != 1.:
        for exc in dataset['exchanges']:
            exc['amount'] = exc['amount'] / abs(ref['amount'])
    
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


def build_Ref_to_variable(dataset):
    Ref_to_variable = {}
    for exc in dataset['exchanges']:
        Ref_to_variable[exc['Ref']] = exc['variable']
        if 'production volume' in exc:
            Ref_to_variable[exc['production volume']['Ref']] = exc['production volume']['variable']
        if 'properties' in exc:
            for p in exc['properties']:
                Ref_to_variable[p['Ref']] = p['variable']
    if 'parameters' in dataset:
        for p in dataset['parameters']:
            Ref_to_variable[p['Ref']] = p['variable']
    return Ref_to_variable


def replace_Ref_by_variable(mathematical_relation, Ref_to_variable):
    for reg in ocelot.io.ecospold2_meta.REF_REGURLAR_EXPRESSIONS:
        founds = reg.findall(mathematical_relation)
        for found in founds:
            mathematical_relation = mathematical_relation.replace(
                found, Ref_to_variable[found])
    return mathematical_relation


def replace_all_Ref_by_variable(dataset):
    '''finds mathematical relations using Ref instead of variables.  
    The Refs are replaced by variables'''
    Ref_to_variable = build_Ref_to_variable(dataset)
    for exc in dataset['exchanges']:
        if 'mathematical relation' in exc:
            exc['mathematical relation'] = replace_Ref_by_variable(
                exc['mathematical relation'], Ref_to_variable)
        if 'production volume' in exc:
            if 'mathematical relation' in exc['production volume']:
                exc['production volume']['mathematical relation'] = replace_Ref_by_variable(
                    exc['production volume']['mathematical relation'], Ref_to_variable)
        if 'properties' in exc:
            for p in exc['properties']:
                if 'mathematical relation' in p:
                    p['mathematical relation'] = replace_Ref_by_variable(
                        p['mathematical relation'], Ref_to_variable)
    if 'parameters' in dataset:
        for p in dataset['parameters']:
            if 'mathematical relation' in p:
                p['mathematical relation'] = replace_Ref_by_variable(
                    p['mathematical relation'], Ref_to_variable)
    
    return dataset


def build_quantity_df(dataset):
    df = {}
    for exc in dataset['exchanges']:
        to_add = {}
        for field in ['Ref', 'variable', 'mathematical relation', 'amount', 
              'name', 'compartment', 'subcompartment', 'activity link', 
              'type']:
            if field in exc:
                to_add[field] = exc[field]
            else:
                to_add[field] = ''
        to_add['data type'] = 'exchanges'
        df[len(df)] = copy(to_add)
        if 'production volume' in exc:
            to_add = {}
            for field in ['name', 'compartment', 'subcompartment', 'activity link', 
                  'type']:
                if field in exc:
                    to_add[field] = exc[field]
                else:
                    to_add[field] = ''
            for field in ['Ref', 'variable', 'mathematical relation', 'amount']:
                if field in exc['production volume']:
                    to_add[field] = exc['production volume'][field]
            to_add['data type'] = 'production volume'
            df[len(df)] = copy(to_add)
        if 'properties' in exc:
            for p in exc['properties']:
                to_add = {}
                for field in ['name', 'compartment', 'subcompartment', 'activity link', 
                              'type']:
                    if field in exc:
                        to_add[field] = exc[field]
                    else:
                        to_add[field] = ''
                for field in ['Ref', 'variable', 'mathematical relation', 'amount']:
                    if field in p:
                        to_add[field] = p[field]
                    else:
                        to_add[field] = ''
                to_add['property name'] = p['name']
                to_add['data type'] = 'properties'
                df[len(df)] = copy(to_add)
    if 'parameters' in dataset:
        for p in dataset['parameters']:
            to_add = {}
            for field in ['Ref', 'variable', 'mathematical relation', 'amount']:
                if field in p:
                    to_add[field] = p[field]
                else:
                    to_add[field] = ''
            to_add['parameter name'] = p['name']
            to_add['data type'] = 'parameters'
            df[len(df)] = copy(to_add)
    df = pd.DataFrame(df).transpose()
    dataset['quantity data frame'] = df.copy()
    
    return dataset

def build_graph(dataset, combined = False):
    '''builds a matrix of dependencies between each mathematical relation and other variables'''
    #Problem: if a mathematicalRelation1 = variable11*2, and the variableName variable1 exists, 
    #and we do "variable1 in mathematicalRelation1", we will get a false dependency of 
    #mathematicalRelation1 on variable1.  
    #Solution: check for the longest variableName first, and once found, remove
    #them from the mathematicalRelation.
    dataset = add_Ref(dataset)
    dataset = add_dummy_variable(dataset)
    dataset = replace_all_Ref_by_variable(dataset)
    dataset = build_quantity_df(dataset)
    quantity_df = dataset['quantity data frame']
    quantity_df['length'] = quantity_df['variable'].apply(len)
    order = list(quantity_df.sort_values(by = 'length', ascending = False).index)
    
    df_with_formula = quantity_df[~quantity_df['mathematical relation'
        ].apply(ocelot.utils.is_empty)]
    df_with_formula = df_with_formula[quantity_df['data type'] != 'production volume']
    c = (df_with_formula['data type'] == 'exchanges') & (df_with_formula['type'] == 'reference product')
    df_with_formula = df_with_formula[~c]
    mathematical_relations = dict(zip(list(df_with_formula.index), 
        list(df_with_formula['mathematical relation'])))
    
    #gathering information for the graph matrix
    rows = []
    columns = []
    variables = dict(zip(list(quantity_df.index), list(quantity_df['variable'])))
    for i in mathematical_relations:
        for j in order:
            variable = variables[j]
            if variable in mathematical_relations[i]:
                mathematical_relations[i] = mathematical_relations[i].replace(variable, '')
                rows.append(int(j))
                columns.append(int(i))
    c = [1 for i in range(len(rows))]
    ij = np.vstack((rows, columns))
    graph = sp.sparse.csr_matrix((c,ij), shape = (len(quantity_df), len(quantity_df)))
    
    #graph contains a "1" in position (i,j) if the mathematical relation i depends on amount j
    dataset['graph'] = graph
    
    return dataset


def calculation_order(dataset):
    #for a given amount, find all the paths between it and the other amounts
    #the calculation order is based on the longest path: amounts with longest 
    #maximum length path are calculated last.
  
    graph = dataset['graph']
    longestPath = {}
    for index in range(graph.shape[0]): #for each amount
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
    dataset['quantity data frame']['calculation order'] = pd.Series(longestPath)
    dataset['quantity data frame'] = dataset['quantity data frame'
        ].sort_values(by = 'calculation order')
    
    return dataset


def quantity_df_to_internal(dataset):
    df = dataset['quantity data frame']
    amounts = dict(zip(df['Ref'], df['amount']))
    for exc in dataset['exchanges']:
        exc['amount'] = amounts[exc['Ref']]
        if 'production volume' in exc:
            if exc['production volume']['Ref'] in amounts:
                exc['production volume']['amount'] = amounts[exc['production volume']['Ref']]
        if 'properties' in exc:
            for p in exc['properties']:
                p['amount'] = amounts[p['Ref']]
    if 'parameters' in dataset:
        for p in dataset['parameters']:
            p['amount'] = amounts[p['Ref']]
    return dataset

def recalculate(dataset):
    
    df = dataset['quantity data frame']
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
    
    dataset['quantity data frame'] = df    
    
    return dataset


def validate_against_linking(datasets, reference_folder, data_format, 
        result_folder, types_to_validate = [], tolerance = .001):
    if len(types_to_validate) == 0:
        types_to_validate = ['reference product', 'from technosphere', 
                             'from environment', 'to environment']
    folder = os.path.join(reference_folder, 'excel and csv')
    filename = 'activity_overview_3.2_cut-off.xlsx'
    ao = pd.read_excel(os.path.join(folder, filename), 'activity overview')
    ao = ao.set_index(['activityName', 'Geography', 'Product']).sortlevel(level=0)
    folder = os.path.join(reference_folder, 'datasets')
    results = {}
    counter = 0
    for dataset in datasets:
        counter += 1
        print('validating', dataset['name'], dataset['location'], dataset['reference product'])
        print(counter, 'of', len(datasets))
        to_add = {'activity name': dataset['name'], 
                  'location': dataset['location'], 
                'reference product': dataset['reference product']}
        index = dataset['name'], dataset['location'], dataset['reference product']
        found = True
        if index in set(ao.index):
            reference_filename = ao.loc[index]['filename']
        elif index[1] == 'GLO':
            index = dataset['name'], 'RoW', dataset['reference product']
            if index in set(ao.index):
                reference_filename = ao.loc[index]['filename']
            else:
                found = False
        else:
            found = False
        if found:
            dataset = build_quantity_df(dataset)
            df = dataset['quantity data frame'].copy()
            df = df[df['data type'] == 'exchanges']
            df = df[df['type'].isin(types_to_validate)]
            if len(df) > 0:
                df = df[df['amount'] != 0.]
            if len(df) > 0:
                reference_filename = os.path.join(folder, reference_filename)
                reference_dataset = ocelot.io.extract_ecospold2.generic_extractor(reference_filename)[0]
                reference_dataset = build_quantity_df(reference_dataset)
                df_reference = dataset['quantity data frame'].copy()
                df_reference = df_reference[df_reference['data type'] == 'exchanges']
                df_reference = df_reference[df_reference['type'].isin(types_to_validate)]
                df = df.set_index(['name', 'compartment', 
                    'subcompartment', 'activity link'])[['amount']]
                df_reference = df_reference.set_index(['name', 'compartment', 
                    'subcompartment', 'activity link'])[['amount']]
                df = df.join(df_reference, how = 'left', rsuffix = '_reference')
                if 0. in set(df['amount_reference']):
                    to_add['message'] = 'differences'
                else:
                    df['test'] = abs(df['amount'].divide(df['amount_reference']))
                    if sum(df['test'] > 1. + tolerance) + sum(df['test'] < 1. - tolerance) > 0:
                        to_add['message'] = 'differences'
                    else:
                        to_add['message'] = 'validation passed'
            else:
                to_add['message'] = 'no exchange in types to validate'
        else:
            to_add['message'] = 'reference not found, (not necessarily an error)'
        if to_add['message'] == 'differences':
            filename = '%s - %s - %s.xlsx' % (dataset['name'], 
                dataset['location'], dataset['reference product'])
            df = df.reset_index()
            columns = ['name', 'compartment', 'subcompartment', 
                'activity link', 'amount', 'amount_reference', 'test']
            df.to_excel(os.path.join(result_folder, filename), 
                columns = columns, index = False, merge_cells = False)
        results[len(results)] = copy(to_add)
        print(to_add['message'])
        print('')
    results = pd.DataFrame(results).transpose()
    filename = 'validation_results.xlsx'
    columns = ['activity name', 'location', 'reference product', 'message']
    results.to_excel(os.path.join(result_folder, filename), columns = columns, 
                     index = False, merge_cells = False)