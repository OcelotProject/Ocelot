# -*- coding: utf-8 -*-
import imp
import pandas as pd
from copy import copy
import os
import ocelot.utils
imp.reload(ocelot.utils)

f = lambda x: None

def activity_overview(datasets, support_excel_folder, support_pkl_folder,
        data_format):
    """creates a spreadsheet with a line for each output to technosphere"""
    data_format = data_format.set_index(['parent', 'field']).sortlevel(level=0)
    df = {}
    dataset_fields_to_keep = [
        'id',
        'name',
        'filepath',
        'location',
        'technology level',
        'type',
        'access restricted',
        'allocation method',
        'start date',
        'end date'
        ]
    exchange_fields_to_keep = [
        'type',
        'name',
        'amount',
        'unit',
        'byproduct classification'
        ]

    for dataset in datasets:
        baseline = {}
        for field in dataset_fields_to_keep:
            if field in dataset:
                baseline[data_format.loc[('dataset', field), 'in dataframe']
                    ] = dataset[field]
        for exc in dataset['exchanges']:
            if exc['type'] in ['reference product', 'byproduct']:
                to_add = copy(baseline)
                for field in exchange_fields_to_keep:
                    to_add[data_format.loc[('exchanges', field), 'in dataframe']
                        ] = exc[field]
                to_add['production volume'] = exc['production volume']['amount']
                df[len(df)] = copy(to_add)
    df = pd.DataFrame(df).transpose()
    df = df.sort_values(by = 'activity name')
    filename = 'activity_overview.xlsx'
    writer = pd.ExcelWriter(os.path.join(support_excel_folder, filename))
    cols = ['filepath', 'activity id', 'activity name', 'location', 'activity type',
            'technology level', 'access restricted', 'allocation method',
            'exchange type', 'exchange name', 'amount', 'production volume', 'unit',
            'byproduct classification']
    df.to_excel(writer, columns = cols, index = False, merge_cells = False)
    filename = 'activity_overview'
    ocelot.utils.save_file(df, support_pkl_folder, filename)

    return df
