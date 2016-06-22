# -*- coding: utf-8 -*-
import os, imp
import ocelot
imp.reload(ocelot)
imp.reload(ocelot.transformations)
imp.reload(ocelot.transformations.activity_overview)
imp.reload(ocelot.transformations.allocation_method)
imp.reload(ocelot.utils)
imp.reload(ocelot.io.extract_ecospold2)
if 0:
    folder = r'C:\python\DB_versions\3.2\undefined\datasets'
    datasets = ocelot.io.extract_ecospold2.extract_directory(folder, False)
    filename = 'ecoinvent_3.2_internal'
    folder = r'C:\ocelot_DB'
    logger = ''
    datasets = ocelot.transformations.allocation_method.allocation_method(datasets, logger)
    support_excel_folder = r'C:\ocelot_DB'
    support_pkl_folder = r'C:\ocelot_DB'
    data_format = ocelot.utils.read_format_definition()
    df = ocelot.transformations.activity_overview.activity_overview(datasets, 
        support_excel_folder, support_pkl_folder, data_format)
    ocelot.utils.save_file(datasets, folder, filename)
    datasets = datasets[:100]
    filename = 'ecoinvent_3.2_internal_small'
    ocelot.utils.save_file(datasets, folder, filename)
else:
    folder = r'C:\ocelot_DB'
    filename = 'ecoinvent_3.2_internal_small'
    #filename = 'ecoinvent_3.2_internal'
    datasets = ocelot.utils.open_file(folder, filename)
    data_format = ocelot.utils.read_format_definition()
    datasets = ocelot.utils.datasets_to_dict(datasets, ['name', 'location'])
    