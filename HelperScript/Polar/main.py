import subprocess
import os
import shutil
import glob
import pandas as pd

# Remove "Results" directory if it exists
results_dir = "Results"
if os.path.exists(results_dir):
    print(f"Removing existing '{results_dir}' directory...")
    shutil.rmtree(results_dir)

global_csv_path = "global_results.csv"  # Define global CSV file path

def modify_su2_config(input_file, output_file, TARGET_CL, MACH):
    """ Modifies an SU2 configuration file by setting FIXED_CL_MODE to YES and TARGET_CL. """
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
                
            file.write(line)

    return output_file

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


def run_su2_simulation(num_cores, cfg_file, TARGET_CL, MACH, global_csv):
    """
    Runs SU2_CFD with the specified number of cores and configuration file in a structured directory.
    Logs output to a file instead of printing to screen. Moves 'solution.dat' to the next CL directory.
    Extracts data from history.csv and appends to a global results CSV.
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
    
    # Process and log results from history.csv
    history_file = os.path.join(work_dir, "history.csv")
    if os.path.exists(history_file):
        process_su2_history(history_file, global_csv, MACH)

    return log_file_path  # Return the path to the log file

# Example usage:
ncores = 8
cfg_file = "inv_ONERAM6.cfg"

# Define Mach and CL values for nested loops
MACH_VALUES = [0.75]  # Outer loop (Mach numbers)
CL_VALUES = [0.0, 0.1]  # Inner loop (CL values)

# Run simulations for all (MACH, CL) combinations
for MACH in MACH_VALUES:
    for TARGET_CL in CL_VALUES:
        print(f"Running SU2_CFD for Mach={MACH}, CL={TARGET_CL}...", end=" ", flush=True)
        log_path = run_su2_simulation(ncores, cfg_file, TARGET_CL, MACH, global_csv_path)
        print("Done!")
