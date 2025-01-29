#!/bin/bash
#
#SBATCH --job-name=initial_PB_tests # Job name for tracking
#SBATCH --partition=parrot  # Partition you wish to use (see above for list)
#SBATCH --cpus-per-task=1      # Number of CPU threads used by your job, set this upto 40 as required.
#SBATCH --mem-per-cpu=5000    # RAM in MB needed per core (i.e. 1500MB * 40 threads = 60GB RAM)
#SBATCH --time=2-00:00:00      # Job time limit set to 2 days (48 hours)
#
#SBATCH --mail-type=END,FAIL,TIME_LIMIT_80 # Events to send email on, remove if you don't want this
#SBATCH --output=joboutput_%j.out # Standard out from your job
#SBATCH --error=joboutput_%j.err  # Standard error from your job

## Initialisation ##
source /etc/profile.d/modules.sh
source /etc/profile.d/conda.sh

## Execute your program(s) ##
source simulation/bin/activate
python3.12 /dcs/22/u2200430/cs344/CS344-Extensions-of-PB-dissertation-main/environment/simulation/main.py