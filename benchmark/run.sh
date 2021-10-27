#!/bin/bash
#SBATCH --time=04:00:00
#SBATCH --exclusive
#SBATCH -p haswell
#SBATCH -A p_readex
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -c 1
#SBATCH --comment=no_monitoring
#SBATCH --job-name benchmark_python

module load Python/3.8.6-GCCcore-10.2.0
module load Score-P/7.0-gompic-2020b

env_dir=~/virtenv/p-3.8.6-GCCcore-10.2.0-scorep-7.0-gompic-2020b/

if [ ! -d $env_dir ]
then
	echo "Please create virtual env under: $env_dir"
	exit -1
fi

source $env_dir/bin/activate

srun compare_commits.sh master faster
