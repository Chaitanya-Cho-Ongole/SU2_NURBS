# SU2 Polar Sweep Automation

This script automates the execution of SU2 CFD simulations for different Mach numbers and lift coefficient (CL) values, processes the history files, and organizes results efficiently.

## Features
- Runs SU2 CFD simulations for a range of Mach numbers and CL values.
- Modifies SU2 configuration files to enable `FIXED_CL_MODE` and adjust `TARGET_CL`.
- Extracts and stores aerodynamic coefficients (CD, CL, CMx, CMy, CMz) for each simulation.
- Organizes results in a structured directory format.
- Supports restart functionality for sequential CL cases.
- Uses `mpirun` for parallel execution.

## Dependencies
Ensure you have the following installed:
- **Python 3**
- **SU2 CFD** (https://su2code.github.io/)
- **MPI (mpirun)**
- Python packages:
  ```bash
  pip install pandas numpy
  ```

## Directory Structure
After running the script, the results are stored in:
```
Results/
├── MACH_0_50/
│   ├── CL_0_00/
│   │   ├── simulation.log
│   │   ├── history.csv
│   │   ├── solution.dat
│   │   ├── flow.meta
│   │   ├── modified_inv_ONERAM6.cfg
│   ├── CL_0_05/
│   ├── ...
│
├── MACH_0_55/
│   ├── CL_0_00/
│   ├── ...
```
The script also generates a global results CSV file:
```
Polar_results.csv
```
This file contains aggregated results for all Mach and CL cases.

## Usage
### Running the script
Run the script with:
```bash
python script.py
```

### Configuration Parameters
Modify the following parameters inside the script as needed:
```python
ncores = 4  # Number of CPU cores for SU2_CFD
cfg_file = "inv_ONERAM6.cfg"  # SU2 configuration file
mach_step = 0.05  # Mach step size
cl_step = 0.05  # CL step size
```

## How It Works
1. **Setup:** Removes previous results (`Results/` directory) and global CSV (`Polar_results.csv`).
2. **Configuration Update:** Modifies the SU2 config file to set `FIXED_CL_MODE=YES` and updates `MACH_NUMBER` and `TARGET_CL` values.
3. **Execution:** Runs `SU2_CFD` using `mpirun` in a structured results directory.
4. **History Processing:** Extracts final values of CD, CL, CMx, CMy, and CMz from `history.csv` and appends them to `Polar_results.csv`.
5. **Restart Handling:** Ensures restart functionality for consecutive CL values.

## Example Output
A sample `Polar_results.csv` entry:
```
CD,CL,CMx,CMy,CMz,AoA,Mach
0.0275,0.50,0.0001,0.002,-0.001,2.5,0.70
```

## Troubleshooting
- Ensure SU2 is installed and accessible in your system's `PATH`.
- If `mpirun` is not recognized, check your MPI installation.
- Missing history files may indicate failed simulations—check `simulation.log`.

## License
MIT License. Contributions welcome!
