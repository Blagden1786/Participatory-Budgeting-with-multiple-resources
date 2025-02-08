from cProfile import label
import os
from parser import *
from rules import *
from analysis import *

from pabutools.election import Project, Instance, ApprovalProfile, ApprovalBallot
from pabutools.election.satisfaction import Cost_Sat

from time import time
from itertools import combinations
import gc
import numpy as np
import random as rand
import matplotlib.pyplot as plt

"""
Parsing data functions
"""
def get_data(loc):
    """Given the location, retrieve the list of paths of the data

    Args:
        loc (str): Root of the dataset folder
        short (bool, optional): Whether to parse the short dataset (under 30) or not. Defaults to True.

    Returns:
        _type_: _description_
    """
    test_projects = os.listdir(loc)
    test_projects = [f"{loc}/{x}" for x in test_projects]

    return test_projects

def generate_instances(paths:list[str], num_resources:int):
    """Returns the array of (instance,profile)s from the data

    Args:
        paths (list[str]): List of paths to use
        num_resources (int): The number of resources

    Returns:
        list[tuple[str, Minstance, pbe.ApprovalProfile]]: Tuples of (filepath, Instance, Profile)
    """
    return np.array([parse(p, num_resources) for p in paths], dtype=object)

"""
Tests
"""
def runtime_test(instance:Minstance, profile:pbe.ApprovalProfile, rule) -> float:
    """Calculates the runtime of the given rule


    Args:
        instance (Minstance)
        profile (pbe.ApprovalProfile)
        rule (function): The voting rule to use (greedy_rule, multi_method_equal_shares, exchange_rates_2d)

    Returns:
        float: Output runtime in seconds
    """
    t1 = time()
    _ = rule(instance, profile)
    t2 = time()
    return t2-t1

def exclusion_test(instance:Minstance, profile:pbe.ApprovalProfile, rule) -> float:
    """Calculates the exclusion ratio given an instance and a rule

    Args:
        instance (Minstance)
        profile (pbe.ApprovalProfile)
        rule (_type_): The voting rule to use (greedy_rule, multi_method_equal_shares, exchange_rates_2d)

    Returns:
        float: Exclusion Ratio
    """
    # Generate winner
    outcome = rule(instance.copy(), profile.copy())

    ratio = exclusion_ratio(instance, profile, outcome)

    return ratio

def ejrplus_conversion_test(instance:Minstance, profile:pbe.ApprovalProfile, rule, up_to_one:bool=False) -> float:
    """Calculate the number of EJR+ violations up to one project or not

    Args:
        instance (Minstance)
        profile (pbe.ApprovalProfile)
        rule (_type_): The voting rule to use (greedy_rule, multi_method_equal_shares, exchange_rates_2d)
        up_to_one (bool, optional): Whether to find violations up to one project or up to any. Defaults to True.

    Returns:
        float: The number of violations
    """
    # Generate outcome
    outcome = rule(instance.copy(), profile.copy())

    # Convert instance, profile and outcome to 1D equivalent
    converted_inst, converted_profile = to_1d_converted(instance, profile)
    converted_outcome = [converted_inst.get_project(c.name) for c in outcome]

    # Calculate the number of EJR+ failures
    failures, _ = strong_ejr_plus_violations(converted_inst, converted_profile, converted_outcome, pbe.Cost_Sat, up_to_one)

    return failures
def ejrpc_one_test(instance:Minstance, profile:pbe.ApprovalProfile, rule):
    """ Calculate EJR+ conversion up to one project

    Args:
        instance (Minstance)
        profile (pbe.ApprovalProfile)
        rule (_type_): The voting rule to use (greedy_rule, multi_method_equal_shares, exchange_rates_2d)

    Returns:
        float: The number of violations
"""
    return ejrplus_conversion_test(instance,profile,rule,True)

def ejrplus_alldim_test(instance:Minstance, profile:pbe.ApprovalProfile, rule, up_to_one:bool=False) -> float:
    """Calculate the number of EJR+ violations up to one project or not

    Args:
        instance (Minstance)
        profile (pbe.ApprovalProfile)
        rule (_type_): The voting rule to use (greedy_rule, multi_method_equal_shares, exchange_rates_2d)
        up_to_one (bool, optional): Whether to find violations up to one project or up to any. Defaults to True.

    Returns:
        float: The number of violations
    """
    # Generate outcome
    outcome = rule(instance.copy(), profile.copy())
    violations = set()
    # Find the EJR+ failures for each resource
    for i in range(instance.budget_limit.size):
        # Convert instance, profile and outcome to 1D equivalent (by restricting to one resource)
        converted_inst, converted_profile = to_1d(instance, profile, i)
        converted_outcome = [converted_inst.get_project(c.name) for c in outcome]

        # Calculate the set of EJR+ failures for this resource
        _, failures = strong_ejr_plus_violations(converted_inst, converted_profile, converted_outcome, pbe.Cost_Sat, up_to_one)

        # Add violations to the set of all violations
        violations.update(failures)

        del converted_inst
        del converted_profile
        del converted_outcome
        del failures
        gc.collect()

    # The number of EJR+ violations is the total number which cause a violation in >= one dimension
    num = len(violations)
    del violations
    gc.collect()
    return num
def ejrpa_one_test(instance:Minstance, profile:pbe.ApprovalProfile, rule) -> float:
    """ Calculate EJR+ all dim violations up to one project

    Args:
        instance (Minstance)
        profile (pbe.ApprovalProfile)
        rule (_type_): The voting rule to use (greedy_rule, multi_method_equal_shares, exchange_rates_2d)

    Returns:
        float: The number of violations
"""
    return ejrplus_alldim_test(instance,profile,rule,True)

## Graphs
'''
Graph Building Functions
'''
def graph_builder(x_ys:dict[str,dict[str, float]], x_title:str, y_title:str, graph_title:str, graph_name:str,  out_folder:str,):
    """Generate a graph given the parameters

    Args:
        x_ys (dict[str,dict[str, float]]): The values, first key is the name, second dict are the x and y values
        x_title (str): Title for x axis
        y_title (str): Title for y axis
        graph_title (str): Graph Title
        out_folder (str): Folder to output the graph to
        graph_name (str): The filename for the graph (no filetype)
    """
    plt.figure(graph_name)
    for rule in x_ys.keys():
        plt.plot(x_ys[rule].keys(), x_ys[rule].values(), label=rule)

    plt.xlabel(x_title)
    plt.ylabel(y_title)
    plt.title(graph_title)
    plt.legend(loc='upper left')

    plt.savefig(f"{out_folder}/{graph_name}.png")

def num_datsets_per_project(data):
    num_datasets = {'1-8': 0, '9-13': 0, '14-21': 0, '22-38': 0, '39+': 0}
    for path in data:
        _, instance, _ = parse(path, 1)
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

"""
Auxillary Functions
"""
def test_metadata(test, test_type:str) -> tuple[str,str,str]:
    """Generate the metadata for a test

    Args:
        test (function): The test e.g runtime_test
        test_type (str): What is being compared in the test e.g resource, projects

    Returns:
        tuple[str,str,str]: (y axis, graph title, filename)
    """
    match (test.__name__):
        case 'runtime_test':
            return ('Time (s)', 'Time for different rules to run', f'runtime_{test_type}')
        case 'exclusion_test':
            return ('Exclusion Ratio', 'Exclusion ratio for different rules', f'exclusion_{test_type}')
        case 'ejrplus_conversion_test':
            return ('Number of Violations', 'EJR+ conversion violations', f'ejrc_{test_type}')
        case 'ejrpc_one_test':
            return ('Number of Violations', 'EJR+ conversion violations up to one project', f'ejrco_{test_type}')
        case 'ejrplus_alldim_test':
            return ('Number of Violations', 'EJR+ (all dimensions) violations', f'ejra_{test_type}')
        case 'ejrpa_one_test':
            return ('Number of Violations', 'EJR+ (all dimensions) violations up to one project', f'ejrao_{test_type}')
        case _:
            return ('','','None')

def project_num_split(n):
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

"""
Wrapper to run tests through
"""
def run_test_projects(test_name, data_location:str, output_folder:str, running_print:bool=False, show_graph:bool = False):
    """Run a given test by changing the projects

    Args:
        test_name (function): The test to run
        data_location (str): Where the dataset is stored
        output_folder (str): The folder to save graphs in
        running_print (bool, optional): Whether to print updates as the program runs. Defaults to False.
        show_graph (bool, optional): Whether to show the graph once the testing is complete
    """
    # Dict for each rule containing the list of values
    g = {'1-8': [],'9-13': [],'14-21': [],'22-38': [],'39+': []}
    mes = {'1-8': [],'9-13': [],'14-21': [],'22-38': [],'39+': []}
    er = {'1-8': [],'9-13': [],'14-21': [],'22-38': [],'39+': []}

    # retrieve list of paths and count them (for printing)
    if running_print:
        print(f"Running test: {test_name.__name__}")
        print("Retrieving file paths")
    paths = get_data(data_location)
    num_paths = len(paths)

    # FOR TESTING, sort to find where first problem instance is
    #instances = sorted(generate_instances(paths, 2), key= lambda x: len(x[1])*(len(x[2])**2), reverse=False)

    # Loop through each election and run the test on it for each rule
    counter = 0
    for path in paths:
        # Generate instance
        _, instance, profile = parse(path, 2)
        projects = len(instance)
        voters = len(profile)

        if running_print:
            counter += 1
            print("-----------------------------------")
            print(path)
            print(f"Projects {projects}")
            print(f"Votes: {voters}")
            print(f"Instance {counter} of {num_paths}")
            print("...................................")

        # Add the outcome of the test to the dictionary
        if running_print:
            print("Greedy Rule", end='')
        g[project_num_split(projects)].append(test_name(instance.copy(), profile.copy(), greedy_rule))

        if running_print:
            print(" Done\nMulti-MES", end='')
        mes[project_num_split(projects)].append(test_name(instance.copy(), profile.copy(), multi_method_equal_shares))

        if running_print:
            print(" Done\nExchange Rates", end='')
        er[project_num_split(projects)].append(test_name(instance.copy(), profile.copy(), exchange_rates_2d))
        if running_print:
            print(" Done")

        del instance
        del profile
        gc.collect()
    # Create the dict for the graph builder and then create the graph
    graph_values = {'Greedy Rule': dict([(k, np.mean(g[k])) for k in g.keys()]),
                    'Multi-MES': dict([(k, np.mean(mes[k])) for k in mes.keys()]),
                    'Exchange Rates': dict([(k, np.mean(er[k])) for k in er.keys()])}
    test_meta = test_metadata(test_name, 'projects')

    graph_builder(graph_values, 'Number of Projects', test_meta[0], test_meta[1], test_meta[2], output_folder)
    if show_graph:
        plt.show()

    del g
    del mes
    del er
    del graph_values
    gc.collect()

def run_test_resources(test_name, max_resource:int, data_location:str, output_folder:str, running_print:bool=False, show_graph:bool = False):
    """Framework for running tests which measure against number of resources. Runs for Greedy and mmes

    Args:
        test_name (_type_): The test name
        data_location (str): Where the datasets are located
        output_folder (str): The folder to output the graphs to
        running_print (bool, optional): Whether to print during the running of the test. Defaults to False.
        show_graph (bool, optional): Whether to show the graph once the test has finished. Defaults to False.
    """
    # Create dictionaries for greedy (g) and multi-mes (mes)
    g = dict([(i,[]) for i in range(1,max_resource+1)])
    mes = dict([(i,[]) for i in range(1,max_resource+1)])

    # Get paths of datasets
    if running_print:
        print(f"Running test: {test_name.__name__}")
        print("Retrieving file paths")
    paths = get_data(data_location)
    num_paths = len(paths)

    # Loop through each resource and run tests
    for i in range(1, max_resource+1):
        # Loop through each election and run the test on it for each rule
        counter = 0
        for path in paths:
            # Generate instance
            _, instance, profile = parse(path, i)
            projects = len(instance)
            voters = len(profile)

            if running_print:
                counter += 1
                print("-----------------------------------")
                print(path)
                print(f"Projects {projects}")
                print(f"Votes: {voters}")
                print(f"Resources: {i}")
                print(f"Instance {counter} of {num_paths}")
                print("...................................")

            # Add the outcome of the test to the dictionary
            if running_print:
                print("Greedy Rule", end='')
            g[i].append(test_name(instance.copy(), profile.copy(), greedy_rule))

            if running_print:
                print(" Done\nMulti-MES", end='')
            mes[i].append(test_name(instance.copy(), profile.copy(), multi_method_equal_shares))

            if running_print:
                print(" Done")


            del instance
            del profile
            gc.collect()
    # Create the dict for the graph builder and then create the graph
    graph_values = {'Greedy Rule': dict([(k, np.mean(g[k])) for k in g.keys()]),
                    'Multi-MES': dict([(k, np.mean(mes[k])) for k in mes.keys()]),}
    test_meta = test_metadata(test_name, 'resources')

    graph_builder(graph_values, 'Number of Resources', test_meta[0], test_meta[1], test_meta[2], output_folder)
    if show_graph:
        plt.show()

    del g
    del mes
    del graph_values
    gc.collect()

def run_test_aggregation(functions:list, data_location:str, output_folder:str, running_print:bool=False, show_graph:bool = False):
    """Run a given test for different aggregation functions with Multi-MES


    Args:
        test_name (function): The test to run
        functions (list[function]): The list of aggregation functions: list[float] -> float
        data_location (str): Where the dataset is stored
        output_folder (str): The folder to save graphs in
        running_print (bool, optional): Whether to print updates as the program runs. Defaults to False.
        show_graph (bool, optional): Whether to show the graph once the testing is complete
    """
    mes = dict([(f'{f.__name__},{g.__name__}', 0) for f,g in combinations(functions, 2)])

    # retrieve list of paths and count them (for printing)
    if running_print:
        print(f"Running test: Different aggregation functions")
        print("Retrieving file paths")
    paths = get_data(data_location)
    num_paths = len(paths)

    # Loop through each election and run the test on it for each rule
    counter = 0
    for path in paths:
        # Generate instance
        _, instance, profile = parse(path, 2)
        projects = len(instance)
        voters = len(profile)

        if running_print:
            counter += 1
            print("-----------------------------------")
            print(path)
            print(f"Projects {projects}")
            print(f"Votes: {voters}")
            print(f"Instance {counter} of {num_paths}")
            print("...................................")

        outputs = dict([(x.__name__,0) for x in functions])
        for f in functions:
            # Add the outcome of the test to the dictionary
            if running_print:
                print(f"Multi-MES({f.__name__})", end='')

            outputs[f.__name__] = multi_method_equal_shares(instance.copy(), profile.copy(), f, False)

            if running_print:
                print(" Done")

        # Count number of differences
        for f,g in combinations(functions, 2):
            if  not outputs[f.__name__] == outputs[g.__name__]:
                # Add 1 to the numbers of differences
                mes[f'{f.__name__},{g.__name__}'] += 1
        del instance
        del profile
        gc.collect()

    # Create the bar graph
    plt.figure("Differences")
    plt.bar(mes.keys(), [x/num_paths for x in mes.values()])
    plt.xlabel("Aggregation Function")
    plt.ylabel("Proportion of instances where output differs")
    plt.title("How the output of different aggregation functions differ")
    plt.savefig(f"{output_folder}/diff_aggregation.png")

    if show_graph:
        plt.show()

    del mes
    gc.collect()
