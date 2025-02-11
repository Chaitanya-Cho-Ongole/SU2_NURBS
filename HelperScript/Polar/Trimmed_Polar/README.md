# SU2 CFD Trimmed Polar Sweep Automation

This script automates the execution of SU2 CFD simulations across multiple Mach numbers and lift coefficient (CL) values, ensuring trimmed flight by dynamically adjusting the tail rotation. It manages configuration updates, simulation execution, and result organization efficiently.

## Features
- Iterates through a range of Mach numbers and CL values.
- Dynamically modifies SU2 configuration files for each case.
- Adjusts tail rotation to ensure balanced flight.
- Organizes results into structured directories.
- Supports restart functionality for sequential CL cases.
- Executes SU2_CFD in parallel using `mpirun`.

## Dependencies
Ensure you have the following installed:
- **Python 3**
- **SU2 CFD** (https://su2code.github.io/)
- **MPI (mpirun)**
- Required Python packages:
  ```bash
  pip install pandas numpy
  ```

## Directory Structure
After execution, results are stored as follows:
```
Results/
├── MACH_0_60/
│   ├── CL_0_00/
│   │   ├── simulation.log
│   │   ├── history.csv
│   │   ├── solution.dat
│   │   ├── flow.meta
│   ├── CL_0_05/
│   ├── ...
│
├── MACH_0_65/
│   ├── CL_0_00/
│   ├── ...
```

## Usage
Run the script with:
```bash
python script.py
```

### Configuration Parameters
Modify the following parameters in the script:
```python
ncores_1 = 12  # Number of CPU cores for SU2_DEF
ncores_2 = 96  # Number of CPU cores for SU2_CFD
cfg_cfd = "Euler_CRM_FBT.cfg"  # SU2 CFD configuration file
cfg_def = "deform_Euler_CRM_FBT.cfg"  # SU2 deformation configuration file
mesh_name = "CRM_WBT_Euler_FFD"  # Mesh file name
dcm_dgamma = -0.0406  # Tail control derivative
```

## How It Works
1. **Iteration:** Loops through defined Mach and CL ranges.
2. **Tail Trim Adjustment:** Adjusts tail rotation to ensure balanced flight.
3. **Directory Management:** Creates structured output directories.
4. **Configuration Update:** Modifies SU2 input files dynamically.
5. **Execution:** Runs SU2_DEF for mesh deformation and SU2_CFD for simulations using `mpirun`.
6. **Result Processing:** Stores simulation logs and history files.

## Example Output
Sample console output:
```
Running SU2_CFD for Mach=0.60, CL=0.00 ... Done!
Running SU2_CFD for Mach=0.60, CL=0.05 ... Adjusting tail ... Done!
...
```

## Troubleshooting
- Ensure SU2 is installed and accessible in your system’s `PATH`.
- If `mpirun` is not recognized, check MPI installation.
- Missing history files may indicate failed simulations—check `simulation.log`.

## License
MIT License. Contributions welcome!
