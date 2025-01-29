from itertools import count
from math import inf
import numpy as np

import pabutools.election as pbe
import pabutools.rules as pbr
from setup import *

"""
Functions to calculate different forms of affordability
"""

def rho_affordable(c:Mproject, voters:list[int], voter_budgets, aggregation) -> tuple[float,list]:
    """Calculate the rho-affordability of the project in the following manor
    1. For each resource calculate the projects rho-affordability were this to be the only resource
    2. Combine with the given aggregation function

    Args:
        c (Mproject): The project
        profile (pbe.ApprovalProfile): The voting profile of the election
        voter_budgets (_type_): The budgets for the voters where the index i is the voter i in the profile
        aggregation (Function, optional): The aggregation function to combine the rho[j] values together. Defaults to max.

    Returns:
        tuple[float,list]: _description_
    """

    rho = [np.Infinity for i in range(len(c.cost))]

    # Calculate rho value for each resource
    for r in range(len(c.cost)):
        # Sort voters by increasing amount of remaining budget
        sorted_voters = sorted(voters, key= lambda x: voter_budgets[x][r])

        price_left = c.cost[r]
        voters_left = len(sorted_voters)

        for i in sorted_voters:
            # If the voter can't afford the remaining cost of the project shared then they spend the full amount
            if voter_budgets[i][r] < price_left/voters_left:
                price_left -= voter_budgets[i][r]
                voters_left -= 1
            else:
                break

        rho_r = price_left / (voters_left * c.cost[r])

        rho[r] = rho_r

        # Calculate the combined value of rho using the given aggregation function.
        # If one of the values is infinity, that means the project cannot be funded along that dimension.
        # Hence the aggregated rho value should be infinity
        aggregated_rho = inf
        if max(rho) < np.Inf:
            aggregated_rho = aggregation(rho)



    return (aggregated_rho,rho)


def rho_epsilon_converted_affordable(c:Mproject, inst:Minstance, voters, voter_budgets:np.array, epsilon_type:str = "rel") -> tuple[float,float]:
    """Calculate the project's (rho,epsilon)-converted_affordability
    1. Convert all funds to resource 1 (Called £)
    2. Calculate rho-affordability
    3. Calculate epsilon as the total amount converted

    Args:
        c (Mproject): Project to calculate for
        inst (Minstance): PB instance
        profile (pbe.ApprovalProfile): Voter profile
        voter_budgets (_type_): The remaining budgets of the voters where index i is the voter corresponding to profile[i]
        epsilon_type (str): The type of value epsilon is. Can be one of the following values:
                                    rel = amount exhcanged / project cost (Default)
                                    abs = amound exchanged
                                    count = number of exchanges needed in the first round of funding
    Returns:
        tuple[float,float]: _description_
    """

    # Convert everything to £
    dollar_to_pound_er = inst.budget_limit[0]/inst.budget_limit[1] # Have $, convert to £

    project_cost = c.cost[0] + c.cost[1]*dollar_to_pound_er
    converted_voter_budgets = [voter_budgets[i][0] + voter_budgets[i][1]*dollar_to_pound_er for i in range(len(voter_budgets))]

    num_voters = len(voters)
    # Calculate Rho
    rho = np.Infinity

    # Sort voters by increasing amount of remaining budget
    sorted_voters = sorted(voters, key= lambda x: converted_voter_budgets[x])

    price_left = project_cost
    voters_left = num_voters

    for i in sorted_voters:
        # If the voter can't afford the remaining cost of the project shared then they spend the full amount
        if converted_voter_budgets[i] < price_left/voters_left:
            price_left -= converted_voter_budgets[i]
            voters_left -= 1
        else:
            break

    if voters_left > 0:
        rho = price_left / (voters_left * project_cost)

    # Calculate epsilon
    # Different ways of calculating epsilon
    match (epsilon_type):
        case "abs":
            epsilon = sum([max(0,c.cost[0]/num_voters - voter_budgets[i][0]) + dollar_to_pound_er*max(0,c.cost[1]/num_voters - voter_budgets[i][1]) for i in voters])
        case "count":
            def will_voter_convert(x):
                if (voter_budgets[x][0] < c.cost[0]/num_voters) ^ (voter_budgets[x][1] < c.cost[1]/num_voters):
                    return 1
                else:
                    return 0
            epsilon = sum(map(will_voter_convert ,voters))
        case _:
            # When no or rel or an incorrect argument is given, default to the relative version
            epsilon = sum([max(0,c.cost[0]/num_voters - voter_budgets[i][0]) + dollar_to_pound_er*max(0,c.cost[1]/num_voters - voter_budgets[i][1]) for i in voters])/project_cost

    return (rho,epsilon)


def alpha_rho_affordable(c:Mproject, instance:Minstance, voters:list[int], voter_budgets:np.array) ->  tuple[tuple[float,float],list[tuple[float,float]]]:
    alpha_rho = [np.Infinity for i in range(len(c.cost))]

    # Calculate rho value for each resource
    for r in range(len(c.cost)):
        # Sort voters by increasing amount of remaining budget
        sorted_voters = sorted(voters, key= lambda x: voter_budgets[x][r])

        # alpha_options:
        options_alpha = []

        # Calculate different options for alpha. Each alpha corresponds to a max payment a voter can make
        for x in sorted_voters:
            max_payment = voter_budgets[x][r]

            def get_payment(y):
                if voter_budgets[y][r] < max_payment:
                    return voter_budgets[y][r]
                else:
                    return max_payment
            a = min(c.cost[r], sum([get_payment(y) for y in voters]))/c.cost[r]
            if a not in options_alpha:
                options_alpha.append(a)
            # Stop if got to fully funded
            if a == 1:
                break

        options_rho = dict()
        for a in options_alpha:
            # Calculate rho for each value of alpha
            options_rho[a] = 0

        # Find best alpha by picking one minimising rho/alpha
        best_alpha = min(options_alpha, key = lambda t: options_rho[t]/t)

        alpha_rho[r] = (best_alpha, options_rho[best_alpha])

    # Return the alpha_rho pair to for comparison (dimension with lowest value of alpha) and the pairs for all dimensions
    return (min(alpha_rho, key= lambda t: t[0]), alpha_rho)
