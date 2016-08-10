# -*- coding: utf-8 -*-
import ocelot
from copy import copy
import numpy as np
import scipy as sp
import pandas as pd
import os
import time
import re
data_format = ocelot.utils.read_format_definition()
dirpath = r'C:\Ocelot\test_cases'
datasets = ocelot.io.extract_excel.extract_excel(dirpath, data_format)
data_formats, compartments = ocelot.io.validate_dataset.prepare_validation()
for dataset in datasets:
    ocelot.io.validate_dataset.validate_dataset(dataset, data_formats, compartments)
1/0
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
else:
    folder = r'C:\ocelot_DB'
    filename = 'ecoinvent_3.2_internal'
    #filename = 'after_combined_production_without_byproducts'
    #filename = 'ecoinvent_3.2_internal_after_allocation'
    #filename = 'after_allocation_treatment_and_recycling'
    #filename = 'after_combined_production_with_byproducts'
    #filename = 'after_economic_allocation'
    #filename = 'after_true_value_allocation'
    datasets = ocelot.utils.open_file(folder, filename)
    
        
    1/0
    data_format = ocelot.utils.read_format_definition()
    support_excel_folder = r'C:\ocelot_DB'
    support_pkl_folder = r'C:\ocelot_DB'
    criteria = {
        #'allocation method': [
            #'recycling activity', 
              #'waste treatment', 
              #'economic allocation', 
                #'true value allocation'
                #'combined production without byproducts'
                #'combined production with byproducts'
              #], 
    'id': '40acc8ff-a89a-421f-8af3-c5b615c38bff'
        #'activity name': ['treatment of residue from mechanical treatment, laser printer, municipal incineration with fly ash extraction'], 
        #'location': ['CH'], 
                }
    activity_overview = ocelot.utils.open_file(folder, 'activity_overview')
    #datasets = ocelot.utils.filter_datasets(datasets, activity_overview, criteria)
    if 0:
        datasets = ocelot.transformations.calculate_available_PV.available_production_volume(
            datasets, '', support_excel_folder, support_pkl_folder)
        1/0
        datasets = ocelot.transformations.allocate_cutoff.allocate_datasets_cutoff(
            datasets, data_format, '')
        folder = 'C:\ocelot_DB'
        filename = 'ecoinvent_3.2_internal_after_allocation'
        ocelot.utils.save_file(datasets, folder, filename)
    if 0:
        system_model_folder = r'C:\python\DB_versions\3.2\cut-off'
        ocelot.utils.validate_against_linking(datasets, system_model_folder, data_format, 
            folder, types_to_validate = ['from environment', 'to environment'])
    #datasets = ocelot.transformations.calculate_available_PV.calculate_available_PV(
    #        datasets, '', support_excel_folder, support_pkl_folder)
    ocelot.transformations.calculate_RoW_PV.calculate_RoW_PV(support_pkl_folder, support_excel_folder)