-- CS344 THIRD YEAR PROJECT - PARTICIPATORY BUDGETING WITH MULTIPLE RESOURCES --

Author: George Blagden


Links to the Data from PabuLib (Data correct as of 24/02/2025):  
- Small instances (Below 30 projects): https://pabulib.org/?hash=67839fdfa933a
- All approval instances: https://pabulib.org/?hash=67bc428000c8e

Requirements:  
- Python 3.10 or later
Modules  
- numpy
- matplotlib
- pabutools (Documentation: https://comsoc-community.github.io/pabutools/index.html)
- time
- csv


Some tests - for some reason (memory leak in python 3.12 or linux?) - don't work on the Batch compute system on the DCS machines, please do not use it.


Files:
- main.py - Location for running the code.
- setup.py - Classes for the election. M_____ is the multi-resource version of the class provided in the pabutools library.
- parser.py - Parser to convert the elections into (Minstance, Profile) pairs. (Edited form of the parser provided here https://pabulib.org/code)
- rules.py - The different voting rules (rho-calculations.py contains additional subroutines).
- analysis.py - Useful functions for analysing the results.
- experiments.py - The tests and experiments that can be run.

Running an experiment
- Set the seed in the "if \_\_name\_\_ == 'name':" code block. Default is 0 and all tests have been run using this.

In main.py, in the function batch_run add an experiment to run:
- run_test_projects(test_name, data_location:str, output_folder:str, running_print:bool=False, show_graph:bool = False)
- run_test_resources(test_name, max_resource:int, data_location:str, output_folder:str, running_print:bool=False, show_graph:bool = False)
- run_test_aggregation(test_name, functions:list, data_location:str, output_folder:str, running_print:bool=False, show_graph:bool = False)

The first argument (test_name) should be the name of the test. These are:
- runtime_test - Runtime
- exclusion_test - Exclusion Ratio
- ejrplus_conversion_test - EJR+ Conversion
- ejrpc_one_test - EJR+ Conversion up to one
- elrplus_alldim_test - EJR+ All Dimensions
- ejrpa_one_test - EJR+ All Dimensions up to one
- False - The default test (Only for run_test_aggregation)

data_location is the location of the folder where the data is stored.  
output_folder is the location of the folder where the graph should be saved to.  
running_print is a bool whether anything should be printed to the terminal during execution (Recommended: True).  
show_graph is a bool whether to show the graph once the test has finished (If multiple tests are being run set as False).  

max_resources is the number of resources to test up to (Recommended: <= 10).  
functions is a list of aggregation functions to use for multi-MES (Recommended: [max,min,np.mean,np.median]).  
