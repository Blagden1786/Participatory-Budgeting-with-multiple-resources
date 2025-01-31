from calendar import c
import os
from parser import *
from rules import *
from analysis import *

from pabutools.election import Project, Instance, ApprovalProfile, ApprovalBallot
from pabutools.election.satisfaction import Cost_Sat

from time import time
import numpy as np
import random as rand
import matplotlib.pyplot as plt

"""This script is used to run experiments on the implemented rules.
The experiments are run on the datasets in the Simulation/datasets folder.
The results are then plotted and saved in the Simulation/plots folder.

The following experiments are run:
1. Projects vs time: The time taken to run the rules on the projects is plotted against the number of projects.
2. Projects vs exclusion: The exclusion ratio of the rules is plotted against the number of projects.
3. EJR+ violations: The number of EJR+ violations is plotted against the number of projects.

The following rules are tested:
1. Exchange Rates (with a greedy completion mechanism)
2. Multi-Method Equal Shares (with a greedy completion mechanism)
3. Greedy Rule
"""

def find_data(loc, short=True):
    test_projects_short = os.listdir(f"{loc}/datasets_under_30")
    test_projects_short = [f"{loc}/datasets_under_30/{x}" for x in test_projects_short]

    test_projects_extended = os.listdir(f"{loc}/datasets_extended")
    test_projects_extended = [f"{loc}/datasets_extended/{x}" for x in test_projects_extended]

    if short:
        test_projects = test_projects_short # Change between a short run and an extended run
    else:
        test_projects = test_projects_extended

    return test_projects

def projects_vs_times(data, out_folder, print_instance=True, show=False):
    er_times = {
        '1-8': [],
        '9-13': [],
        '14-21': [],
        '22-38': [],
        '39+': []
    }
    mmes_times = {
        '1-8': [],
        '9-13': [],
        '14-21': [],
        '22-38': [],
        '39+': []
    }
    greedy_times = {
        '1-8': [],
        '9-13': [],
        '14-21': [],
        '22-38': [],
        '39+': []
    }

    counter = 0

    for path in data:
        counter += 1
        instance, profile = parse(path, 2)


        num_projects = len(instance)

        if print_instance:
            print("-----------------------------------")
            print(path)
            print(f"Projects {num_projects}")
            print(f"Votes: {len(profile)}")
            print(f"Instance {counter} of {len(data)}")
            print("-----------------------------------")

        t1 = time()
        er = exchange_rates_2d(instance.copy(), profile.copy())
        t2 = time()

        t3 = time()
        mmes = multi_method_equal_shares(instance.copy(), profile.copy())
        t4 = time()

        t5 = time()
        greedy = greedy_rule(instance.copy(), profile.copy())
        t6 = time()

        er_times[data_split(num_projects)].append(t2-t1)
        mmes_times[data_split(num_projects)].append(t4-t3)
        greedy_times[data_split(num_projects)].append(t6-t5)


    er_y_values = [np.mean(er_times[x]) for x in er_times.keys()]
    mmes_y_values = [np.mean(mmes_times[x]) for x in mmes_times.keys()]
    greedy_y_values = [np.mean(greedy_times[x]) for x in greedy_times.keys()]

    plt.figure(0)
    plt.plot(er_times.keys(),er_y_values, c='b', label='Exchange Rates')
    plt.plot(mmes_times.keys(), mmes_y_values, c='r', label='Multi-Method Equal Shares')
    plt.plot(greedy_times.keys(), greedy_y_values, c='g', label='Greedy Rule')

    plt.xlabel("Number of Projects")
    plt.ylabel("Time (s)")
    plt.title("How the number of projects affects runtime")
    plt.legend(loc='upper left')

    plt.savefig(f"{out_folder}/projects_vs_time.png")
    if show:
        plt.show()

def projects_vs_exclusion(data, out_folder, print_instance=True, show=False):
    er_exclusion = {
        '1-8': [],
        '9-13': [],
        '14-21': [],
        '22-38': [],
        '39+': []
    }
    mmes_exclusion = {
        '1-8': [],
        '9-13': [],
        '14-21': [],
        '22-38': [],
        '39+': []
    }
    mgreedy_exclusion = {
        '1-8': [],
        '9-13': [],
        '14-21': [],
        '22-38': [],
        '39+': []
    }

    counter = 0

    for path in data:
        counter += 1
        instance, profile = parse(path, 2)
        num_projects = len(instance)

        if print_instance:
            print("-----------------------------------")
            print(path)
            print(f"Projects {num_projects}")
            print(f"Votes: {len(profile)}")
            print(f"Instance {counter} of {len(data)}")
            print("-----------------------------------")

        er = exchange_rates_2d(instance.copy(), profile.copy(), completion=True)
        mmes = multi_method_equal_shares(instance.copy(), profile.copy())
        mgreedy = greedy_rule(instance.copy(), profile.copy())

        er_exclusion[data_split(num_projects)].append(exclusion_ratio(instance, profile, er))
        mmes_exclusion[data_split(num_projects)].append(exclusion_ratio(instance, profile, mmes))
        mgreedy_exclusion[data_split(num_projects)].append(exclusion_ratio(instance, profile, mgreedy))


    er_y_values = [np.mean(er_exclusion[x]) for x in er_exclusion.keys()]
    mmes_y_values = [np.mean(mmes_exclusion[x]) for x in mmes_exclusion.keys()]
    mgreedy_y_values = [np.mean(mgreedy_exclusion[x]) for x in mgreedy_exclusion.keys()]

    """ 1D equivalent
    mes_exclusion_per_num_projects = dict([(x,[]) for x in range(1,31)])
    greedy_exclusion_per_num_projects = dict([(x,[]) for x in range(1,31)])

    converted_instance, converted_profile = to_1d_converted(profile, instance)

    mes = pbr.method_of_equal_shares(converted_instance.copy(), converted_profile.copy(), sat_class=Cost_Sat)
    greedy = pbr.greedy_utilitarian_welfare(converted_instance.copy(), converted_profile.copy(), sat_class=Cost_Sat)
    mes_exclusion_per_num_projects[num_projects].append(exclusion_ratio(converted_instance, converted_profile, mes))
    greedy_exclusion_per_num_projects[num_projects].append(exclusion_ratio(converted_instance, converted_profile, greedy))

    mes_y_values = [mean_excluding_outliers(mes_exclusion_per_num_projects[x]) for x in mes_exclusion_per_num_projects.keys()]
    greedy_y_values = [mean_excluding_outliers(greedy_exclusion_per_num_projects[x]) for x in greedy_exclusion_per_num_projects.keys()]

    plt.scatter(mes_exclusion_per_num_projects.keys(), mes_y_values, c='r', marker='x', label='Method Equal Shares')
    plt.scatter(greedy_exclusion_per_num_projects.keys(), greedy_y_values, c='b',, marker='x' label='Greedy Rule')
    """
    plt.figure(1)
    plt.plot(er_exclusion.keys(),er_y_values, c='b', label='Exchange Rates')
    plt.plot(mmes_exclusion.keys(), mmes_y_values, c='r', label='Multi-Method Equal Shares')
    plt.plot(mgreedy_exclusion.keys(), mgreedy_y_values, c='g', label='Greedy Rule')

    plt.legend(loc='upper right')
    plt.xlabel("Number of Projects")
    plt.ylabel("Exclusion Ratio")
    plt.title("How the number of projects affects exclusion ratio")

    plt.savefig(f"{out_folder}/projects_vs_exclusion.png")
    if show:
        plt.show()

def ejr_plus_conversion_violations(data, out_folder, up_to_one, print_instance=True, show=False):
    er_violations = {
        '1-8': [],
        '9-13': [],
        '14-21': [],
        '22-38': [],
        '39+': []
    }
    mmes_violations = {
        '1-8': [],
        '9-13': [],
        '14-21': [],
        '22-38': [],
        '39+': []
    }
    greedy_violations = {
        '1-8': [],
        '9-13': [],
        '14-21': [],
        '22-38': [],
        '39+': []
    }

    counter = 0

    for path in data:
        instance, profile = parse(path, 2)
        counter += 1

        num_projects = len(instance)

        if print_instance:
            print("-----------------------------------")
            print(path)
            print(f"Projects {num_projects}")
            print(f"Votes: {len(profile)}")
            print(f"Instance {counter} of {len(data)}")
            print("-----------------------------------")

        y = exchange_rates_2d(instance.copy(), profile.copy())
        er_violation = ejr_plus_conversion(instance, profile, y, up_to_one)

        y = multi_method_equal_shares(instance.copy(), profile.copy())
        mmes_violation = ejr_plus_conversion(instance, profile, y, up_to_one)

        y = greedy_rule(instance.copy(), profile.copy())
        greedy_violation = ejr_plus_conversion(instance, profile, y, up_to_one)


        er_violations[data_split(num_projects)].append(er_violation)
        mmes_violations[data_split(num_projects)].append(mmes_violation)
        greedy_violations[data_split(num_projects)].append(greedy_violation)

    er_y_values = [np.mean(er_violations[x]) for x in er_violations.keys()]
    mmes_y_values = [np.mean(mmes_violations[x]) for x in mmes_violations.keys()]
    greedy_y_values = [np.mean(greedy_violations[x]) for x in greedy_violations.keys()]


    if up_to_one:
        plt.figure(2)
        plt.plot(er_violations.keys(),er_y_values, c='b', label='Exchange Rates')
        plt.plot(mmes_violations.keys(), mmes_y_values, c='r', label='Multi-Method Equal Shares')
        plt.plot(greedy_violations.keys(), greedy_y_values, c='g', label='Greedy Rule')

        plt.xlabel("Number of Projects")
        plt.ylabel("EJR+ conversion violations")
        plt.legend(loc='upper left')

        plt.title("EJR+ conversion violations up to one project")
        plt.savefig(f"{out_folder}/ejr_plus_max_up_to_one.png")
    else:
        plt.figure(3)
        plt.plot(er_violations.keys(),er_y_values, c='b', label='Exchange Rates')
        plt.plot(mmes_violations.keys(), mmes_y_values, c='r', label='Multi-Method Equal Shares')
        plt.plot(greedy_violations.keys(), greedy_y_values, c='g', label='Greedy Rule')

        plt.xlabel("Number of Projects")
        plt.ylabel("EJR+ conversion violations")
        plt.legend(loc='upper left')
        plt.title("EJR+ conversion violations")

        plt.savefig(f"{out_folder}/ejr_plus_max.png")
    if show:
        plt.show()

def ejr_plus_alldim_violations(data, out_folder, up_to_one, print_instance=True, show=False):
    er_violations = {
        '1-8': [],
        '9-13': [],
        '14-21': [],
        '22-38': [],
        '39+': []
    }
    mmes_violations = {
        '1-8': [],
        '9-13': [],
        '14-21': [],
        '22-38': [],
        '39+': []
    }
    greedy_violations = {
        '1-8': [],
        '9-13': [],
        '14-21': [],
        '22-38': [],
        '39+': []
    }

    counter = 0

    for path in data:
        instance, profile = parse(path, 2)
        counter += 1

        num_projects = len(instance)

        f = open(f"{out_folder}/out.txt", "a")
        f.write("-----------------------------------\n")
        f.write(path+'\n')
        f.write(f"Projects {num_projects}\n")
        f.write(f"Votes: {len(profile)}\n")
        f.write(f"Instance {counter} of {len(data)}\n")
        
        
        
        t = time()
        g = greedy_rule(instance.copy(), profile.copy())
        f.write(f"Found output, doing pound violations {time()-t}\n")
        instance_pound, profile_pound = to_1d(instance, profile, 0)
        f.write(f"Restricted to pound, now checking violations {time() - t}\n")
        _ , pound_violations = strong_ejr_plus_violations(instance_pound, profile_pound, [instance_pound.get_project(c.name) for c in g], Cost_Sat, up_to_one)
        f.write(f"Pound done, moving onto dollar {time()-t}\n")
        instance_dollar, profile_dollar = to_1d(instance, profile, 1)
        f.write(f"Converted to dollar, now checking violations {time()-t}")
        _ , dollar_violations = strong_ejr_plus_violations(instance_dollar, profile_dollar, [instance_dollar.get_project(c.name) for c in g], Cost_Sat, up_to_one)

        greedy_violations[data_split(num_projects)].append(len(set.union(pound_violations, dollar_violations)))
        f.write(f"Instance complete {time()-t}\n")
        f.write("-----------------------------------\n")
        f.close()

    greedy_y_values = [np.mean(greedy_violations[x]) for x in greedy_violations.keys()]


    if up_to_one:
        plt.figure(4)
        #plt.plot(er_violations.keys(),er_y_values, c='b', label='Exchange Rates')
        #plt.plot(mmes_violations.keys(), mmes_y_values, c='r', label='Multi-Method Equal Shares')
        plt.plot(greedy_violations.keys(), greedy_y_values, c='g', label='Greedy Rule')

        plt.xlabel("Number of Projects")
        plt.ylabel("Average EJR+ min violations")
        plt.legend(loc='upper left')
        plt.title("EJR+ all dimension violations up to one project")

        plt.savefig(f"{out_folder}/ejr_plus_min_up_to_one.png")
    else:
        plt.figure(5)
        #plt.plot(er_violations.keys(),er_y_values, c='b', label='Exchange Rates')
        #plt.plot(mmes_violations.keys(), mmes_y_values, c='r', label='Multi-Method Equal Shares')
        plt.plot(greedy_violations.keys(), greedy_y_values, c='g', label='Greedy Rule')

        plt.xlabel("Number of Projects")
        plt.ylabel("Average EJR+ min violations")
        plt.legend(loc='upper left')
        plt.title("EJR+ all dimension violations")

        plt.savefig(f"{out_folder}/ejr_plus_min.png")
    if show:
        plt.show()

def resources_vs_time(data, out_folder,project_number = 8, print_instance=True, show=False):
    mmes_times = dict([(i,[]) for i in range(1,11)])
    greedy_times = dict([(i,[]) for i in range(1,11)])

    counter = 0

    for path in data:
        counter += 1
        instance, profile = parse(path, 1)


        num_projects = len(instance)
        if num_projects == project_number:
            if print_instance:
                print("-----------------------------------")
                print(path)
                print(f"Projects {num_projects}")
                print(f"Votes: {len(profile)}")
                print(f"Instance {counter} of {len(data)}")
                print("-----------------------------------")

            for i in range(1,11):
                # For each number of resources, test both multi-mes and greedy
                instance, profile = parse(path, i)
                t1 = time()
                mmes = multi_method_equal_shares(instance.copy(), profile.copy())
                t2 = time()

                t3 = time()
                greedy = greedy_rule(instance.copy(), profile.copy())
                t4 = time()

                mmes_times[i].append(t2-t1)
                greedy_times[i].append(t4-t3)


    mmes_y_values = [np.mean(mmes_times[x]) for x in mmes_times.keys()]
    greedy_y_values = [np.mean(greedy_times[x]) for x in greedy_times.keys()]

    plt.figure(6)
    plt.plot(mmes_times.keys(), mmes_y_values, c='r', label='Multi-Method Equal Shares')
    plt.plot(greedy_times.keys(), greedy_y_values, c='g', label='Greedy Rule')

    plt.xlabel("Number of Resources")
    plt.ylabel("Time (s)")
    plt.title(f"How the number of resources affects runtime ({project_number} projects per instance)")
    plt.legend(loc='upper left')

    plt.savefig(f"{out_folder}/resources_vs_time.png")
    if show:
        plt.show()

def resources_vs_exclusion(data, out_folder,project_number = 8, print_instance=True, show=False):
    mmes_exclusion = dict([(i,[]) for i in range(1,11)])
    greedy_exclusion = dict([(i,[]) for i in range(1,11)])

    counter = 0

    for path in data:
        counter += 1
        instance, profile = parse(path, 1)


        num_projects = len(instance)
        if num_projects == project_number:
            if print_instance:
                print("-----------------------------------")
                print(path)
                print(f"Projects {num_projects}")
                print(f"Votes: {len(profile)}")
                print(f"Instance {counter} of {len(data)}")
                print("-----------------------------------")

            for i in range(1,11):
                # For each number of resources, test both multi-mes and greedy
                instance, profile = parse(path, i)

                mmes = multi_method_equal_shares(instance.copy(), profile.copy())
                greedy = greedy_rule(instance.copy(), profile.copy())

                mmes_exclusion[i].append(exclusion_ratio(instance, profile, mmes))
                greedy_exclusion[i].append(exclusion_ratio(instance, profile, greedy))


    mmes_y_values = [np.mean(mmes_exclusion[x]) for x in mmes_exclusion.keys()]
    greedy_y_values = [np.mean(greedy_exclusion[x]) for x in greedy_exclusion.keys()]

    plt.figure(6)
    plt.plot(mmes_exclusion.keys(), mmes_y_values, c='r', label='Multi-Method Equal Shares')
    plt.plot(greedy_exclusion.keys(), greedy_y_values, c='g', label='Greedy Rule')

    plt.xlabel("Number of Resources")
    plt.ylabel("Exclusion Ration")
    plt.title(f"How the number of resources affects exclusion ratio ({project_number} projects per instance)")
    plt.legend(loc='upper left')

    plt.savefig(f"{out_folder}/resources_vs_exclusion.png")
    if show:
        plt.show()

def num_datsets_vs_projects(data):
    num_datasets = {'1-8': 0, '9-13': 0, '14-21': 0, '22-38': 0, '39+': 0}
    for path in data:
        instance, _ = parse(path, 1)
        print("-----------------------------------")
        print(path)
        print(f"Projects {len(instance)}")
        print("-----------------------------------")

        num_projects = len(instance)
        if num_projects <= 8:
            num_datasets['1-8'] += 1
        elif num_projects <= 13:
            num_datasets['9-13'] += 1
        elif num_projects <= 21:
            num_datasets['14-21'] += 1
        elif num_projects <= 38:
            num_datasets['22-38'] += 1
        else:
            num_datasets['39+'] += 1

    plt.figure(-1)
    plt.bar(num_datasets.keys(), num_datasets.values())
    plt.xlabel("Number of Projects")
    plt.ylabel("Number of Datasets")
    plt.savefig("Simulation/plots/datasets_vs_projects.png")
    plt.show()

# [  1.   8.  13.  21.  38. 163.]
# Want the gaps to be 1-8, 9-13, 14-21, 22-38, 39+
# Split data into 5 roughly equal parts
# Speak to Brill about this next week
def data_split(n):
    if n <= 8:
        return '1-8'
    elif n <= 13:
        return '9-13'
    elif n <= 21:
        return '14-21'
    elif n <= 38:
        return '22-38'
    else:
        return '39+'
