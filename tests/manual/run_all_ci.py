from parameterization import run_all_parameterization
from combined import run_all_combined
import sys
import traceback

try:
    run_all_parameterization()
    run_all_combined()
    print("Manual tests passed")
except:
    print(traceback.format_exc())
    sys.exit(1)
