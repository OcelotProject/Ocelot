# -*- coding: utf-8 -*-
from ..filesystem import get_base_output_directory
import os
import shutil
import time


def cleanup_data_directory():
    base_dir = get_base_output_directory()
    one_week, now, to_delete = 7 * 24 * 60 * 60, time.time(), []

    print("\nCleaning up data directory {}".format(base_dir))
    for report in os.listdir(base_dir):
        dirpath = os.path.join(base_dir, report)
        if not os.path.isdir(dirpath):
            continue
        created = os.path.getctime(dirpath)
        if created < now - one_week:
            to_delete.append((created, report, dirpath))

    if not to_delete:
        print("\nNo old reports to delete!\n")
        return
    to_delete.sort()
    template = "Deleting {count} reports:\n{items}"
    items = "".join(["\t{report} from {created}\n".format(
                     report=y, created=time.ctime(x)) for x, y, z in to_delete])
    print(template.format(count=len(to_delete), items=items))

    for _, _, dirpath in to_delete:
        shutil.rmtree(dirpath)
