# Plot S11
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

currDir = os.getcwd()
Sim_Path = os.path.join(currDir, r'simulation_output')
print(currDir)

## setup FDTD parameter & excitation function
max_timesteps = 10000
min_decrement = 0.0001 # 10*log10(min_decrement) dB  (i.e. 1E-5 means -50 dB)
CSX = CSXCAD.ContinuousStructure()
FDTD = openEMS(NrTS=max_timesteps, EndCriteria=min_decrement)
FDTD.SetCSX(CSX)

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
max_res = C0 / (f0 + fc) / 20

#######################################################################################################################################
# MATERIALS AND GEOMETRY
#######################################################################################################################################
materialList = {}

#######################################################################################################################################
# GRID LINES
#######################################################################################################################################

## GRID - grid_1mm - Cylinder_up (Fixed Distance)
mesh.x = np.delete(mesh.x, np.argwhere((mesh.x >= -215.951) & (mesh.x <= 216)))
mesh.x = np.concatenate((mesh.x, arangeWithEndpoint(-215.951,216,1)))
mesh.y = np.delete(mesh.y, np.argwhere((mesh.y >= -215.988) & (mesh.y <= 215.988)))
mesh.y = np.concatenate((mesh.y, arangeWithEndpoint(-215.988,215.988,1)))
mesh.z = np.delete(mesh.z, np.argwhere((mesh.z >= 10) & (mesh.z <= 490)))
mesh.z = np.concatenate((mesh.z, arangeWithEndpoint(10,490,1)))

## GRID - grid_0.1mm - Cylinder_midle (Fixed Distance)
mesh.x = np.delete(mesh.x, np.argwhere((mesh.x >= -215.951) & (mesh.x <= 216)))
mesh.x = np.concatenate((mesh.x, arangeWithEndpoint(-215.951,216,0.1)))
mesh.y = np.delete(mesh.y, np.argwhere((mesh.y >= -215.988) & (mesh.y <= 215.988)))
mesh.y = np.concatenate((mesh.y, arangeWithEndpoint(-215.988,215.988,0.1)))
mesh.z = np.delete(mesh.z, np.argwhere((mesh.z >= -10) & (mesh.z <= 10)))
mesh.z = np.concatenate((mesh.z, arangeWithEndpoint(-10,10,0.1)))

## GRID - grid_1mm - Cylinder_down (Fixed Distance)
mesh.x = np.delete(mesh.x, np.argwhere((mesh.x >= -215.951) & (mesh.x <= 216)))
mesh.x = np.concatenate((mesh.x, arangeWithEndpoint(-215.951,216,1)))
mesh.y = np.delete(mesh.y, np.argwhere((mesh.y >= -215.988) & (mesh.y <= 215.988)))
mesh.y = np.concatenate((mesh.y, arangeWithEndpoint(-215.988,215.988,1)))
mesh.z = np.delete(mesh.z, np.argwhere((mesh.z >= -490) & (mesh.z <= -10)))
mesh.z = np.concatenate((mesh.z, arangeWithEndpoint(-490,-10,1)))

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

## postprocessing & do the plots
freq = np.linspace(max(1e6,f0-fc), f0+fc, 501)
port[1].CalcPort(Sim_Path, freq)

Zin = port[1].uf_tot / port[1].if_tot
s11 = port[1].uf_ref / port[1].uf_inc
s11_dB = 20.0*np.log10(np.abs(s11))

# plot the feed point impedance
figure()
plot(freq / 1e6, np.real(Zin), 'k-', linewidth=2, label=r'$\Re(Z_{in})$')
grid()
plot(freq / 1e6, np.imag(Zin), 'r--', linewidth=2, label=r'$\Im(Z_{in})$')
title('impedance of portin - portin001')
xlabel('frequency (MHz)')
ylabel('$Z (\Omega)$')
legend()

# plot S11 parameter
figure()
plot(freq/1e6, s11_dB, 'k-', linewidth=2, label='$S_{11}$')
grid()
legend()
title('S11-Parameter (dB) of portin - portin001')
ylabel('S11 (dB)')
xlabel('Frequency (MHz)')

show()  #show all figures at once

#
#   Write S11, real and imag Z_in into CSV file separated by ';'
#
filename = 'openEMS_simulation_s11_dB.csv'

with open(filename, 'w', newline='') as csvfile:
	writer = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
	writer.writerow(['freq (MHz)', 's11 (dB)', 'real Z_in', 'imag Z_in', 'Z_in total'])
	writer.writerows(np.array([
		(freq/1e6),
		s11_dB,
		np.real(Zin),
		np.imag(Zin),
		np.abs(Zin)
	]).T) #creates array with 1st row frequencies, 2nd row S11, ... and transpose it
