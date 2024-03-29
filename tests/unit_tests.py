import os
import sys
import numpy as np
import pandas as pd
import time


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import mistlib as mist
import ramenlib as ramen

import unittest

# Quantity of interest function for point data, data
def test_func1(data):
    return data["5"].values

# Classification function for gridded data, Z
def test_func2(Z, i, j):
    var = Z[0][i,j]

    if var > 150.0:
        return False
    else:
        return True

# Quantity of interest function for point data, data
def test_func3(data):
    return data["5"].values

# Classification function for gridded data for keyholing
def test_func4(Z, i, j):
    spot_size = 55

    var = Z[0][i,j]
    depth = var
    if depth/spot_size < 2.0:
        return False
    else:
        return True
    
# Classification function for gridded data for lack of fusion
def test_func5(Z, i, j):
    layer_thickness = 30

    var = Z[0][i,j]
    depth = var
    if depth > layer_thickness:
        return False
    else:
        return True


class TestSuite(unittest.TestCase):
    """Test cases."""

    def test_point_data_plot(self):
        print("Test: test_point_data_plot")
        data = pd.read_csv("pmap_test_data.csv")
        mesh_size = 100

        grid_bounds_x = (min(data["2"]), max(data["2"]))
        grid_bounds_y = (min(data["1"]), max(data["1"]))

        pmap = ramen.ProcessMap2D(num_grid_points=[mesh_size, mesh_size], grid_bounds_x=grid_bounds_x, grid_bounds_y=grid_bounds_y)
        pmap.add_point_data_plot(data, test_func1, x_name="2", y_name="1")
        pmap.finalize(1.0)

    def test_grid_data_plot(self):
        print("Test: test_grid_data_plot")
        mesh_size = 100
        grid_bounds_x = (0.5, 3.5)
        grid_bounds_y = (100.0, 500.0)
        pmap = ramen.ProcessMap2D(num_grid_points=[mesh_size,mesh_size], grid_bounds_x=grid_bounds_x, grid_bounds_y=grid_bounds_y)

        Z = np.zeros([mesh_size, mesh_size])
        Z = pmap.X + pmap.Y**2


        pmap.add_gridded_data_plot(Z)
        pmap.finalize(1.0)

    def test_grid_data_region_plot(self):
        print("Test: test_grid_data_region_plot")
        data = pd.read_csv("pmap_test_data.csv")
        mesh_size = 100
        grid_bounds_x = (min(data["2"]), max(data["2"]))
        grid_bounds_y = (min(data["1"]), max(data["1"]))

        pmap = ramen.ProcessMap2D(num_grid_points=[mesh_size, mesh_size], grid_bounds_x=grid_bounds_x, grid_bounds_y=grid_bounds_y)
        
        Z = np.zeros([mesh_size, mesh_size])
        Z = pmap.Y + pmap.X**2

        
        pmap.add_gridded_region([Z], test_func2)

        pmap.finalize(1.0)
    
    def test_point_data_region_plot(self):
        print("Test: test_point_data_region_plot")
        data = pd.read_csv("pmap_test_data.csv")
        mesh_size = 100
        grid_bounds_x = (min(data["2"]), max(data["2"]))
        grid_bounds_y = (min(data["1"]), max(data["1"]))

        pmap = ramen.ProcessMap2D(num_grid_points=[mesh_size, mesh_size], grid_bounds_x=grid_bounds_x, grid_bounds_y=grid_bounds_y)

        pmap.add_point_data_region(data, [test_func3], test_func4, x_name="2", y_name="1")

        pmap.finalize(1.0)

    def test_full_process_map(self):
        print("Test: test_full_process_map")
        data = pd.read_csv("pmap_test_data.csv")
        mesh_size = 100
        grid_bounds_x = (min(data["2"]), max(data["2"]))
        grid_bounds_y = (min(data["1"]), max(data["1"]))

        pmap = ramen.ProcessMap2D(num_grid_points=[mesh_size, mesh_size], grid_bounds_x=grid_bounds_x, grid_bounds_y=grid_bounds_y)

        Z = np.zeros([mesh_size, mesh_size])
        Z = pmap.X + pmap.Y**2

        pmap.add_gridded_data_plot(Z)
        pmap.add_point_data_region(data, [test_func3], test_func4, x_name="2", y_name="1")
        pmap.add_point_data_region(data, [test_func3], test_func5, x_name="2", y_name="1")

        pmap.finalize(1.0)


if __name__ == '__main__':
    unittest.main()