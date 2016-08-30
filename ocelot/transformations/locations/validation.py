# -*- coding: utf-8 -*-
from ...errors import MultipleGlobalDatasets


def check_single_global_dataset(datasets):
    """Raises ``MultipleGlobalDatasets`` if more than one global dataset is present."""
    if len([ds for ds in datasets if ds['location'] == 'GLO']) > 1:
        raise MultipleGlobalDatasets
