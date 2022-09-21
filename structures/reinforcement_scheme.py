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
            for zone in self.reinforcement_zones[location]:
                zone_elements_indices = self.reinforcement_data.elements_table.loc[zone.elements].Reinforcement_index
                zone_directions = self.scad_data.loc[zone_elements_indices.astype(int)]

                if (len(np.unique(np.stack(zone_directions.Direction.values), axis=0)) == 1 and
                        len(zone_directions.Rotation_type.unique()) == 1):
                    rotation_type = zone_directions.Rotation_type.unique()[0]
                    direction = np.unique(np.stack(zone_directions.Direction.values), axis=0)[0]

                    if rotation_type == 'EX':
                        zone.set_reinforcement_direction(*direction)

    @staticmethod
    def make_rotation_matrix_2d(x, y) -> np.array:
        tan_alpha = y / (x + 1e-9)
        alpha = np.arctan(tan_alpha)

        return np.array([[np.cos(alpha), -np.sin(alpha)],
                         [np.sin(alpha), np.cos(alpha)]])
