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
nDV = 80
x0 = np.zeros((nDV,))

# Define InputVariable class object: ffd
ffd = InputVariable(0.0, PreStringHandler("DV_VALUE="), nDV)
ffd = InputVariable(x0,ArrayLabelReplacer("__FFD_PTS__"), 0, np.ones(nDV), -0.11,0.11)

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

# Replace "OBJ_FUNC= SOME NAME" with "OBJ_FUNC= MOMENT_Y"
func_mom = Parameter(["OBJECTIVE_FUNCTION= MOMENT_Y"],\
         LabelReplacer("OBJECTIVE_FUNCTION= TOPOL_COMPLIANCE"))

# EVALUATIONS---------------------------------------#

#Number of of available cores
ncores = "96"
ncores2 = '48'

# Master cfg file used for DIRECT and ADJOINT calculations
configMaster="turb_CHEETA_FADO.cfg"

deformMaster="deform.cfg"

# cfg file used for FUSELAGE GEOMETRY calculations
geoMasterFuse = "CHEETA_Fuse_geo.cfg"

# Input mesh to perform deformation
meshName="CHEETA_TURB_M00_FFD.su2"

# Mesh deformation
def_command = "mpirun -n " + ncores + " SU2_DEF " + deformMaster

# Geometry evaluation
geo_commandFuse ="mpirun -n " + ncores2 + " --mca sharedfp sm SU2_GEO " + geoMasterFuse

# Forward analysis
cfd_command = "mpirun -n " + ncores + " --mca sharedfp sm SU2_CFD " + configMaster

# Adjoint analysis -> AD + projection
adjoint_command = "mpirun -n " + ncores + " --mca sharedfp sm SU2_CFD_AD " + configMaster + " && mpirun -n " + ncores + " --mca sharedfp sm SU2_DOT_AD " + geoMasterFuse

# Define the sequential steps for shape-optimization
max_tries = 1

# MESH DEFORMATON------------------------------------------------------#
deform = ExternalRun("DEFORM",def_command,True)
deform.setMaxTries(max_tries)
deform.addConfig(deformMaster)
deform.addData("CHEETA_TURB_M00_FFD.su2")
deform.addExpected("CHEETA_TURB_M00_FFD_def.su2")
deform.addParameter(enable_direct)
deform.addParameter(mesh_in)
#deform.addParameter(enable_def)

# GEOMETRY EVALUATION FUSELAGE-----------------------------------------#
geometryF = ExternalRun("GEOMETRY_FUSE",geo_commandFuse,True)
geometryF.setMaxTries(max_tries)
geometryF.addConfig(geoMasterFuse)
geometryF.addConfig(configMaster)
geometryF.addData("DEFORM/CHEETA_TURB_M00_FFD_def.su2")
geometryF.addExpected("of_func.csv")
geometryF.addExpected("of_grad.csv")

# FORWARD ANALYSIS---------------------------------------------------#
direct = ExternalRun("DIRECT",cfd_command,True)
direct.setMaxTries(max_tries)
direct.addConfig(configMaster)
direct.addData("DEFORM/CHEETA_TURB_M00_FFD_def.su2")
direct.addExpected("solution.dat")
direct.addParameter(enable_direct)


# ADJOINT ANALYSIS---------------------------------------------------#
def makeAdjRun(name, func=None) :
    adj = ExternalRun(name,adjoint_command,True)
    adj.setMaxTries(max_tries)
    adj.addConfig(configMaster)
    adj.addConfig(geoMasterFuse)
    adj.addData("DEFORM/CHEETA_TURB_M00_FFD_def.su2")
    adj.addData("DIRECT/solution.dat")
    adj.addData("DIRECT/flow.meta")
    adj.addExpected("of_grad.dat")
    adj.addParameter(enable_adjoint)
    if (func is not None) : adj.addParameter(func)
    return adj

# Drag adjoint
drag_adj = makeAdjRun("DRAG_ADJ",func_drag)

# Moment adjoint
mom_adj = makeAdjRun("MOM_ADJ",func_mom)

# FUNCTIONS ------------------------------------------------------------ #
drag = Function("drag","DIRECT/history.csv",LabeledTableReader('"CD"'))
drag.addInputVariable(ffd,"DRAG_ADJ/of_grad.dat",TableReader(None,0,(1,0),delim="",zero_except_last=False, zero_last=True))
drag.addValueEvalStep(deform)
drag.addValueEvalStep(direct)
drag.addGradientEvalStep(drag_adj)
drag.setDefaultValue(1.0)

mom = Function("mom","DIRECT/history.csv",LabeledTableReader('"CMy"'))
mom.addInputVariable(ffd,"MOM_ADJ/of_grad.dat",TableReader(None,0,(1,0),delim="",zero_except_last=False, zero_last=True))
mom.addValueEvalStep(deform)
mom.addValueEvalStep(direct)
mom.addGradientEvalStep(mom_adj)
mom.setDefaultValue(-1.0)

FuseVol = Function("FuseVol","GEOMETRY_FUSE/of_func.csv",LabeledTableReader('"FUSELAGE_VOLUME"'))
FuseVol.addInputVariable(ffd,"GEOMETRY_FUSE/of_grad.csv",LabeledTableReader('"FUSELAGE_VOLUME"',',',(0,None),set_theta_zero=True))
FuseVol.addValueEvalStep(deform)
FuseVol.addValueEvalStep(geometryF)
FuseVol.setDefaultValue(0.0)

# SCALING PARAMETERS ------------------------------------------------------------ #
GlobalScale = 1
ConScale = 1
FtolCr = 1E-6
Ftol = FtolCr * GlobalScale
OptIter = 100

# FUSELAGE AND WING VOLUME SCALING PARAMETERS (MKIII)
BSL_FUSE_VOL = 401.296
FACTOR_FV = 0.99
TRG_FUSE_VOL = BSL_FUSE_VOL * FACTOR_FV


# DRIVER IPOPT-------------------------------------------------------#
driver = IpoptDriver()


 # Objective function
driver.addObjective("min", drag, 1)


# Wing pitching moment constraint
#driver.addLowerBound(mom, -0.006543, GlobalScale , ConScale)

# Fuselage volume constraint
driver.addLowerBound(FuseVol, TRG_FUSE_VOL, GlobalScale)

# Wing volume constraint
#driver.addLowerBound(WingVol, TRG_WING_VOL, GlobalScale)


driver.setWorkingDirectory("WORKDIR")
driver.setEvaluationMode(False,2.0)

driver.setStorageMode(True,"DSN_")
driver.setFailureMode("HARD")

# DRIVERL IPOPT-------------------------------------------------------#
nlp = driver.getNLP()

# Optimization
x0 = driver.getInitial()

# Warm start parameters
ncon = 1
lbMult = np.zeros(nDV)
ubMult= np.zeros(nDV)
conMult = np.zeros(ncon)

print("Initial Design Variable vector:")
print(x0)

# WARM START PARAMETERS
#x0 = array([])

#ubMult = array([])

#lbMult = array([])

#conMult = array([])


# NLP settings
nlp.set(warm_start_init_point = "no",
        nlp_scaling_method = "gradient-based",
        nlp_scaling_max_gradient = 1.0, # we are already doing some scaling
        accept_every_trial_step = "no", # can be used to force single ls per iteration
        limited_memory_max_history = 20,# the "L" in L-BFGS
        max_iter = OptIter,
        tol = Ftol,
        mu_strategy = "adaptive",
        mu_oracle = "quality-function",
        mu_min = 1e-9,
        adaptive_mu_globalization="obj-constr-filter",
        sigma_max = 100.0,
        sigma_min = 1e-06,# this and max_iter are the main stopping criteria
        acceptable_iter = OptIter,
        acceptable_tol = Ftol,
        acceptable_obj_change_tol=1e-12, # Cauchy-type convergence over "acceptable_iter"
        dual_inf_tol=1e-07,             # Tolerance for optimality criteria
        output_file = 'ipopt_output.txt')      # helps converging the dual problem with L-BFGS

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
