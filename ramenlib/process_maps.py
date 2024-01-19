import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.interpolate import LinearNDInterpolator
from scipy.interpolate import CloughTocher2DInterpolator
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
from matplotlib.colors import ListedColormap

class ProcessMap2D:
    def __init__(self, num_grid_points, grid_bounds_x, grid_bounds_y, x_label=None, y_label=None, fig_title=None):
        self.num_grid_points = num_grid_points
        self.grid_bounds_x = grid_bounds_x
        self.grid_bounds_y = grid_bounds_y
        self.x_label = x_label
        self.y_label = y_label
        self.fig_title = fig_title
        self.fig, self.ax = plt.subplots()

        self.x = np.linspace(grid_bounds_x[0], grid_bounds_x[1], num_grid_points[0])
        self.y = np.linspace(grid_bounds_y[0], grid_bounds_y[1], num_grid_points[1])

        self.X, self.Y = np.meshgrid(self.x, self.y)

        self.region_colors = ["#bb3f3f", "#49759c"]

        self.num_regions = 0
        self.legend_handles = []


    def interpolate_point_data_to_grid(self, data, func, x_name, y_name, interpolator='linear'):
        x_points = data[x_name].values
        y_points = data[y_name].values

        z_points = func(data)

        interp = None
        if (interpolator == 'linear'):
            interp =  LinearNDInterpolator(list(zip(x_points, y_points)), z_points)
        elif (interpolator == 'cubic'):
            interp =  CloughTocher2DInterpolator(list(zip(x_points, y_points)), z_points)

        Z = interp(self.X, self.Y)
        return Z


    def add_gridded_data_plot(self, Z, label=None):
        gdp = self.ax.contourf(self.X, self.Y, Z, cmap='Greys', levels=20)

        plt.colorbar(gdp, label=label)


    def add_point_data_plot(self, data, func, x_name, y_name, interpolator='linear', label=None):
        Z = self.interpolate_point_data_to_grid(data, func, x_name, y_name, interpolator)

        self.add_gridded_data_plot(Z)


    def add_point_data_locations(self, data, x_name, y_name):
        x_points = data[x_name].values
        y_points = data[y_name].values
        self.ax.plot(x_points,y_points, "ok", label="input points", markerfacecolor='none')

        legend_entry = mlines.Line2D([], [], color='k', marker='o', linewidth=0., markerfacecolor='w', label="Data locations")
        self.legend_handles.append(legend_entry)


    def add_point_data_region(self, data, func_list, classifier_func, x_name, y_name, interpolator='linear', region_name=None, color=None, alpha=1):
        Z_collection = []
        for func in func_list:
            Z = self.interpolate_point_data_to_grid(data, func, x_name, y_name, interpolator)
            Z_collection.append(Z)

        # Number of regions is incremented in `add_gridded_region`
        self.add_gridded_region(Z_collection, classifier_func, region_name, color, alpha)


    def add_gridded_region(self, Z_collection, classifier_func, region_name=None, color=None, alpha=1):
        classification = np.zeros(self.num_grid_points)

        region_color = None
        if (color):
            region_color = color
        else:
            region_color = self.region_colors[self.num_regions]

        for i in range(0,self.num_grid_points[0]):
            for j in range(0,self.num_grid_points[1]):
                # I'm not quite sure why I have to flip this
                classification[i,j] = not classifier_func(Z_collection, i, j)

        cmap = ListedColormap(['w', region_color])
        self.ax.contourf(self.X, self.Y, classification, cmap=cmap, levels=[-0.5,0.5], alpha=alpha)

        print('alpha is', alpha)

        if (region_name):
            legend_entry = mpatches.Patch(color=region_color, label=region_name, alpha=alpha)
            self.legend_handles.append(legend_entry)

        self.num_regions = self.num_regions + 1


    def finalize(self, fixed_show_time=None):
        self.ax.set_title(self.fig_title)
        self.ax.set_xlabel(self.x_label)
        self.ax.set_ylabel(self.y_label)
        self.ax.minorticks_on()

        if (len(self.legend_handles) > 0):
            self.ax.legend(handles=self.legend_handles, loc="best")
        if (fixed_show_time == None):
            plt.show()
        else:
            plt.show(block=False)
            plt.pause(fixed_show_time)
            plt.close()

    def save_figure(self, filename):
        self.fig.savefig(filename, dpi=300)



