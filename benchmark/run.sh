#!/bin/bash
#SBATCH --time=04:00:00
#SBATCH --exclusive
#SBATCH -p haswell
#SBATCH -A p_readex
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH -c 24
#SBATCH --comment=no_monitoring
#SBATCH --job-name benchmark_python


module load Python/3.6.6-foss-2019a

module use /home/gocht/modules
module load scorep/scorep-6.0-python3.6.6-foss-2019a
# Score-P 6.0 build with
# ../configure --prefix=/home/gocht/sw/scorep/scorep-6.0-python3.6.6-foss-2019a --enable-shared
# scorep_binding_python git sha: e3a52d315daf8d2f6273ba825597d544af9074c7
# installed in virtual environment

. ~/virtenv/Python-3.6.6-foss-2019a/bin/activate

srun taskset -c 0 python benchmark.py
