# -*- coding: utf-8 -*-
import pandas as pd
from cPickle import dump
from copy import copy
import os

def activity_overview(datasets, logger, support_excel_folder, support_pkl_folder):
    """ creates a spreadsheet with a line for each output to technosphere"""
    
    df = {}
    dataset_mapping = {
        'id': 'activity id', 
        'name': 'activity name', 
        'filepath': 'filepath', 
        'location': 'location', 
        'technology level': 'technology level', 
        'type': 'activity type', 
        'access restricted': 'access restricted', 
        'allocation method': 'allocation method'
        }
    exchange_mapping = {'type': 'exchange type', 
                'name': 'exchange name', 
                'amount': 'amount', 
                'unit': 'unit', 
                'byproduct classification': 'byproduct classification', 
                }
    for dataset in datasets:
        baseline = {}
        for key in dataset_mapping:
            baseline[dataset_mapping[key]] = dataset[key]
        baseline['start date'] = dataset['temporal'][0]
        baseline['end date'] = dataset['temporal'][1]
        for exc in dataset['exchanges']:
            if exc['type'] in ['reference product', 'byproduct']:
                to_add = copy(baseline)
                for key in exchange_mapping:
                    to_add[exchange_mapping[key]] = exc[key]
                to_add['production volume'] = exc['production volume']['amount']
                df[len(df)] = copy(to_add)
    df = pd.DataFrame(df).transpose()
    df = df.sort('activity name')
    filename = 'activity_overview.xlsx'
    writer = pd.ExcelWriter(os.path.join(support_excel_folder, filename))
    cols = ['filepath', 'activity id', 'activity name', 'location', 'activity type', 
            'technology level', 'access restricted', 'allocation method', 
            'exchange type', 'exchange name', 'amount', 'unit', 'byproduct classification']
    df.to_excel(writer, cols = cols, index = False, merge_cells = False)
    filename = 'activity_overview.pkl'
    dump(df, os.path.join(support_pkl_folder, filename))
    
    return df