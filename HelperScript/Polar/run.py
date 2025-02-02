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
    
global_csv_path = "Polar_results.csv"  # Define global CSV file path
    
# Remove global_results.csv if it exists
if os.path.exists(global_csv_path):
    print(f"Removing existing '{global_csv_path}' file...")
    os.remove(global_csv_path)

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
        
    # Identify history.csv in WORKDIR
    history_file = os.path.join(work_dir, "history.csv")
    
    pitching_moment = get_moment(history_file)
    target_pitching_moment = 0.0
    
    print("Cmy: ", pitching_moment)
    
    if ((abs(pitching_moment)-target_pitching_moment) > 0.001):
        print("Aircraft not balanced!")
    #end
    
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