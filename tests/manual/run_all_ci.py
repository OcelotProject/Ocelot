from parameterization import run_all_parameterization
import sys
import traceback

try:
    run_all_parameterization()
except:
    print(traceback.format_exc())
    sys.exit(1)
