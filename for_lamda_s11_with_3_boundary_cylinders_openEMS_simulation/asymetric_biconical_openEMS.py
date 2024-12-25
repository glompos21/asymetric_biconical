# OpenEMS FDTD Analysis Automation Script
#
# To be run with python.
# FreeCAD to OpenEMS plugin by Lubomir Jagos, 
# see https://github.com/LubomirJagos/FreeCAD-OpenEMS-Export
#
# This file has been automatically generated. Manual changes may be overwritten.
#
### Import Libraries
import math
import numpy as np
import os, tempfile, shutil
from pylab import *
import csv
import CSXCAD
from openEMS import openEMS
from openEMS.physical_constants import *

#
# FUNCTION TO CONVERT CARTESIAN TO CYLINDRICAL COORDINATES
#     returns coordinates in order [theta, r, z]
#
def cart2pol(pointCoords):
	theta = np.arctan2(pointCoords[1], pointCoords[0])
	r = np.sqrt(pointCoords[0] ** 2 + pointCoords[1] ** 2)
	z = pointCoords[2]
	return theta, r, z

#
# FUNCTION TO GIVE RANGE WITH ENDPOINT INCLUDED arangeWithEndpoint(0,10,2.5) = [0, 2.5, 5, 7.5, 10]
#     returns coordinates in order [theta, r, z]
#
def arangeWithEndpoint(start, stop, step=1, endpoint=True):
	if start == stop:
		return [start]

	arr = np.arange(start, stop, step)
	if endpoint and arr[-1] + step == stop:
		arr = np.concatenate([arr, [stop]])
	return arr

# Change current path to script file folder
#
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)
## constants
unit    = 0.001 # Model coordinates and lengths will be specified in mm.
fc_unit = 0.001 # STL files are exported in FreeCAD standard units (mm).

## switches & options
draw_3d_pattern = 0  # this may take a while...
use_pml = 0          # use pml boundaries instead of mur

currDir = os.getcwd()
print(currDir)

# setup_only : dry run to view geometry, validate settings, no FDTD computations
# debug_pec  : generated PEC skeleton (use ParaView to inspect)
debug_pec = False
setup_only = False

## prepare simulation folder
Sim_Path = os.path.join(currDir, 'simulation_output')
Sim_CSX = 'asymetric_biconical.xml'
if os.path.exists(Sim_Path):
	shutil.rmtree(Sim_Path)   # clear previous directory
	os.mkdir(Sim_Path)    # create empty simulation folder

## setup FDTD parameter & excitation function
max_timesteps = 10000
min_decrement = 0.0001 # 10*log10(min_decrement) dB  (i.e. 1E-5 means -50 dB)
CSX = CSXCAD.ContinuousStructure()
FDTD = openEMS(NrTS=max_timesteps, EndCriteria=min_decrement)
FDTD.SetCSX(CSX)

#######################################################################################################################################
# BOUNDARY CONDITIONS
#######################################################################################################################################
BC = ["MUR","MUR","MUR","MUR","PML_8","PML_8"]
FDTD.SetBoundaryCond(BC)

#######################################################################################################################################
# COORDINATE SYSTEM
#######################################################################################################################################
def mesh():
	x,y,z

mesh.x = np.array([]) # mesh variable initialization (Note: x y z implies type Cartesian).
mesh.y = np.array([])
mesh.z = np.array([])

openEMS_grid = CSX.GetGrid()
openEMS_grid.SetDeltaUnit(unit) # First call with empty mesh to set deltaUnit attribute.

#######################################################################################################################################
# EXCITATION ext_gaussian
#######################################################################################################################################
f0 = 1.5*1000000000.0
fc = 0.5*1000000000.0
FDTD.SetGaussExcite(f0, fc)
max_res = C0 / (f0 + fc) / 20

#######################################################################################################################################
# MATERIALS AND GEOMETRY
#######################################################################################################################################
materialList = {}

## MATERIAL - Air
materialList['Air'] = CSX.AddMaterial('Air')

materialList['Air'].SetMaterialProperty(epsilon=1, mue=1)
materialList['Air'].AddPolyhedronReader(os.path.join(currDir,'Cylinder_up_gen_model.stl'), priority=9700).ReadFile()
materialList['Air'].AddPolyhedronReader(os.path.join(currDir,'Cylinder_midle_gen_model.stl'), priority=9900).ReadFile()
materialList['Air'].AddPolyhedronReader(os.path.join(currDir,'Cylinder_down_gen_model.stl'), priority=9800).ReadFile()

## MATERIAL - PEC
materialList['PEC'] = CSX.AddMetal('PEC')

materialList['PEC'].AddPolyhedronReader(os.path.join(currDir,'up002_gen_model.stl'), priority=9500).ReadFile()
materialList['PEC'].AddPolyhedronReader(os.path.join(currDir,'down001_gen_model.stl'), priority=9600).ReadFile()


#######################################################################################################################################
# GRID LINES
#######################################################################################################################################

## GRID - grid_1mm - Cylinder_up (Fixed Distance)
mesh.x = np.delete(mesh.x, np.argwhere((mesh.x >= -144) & (mesh.x <= 144)))
mesh.x = np.concatenate((mesh.x, arangeWithEndpoint(-144,144,1)))
mesh.y = np.delete(mesh.y, np.argwhere((mesh.y >= -143.955) & (mesh.y <= 143.955)))
mesh.y = np.concatenate((mesh.y, arangeWithEndpoint(-143.955,143.955,1)))
mesh.z = np.delete(mesh.z, np.argwhere((mesh.z >= 5) & (mesh.z <= 325)))
mesh.z = np.concatenate((mesh.z, arangeWithEndpoint(5,325,1)))

## GRID - grid_0.1mm - Cylinder_midle (Fixed Distance)
mesh.x = np.delete(mesh.x, np.argwhere((mesh.x >= -144) & (mesh.x <= 144)))
mesh.x = np.concatenate((mesh.x, arangeWithEndpoint(-144,144,0.1)))
mesh.y = np.delete(mesh.y, np.argwhere((mesh.y >= -143.955) & (mesh.y <= 143.955)))
mesh.y = np.concatenate((mesh.y, arangeWithEndpoint(-143.955,143.955,0.1)))
mesh.z = np.delete(mesh.z, np.argwhere((mesh.z >= -5) & (mesh.z <= 5)))
mesh.z = np.concatenate((mesh.z, arangeWithEndpoint(-5,5,0.1)))

## GRID - grid_1mm - Cylinder_down (Fixed Distance)
mesh.x = np.delete(mesh.x, np.argwhere((mesh.x >= -144) & (mesh.x <= 144)))
mesh.x = np.concatenate((mesh.x, arangeWithEndpoint(-144,144,1)))
mesh.y = np.delete(mesh.y, np.argwhere((mesh.y >= -143.955) & (mesh.y <= 143.955)))
mesh.y = np.concatenate((mesh.y, arangeWithEndpoint(-143.955,143.955,1)))
mesh.z = np.delete(mesh.z, np.argwhere((mesh.z >= -325) & (mesh.z <= -5)))
mesh.z = np.concatenate((mesh.z, arangeWithEndpoint(-325,-5,1)))

openEMS_grid.AddLine('x', mesh.x)
openEMS_grid.AddLine('y', mesh.y)
openEMS_grid.AddLine('z', mesh.z)

#######################################################################################################################################
# PORTS
#######################################################################################################################################
port = {}
portNamesAndNumbersList = {}
## PORT - portin - portin001
portStart = [ -1.49121, -1.4978, -1 ]
portStop  = [ 1.5, 1.4978, 4 ]
portR = 50
portUnits = 1
portExcitationAmplitude = 1.0
portDirection = 'z'
port[1] = FDTD.AddLumpedPort(port_nr=1, R=portR*portUnits, start=portStart, stop=portStop, p_dir=portDirection, priority=10000, excite=1.0*portExcitationAmplitude)
portNamesAndNumbersList["portin001"] = 1;

#######################################################################################################################################
# RUN
#######################################################################################################################################
### Run the simulation
CSX_file = os.path.join(Sim_Path, Sim_CSX)
if not os.path.exists(Sim_Path):
	os.mkdir(Sim_Path)
CSX.Write2XML(CSX_file)
from CSXCAD import AppCSXCAD_BIN
os.system(AppCSXCAD_BIN + ' "{}"'.format(CSX_file))

FDTD.Run(Sim_Path, verbose=3, cleanup=True, setup_only=setup_only, debug_pec=debug_pec)
