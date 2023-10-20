import os
import sys
import numpy as np
import pandas as pd

# Add to the path so that Ramen doesn't have to be installed
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import mistlib as mist
import ramenlib as ramen

# Functions to select data fields
def get_depth(data):
    return data["5"].values

# Functions for classifying regions
def keyhole_classifer(Z, i, j):
    spot_size = 55
    depth = Z[0][i,j]
    return ramen.keyhole_porosity_classifier(depth, spot_size)
    
def lack_of_fusion_classifier(Z, i, j):
    layer_thickness = 30
    depth = Z[0][i,j]
    return ramen.lack_of_fusion_porosity_classifier(depth, layer_thickness)
    
def nan_classifier(Z, i, j):
    depth = Z[0][i,j]
    return ramen.nan_classifier(depth)

# Load the AdditiveFOAM process data
sim_data = pd.read_csv("acmz_process_data.csv")

# Create the process map
power = sim_data["1"]
velocity = sim_data["2"]

mesh_size = 500
grid_bounds_x = (min(velocity), max(velocity))
grid_bounds_y = (min(power), max(power))

pmap = ramen.ProcessMap2D(num_grid_points=[mesh_size, mesh_size], grid_bounds_x=grid_bounds_x, grid_bounds_y=grid_bounds_y, x_label="Velocity (m/s)", y_label="Power (W)", fig_title="Process Map: ACMZ")

# Calculate the lamellar spacing
path_to_example_data = os.path.join(os.path.dirname(__file__), 'AlCu.json')
mat = mist.core.MaterialInformation(path_to_example_data)
c_Cu = 2.6 # at. %

phases = ['alpha', 'theta']
phase_fractions = ramen.get_eutectic_phase_fractions(mat, phases, c_Cu)

lamellar_spacing = np.zeros([mesh_size, mesh_size])
velocity_grid_data = pmap.X
lamellar_spacing = ramen.get_eutectic_lamellar_spacing(mat, phases, phase_fractions, velocity_grid_data)

# Add the plots to the process map
pmap.add_gridded_data_plot(lamellar_spacing, label="Lamellar spacing (m)")

pmap.add_point_data_region(sim_data, [get_depth], keyhole_classifer, x_name="2", y_name="1", region_name="Keyhole regime")

pmap.add_point_data_region(sim_data, [get_depth], lack_of_fusion_classifier, x_name="2", y_name="1", region_name="Lack-of-fusion regime")

# Plot regions with no data
#pmap.add_point_data_region(sim_data, [get_depth], nan_classifier, x_name="2", y_name="1", region_name="No data", color='oldlace')

# Plot the locations of the simulation data
#pmap.add_point_data_locations(sim_data, x_name="2", y_name="1")

pmap.finalize()
pmap.save_figure("acmz_process_map.png")

