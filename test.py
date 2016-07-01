# -*- coding: utf-8 -*-
import ocelot
from copy import copy
import numpy as np
import scipy as sp
import pandas as pd

if 0:
    folder = r'C:\python\DB_versions\3.2\undefined\datasets'
    datasets = ocelot.io.extract_ecospold2.extract_directory(folder, False)
    filename = 'ecoinvent_3.2_internal'
    folder = r'C:\ocelot_DB'
    logger = ''
    datasets = ocelot.transformations.find_allocation_method_cutoff.allocation_method(datasets, logger)
    datasets = ocelot.transformations.fix_known_issues_ecoinvent_32.fix_known_issues(
        datasets, '')
    support_excel_folder = r'C:\ocelot_DB'
    support_pkl_folder = r'C:\ocelot_DB'
    data_format = ocelot.utils.read_format_definition()
    if 0:
        ocelot.transformations.activity_overview.build_activity_overview(datasets, 
            support_excel_folder, support_pkl_folder, data_format)
    ocelot.utils.save_file(datasets, folder, filename)
    datasets = datasets[:100]
    filename = 'ecoinvent_3.2_internal_small'
    ocelot.utils.save_file(datasets, folder, filename)
else:
    folder = r'C:\ocelot_DB'
    #filename = 'ecoinvent_3.2_internal_small'
    filename = 'ecoinvent_3.2_internal'
    datasets = ocelot.utils.open_file(folder, filename)
    filename = 'activity_overview'
    activity_overview = ocelot.utils.open_file(folder, filename)
    data_format = ocelot.utils.read_format_definition()
    criteria = {'activity name': ['cement production, alternative constituents 21-35%'], 
                'location': ['Europe without Switzerland']}
    datasets = ocelot.utils.filter_datasets(datasets, activity_overview, criteria)
    #dataset = datasets[0]
    #ocelot.utils.print_dataset_to_excel(dataset, folder, data_format, activity_overview)
    
    datasets = ocelot.transformations.allocate_cutoff.allocate_datasets_cutoff(
        datasets, data_format, '')
    
    for dataset in datasets:
        ocelot.utils.print_dataset_to_excel(dataset, folder, data_format, activity_overview)
