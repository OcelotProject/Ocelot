# -*- coding: utf-8 -*-
import ocelot
from ocelot import utils

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
    data_format = utils.read_format_definition()
    if 1:
        ocelot.transformations.activity_overview.build_activity_overview(datasets, 
            support_excel_folder, support_pkl_folder, data_format)
    utils.save_file(datasets, folder, filename)
    datasets = datasets[:100]
    filename = 'ecoinvent_3.2_internal_small'
    utils.save_file(datasets, folder, filename)
else:
    folder = r'C:\ocelot_DB'
    #filename = 'ecoinvent_3.2_internal_small'
    filename = 'ecoinvent_3.2_internal'
    datasets = utils.open_file(folder, filename)
    filename = 'activity_overview'
    activity_overview = utils.open_file(folder, filename)
    data_format = utils.read_format_definition()
    criteria = {'activity name': ['heat and power co-generation, diesel, 200kW electrical, SCR-NOx reduction'], 
                'location': ['CH']}
    datasets = utils.filter_datasets(datasets, activity_overview, criteria)
    datasets = ocelot.transformations.allocate_cutoff.allocate_datasets_cutoff(
        datasets, data_format, '')
    for dataset in datasets:
        utils.print_dataset_to_excel(dataset, folder, data_format, activity_overview)