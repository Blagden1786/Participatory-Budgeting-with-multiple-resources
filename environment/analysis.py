import numpy as np
import random as rand

import pabutools
import pabutools.election as pbe
import pabutools.analysis as pba
from setup import *
from rules import *

# Different ways to convert the multi-dimensional instance to a single dimension
def to_1d(instance:Minstance, profile:pbe.ApprovalProfile, dimension:int) -> tuple[pbe.Instance, pbe.AbstractProfile]:
    """Turn the election into a 1D version by reducing the dimension down to 1

    Args:
        profile (pbe.AbstractProfile): Voter profile
        instance (Minstance): Instance to reduce
        dimension (int): Index of budget to restrict to

    Raises:
        IndexError: error for when the dimension is higher than the number of dimensions

    Returns:
        tuple[pbe.AbstractProfile, pbe.Instance]: New election using default Pabutools objects
    """
    if dimension >= np.size(instance.budget_limit):
        raise  IndexError("Dimension out of bounds for number of resources")

    new_budget_limit = instance.budget_limit[dimension]

    new_projects = [pbe.Project(p.name, p.cost[dimension], p.categories, p.targets) for p in instance]

    new_instance = pbe.Instance(new_projects, new_budget_limit, instance.categories, instance.targets)

    new_ballots = [pbe.ApprovalBallot([new_instance.get_project(c.name) for c in i]) for i in profile]
    return(new_instance, pbe.ApprovalProfile(new_ballots, new_instance))

def to_1d_converted(inst:Minstance, profile:pbe.ApprovalProfile):
    """Use the exchange rate to convert the budgets and projects to a single resource scenario.

    Args:
        profile (pbe.ApprovalProfile): The profile of votes
        inst (Minstance): The multi instance that needs to be changed
    """
    exchange_rates = [inst.budget_limit[0]/inst.budget_limit[i] for i in range(inst.budget_limit.size)]

    # Get the new budget limit
    budget = sum([inst.budget_limit[i]*exchange_rates[i] for i in range(inst.budget_limit.size)])

    new_projects = [pbe.Project(p.name, sum([p.cost[i]*exchange_rates[i] for i in range(p.cost.size)])) for p in inst]

    new_inst = pbe.Instance(new_projects, float(budget), inst.categories, inst.targets)
    new_ballots = [pbe.ApprovalBallot([new_inst.get_project(c.name) for c in i]) for i in profile]
    return(new_inst,pbe.ApprovalProfile(new_ballots, new_inst))

# EJR+ violations
def ejr_plus_conversion(inst:Minstance, profile:pbe.ApprovalProfile, outcome:Collection[Mproject], up_to_one:bool = True) -> int:
    """Consider the PB instance where the budget and project costs are reduced to one dimension. Check for EJR+ violatios in this scenario.

        Args:
            inst (Minstance): The instance to check
            profile (pbe.ApprovalProfile): Approval profile
            outcome (Collection[Mproject]): The outcome to check
            up_to_one (bool, optional): Whether to consider EJR+ up to one project or up to any. Defaults to True.

        Returns:
            int: Number of violations of this type.
        """
    converted_inst, converted_profile = to_1d_converted(inst, profile)

    converted_outcome = [converted_inst.get_project(c.name) for c in outcome]

    failures, _ = strong_ejr_plus_violations(converted_inst, converted_profile, converted_outcome, pbe.Cost_Sat, up_to_one)

    return failures

def ejr_plus_restricted(inst:Minstance, profile:pbe.ApprovalProfile, outcome:Collection[Mproject], up_to_one:bool = True) -> int:
    """Consider the PB instance where the budget is restricted to a single dimension and check for EJR+ violations.
    Repeat this for all dimensios. We say a project violates EJR+ if it violates it in any dimension.

        Args:
            inst (Minstance): The instance to check
            profile (pbe.ApprovalProfile): Approval profile
            outcome (Collection[Mproject]): The outcome to check
            up_to_one (bool, optional): Whether to consider EJR+ up to one project or not. Defaults to True.

        Returns:
            int: Number of violations of this type.
    """
    failed_projects = [set() for _ in range(inst.budget_limit.size)]

    for i in range(inst.budget_limit.size):
        print(f"Resource {i}")
        converted_inst, converted_profile = to_1d(inst, profile, i)

        converted_outcome = [converted_inst.get_project(c.name) for c in outcome]
        print("Now checking violations")
        _, failed = strong_ejr_plus_violations(converted_inst, converted_profile, converted_outcome, pbe.Cost_Sat, up_to_one)
        failed_projects[i] = failed
        print(f"Failures {failed}")

    # A project violates EJR+ MIN if it violates it in any dimension
    failures = set.union(*failed_projects)
    return len(failures)

def get_utilities_maps(instance, sat_profile):
    proj_utils = {c: {} for c in instance}
    vot_utils = {}

    for i, sat in enumerate(sat_profile):
        vot_utils[i] = {}
        for c in instance:
            if sat.sat_project(c) > 0:
                proj_utils[c][i] = float(sat.sat_project(c))
                vot_utils[i][c] = float(sat.sat_project(c))

    return proj_utils, vot_utils

def strong_ejr_plus_violation(proj_utils, vot_utils_arg, outcome, cand, threshold, up_to_one = True):
    extended_outcome = set(outcome)
    extended_outcome.add(cand)
    vot_utils = {
        i: {c: vot_utils_arg[i][c] for c in extended_outcome if c in vot_utils_arg[i]}
        for i in vot_utils_arg
    }

    sat_map = {}
    for c in extended_outcome:
        sat_map[c] = sum(proj_utils[c].values())

    active_voters = set([i for i in vot_utils.keys()])

    while active_voters and sat_map[cand] > 0:
        to_remove = []
        for i in active_voters:
            voter_sat = 0
            for c in vot_utils[i].keys():
                if c != cand or up_to_one:
                    voter_sat += proj_utils[c][i] * min(c.cost / sat_map[c], cand.cost / sat_map[cand])
            if voter_sat > threshold:
                to_remove.append(i)
        if len(to_remove) == 0:
            return True
        for i in to_remove:
            active_voters.remove(i)
            for c in vot_utils[i].keys():
                sat_map[c] -= vot_utils[i][c]
    return False

def strong_ejr_plus_violations(instance, profile, outcome, sat_class, up_to_one):
    sat_profile = profile.as_sat_profile(sat_class)
    res = get_utilities_maps(instance = instance, sat_profile = sat_profile)
    proj_utils = res[0]
    vot_utils = res[1]
    threshold = instance.budget_limit / len(profile)

    failures = 0
    failures_set = set()

    for c in instance:
        if c not in outcome:
            violation = strong_ejr_plus_violation(proj_utils, vot_utils, outcome, c, threshold, up_to_one)
            if violation:
                failures += 1
                failures_set.add(c)
    return failures, failures_set

# Other functions
def exclusion_ratio(instance:Minstance, profile:pbe.ApprovalProfile, allocation:pbr.BudgetAllocation)->float:
    """Determines the exclusion ratio of the allocation. That is, the proportion of voters who didn't have any projects they voted for selected.

    Args:
        instance (Minstance): The instance
        profile (pbe.ApprovalProfile): The approval profile
        allocation (pbr.BudgetAllocation): The final budget allocation

    Returns:
        float: The exclusion ratio
    """
    return 1-pba.percent_non_empty_handed(instance, profile, allocation)

def mean_excluding_outliers(data):
    Q1 = np.percentile(data, 25)
    Q3 = np.percentile(data, 75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    filtered_data = [x for x in data if lower_bound <= x <= upper_bound]
    return np.mean(filtered_data)
