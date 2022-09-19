from utils.imports import ReinforcementData
from reinforcement_zone import ReinforcementZone
from typing import List
from numpy import intersect1d
import pandas as pd


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

    def load_reinforcement_data(self, reinforcement_data: ReinforcementData):
        self.reinforcement_data = reinforcement_data

    def find_reinforcement_zones(self, location, min_value=0):
        assert self.reinforcement_data, 'No reinforcement data'

        reinforced_elements = self.reinforcement_data.reinforcement_table.query(f'{location} > {min_value}')
        reinforced_elements_indices = reinforced_elements.Element_index.astype(int).to_list()

        while len(reinforced_elements_indices) > 0:
            first_element = reinforced_elements_indices.pop(0)
            first_element_nodes = self.reinforcement_data.elements_table.loc[first_element].Nodes

            zone = ReinforcementZone()
            zone.add_to_zone(first_element, first_element_nodes)

            while True:
                next_elements = self.find_elements_with_nodes(self.reinforcement_data.elements_table, zone.nodes)
                next_elements = intersect1d(next_elements, reinforced_elements_indices)

                if len(next_elements) > 0:
                    for element in next_elements:
                        element = int(element)
                        nodes = self.reinforcement_data.elements_table.loc[element].Nodes
                        zone.add_to_zone(element, nodes)
                        reinforced_elements_indices.remove(element)
                else:
                    break

            self.reinforcement_zones[location].append(zone)

    @staticmethod
    def find_elements_with_nodes(elements_table: pd.DataFrame, nodes: List[int]) -> List[int]:
        result_elements = []

        for element in elements_table.index:
            element_nodes = elements_table.loc[element].Nodes
            if len(intersect1d(element_nodes, nodes)) > 0:
                result_elements.append(element)

        return result_elements


