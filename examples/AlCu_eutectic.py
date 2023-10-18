import os
import sys
import numpy as np
PROJECT_ROOT = os.path.abspath(os.path.join(
                  os.path.dirname(__file__), 
                  os.pardir)
)
sys.path.append(PROJECT_ROOT)

import mistlib as mist
import ramenlib as ramen

# Create from the AlCu JSON file
path_to_example_data = os.path.join(os.path.dirname(__file__), 'AlCu.json')
mat = mist.core.MaterialInformation(path_to_example_data)

# User-set parameters
velocity = 1.3 # m/s
c_Cu = 2.6 # at. %
grain_diameter = 5.0e-6 # m

# Calculate the equilibrium eutectic phase fractions
phases = ['alpha', 'theta']
phase_fractions = ramen.get_eutectic_phase_fractions(mat, phases, c_Cu)

# Calculate the eutectic lamellar spacing
spacing = ramen.get_eutectic_lamellar_spacing(mat, phases, phase_fractions, velocity)
print("Lamellar spacing: ", spacing*1.e9, "nm")
print("")

# Calculate the strengthening contribution of the lamella
matrix_phase = 'alpha'
secondary_phase = 'theta'
orowan_strengthening_lamella = ramen.get_orowan_strengthening_lamella(mat, matrix_phase, secondary_phase, spacing, phase_fractions)
print("Orowan strengthening, eutectic lamella:", orowan_strengthening_lamella * 1e-6, "MPa")

# Calculate the strengthening contribution of the solute in solution
matrix_phase = 'alpha'
solid_solution_strengthening = ramen.get_solid_solution_strengthening(mat, matrix_phase)
print("Solid solution strengthening:", solid_solution_strengthening * 1e-6, "MPa")

# Calculate the strengthening contribution of grain boundaries
grain_boundary_strengthening = ramen.get_grain_boundary_strengthening(mat, grain_diameter)
print("Grain boundary strengthening:", grain_boundary_strengthening * 1e-6, "MPa")

# Calculate the total yield strength
yield_strength = orowan_strengthening_lamella + solid_solution_strengthening + grain_boundary_strengthening
print("")
print("Predicted yield strength:", yield_strength * 1e-6, "MPa")
