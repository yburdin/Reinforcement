import numpy as np
import pandas as pd
from utils.decorators import Decorators
from typing import List
import re


class ReinforcementData:
    def __init__(self):
        self.nodes_table = pd.DataFrame(columns=('X', 'Y', 'Z'))
        self.elements_table = pd.Series(name='Nodes', dtype=object)
        self.reinforcement_table = pd.DataFrame(columns=('Element_center_X', 'Element_center_Y', 'Element_center_Z',
                                                         'Top_X', 'Top_Y', 'Lat_X', 'Bot_X', 'Bot_Y', 'Lat_Y'))
        self.polygons = []

    @Decorators.timed
    def import_asf(self, path: str) -> None:
        with open(path) as f:
            data = f.read()

        self.polygons = self.import_polygons(data)

        nodes_index, nodes_coordinates = self.import_nodes(data)
        self.nodes_table = self.nodes_table.reindex(nodes_index)
        self.nodes_table.loc[nodes_index] = nodes_coordinates

        elements_data = np.array(self.import_elements(data))
        elements_index = elements_data[:, 0]
        elements_nodes = elements_data[:, 1:]
        self.elements_table = self.elements_table.reindex(elements_index)
        self.elements_table.loc[:] = tuple(elements_nodes)

        reinforcement_data = self.import_reinforcement(data)
        self.reinforcement_table = pd.DataFrame(data=reinforcement_data, columns=self.reinforcement_table.columns)

        self.calculate_element_centers()

    @staticmethod
    def import_polygons(data: str) -> List[np.array]:
        return_polygons = []

        polygons = re.findall(r'GL POLY \d+', data)

        positions = []
        for poly in polygons:
            if len(positions) == 0:
                positions.append(data.index(poly))
            else:
                positions.append(data.index(poly, positions[-1] + 1))

        for i, poly in enumerate(polygons):
            position = positions[i]
            n_points = int(re.search(r'\d+', poly).group())
            polygon_points = data[position:].split('\n')[1:n_points + 1]
            polygon_points = [list(map(float, re.findall(r'[\d.\-e]+', point_line))) for point_line in polygon_points]
            return_polygons.append(np.array(polygon_points))

        return return_polygons

    @Decorators.timed
    def import_reinforcement(self, data: str) -> List[List[float]]:
        reinforcement = re.findall(r'QM [\d\s\-.,]+\n', data)
        reinforcement = list(map(self.strip_reinforcement_line, reinforcement))

        return reinforcement

    @Decorators.timed
    def import_elements(self, data: str) -> List[List[int]]:
        element_data_first_line = re.search(r'GF ELEM \d+', data)
        n_elements = int(element_data_first_line.group().split(' ')[-1])

        elements_data = data[element_data_first_line.end():].split('\n')[1:n_elements+1]
        elements = list(map(self.strip_element_line, elements_data))

        return elements

    @Decorators.timed
    def import_nodes(self, data: str) -> (List[int], np.array):
        nodes_data_first_line = re.search(r'GP KNOT \d+', data)
        n_nodes = int(nodes_data_first_line.group().split(' ')[-1])

        nodes_data = data[nodes_data_first_line.end():].split('\n')[1:n_nodes+1]
        nodes = np.array(list(map(self.strip_node_line, nodes_data)))

        nodes_index = list(nodes[:, 0].astype(int))
        nodes_coordinates = nodes[:, 1:]

        return nodes_index, nodes_coordinates

    @staticmethod
    def strip_reinforcement_line(line: str) -> List[float]:
        values = re.findall(r'-?\d+\.\d+', line)
        values = list(map(float, values))

        assert len(values) == 9, f'ASF Reinforcement import error\n{line}\n{values}'

        return values

    @staticmethod
    def strip_element_line(line: str) -> List[int]:
        split_line = [line[i * len(line) // 5: (i+1) * len(line) // 5] for i in range(5)]
        values = list(map(int, split_line))

        assert len(values) == 5, f'ASF Elements import error\n{line}\n{values}'

        return values

    @staticmethod
    def strip_node_line(line: str) -> List[int]:
        split_line = [item for item in line.split(' ') if item != '']
        values = [int(split_line[0])]
        values += list(map(float, split_line[1:]))

        assert len(values) == 4, f'ASF Nodes import error\n{line}\n{values}'

        return values

    @Decorators.timed
    def calculate_element_centers(self):
        coordinates = list(map(self.get_coordinates, self.elements_table.values))
        element_centers = list(map(self.get_mean, coordinates))

        elements_centers_table = pd.DataFrame(data=element_centers, index=self.elements_table.index,
                                              columns=('Element_center_X', 'Element_center_Y', 'Element_center_Z'))

        self.elements_table = pd.concat([self.elements_table, elements_centers_table], axis=1)

    def get_coordinates(self, nodes) -> np.array:
        nodes = nodes[nodes != 0]
        coordinates = self.nodes_table.loc[nodes, ['X', 'Y', 'Z']].values.astype(float)
        return coordinates

    @staticmethod
    def get_mean(array) -> np.array:
        return np.mean(array, axis=0)
