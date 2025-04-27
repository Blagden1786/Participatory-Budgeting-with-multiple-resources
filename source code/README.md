# CS344 THIRD YEAR PROJECT - PARTICIPATORY BUDGETING WITH MULTIPLE RESOURCES SIMULATION

Author: George Blagden

As part of a university research project, I have been investigating a voting system called Participatory Budgeting (PB) (<https://en.wikipedia.org/wiki/Participatory_budgeting>) and an extension to one with multiple resources. As part of this, one part was to conduct some experiments to see how well different voting mechanisms work in practice. This repository contains the code required to run tests on some PB elections using the mechanisms developed during my research.

Links to the Data from PabuLib (Data correct as of 24/02/2025):

- Small instances (Below 30 projects): <https://pabulib.org/?hash=67839fdfa933a>
- All approval instances: <https://pabulib.org/?hash=67bc428000c8e>

Requirements:

- Python 3.10 or later
Modules
- numpy
- matplotlib
- pabutools (Documentation: <https://comsoc-community.github.io/pabutools/index.html>)
- time
- csv

Some tests - for some reason (memory leak in python 3.12 or linux?) - don't work on the Batch compute system on the DCS machines, please do not use it.

Files:
The files included here are .txt files as in accordance with the submission guidance on <https://warwick.ac.uk/fac/sci/dcs/teaching/material/cs310/components/final/submission/>. When converting them to .py, make sure the file has the same name.

- main.py - Location for running the code.
- setup.py - Classes for the election. M_____ is the multi-resource version of the class provided in the pabutools library.
- parser.py - Parser to convert the elections into ```(Minstance, Profile)``` pairs. (Edited form of the parser provided here <https://pabulib.org/code>)
- rules.py - The different voting rules (rho-calculations.py contains additional subroutines). The code was written before EES was named, the name used in the code is 'exchange rates'.
- analysis.py - Useful functions for analysing the results.
- experiments.py - The tests and experiments that can be run.
- system.py - A framework for creating an election and finding out the results of Greedy, multi-MES and EES.
- outcomes.txt - A text file that stores the outcomes of the experiments that are run.

Running an experiment

- Download some elections from <https://pabulib.org/> and save them in a folder.
- Set the seed in the ```if __name__ == 'name':``` code block. The seed was randomly generated as 53. The results in the paper use this. Depending on the tests run, results may differ.

In main.py, in the function batch_run add an experiment to run:

```python
run_test_projects(test_name, data_location:str, output_folder:str, running_print:bool=False, show_graph:bool = False)
run_test_resources(test_name, max_resource:int, data_location:str, output_folder:str, running_print:bool=False, show_graph:bool = False)
run_test_aggregation(test_name, functions:list, data_location:str, output_folder:str, running_print:bool=False, show_graph:bool = False)
```

The first argument (test_name) should be the name of the test. These are:

- ```runtime_test``` - Runtime
- ```exclusion_test``` - Exclusion Ratio
- ```budget_test``` - Budget usage
- ```cejr_test``` - CEJR+
- ```all_ejr_test``` - All-EJR+
- ```one_ejr_test``` - 1-EJR+
- ```False``` - The default test (Only for run_test_aggregation)

```data_location``` is the location of the folder where the data is stored.
```output_folder``` is the location of the folder where the graph should be saved to.
```running_print``` is a bool whether anything should be printed to the terminal during execution (Recommended: True).
```show_graph``` is a bool whether to show the graph once the test has finished (If multiple tests are being run set as False).

```max_resources``` is the number of resources to test up to (Recommended: <= 10).
```functions``` is a list of aggregation functions to use for multi-MES (Recommended: ```[max,min,np.mean,np.median]```).

Credits:

- PabuLib - <https://pabulib.org/>,
Piotr Faliszewski, Jaroslaw Flis, Dominik Peters, Grzegorz Pierczy´nski, Piotr Skowron, Dariusz Stolicki,
Stanislaw Szufa, and Nimrod Talmon. Participatory budgeting: Data, tools, and analysis. arXiv
preprint arXiv:2305.11035, 2023.
