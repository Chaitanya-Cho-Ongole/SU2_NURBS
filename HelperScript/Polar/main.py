import subprocess
import os
import shutil
import glob

# Remove "Results" directory if it exists
results_dir = "Results"
if os.path.exists(results_dir):
    print(f"Removing existing '{results_dir}' directory...")
    shutil.rmtree(results_dir)

def run_su2_simulation(num_cores, cfg_file, TARGET_CL, MACH, next_cl_dir=None):
    """
    Runs SU2_CFD with the specified number of cores and configuration file in a structured directory.
    Logs output to a file instead of printing to screen. Moves 'solution.dat' to the next CL directory.

    Parameters:
    num_cores (int): Number of processor cores to use.
    cfg_file (str): Name of the configuration file.
    TARGET_CL (float): Target CL to append to configuration file.
    MACH (float): Cruise Mach number.
    next_cl_dir (str, optional): Directory for the next CL where 'solution.dat' will be moved.

    Returns:
    str: The path to the log file.
    """
    # Create Results directory
    os.makedirs(results_dir, exist_ok=True)

    # Create the Mach-specific subdirectory
    mach_dir = os.path.join(results_dir, f"MACH_{MACH:.2f}".replace(".", "_"))
    os.makedirs(mach_dir, exist_ok=True)

    # Create the CL-specific subdirectory inside Mach
    work_dir = os.path.join(mach_dir, f"CL_{TARGET_CL:.2f}".replace(".", "_"))
    log_file_path = os.path.join(work_dir, "simulation.log")
    os.makedirs(work_dir, exist_ok=True)

    # Copy the config file into the directory
    cfg_dest = os.path.join(work_dir, os.path.basename(cfg_file))
    shutil.copy(cfg_file, cfg_dest)

    # Create symbolic links for .su2 files in the directory
    for su2_file in glob.glob("*.su2"):
        link_dest = os.path.join(work_dir, su2_file)
        if not os.path.exists(link_dest):
            os.symlink(os.path.abspath(su2_file), link_dest)
    
    # Modify the copied config file inside work_dir
    modified_cfg = os.path.join(work_dir, "modified_" + os.path.basename(cfg_file))
    modify_su2_config(cfg_dest, modified_cfg, TARGET_CL, MACH)

    # Change directory to work_dir and run the command with logging
    command = ["mpirun", "-np", str(num_cores), "SU2_CFD", os.path.basename(modified_cfg)]

    with open(log_file_path, "w") as log_file:
        process = subprocess.Popen(
            command, cwd=work_dir, stdout=log_file, stderr=log_file, text=True
        )
        process.wait()  # Wait for the process to complete
    
    update_restart_config(modified_cfg, modified_cfg)

    # Move solution.dat to the next CL directory if applicable
    solution_file = os.path.join(work_dir, "solution.dat")
    if next_cl_dir:
        os.makedirs(next_cl_dir, exist_ok=True)  # Ensure the next CL directory exists
        if os.path.exists(solution_file):
            print(f"Moving 'solution.dat' to {next_cl_dir}")
            shutil.move(solution_file, os.path.join(next_cl_dir, "solution.dat"))

    return log_file_path  # Return the path to the log file


# Define the function to modify the SU2 configuration file
def modify_su2_config(input_file, output_file, TARGET_CL, MACH):
    """
    Modifies an SU2 configuration file by setting FIXED_CL_MODE to YES 
    and TARGET_CL to the given value.

    Parameters:
        input_file (str): Path to the original SU2 configuration file.
        output_file (str): Path to save the modified configuration file.
        TARGET_CL (float): The value to set for TARGET_CL.
        MACH (float): The value to set for MACH_NUMBER.

    Returns:
        str: Path to the modified configuration file.
    """
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
                    line = f"{key}= NO\n"
                
            file.write(line)

    return output_file

def update_restart_config(input_file, output_file):
    """
    Sets the RESTART_SOL to YES

    Parameters:
        input_file (str): Path to the original SU2 configuration file.
        Overwrite this file to prevent multiple .cfg files

    Returns:
        str: Path to the modified configuration file.
    """
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
                if key == "RESTART_SOL":
                    line = f"{key}= YES\n"
                
            file.write(line)

    return output_file


# Example usage:
ncores = 4
cfg_file = "Euler_CRM_FBT.cfg"

# Define Mach and CL values for nested loops
MACH_VALUES = [0.75]  # Outer loop (Mach numbers)
CL_VALUES = [0.0, 0.1, 0.2]  # Inner loop (CL values)

# Run simulations for all (MACH, CL) combinations
for MACH in MACH_VALUES:
    for i, TARGET_CL in enumerate(CL_VALUES):
        print(f"Running SU2_CFD for Mach={MACH}, CL={TARGET_CL}...", end=" ", flush=True)

        # Determine next CL directory (except for the last CL value)
        next_cl_dir = None
        if i < len(CL_VALUES) - 1:
            next_cl_dir = os.path.join(
                "Results", f"MACH_{MACH:.2f}".replace(".", "_"), f"CL_{CL_VALUES[i+1]:.2f}".replace(".", "_")
            )

        log_path = run_su2_simulation(ncores, cfg_file, TARGET_CL, MACH, next_cl_dir)
        print("Done!")
