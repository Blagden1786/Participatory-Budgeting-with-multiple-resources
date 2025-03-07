from setup import *
from rules import *
from analysis import *
from parser import *
from experiments import *

def run_election():
    # Get number of resources
    r = int(input("Number of Resources: "))
    b = np.zeros(r)

    for i in range(b.size):
        b[i] = float(input(f"Budget of resource {i}: "))

    print(f"Budget: {b}")

    print("Select your projects, type exit in the name to finish")
    projects = set()
    while True:
        name = input("Project Name: ")
        if name.lower() == 'exit':
            break

        cost = np.zeros(r)
        for i in range(cost.size):
            cost[i] = float(input(f"Cost for resource {i}: "))

        projects.add(Mproject(name, cost))

    instance = Minstance(projects, b)
    print(instance)

    print("Place an x next to the supported projects, then state the number who have that approval\nType n when starting a new ballot to stop making new ones. ")
    ballots = []
    while True:
        if input("New ballot? (y/n) ") == 'n':
            break

        approved = set()

        for p in projects:
            supported = input(f"{p}: ").lower()

            if supported == 'x':
                approved.add(p)

        num = int(input("Supporters of this ballot: "))

        for _ in range(num):
            ballots.append(pbe.ApprovalBallot(approved))

    print(ballots)

    profile = pbe.ApprovalProfile(ballots, instance)

    print("Thanks, now here are the outputs of the different elections:")
    print(f"Greedy: {greedy_rule(instance.copy(), profile.copy())}")
    print(f"MES: {multi_method_equal_shares(instance.copy(), profile.copy())}")
    print(f"Exchange rates: {exchange_rates_2d(instance.copy(), profile.copy())}")

run_election()
