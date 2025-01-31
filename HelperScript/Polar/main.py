import subprocess
import os
import shutil
import glob

def run_su2_simulation(num_cores, cfg_file, TARGET_CL, MACH):
    """
    Runs SU2_CFD with the specified number of cores and configuration file in a new directory.
    Logs output to a file instead of printing to screen.

    Parameters:
    num_cores (int): Number of processor cores to use.
    cfg_file (str): Name of the configuration file.
    TARGET_CL (float): Target CL to append to configuration file
    MACH (float): Cruise Mach number
    
    Returns:
    str: The path to the log file.
    """
    work_dir = f"MACH_{MACH}_CL_{TARGET_CL}"
    log_file_path = os.path.join(work_dir, "simulation.log")

    # Create the directory if it doesn't exist
    os.makedirs(work_dir, exist_ok=True)

    # Copy the config file into the directory
    cfg_dest = os.path.join(work_dir, os.path.basename(cfg_file))
    shutil.copy(cfg_file, cfg_dest)

    # Create symbolic links for .su2 files in the directory
    for su2_file in glob.glob("*.su2"):
        link_dest = os.path.join(work_dir, su2_file)
        if not os.path.exists(link_dest):  # Avoid overwriting existing symlinks
            os.symlink(os.path.abspath(su2_file), link_dest)
    
    # Modify the copied config file inside alfa_0
    modified_cfg = os.path.join(work_dir, "modified_" + os.path.basename(cfg_file))
    modify_su2_config(cfg_dest, modified_cfg, TARGET_CL, MACH)

    # Change directory to alfa_0 and run the command with logging
    command = ["mpirun", "-np", str(num_cores), "SU2_CFD", os.path.basename(modified_cfg)]

    with open(log_file_path, "w") as log_file:
        process = subprocess.Popen(
            command, cwd=work_dir, stdout=log_file, stderr=log_file, text=True
        )
        process.wait()  # Wait for the process to complete

    return log_file_path  # Return the path to the log file


# Define the function to modify the SU2 configuration file
def modify_su2_config(input_file, output_file, TARGET_CL, MACH):
    """
    Modifies an SU2 configuration file by setting FIXED_CL_MODE to YES 
    and TARGET_CL to the given value.

    Parameters:
        input_file (str): Path to the original SU2 configuration file.
        output_file (str): Path to save the modified configuration file.
        target_cl_value (float): The value to set for TARGET_CL.
        Mach (float): The value to set for MACH_NUMBER.

    Returns:
        str: Path to the modified configuration file.
    """
    # Read the file content
    with open(input_file, "r") as file:
        lines = file.readlines()

    # Modify the required parameters
    with open(output_file, "w") as file:
        for line in lines:
            stripped_line = line.strip()

            # Ignore comments and empty lines
            if not stripped_line or stripped_line.startswith("%"):
                file.write(line)  # Preserve comments and empty lines
                continue

            # Split key-value pairs on '='
            if "=" in stripped_line:
                key, value = map(str.strip, stripped_line.split("=", 1))

                # Modify MACH_NUMBER, FIXED_CL_MODE and TARGET_CL
                if key == "MACH_NUMBER":
                    line = f"{key}= {MACH}\n"
                    
                elif key == "FIXED_CL_MODE":
                    line = f"{key}= YES\n"
                    
                elif key == "TARGET_CL":
                    line = f"{key}= {TARGET_CL}\n"
                
            file.write(line)  # Write modified or original line

    return output_file


# Example usage:
ncores = 4
cfg_file = "Euler_CRM_FBT.cfg"

# Flow conditions
TARGET_CL = 0.0
MACH = 0.80

log_path = run_su2_simulation(ncores, cfg_file, TARGET_CL, MACH)

print(f"Simulation running. Monitor logs with: tail -f {log_path}")
