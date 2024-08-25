#!/bin/bash
#SBATCH --nodes=6
#SBATCH --ntasks-per-node=128    # <- match to OMP_NUM_THREADS
#SBATCH --partition=cpu      # <- or one of: gpuA100x4 gpuA40x4 gpuA100x8 gpuMI100x8
#SBATCH --account=bcrx-delta-cpu    # <- match to a "Project" returned by the "accounts" command
#SBATCH --job-name=A1
#SBATCH --time=48:00:00      # hh:mm:ss for the job
#SBATCH --constraint="scratch"
#SBATCH --output=FAILURE.ERR
#SBATCH --exclusive
module purge

module load anaconda3_cpu/23.7.4
module load gcc/11.4.0
module load slurm-env/0.1
module load openmpi/4.1.6
module load cue-login-env/1.0
#mpirun -np 20 SU2_CFD setup_FFD.cfg > log.CFD &
python3 RunOptimIP.py
