#!/bin/bash
#SBATCH --time=8:00:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=40
#SBATCH --job-name="ITER_5"
#SBATCH --partition=IllinoisComputes
#SBATCH --account=kaijames-ic
#SBATCH --output=FAILURE.ERR
#SBATCH --exclude=ccc0354,ccc0353
module purge
module load anaconda/2023-Jul/3
module load openmpi/4.1.1-gcc-9.2.0

python3 RunOptimIP.py

#mpirun -np 40 SU2_CFD turb_CRMWS.cfg > log.CFD
