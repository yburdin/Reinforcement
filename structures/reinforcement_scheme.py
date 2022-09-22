from utils.reinforcement_data import ReinforcementData
from reinforcement_zone import ReinforcementZone
from scad_data import SCADData
from utils.decorators import Decorators
from typing import List
from numpy import intersect1d
import pandas as pd
import numpy as np


class ReinforcementScheme:
    def __init__(self):
        self.reinforcement_data = None
        self.reinforcement_zones = {'Top_X': [],
                                    'Top_Y': [],
                                    'Bot_X': [],
                                    'Bot_Y': [],
                                    'Lat_X': [],
                                    'Lat_Y': [],
                                    }
        self.scad_data = None

    @Decorators.timed
    def load_reinforcement_data(self, reinforcement_data: ReinforcementData):
        self.reinforcement_data = reinforcement_data

    @Decorators.timed
    def find_reinforcement_zones(self, location, min_value=0):
        assert self.reinforcement_data, 'No reinforcement data'

        reinforced_elements = self.reinforcement_data.reinforcement_table.query(f'{location} > {min_value}')
        reinforced_elements_indices = reinforced_elements.Element_index.astype(int).to_list()

        while len(reinforced_elements_indices) > 0:
            first_element = reinforced_elements_indices.pop(0)
            first_element_nodes = self.reinforcement_data.elements_table.loc[first_element].Nodes

            zone = ReinforcementZone()
            zone.add_one_element_to_zone(first_element, first_element_nodes)

            while True:
                next_elements = self.find_elements_with_nodes(self.reinforcement_data.elements_table, zone.nodes)
                next_elements = intersect1d(next_elements, reinforced_elements_indices)

                if len(next_elements) > 0:
                    nodes = np.stack(self.reinforcement_data.elements_table.loc[next_elements].Nodes.values).flatten()
                    zone.add_multiple_elements_to_zone(next_elements, nodes)
                    reinforced_elements_indices = [element for element in reinforced_elements_indices
                                                   if element not in next_elements]
                else:
                    break

            self.reinforcement_zones[location].append(zone)

    def reset_reinforcement_zones(self):
        self.reinforcement_zones = {'Top_X': [],
                                    'Top_Y': [],
                                    'Bot_X': [],
                                    'Bot_Y': [],
                                    'Lat_X': [],
                                    'Lat_Y': [],
                                    }

    @staticmethod
    @Decorators.timed
    def find_elements_with_nodes(elements_table: pd.DataFrame, nodes_to_find: List[int]) -> List[int]:
        result_elements = []

        nodes = np.stack(elements_table.Nodes.values)
        search_result = [np.where(nodes == node)[0] for node in nodes_to_find]
        for item in search_result:
            result_elements += elements_table.iloc[item].index.tolist()

        result_elements = list(np.unique(result_elements))

        return result_elements

    def load_scad_data(self, scad_data: SCADData, name: str):
        self.scad_data = scad_data.elements_table.loc[scad_data.reinforcement_groups[name]]

        self.scad_data = self.scad_data.reset_index()
        # self.scad_data.index = range(1, len(self.scad_data) + 1)

    def transfer_reinforcement_direction_to_zones(self):
        for location in self.reinforcement_zones.keys():
            for zone in self.reinforcement_zones[location][:]:
                zone_elements_indices = self.reinforcement_data.elements_table.loc[zone.elements].Reinforcement_index
                zone_directions = self.scad_data.loc[zone_elements_indices.astype(int)]

                if all([coordinate != 0 for coordinate in zone.reinforcement_direction]):
                    continue

                if (len(np.unique(np.stack(zone_directions.Direction.values), axis=0)) == 1 and
                        len(zone_directions.Rotation_type.unique()) == 1):
                    rotation_type = zone_directions.Rotation_type.unique()[0]
                    direction = np.unique(np.stack(zone_directions.Direction.values), axis=0)[0]

                    if rotation_type == 'EX':
                        zone.set_reinforcement_direction(*direction)
                    elif rotation_type == 'EY':
                        ey_direction = direction
                        ey_to_ex_rotation = np.array([[0, 1, 0],
                                                      [-1, 0, 0],
                                                      [0, 0, 1]])
                        ex_direction = ey_to_ex_rotation @ ey_direction
                        zone.set_reinforcement_direction(*ex_direction)

                    zone.set_bounding_rectangle(self.get_zone_bounding_rectangle(zone))

                elif len(zone_directions.Rotation_type.unique()) == 1:
                    rotation_type = zone_directions.Rotation_type.unique()[0]
                    directions = np.unique(np.stack(zone_directions.Direction.values), axis=0)
                    for direction in directions:
                        direction_filter = [all(item) for item in
                                            np.stack(zone_directions.Direction.values) == direction]

                        new_zone_indices = zone_directions.iloc[direction_filter].index
                        new_zone_elements = self.reinforcement_data.reinforcement_table.loc[
                            new_zone_indices].Element_index.astype(int)
                        new_zone_nodes = np.stack(
                            self.reinforcement_data.elements_table.loc[new_zone_elements].Nodes.values)
                        new_zone_nodes = np.unique(new_zone_nodes)

                        new_zone = ReinforcementZone()
                        new_zone.add_multiple_elements_to_zone(new_zone_elements, new_zone_nodes)

                        if rotation_type == 'EX':
                            new_zone.set_reinforcement_direction(*direction)

                        new_zone.set_bounding_rectangle(self.get_zone_bounding_rectangle(new_zone))

                        self.reinforcement_zones[location].append(new_zone)

                    self.reinforcement_zones[location].remove(zone)

    def get_zone_bounding_rectangle(self, zone: ReinforcementZone) -> np.array:
        zone_nodes = self.reinforcement_data.nodes_table.loc[zone.nodes]

        rotation_matrix = self.make_rotation_matrix_2d(*zone.reinforcement_direction[:2])
        zone_nodes_coordinates = zone_nodes.loc[:, ['X', 'Y']]
        local_coordinates = (rotation_matrix @ zone_nodes_coordinates.values.T).T

        min_x_local, min_y_local = local_coordinates[:, 0].min(), local_coordinates[:, 1].min()
        max_x_local, max_y_local = local_coordinates[:, 0].max(), local_coordinates[:, 1].max()

        points_local = np.array([[min_x_local, min_y_local],
                                 [min_x_local, max_y_local],
                                 [max_x_local, max_y_local],
                                 [max_x_local, min_y_local],
                                 ])
        points_global = np.linalg.inv(rotation_matrix) @ points_local.T
        return points_global

    @staticmethod
    def make_rotation_matrix_2d(x, y) -> np.array:
        tan_alpha = y / (x + 1e-9)
        alpha = np.arctan(tan_alpha)

        return np.array([[np.cos(alpha), -np.sin(alpha)],
                         [np.sin(alpha), np.cos(alpha)]])
