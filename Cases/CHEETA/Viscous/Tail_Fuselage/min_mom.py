# Dummy script for FADO_DEV

from FADO import *
import subprocess
import numpy as np
import csv
import os
import glob
import shutil
import pandas as pd
import ipyopt
from numpy import ones, array, zeros

# Design Variables-----#
nDV = 4
x0 = np.zeros((nDV,))

# Define InputVariable class object: ffd
ffd = InputVariable(0.0, PreStringHandler("DV_VALUE="), nDV)
ffd = InputVariable(x0,ArrayLabelReplacer("__FFD_PTS__"), 0, np.ones(nDV), -1.0,1.0)

# Replace %__DIRECT__% with an empty string when using enable_direct
enable_direct = Parameter([""], LabelReplacer("%__DIRECT__"))

# Replace %__ADJOINT__% with an empty string when using enable_adjoint
enable_adjoint = Parameter([""], LabelReplacer("%__ADJOINT__"))


#enable_not_def = Parameter([""], LabelReplacer("%__NOT_DEF__"))
#enable_def = Parameter([""], LabelReplacer("%__DEF__"))

# Replace *_def.cfg with *_FFD.cfg as required
mesh_in = Parameter(["MESH_FILENAME= CHEETA_TURB_M00_FFD.su2"],\
       LabelReplacer("MESH_FILENAME= CHEETA_TURB_M00_FFD_def.su2"))

# Replace "OBJ_FUNC= SOME NAME" with "OBJ_FUNC= DRAG"
func_drag = Parameter(["OBJECTIVE_FUNCTION= DRAG"],\
         LabelReplacer("OBJECTIVE_FUNCTION= TOPOL_COMPLIANCE"))

# Replace "OBJ_FUNC= SOME NAME" with "OBJ_FUNC= MOMENT_Z"
func_mom = Parameter(["OBJECTIVE_FUNCTION= MOMENT_Y"],\
         LabelReplacer("OBJECTIVE_FUNCTION= TOPOL_COMPLIANCE"))

# EVALUATIONS---------------------------------------#

#Number of of available cores
ncores = "256"

# Master cfg file used for DIRECT  calculations
configMaster="turb_CHEETA_FADO.cfg"

directMaster="DIRECT.cfg"


# Master cfg file used for Drag Adjint calculations
momentAdjointMaster="MOMENT_ADJOINT.cfg"

tailPerturb_Master="CHEETA_TAIL_PERTURB.cfg"



# Input mesh to perform deformation
meshName="CHEETA_TURB_M00_FFD.su2"

# Mesh deformation
def_command = "mpirun -n " + ncores + " SU2_DEF " + configMaster


# Forward analysis
cfd_command = "mpirun -n " + ncores + " SU2_CFD " + directMaster


# moment adjoint analysis -> AD + projection
moment_adjoint_command = "mpirun -n " + ncores + " SU2_CFD_AD " + momentAdjointMaster + " && mpirun -n " + ncores + " SU2_DOT_AD " + tailPerturb_Master

# Define the sequential steps for shape-optimization
max_tries = 1

# MESH DEFORMATON------------------------------------------------------#
deform = ExternalRun("DEFORM",def_command,True)
deform.setMaxTries(max_tries)
deform.addConfig(configMaster)
deform.addData("CHEETA_TURB_M00_FFD.su2")
deform.addExpected("CHEETA_TURB_M00_FFD_def.su2")
deform.addParameter(enable_direct)
deform.addParameter(mesh_in)
#deform.addParameter(enable_def)

# FORWARD ANALYSIS---------------------------------------------------#
direct = ExternalRun("DIRECT",cfd_command,True)
direct.setMaxTries(max_tries)
direct.addConfig(directMaster)
direct.addData("DEFORM/CHEETA_TURB_M00_FFD_def.su2")
direct.addExpected("solution.dat")
direct.addParameter(enable_direct)


# MOMENT ADJOINT ANALYSIS---------------------------------------------------#
def make_mom_AdjRun(name, func=None) :
    adj = ExternalRun(name,moment_adjoint_command,True)
    adj.setMaxTries(max_tries)
    adj.addConfig(momentAdjointMaster)
    adj.addConfig(tailPerturb_Master)
    adj.addData("DEFORM/CHEETA_TURB_M00_FFD_def.su2")
    adj.addData("DIRECT/solution.dat")
    adj.addData("DIRECT/flow.meta")
    adj.addExpected("of_grad.dat",parse_and_modify=False)
    adj.addParameter(enable_adjoint)
    if (func is not None) : adj.addParameter(func)
    return adj

# Moment adjoint
mom_adj = make_mom_AdjRun("MOM_ADJ",func_mom)

# FUNCTIONS ------------------------------------------------------------ #
mom = Function("mom","DIRECT/history.csv",LabeledTableReader('"CMy"'))
mom.addInputVariable(ffd,"MOM_ADJ/of_grad.dat",TableReader(None,0,(1,0),delim="",zero_except_last=True))
#reader = DataReader(row=total_rows-1, col=0, start=(total_rows-1, 0), end=(total_rows, None))
mom.addValueEvalStep(deform)
mom.addValueEvalStep(direct)
mom.addGradientEvalStep(mom_adj)
mom.setDefaultValue(-1.0)


# SCALING PARAMETERS ------------------------------------------------------------ #
GlobalScale = 1
ConScale = 1
FtolCr = 1E-12
Ftol = FtolCr * GlobalScale
OptIter = 1


# DRIVER IPOPT-------------------------------------------------------#
driver = IpoptDriver()


 # Objective function
driver.addObjective("min", mom, GlobalScale)


driver.setWorkingDirectory("WORKDIR")
driver.setEvaluationMode(False,2.0)

driver.setStorageMode(True,"DSN_")
driver.setFailureMode("HARD")

# DRIVERL IPOPT-------------------------------------------------------#
nlp = driver.getNLP()

# Optimization
x0 = driver.getInitial()

# Warm start parameters
ncon = 0
lbMult = np.zeros(nDV)
ubMult= np.zeros(nDV)
conMult = np.zeros(ncon)

print("Initial Design Variable vector:")
print(x0)


# NLP settings
nlp.set(warm_start_init_point = "no",
            nlp_scaling_method = "none",    # we are already doing some scaling
            accept_every_trial_step = "yes", # can be used to force single ls per iteration
            limited_memory_max_history = 15,# the "L" in L-BFGS
            max_iter = OptIter,
            tol = Ftol,                     # this and max_iter are the main stopping criteria
            acceptable_iter = OptIter,
            acceptable_tol = Ftol,
            acceptable_obj_change_tol=1e-12, # Cauchy-type convergence over "acceptable_iter"
            dual_inf_tol=1e-07,             # Tolerance for optimality criteria
            mu_min = 1e-8,                  # for very low values (e-10) the problem "flip-flops"
            recalc_y_feas_tol = 0.1,
            output_file = 'ipopt_output.txt')        # helps converging the dual problem with L-BFGS

x, obj, status = nlp.solve(x0, mult_g = conMult, mult_x_L = lbMult, mult_x_U = ubMult)

# Print the optimized results---->

print("Primal variables solution")
print("x: ", x)

print("Bound multipliers solution: Lower bound")
print("lbMult: ", lbMult)

print("Bound multipliers solution: Upper bound")
print("ubMult: ", ubMult)


print("Constraint multipliers solution")
print("lambda:",conMult)