from time import time
import random as rand
import sys

from matplotlib.pyplot import plot
from numpy import floor
import pabutools
import pabutools.election as pbe
import pabutools.election
import pabutools.rules as pbr
import pabutools.analysis.justifiedrepresentation as pbejr
import pabutools.analysis.votersatisfaction as pbas
from pabutools.election.satisfaction import Cost_Sat
import pabutools.tiebreaking as pbt


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
    run_test_resources(runtime_test, 10, './environment/datasets_resources', './environment/plots_batch', False, False)
    run_test_resources(exclusion_test, 10, './environment/datasets_resources', './environment/plots_batch', False, False)
    #run_test_projects(ejrplus_alldim_test, './environment/datasets_extended', './environment/plots_batch', True)
    #run_test_resources(ejrplus_conversion_test, 10, './environment/datasets_resources', './environment/plots_batch', True, False)
    #run_test_resources(ejrpc_one_test, 10, './environment/datasets_resources', './environment/plots_batch', True, False)
    #run_test_resources(ejrplus_alldim_test, 10, './environment/datasets_resources', './environment/plots_batch', True, False)
    #run_test_resources(ejrpa_one_test, 10, './environment/datasets_resources', './environment/plots_batch', True, False)
    #run_test_projects(ejrpa_one_test, './environment/datasets_extended', './environment/plots_batch', True)
    #run_test_projects(ejrplus_alldim_test, './environment/datasets_extended', './environment/plots_batch', True)
    t2 = time()

    def to_hours(x):
        h = floor(x/3600)
        m = floor(x/60 - h*60)
        return f"{h}:{m}"

    print("Done")
    print(f"Time taken: {to_hours(t2-t1)}")
    print(f"See plots in ./environment/plots_batch")

if __name__ == "__main__":
    seed = 0

    batch_run(seed)
