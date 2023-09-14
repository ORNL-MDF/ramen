import os
import sys
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

# Set the velocity and average composition
v = mist.core.Property(name = "solidification_velocity", unit = "m/s", value = 0.1, print_name = "Solidification velocity", reference = 'Manually set by user', print_symbol = "$v$")
mat.solidification_conditions['solidification_velocity'] = v

c_avg = mist.core.Property(name = "Cu", unit = "at.\\%", value = 2.9, print_name = "Composition (Cu)", reference = 'Manually set by user', print_symbol = "$c_{Cu}$")
mat.composition['Cu'] = c_avg

# Calculate the eutectic lamellar spacing
phases = ['alpha', 'theta']
spacing = ramen.get_eutectic_lamellar_spacing(mat, phases)
print("Lamellar spacing: ", spacing*1.e9, "nm")

# Calculate the strengthening contribution of the lamella
matrix_phase = 'alpha'
secondary_phase = 'theta'
orowan_strengthening_lamella = ramen.get_orowan_strengthening_lamella(mat, matrix_phase, secondary_phase)
print("Orowan strengthening, eutectic lamella:", orowan_strengthening_lamella * 1e-6, "MPa")