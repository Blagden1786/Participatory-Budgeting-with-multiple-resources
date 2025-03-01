from time import time
import random as rand
from numpy import floor
import sys

from setup import *
from rules import *
from analysis import *
from parser import *
from experiments import *
"""
Cannot use ApprovalProfile.is_trivial() since requires the cost to be an integer
"""

"""DATA TO ANALYSE:
- Avg running time
- Exclusion ratio: Fraction of voters not supporting any project
- EJR+ violations
- Avg satisfaction?


- Different number of resources
- Different epsilon for exchange rates
- Different aggregation functions for MES
"""
def batch_run(seed):
    rand.seed(seed)

    t1 = time()
    #run_test_aggregation(False, [max, min, np.mean, np.median], './environment/datasets_under_30', './environment/plots', True, True)
    run_test_projects(budget_test, './environment/datasets_extended', './environment/plots_batch')
    run_test_resources(budget_test, 10, './environment/datasets_extended', './environment/plots_batch')
    #run_test_resources(exclusion_test, 10, './environment/datasets_resources', './environment/plots_batch', True, False)
    #run_test_resources(ejrpc_one_test, 10, './environment/datasets_resources', './environment/plots_batch', True, False)
    #run_test_resources(ejrpa_one_test, 10, './environment/datasets_resources', './environment/plots_batch', True, False)
    t2 = time()

    def to_hours(x):
        h = int(floor(x/3600))
        m = int(floor(x/60 - h*60))
        return f"{h} hours and {m} minutes"

    print("Done")
    print(f"Time taken: {to_hours(t2-t1)}")
    print(f"See plots in ./environment/plots_batch")

if __name__ == "__main__":
    seed = 0

    batch_run(seed)
