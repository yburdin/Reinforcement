from utils.reinforcement_data import ReinforcementData
from structures.reinforcement_scheme import ReinforcementScheme
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import pandas as pd
import numpy as np
from matplotlib import cm


class Plotter:
    def __init__(self):
        pass

    @staticmethod
    def plot_reinforcement_3d(reinforcement: ReinforcementData, reinforcement_loc: str):
        fig = plt.figure()
        ax = fig.add_subplot(projection='3d')
        plt.tight_layout()
        ax.set_axis_off()

        fig.suptitle(reinforcement_loc)

        min_coordinate = min(reinforcement.nodes_table.loc[:, ['X', 'Y']].min().values)
        max_coordinate = max(reinforcement.nodes_table.loc[:, ['X', 'Y']].max().values)
        ax.set_xlim([min_coordinate, max_coordinate])
        ax.set_ylim([min_coordinate, max_coordinate])

        v_min = reinforcement.reinforcement_table.loc[:, reinforcement_loc].min()
        v_max = reinforcement.reinforcement_table.loc[:, reinforcement_loc].max()

        if v_min == v_max:
            v_max += 1e-5
            v_min -= 1e-5

        for element in reinforcement.elements_table.index:
            element_nodes = reinforcement.elements_table.loc[element, 'Nodes']
            xs = reinforcement.nodes_table.loc[element_nodes, 'X'].values
            ys = reinforcement.nodes_table.loc[element_nodes, 'Y'].values
            zs = reinforcement.nodes_table.loc[element_nodes, 'Z'].values

            xs = np.append(xs, xs[0])
            ys = np.append(ys, ys[0])
            zs = np.append(zs, zs[0])

            ax.plot(xs, ys, zs, c='xkcd:grey')

            reinforcement_con = reinforcement.reinforcement_table.Element_index == element
            reinforcement_value = reinforcement.reinforcement_table.loc[reinforcement_con, reinforcement_loc].iloc[0]

            vertices = [list(zip(xs, ys, zs))]
            face_color = cm.rainbow((reinforcement_value - v_min) / (v_max - v_min))
            ax.add_collection3d(Poly3DCollection(vertices, facecolors=face_color))

        sm = plt.cm.ScalarMappable(cmap=cm.rainbow,
                                   norm=plt.Normalize(vmin=v_min,
                                                      vmax=v_max)
                                   )
        fig.colorbar(sm, ticks=np.linspace(v_min, v_max, 9), format='%.3g')
        plt.show()

    @staticmethod
    def plot_reinforcement_2d(reinforcement: ReinforcementData, reinforcement_loc: str, min_value=0):
        fig = plt.figure()
        ax = fig.add_subplot()

        fig.suptitle(reinforcement_loc.replace("_", " "))

        v_min = max(reinforcement.reinforcement_table.loc[:, reinforcement_loc].min(), min_value)
        v_max = reinforcement.reinforcement_table.loc[:, reinforcement_loc].max()

        if v_min == v_max:
            v_max += 1e-5
            v_min -= 1e-5

        for element in reinforcement.elements_table.index:
            element_nodes = reinforcement.elements_table.loc[element, 'Nodes']
            xs = reinforcement.nodes_table.loc[element_nodes, 'X'].values
            ys = reinforcement.nodes_table.loc[element_nodes, 'Y'].values

            xs = np.append(xs, xs[0])
            ys = np.append(ys, ys[0])

            ax.plot(xs, ys, c='xkcd:grey')

            reinforcement_con = reinforcement.reinforcement_table.Element_index == element
            reinforcement_value = reinforcement.reinforcement_table.loc[reinforcement_con, reinforcement_loc].iloc[0]

            if reinforcement_value <= min_value:
                face_color = (1, 1, 1, 1)
            else:
                face_color = cm.rainbow((reinforcement_value - v_min) / (v_max - v_min))

            ax.fill(xs, ys, color=face_color)

        sm = plt.cm.ScalarMappable(cmap=cm.rainbow,
                                   norm=plt.Normalize(vmin=v_min,
                                                      vmax=v_max)
                                   )
        fig.colorbar(sm, ticks=np.linspace(v_min, v_max, 9), format='%.3g')
        plt.show()

    def plot_reinforcement_zones_2d(self, scheme: ReinforcementScheme, reinforcement_loc: str):
        fig = plt.figure()
        ax = fig.add_subplot()

        fig.suptitle(f'Zones {reinforcement_loc.replace("_", " ")}')

        self.add_mesh_to_ax_2d(ax, scheme.reinforcement_data.nodes_table, scheme.reinforcement_data.elements_table)
        self.add_force_directions_to_ax_2d(ax, scheme.reinforcement_data.reinforcement_table,
                                           scheme.scad_data)
        self.add_reinforcement_zones_to_ax_2d(ax, scheme, reinforcement_loc)

    @staticmethod
    def add_mesh_to_ax_2d(ax: plt.Axes, nodes_table: pd.DataFrame, elements_table: pd.DataFrame):
        for element in elements_table.index:
            element_nodes = elements_table.loc[element, 'Nodes']
            xs = nodes_table.loc[element_nodes, 'X'].values
            ys = nodes_table.loc[element_nodes, 'Y'].values

            xs = np.append(xs, xs[0])
            ys = np.append(ys, ys[0])

            ax.plot(xs, ys, c='xkcd:grey')

    @staticmethod
    def add_force_directions_to_ax_2d(ax: plt.Axes, elements_table: pd.DataFrame, rotation_table: pd.DataFrame):
        for element in elements_table.index:
            x, y = elements_table.loc[element, ['Element_center_X', 'Element_center_Y']]
            rotation_type, direction = rotation_table.loc[element, ['Rotation_type', 'Direction']]

            if rotation_type == 'EX':
                dx = direction[0] / max(direction) * 0.1
                dy = direction[1] / max(direction) * 0.1

            ax.arrow(x, y, dx, dy, width=0.05, head_length=0.1)

    @staticmethod
    def add_reinforcement_zones_to_ax_2d(ax: plt.Axes, scheme: ReinforcementScheme, reinforcement_loc: str):
        for zone in scheme.reinforcement_zones[reinforcement_loc]:
            if zone.bounding_rectangle is not None:
                ax.plot(zone.bounding_rectangle[:, 0], zone.bounding_rectangle[:, 1], c='xkcd:red', lw=3)
                ax.plot([zone.bounding_rectangle[-1, 0], zone.bounding_rectangle[0, 0]],
                        [zone.bounding_rectangle[-1, 1], zone.bounding_rectangle[0, 1]], c='xkcd:red', lw=3)
