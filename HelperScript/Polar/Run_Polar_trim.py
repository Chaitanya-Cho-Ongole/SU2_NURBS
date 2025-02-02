import subprocess
import os
import shutil
import glob
import pandas as pd
import numpy as np

#import run as rn


# Remove "Results" directory if it exists
results_dir = "Results"
if os.path.exists(results_dir):
    print(f"Removing existing '{results_dir}' directory...")
    shutil.rmtree(results_dir)
    
global_csv_path = "Polar_results.csv"  # Define global CSV file path
    
# Remove global_results.csv if it exists
if os.path.exists(global_csv_path):
    print(f"Removing existing '{global_csv_path}' file...")
    os.remove(global_csv_path)
    


def get_moment(history_file):
    """
    Reads the SU2-generated history.csv file, extracts the pitching moment value.
    """
    try:
        # Read the CSV file
        df = pd.read_csv(history_file)
        
        # Clean column names (strip spaces and remove quotes)
        df.columns = df.columns.str.strip().str.replace('"', '', regex=True)

        # Ensure required columns exist
        if "CMy" not in df.columns:
            print(f"Error: Missing pitching moment (CMy) in {history_file}")
            return None

        # Extract the last row value
        return df.iloc[-1]["CMy"]

    except Exception as e:
        print(f"Error processing {history_file}: {e}")
        return None

def process_su2_history(history_file, global_csv, mach_number):
    """
    Reads the SU2-generated history.csv file, extracts the last values of CD, CL, CMx, CMy, and CMz,
    and appends these values along with the corresponding Mach number to a global CSV file.
    """
    try:
        # Read the CSV file
        df = pd.read_csv(history_file)
        
        # Clean column names (strip spaces and remove quotes)
        df.columns = df.columns.str.strip().str.replace('"', '')

        # Ensure required columns exist
        required_columns = ["CD", "CL", "CMx", "CMy", "CMz"]
        if not all(col in df.columns for col in required_columns):
            print(f"Error: Missing required columns in {history_file}")
            return

        # Extract the last row values
        last_values = df.iloc[-1][required_columns].to_dict()
        last_values["Mach"] = mach_number  # Add Mach number

        # Convert dictionary to DataFrame
        result_df = pd.DataFrame([last_values])

        # Append to global CSV file, creating if necessary
        file_exists = os.path.isfile(global_csv)
        result_df.to_csv(global_csv, mode='a', header=not file_exists, index=False)

        print(f"Appended results from {history_file} to {global_csv}")
    
    except Exception as e:
        print(f"Error processing {history_file}: {e}")


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

def run_su2_simulation_trim(num_cores, cfg_file, TARGET_CL, MACH, restart=False, next_cl_dir=None, max_retries=3):
    """
    Runs SU2_CFD, logs results, and ensures the aircraft is balanced by re-running if necessary.
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

    attempt = 0
    target_pitching_moment = 0.0

    while attempt < max_retries:
        print(f"Running SU2_CFD (attempt {attempt + 1}/{max_retries})...")

        # Run SU2_CFD with mpirun
        command = ["mpirun", "-np", str(num_cores), "SU2_CFD", os.path.basename(modified_cfg)]
        with open(log_file_path, "w") as log_file:
            process = subprocess.Popen(command, cwd=work_dir, stdout=log_file, stderr=log_file, text=True)
            process.wait()
        
        # Identify history.csv in WORKDIR
        history_file = os.path.join(work_dir, "history.csv")

        if not os.path.exists(history_file):
            print(f"Error: {history_file} not found.")
            return log_file_path
        
        pitching_moment = get_moment(history_file)

        if pitching_moment is None:
            print("Error: Could not retrieve valid pitching moment. Stopping execution.")
            return log_file_path

        print(f"CMy = {pitching_moment}")

        if abs(pitching_moment - target_pitching_moment) <= 0.001:
            print("Aircraft is balanced.")
            break  # Exit the loop if balanced

        print("Aircraft not balanced! Re-running SU2_CFD...")
        attempt += 1

    if attempt == max_retries:
        print(f"Warning: Aircraft not balanced after {max_retries} attempts.")

    # Extract aerodynamic coefficients from history.csv
    process_su2_history(history_file, global_csv_path, MACH)

    # Move solution.dat to the next CL directory if applicable
    solution_file = os.path.join(work_dir, "solution.dat")
    flow_meta_file = os.path.join(work_dir, "flow.meta")
    
    if next_cl_dir:
        os.makedirs(next_cl_dir, exist_ok=True)

        # Move solution.dat
        if os.path.exists(solution_file):
            print(f"Moving 'solution.dat' to {next_cl_dir}")
            shutil.move(solution_file, os.path.join(next_cl_dir, "solution.dat"))

        # Move flow.meta
        if os.path.exists(flow_meta_file):
            print(f"Moving 'flow.meta' to {next_cl_dir}")
            shutil.move(flow_meta_file, os.path.join(next_cl_dir, "flow.meta"))
            
        # Copy modified configuration file to the next CL directory
        next_cfg = os.path.join(next_cl_dir, "modified_" + os.path.basename(cfg_file))
        shutil.copy(modified_cfg, next_cfg)

        # Update RESTART_SOL=YES in the next CL directory before the next simulation
        update_restart_config(next_cfg)

    return log_file_path


# Example usage:
ncores = 6
cfg_file = "inv_ONERAM6.cfg"

# Define Mach and CL values for nested loops
#MACH_VALUES = [0.60, 0.65, 0.70]  # Outer loop (Mach numbers)
#CL_VALUES = [0.0, 0.1, 0.2, 0.3]  # Inner loop (CL values)

MACH_VALUES = np.arange(0.50, 0.85 + 0.01, 0.1)  # Mach from 0.50 to 0.85 in steps of 0.1
CL_VALUES = np.arange(0.0, 0.7 + 0.01, 0.01)  # CL from 0.0 to 0.7 in steps of 0.01

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

        log_path = run_su2_simulation_trim(ncores, cfg_file, TARGET_CL, MACH, restart, next_cl_dir)
        print("Done!")
