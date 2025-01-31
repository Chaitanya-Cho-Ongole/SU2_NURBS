import subprocess
import os
import shutil
import glob
import pandas as pd
import os

from postProcess import *


# Remove "Results" directory if it exists
results_dir = "Results"
if os.path.exists(results_dir):
    print(f"Removing existing '{results_dir}' directory...")
    shutil.rmtree(results_dir)

global_csv_path = "global_results.csv"  # Define global CSV file path

def modify_su2_config(input_file, output_file, TARGET_CL, MACH, restart=False):
    """ Modifies an SU2 configuration file by setting FIXED_CL_MODE to YES, TARGET_CL, and RESTART_SOL. """
    with open(input_file, "r") as file:
        lines = file.readlines()

    with open(output_file, "w") as file:
        for line in lines:
            stripped_line = line.strip()
            if not stripped_line or stripped_line.startswith("%"):
                file.write(line)
                continue

            if "=" in stripped_line:
                key, value = map(str.strip, stripped_line.split("=", 1))
                if key == "MACH_NUMBER":
                    line = f"{key}= {MACH}\n"
                elif key == "FIXED_CL_MODE":
                    line = f"{key}= YES\n"
                elif key == "TARGET_CL":
                    line = f"{key}= {TARGET_CL}\n"
                elif key == "RESTART_SOL":
                    line = f"{key}= {'YES' if restart else 'NO'}\n"  # First CL = NO, others = YES
                
            file.write(line)

    return output_file

def update_restart_config(input_file):
    """
    Updates RESTART_SOL=YES in the SU2 configuration file.
    """
    temp_file = input_file + ".tmp"
    with open(input_file, "r") as file, open(temp_file, "w") as temp:
        for line in file:
            stripped_line = line.strip()
            if not stripped_line or stripped_line.startswith("%"):
                temp.write(line)
                continue

            if "=" in stripped_line:
                key, value = map(str.strip, stripped_line.split("=", 1))
                if key == "RESTART_SOL":
                    line = f"{key}= YES\n"  # Enable restart for the next CL
                
            temp.write(line)

    os.replace(temp_file, input_file)  # Overwrite the original file
    print(f"Updated restart configuration in {input_file}")

def run_su2_simulation(num_cores, cfg_file, TARGET_CL, MACH, restart=False, next_cl_dir=None):
    """
    Runs SU2_CFD, logs results, and prepares the next CL case with RESTART_SOL=YES.
    """
    os.makedirs(results_dir, exist_ok=True)

    # Create Mach-specific directory
    mach_dir = os.path.join(results_dir, f"MACH_{MACH:.2f}".replace(".", "_"))
    os.makedirs(mach_dir, exist_ok=True)

    # Create CL-specific directory
    work_dir = os.path.join(mach_dir, f"CL_{TARGET_CL:.2f}".replace(".", "_"))
    os.makedirs(work_dir, exist_ok=True)

    log_file_path = os.path.join(work_dir, "simulation.log")

    # Copy config file
    cfg_dest = os.path.join(work_dir, os.path.basename(cfg_file))
    shutil.copy(cfg_file, cfg_dest)

    # Create symbolic links for .su2 files
    for su2_file in glob.glob("*.su2"):
        link_dest = os.path.join(work_dir, su2_file)
        if not os.path.exists(link_dest):
            os.symlink(os.path.abspath(su2_file), link_dest)
    
    # Modify configuration file
    modified_cfg = os.path.join(work_dir, "modified_" + os.path.basename(cfg_file))
    modify_su2_config(cfg_dest, modified_cfg, TARGET_CL, MACH, restart)

    # Run SU2_CFD with mpirun
    command = ["mpirun", "-np", str(num_cores), "SU2_CFD", os.path.basename(modified_cfg)]
    with open(log_file_path, "w") as log_file:
        process = subprocess.Popen(
            command, cwd=work_dir, stdout=log_file, stderr=log_file, text=True
        )
        process.wait()

    # Move solution.dat to the next CL directory if applicable
    solution_file = os.path.join(work_dir, "solution.dat")
    if next_cl_dir:
        os.makedirs(next_cl_dir, exist_ok=True)

        # Move solution.dat
        if os.path.exists(solution_file):
            print(f"Moving 'solution.dat' to {next_cl_dir}")
            shutil.move(solution_file, os.path.join(next_cl_dir, "solution.dat"))

        # Copy modified configuration file to the next CL directory
        next_cfg = os.path.join(next_cl_dir, "modified_" + os.path.basename(cfg_file))
        shutil.copy(modified_cfg, next_cfg)

        # Update RESTART_SOL=YES in the next CL directory before the next simulation
        update_restart_config(next_cfg)

    return log_file_path

# Example usage:
ncores = 8
cfg_file = "inv_ONERAM6.cfg"

# Define Mach and CL values for nested loops
MACH_VALUES = [0.75]  # Outer loop (Mach numbers)
CL_VALUES = [0.0, 0.1]  # Inner loop (CL values)

# Run simulations for all (MACH, CL) combinations
for i, MACH in enumerate(MACH_VALUES):
    for j, TARGET_CL in enumerate(CL_VALUES):
        print(f"Running SU2_CFD for Mach={MACH}, CL={TARGET_CL}...", end=" ", flush=True)

        next_cl_dir = None
        restart = j > 0  # Restart from the second CL onwards

        if j < len(CL_VALUES) - 1:
            next_cl_dir = os.path.join(
                "Results", f"MACH_{MACH:.2f}".replace(".", "_"), f"CL_{CL_VALUES[j+1]:.2f}".replace(".", "_")
            )

        log_path = run_su2_simulation(ncores, cfg_file, TARGET_CL, MACH, restart, next_cl_dir)
        print("Done!")
