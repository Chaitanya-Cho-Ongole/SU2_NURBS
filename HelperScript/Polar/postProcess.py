import subprocess
import os
import shutil
import glob
import pandas as pd
import os


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