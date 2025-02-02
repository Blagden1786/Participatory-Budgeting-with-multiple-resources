from math import inf

# pabutools library
from numpy import float64
import pabutools.election as pbe
import pabutools.rules as pbr

# Own files
from setup import *
from rho_calculations import *


"""
Cannot use ApprovalProfile.is_trivial() since requires the cost to be an integer not a list
"""

"""
The rules below are as follows:
Greedy - Recursively picks projects with the highest number of votes until no budget is left
multi-MES - Split the budget equally among voters, choose projects and then allow the voters to fund the projects

"""
#TODO: multi-BOS, multi-charged-overspending, exchange-rates(n variables)


def greedy_rule(inst:Minstance, profile:pbe.ApprovalProfile) -> pbr.BudgetAllocation:
    """Greedy allocation rule:
        - Chooses projects with the most votes first until all projects chosen and no more can be afforded

    Args:
        instance (Minstance): The instance
        profile (pbe.ApprovalProfile): Approval profile
    """

    output = []
    remaining_budget = inst.budget_limit

    # Sort projects in descending order of number of votes
    sorted_projects:list[Mproject] = sorted(inst, key=lambda c: -1*profile.approval_score(c)) # type: ignore
    # Fund projects
    while len(sorted_projects) > 0:
        max_score = sorted_projects.pop(0)

        # If the project is affordable then fund it
        if min(remaining_budget - max_score.cost) >= 0:
            output.append(max_score)
            remaining_budget -= max_score.cost

    return pbr.BudgetAllocation(output)

def multi_method_equal_shares(inst:Minstance, profile:pbe.ApprovalProfile, aggregation=max, completion=True) -> pbr.BudgetAllocation:
    """This method extends the method of equal shares into higher dimensions
    1. Splits budget evenly between voters
    2. Chooses project with lowest value for which it is rho-affordable - see rho_affordable function for description of how its defined
    3. Each person funds their share of the cost

    Args:
        inst (Minstance): The PB instance
        profile (pbe.ApprovalProfile): Voting profile of the projects
        aggregation (Function, optional): The aggregation function to use when calculating the rho-affordability of the project. Defaults to max.

    Returns:
        pbr.BudgetAllocation: The collection of winners of the election
    """
    num_voters = len(profile)
    # Get voters for each project
    project_voters = dict([(i,get_voters_for_project(i, profile)) for i in inst])

    # Set budgets for each voter
    voter_budgets = np.array([[inst.budget_limit[i]/num_voters for i in range(inst.budget_limit.size)] for _ in range(num_voters)])
    funded = set()

    # Loop until no more projects remaining
    while len(inst) > 0:
        # Get the rho values for each project
        rho_values = dict([(c, rho_affordable(c, project_voters[c], voter_budgets, aggregation)) for c in inst])

        chosen_project = min(inst, key= lambda c: rho_values[c][0])
        # If chosen project has rho value infinty then all projects have rho value infinity; finish since no more can be funded.
        if rho_values[chosen_project][0] == inf:
            break

        # Fund it
        for v in range(num_voters):
            if chosen_project in profile[v]:
                for r in range(len(inst.budget_limit)):
                    voter_budgets[v][r] -= min(voter_budgets[v][r],chosen_project.cost[r]*rho_values[chosen_project][1][r])

        # Remove the projects cost from budget,
        inst.budget_limit -= chosen_project.cost
        funded.add(chosen_project)
        inst.remove(chosen_project)

    if completion:
        extra = greedy_rule(inst, profile)
        funded.update(extra)

    return pbr.BudgetAllocation(funded)

def exchange_rates_2d(inst:Minstance, profile:pbe.ApprovalProfile, epsilon_type:str = "rel", completion=True) -> pbr.BudgetAllocation:
    """Uses the exchange rates mechanism as described below to calculate the winner. Only for 2 resources

    1. Split the budget evenly
    2. Choose the project with lowest value of rho*(1+epsilon) for which it is (rho,epsilon)-converted_affordable (see corresponding function for details)
    3. Fund the project, when the voter doesn't have sufficient funds, they try to convert some from the other resource

    Args:
        inst (Minstance): PB instance
        profile (pbe.ApprovalProfile): Voting profile
        epsilon_type (str): The type of value epsilon is for the rho-epsilon affordability. Can be one of the following values:
                                    rel = amount exhcanged / project cost (Default)
                                    abs = amound exchanged
                                    count = number of exchanges needed in the first round of funding
    Returns:
        pbr.BudgetAllocation: The collection of winners of the election
    """
    # Return if number of resources isn't 2
    if inst.budget_limit.size != 2:
        print("Issue")
        return None
    else:
        # Now we know there are only 2 resources
        num_voters = len(profile)
        # Get voters for each project
        project_voters = dict([(i,get_voters_for_project(i, profile)) for i in inst])
        funded = set()

        # Step 1: Voter budgets
        voter_budgets = np.array([[inst.budget_limit[i]/num_voters for i in range(inst.budget_limit.size)] for _ in range(num_voters)])

        while len(inst) > 0:
            # Remove unaffordable projects
            inst.remove_unaffordable_projects()

            if len(inst) == 0:
                break # Finish loop if no projects remain

            # Calculate exchange rates
            pound_to_dollar_er = inst.budget_limit[1]/inst.budget_limit[0] # Have £, convert to $
            dollar_to_pound_er = inst.budget_limit[0]/inst.budget_limit[1] # Have $, convert to £

            # Step 2: Select project
            rho_epsilon_values = dict([(c,rho_epsilon_converted_affordable(c, inst, project_voters[c], voter_budgets, epsilon_type)) for c in inst])
            # Project selected will be the one with maximum value of rho * (1+epsilon)

            chosen_project = min(inst, key= lambda c: rho_epsilon_values[c][0]*(1+rho_epsilon_values[c][1]))
            if rho_epsilon_values[chosen_project][0] == inf:
                break
            # Step 3 Fund
            # Find voters for project
            voters = get_voters_for_project(chosen_project, profile)
            remaining_cost = np.array([float(x) for x in chosen_project.cost])

            # Loop until project is funded
            while any([x > 0 for x in remaining_cost]):
                # Remove voters who have no funds
                voters = list(filter(lambda x: max(voter_budgets[x]) > 0, voters))
                if len(voters) == 0:
                    print("Error: No voters left")
                    print(f"Rho for this project: {rho_epsilon_values[chosen_project][0]}")
                    print(f"Remaining cost: {remaining_cost}")
                    break
                target_pp = remaining_cost/len(voters) # The cost each voter needs to pay
                # Loop through each voter and work out their bit to pay
                for i in voters:
                    """
                    Case 1: If voter can afford the target_pp, they pay it
                    Case 2: The voter can't afford $ but can in £, They use resource £ to buy units of $ with exchange rate
                    Case 3: Opposite of above
                    Case 4: Can't afford either, spends full amount
                    """
                    surplus = voter_budgets[i] - target_pp

                    # Case 1
                    if all([x >= 0 for x in surplus]):
                        voter_budgets[i] -= target_pp
                        remaining_cost -= target_pp

                    # Case 2 - Convert $ to £
                    elif surplus[0] < 0 and surplus[1] >= 0:
                        pound_needed = -surplus[0]
                        dollar_to_convert = pound_needed * pound_to_dollar_er
                        if dollar_to_convert <= surplus[1]:
                            # Spend the full amount of £ and spend the target $ plus the amount converted
                            remaining_cost -= np.array(target_pp)
                            voter_budgets[i] -= np.array([voter_budgets[i][0], target_pp[1]+dollar_to_convert])
                        else: # Convert surplus $ into £
                            pounds_gained = surplus[1] * dollar_to_pound_er

                            remaining_cost -= np.array([voter_budgets[i][0]+pounds_gained, target_pp[1]])
                            voter_budgets[i] = np.array([0,0])

                    # Case 3 - Convert £ to $
                    elif surplus[1] < 0 and surplus[0] >= 0:
                        dollar_needed = -surplus[1]
                        pound_to_convert = dollar_needed * dollar_to_pound_er
                        if pound_to_convert <= surplus[0]:
                            # Spend the full amount of $ and spend the target £ plus the amount converted
                            remaining_cost -= np.array(target_pp)
                            voter_budgets[i] -= np.array([target_pp[0]+pound_to_convert, voter_budgets[i][1]])
                        else: # Convert surplus £ into $
                            dollars_gained = surplus[0] * pound_to_dollar_er

                            remaining_cost -= np.array([target_pp[0], voter_budgets[i][1]+dollars_gained])
                            voter_budgets[i] = np.array([0,0])
                    else: # Case 4 - Spend full amount
                        remaining_cost -= voter_budgets[i]
                        voter_budgets[i] = np.array([0,0])


                # Floor the number once too small due to floating point errors
                if max(remaining_cost) < 1e-10:
                    remaining_cost = np.array([0,0])

            inst.budget_limit -= chosen_project.cost
            funded.add(chosen_project)
            inst.remove(chosen_project)
            #print("Project funded")
        if completion:
            extra = greedy_rule(inst, profile)
            funded.update(extra)


        return pbr.BudgetAllocation(funded)

def multi_BOS(inst: Minstance, profile:pbe.ApprovalProfile, charged_overspending=False) -> pbr.BudgetAllocation:
    num_voters = len(profile)

    # Set budgets for each voter
    voter_budgets = [[inst.budget_limit[i]/num_voters for i in range(inst.budget_limit.size)] for _ in range(num_voters)]
    funded = set()

    # Loop until no more projects remaining
    while len(inst) > 0:

        #Remove projects
        inst.remove_unaffordable_projects()

        # If no more projects then finish
        if len(inst) <= 0:
            break

        # Get the rho values for each project
        rho_values = dict([(c, 0) for c in inst])

        chosen_project = min(inst, key= lambda c: rho_values[c][0])

        # If chosen project has rho value infinty then all projects have rho value infinity; finish since no more can be funded.
        if rho_values[chosen_project][0] == inf:
            break

        # Fund it
        for v in range(num_voters):
            if chosen_project in profile[v]:
                for r in range(len(inst.budget_limit)):
                    voter_budgets[v][r] -= chosen_project.cost[r]*rho_values[chosen_project][1][r]

                    # Charge the voter if they overspent
                    if charged_overspending:
                        voter_budgets[v][r] -= 0

        # Remove the projects cost from budget,
        inst.budget_limit -= chosen_project.cost
        funded.add(chosen_project)
        inst.remove(chosen_project)

    return pbr.BudgetAllocation()
