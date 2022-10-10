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

        data = data.split('\n')
        assert data[0] == '1.0 Nemetschek ALLPLAN', 'Only 1.0 Nemetschek ALLPLAN files are supported'

        line_type = None
        for line in data:
            if len(line) < 5:
                pass
            elif 'GL POLY' in line:
                line_type = None
            elif 'GP KNOT' in line:
                line_type = 'node'
            elif 'GF ELEM' in line:
                line_type = 'element'
            elif line[0:2] == 'QM':
                self.import_reinforcement_line(line)
            elif line[0:2] == 'QR':
                pass
            else:
                if line_type == 'node':
                    self.import_node_line(line)
                elif line_type == 'element':
                    self.import_element_line(line)

        self.calculate_element_centers()

    def import_node_line(self, line: str):
        split_line = [item for item in line.split(' ') if item != '']
        self.nodes_table.loc[int(split_line[0])] = [float(item) for item in (split_line[1:4])]

    def import_element_line(self, line: str):
        split_line = [line[i * len(line) // 5: (i+1) * len(line) // 5] for i in range(5)]
        self.elements_table.loc[int(split_line[0])] = [int(item) for item in (split_line[1:])]

    def import_reinforcement_line(self, line: str):
        split_line = [item for item in line.split(' ') if item != '']
        self.reinforcement_table.loc[len(self.reinforcement_table)] = [float(item) for item in (split_line[3:12])]

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
    def calculate_element_centers(self):
        elements_centers = pd.DataFrame(columns=('Element_center_X', 'Element_center_Y', 'Element_center_Z'))

        for i in self.elements_table.index:
            element_nodes = self.elements_table.loc[i]
            n_nodes = len([node for node in element_nodes if node > 0])

            element_center_x = 0
            element_center_y = 0
            element_center_z = 0

            for node in element_nodes:
                if node == 0:
                    continue

                element_center_x += self.nodes_table.loc[node, 'X']
                element_center_y += self.nodes_table.loc[node, 'Y']
                element_center_z += self.nodes_table.loc[node, 'Z']

            elements_centers.loc[i] = (element_center_x / n_nodes,
                                       element_center_y / n_nodes,
                                       element_center_z / n_nodes)

        self.elements_table = pd.concat([self.elements_table, elements_centers], axis=1)
