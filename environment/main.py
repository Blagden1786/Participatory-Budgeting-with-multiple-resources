from time import time
import numpy as np
import random as rand
import sys

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

def main(loc, seed, test):
    rand.seed(seed)

    data = find_data(loc)

    t1 = time()
    match test:
        case 'time':
            print("Time test")
            projects_vs_times(data, f"{loc}/plots", show=True)
        case 'exc':
            print("Exclusion test")
            projects_vs_exclusion(data, f"{loc}/plots", show=True)
        case 'ejrc':
            print("EJR+ violations conversion test")
            ejr_plus_conversion_violations(data, f"{loc}/plots", False, show=True)
        case 'ejrr':
            print("EJR+ violations all dimension test")
            ejr_plus_alldim_violations(data, f"{loc}/plots", False, show=True)
        case 'ejrc_one':
            print("EJR+ violations conversion up to one project test")
            ejr_plus_conversion_violations(data, f"{loc}/plots", True, show=True)
        case 'ejrr_one':
            print("EJR+ violations all dimensions up to one project test")
            ejr_plus_alldim_violations(data, f"{loc}/plots", True, show=True)
        case 'num':
            print("Num datasets vs projects")
            num_datsets_vs_projects(data)

        case 'all':
            print("Run all tests")
            print("Time")
            #projects_vs_times(data, f"{loc}/plots")
            print("Exclusion")
            #projects_vs_exclusion(data, f"{loc}/plots")
            print("EJR+ conversion")
            ejr_plus_conversion_violations(data, f"{loc}/plots", False)
            print("EJR+ conversion up to one project")
            ejr_plus_conversion_violations(data, f"{loc}/plots", True)
            print("EJR+ all dimensions")
            ejr_plus_alldim_violations(data, f"{loc}/plots", False)
            print("EJR+ all dimensions up to one project")
            ejr_plus_alldim_violations(data, f"{loc}/plots", True)

        case _:
            print("Invalid test")
            print("Please see below for valid tests:")
            print("time: Time test")
            print("exc: Exclusion vs Projects test")
            print("ejrc: EJR+ violations conversion vs Projects test")
            print("ejrr: EJR+ violations all dimension vs Projects test")
            print("ejrc_one: EJR+ violations conversion up to one vs Projects test")
            print("ejrr_one: EJR+ violations all dimension up to one  vs Projects test")
            print("all: Run all tests")
            print("num: Num datasets vs Projects")
            return
    t2 = time()

    print("Done")
    print(f"Time taken: {(t2-t1)/60}")
    print(f"See plots in {loc}/plots")

def batch_run(loc, seed):
    rand.seed(seed)

    data = find_data(loc, False)

    t1 = time()
    projects_vs_times(data, out_folder=f"{loc}/plots_batch")
    projects_vs_exclusion(data, out_folder=f"{loc}/plots_batch")
    ejr_plus_conversion_violations(data, f"{loc}/plots_batch", False)
    ejr_plus_alldim_violations(data, f"{loc}/plots_batch", False)
    ejr_plus_conversion_violations(data, f"{loc}/plots_batch", True)
    ejr_plus_alldim_violations(data, f"{loc}/plots_batch", True)
    t2 = time()

    print("Done")
    print(f"Time taken: {(t2-t1)/60}")
    print(f"See plots in {loc}/plots_batch")

if __name__ == "__main__":
    loc = './environment'
    seed = 0
    test = 'time'

    main(loc, seed, test)