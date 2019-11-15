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

module load Python/3.6.4-intel-2018a
module unload intel
module load intel

export PATH=/scratch/rschoene/scorep-6-inst/bin:$PATH

. ~/scorep_binding_python/test/bin/activate

srun python benchmark.py
