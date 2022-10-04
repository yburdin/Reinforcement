from utils.decorators import Decorators
from typing import List
import pandas as pd
import numpy as np
import re


class SCADData:
    def __init__(self):
        self.nodes_table = None
        self.elements_table = None
        self.reinforcement_groups = {}

    @Decorators.timed
    def import_txt(self, path: str) -> None:
        with open(path) as f:
            data = f.read()

        self.nodes_table = self.import_nodes_form_txt_data(data)
        self.elements_table = self.import_elements_from_txt_data(data)

        force_direction_table = self.import_force_directions_from_txt_data(data)
        self.elements_table = pd.concat([self.elements_table, force_direction_table], axis=1)

        # element_centers_table = self.calculate_element_centers(self.elements_table.Nodes, self.nodes_table)
        # self.elements_table = pd.concat([self.elements_table, element_centers_table], axis=1)

        self.reinforcement_groups = self.import_reinforcement_groups_from_txt_data(data)

    @Decorators.timed
    def import_force_directions_from_txt_data(self, data: str) -> pd.DataFrame:
        force_direction_table = pd.DataFrame(columns=('Rotation_type', 'Direction'))

        force_axis = re.search(r'\(33/[\s\w=:\-/.+"]+\)', data).group().replace('\n', ' ')
        force_axis = force_axis.split('/')
        force_axis = [line.replace('  ', ' ').strip() for line in force_axis if 'EX' in line or 'EY' in line]

        for n, line in enumerate(force_axis):
            line_info, elements = line.split(':')

            rotation_type, x, y, z = line_info.split(' ')[0:4]
            element_indices = self.get_element_list_from_string(elements)

            rotation_type_series = pd.Series(index=element_indices,
                                             data=rotation_type,
                                             name='Rotation_type')

            direction_series = pd.Series(index=element_indices,
                                         data=[[float(x), float(y), float(z)]
                                               for _ in range(len(element_indices))],
                                         name='Direction')

            new_frame = pd.concat([rotation_type_series, direction_series], axis=1)
            force_direction_table = pd.concat([force_direction_table, new_frame])

        return force_direction_table

    @Decorators.timed
    def import_reinforcement_groups_from_txt_data(self, data: str) -> dict:
        reinforcement_groups_dict = {}

        reinforcement_groups = re.search(r'\(53/[\w\s\d=\".:\-/,]+\)', data).group().replace('\n', ' ')
        reinforcement_groups = reinforcement_groups.split('/')

        for line in reinforcement_groups:
            if 'Name' in line:
                name = re.search(r'Name="[\w\s\d.,\-+]+"', line).group().split('"')[1]
                elements = line.split(':')[-1].replace('  ', ' ')

                element_indices = self.get_element_list_from_string(elements)
                reinforcement_groups_dict[name] = element_indices

        return reinforcement_groups_dict

    @Decorators.timed
    def import_elements_from_txt_data(self, data: str) -> pd.DataFrame:
        elements_table = pd.DataFrame(columns=('Element_type', 'Stiffness'))
        nodes_series = pd.Series(name='Nodes', dtype=object)

        elements_data = re.search(r'\(1/[\d\s\w:/]+\)', data).group().replace('\n', ' ')
        while '  ' in elements_data:
            elements_data = elements_data.replace('  ', ' ')

        elements_data = elements_data.replace('(1/', '').split('/')
        repeat_operators_positions = [-1] + [i for i in range(len(elements_data)) if 'r' in elements_data[i]] + [-1]
        for i in range(1, len(repeat_operators_positions)):
            pos_prev = repeat_operators_positions[i-1] + 1
            pos = repeat_operators_positions[i]

            elements_data_i = elements_data[pos_prev:pos]
            elements_data_i = [list(map(int, element.strip().split(' '))) for element in elements_data_i]

            element_indices = list(range(len(elements_table), len(elements_table) + len(elements_data_i)))
            new_elements_table = pd.DataFrame(index=element_indices,
                                              data=[element[:2] for element in elements_data_i],
                                              columns=('Element_type', 'Stiffness'))
            new_nodes_series = pd.Series(index=element_indices,
                                         data=[element[2:] for element in elements_data_i],
                                         name='Nodes', dtype=object)

            if pos != -1:
                n_list, k_list = self.scad_repeat_line_operator(elements_data[pos])
                n2 = n_list[1]
                k_type = int(k_list[0])
                k_stiffness = int(k_list[1])
                k_nodes = k_list[2:]

                for _ in range(n2):
                    index_of_last = new_nodes_series.index.max()

                    new_elements_table.loc[index_of_last + 1] = (
                        new_elements_table.iloc[-1].Element_type + k_type,
                        new_elements_table.iloc[-1].Stiffness + k_stiffness)

                    new_nodes_series.loc[index_of_last + 1] = [new_nodes_series.iloc[-1][i] + int(k_nodes[i])
                                                                   for i in range(len(k_nodes))]

            elements_table = pd.concat([elements_table, new_elements_table], axis=0)
            nodes_series = pd.concat([nodes_series, new_nodes_series], axis=0)

        elements_table = pd.concat([elements_table, nodes_series], axis=1)
        elements_table.index = range(1, len(elements_table) + 1)

        return elements_table

    @Decorators.timed
    def import_nodes_form_txt_data(self, data: str) -> pd.DataFrame:
        nodes_table = pd.DataFrame(columns=('X', 'Y', 'Z'))

        nodes_data = re.search(r'\(4/[\d\s\w:/".,\-]+\)', data).group().replace('\n', ' ')
        while '  ' in nodes_data:
            nodes_data = nodes_data.replace('  ', ' ')
        nodes_data = nodes_data.replace('(4/', '').split('/')

        repeat_operators_positions = [-1] + [i for i in range(len(nodes_data)) if 'r' in nodes_data[i]]
        for i in range(1, len(repeat_operators_positions)):
            pos_prev = repeat_operators_positions[i-1] + 1
            pos = repeat_operators_positions[i]

            nodes_data_i = nodes_data[pos_prev:pos]
            nodes_data_i = [list(map(float, node.strip().split(' '))) for node in nodes_data_i]
            nodes_data_i = list(map(self.add_zeros, nodes_data_i))

            nodes_coordinates = np.zeros((len(nodes_data_i), 3)) + np.array(nodes_data_i)
            nodes_indices = list(range(len(nodes_table), len(nodes_table) + len(nodes_coordinates)))
            new_nodes_table = pd.DataFrame(index=nodes_indices, data=nodes_coordinates, columns=('X', 'Y', 'Z'))

            n_list, k_list = self.scad_repeat_line_operator(nodes_data[pos])

            n_2 = n_list[1]
            k_x = k_list[0]
            k_y = 0 if len(k_list) < 2 else k_list[1]
            k_z = 0 if len(k_list) < 3 else k_list[2]

            for i_repeat in range(n_2):
                new_nodes_table.loc[max(nodes_indices) + i_repeat + 1] = (new_nodes_table.iloc[-1].X + k_x,
                                                                          new_nodes_table.iloc[-1].Y + k_y,
                                                                          new_nodes_table.iloc[-1].Z + k_z)

            nodes_table = pd.concat([nodes_table, new_nodes_table], axis=0)

        nodes_table.index = list(range(1, len(nodes_table) + 1))
        return nodes_table

    @staticmethod
    def add_zeros(node: List[float]) -> List[float]:
        while len(node) < 3:
            node += [0]
        return node

    @staticmethod
    def get_element_list_from_string(s: str) -> List[int]:
        element_indices = []

        ranges = re.findall(r'\d+-\d+', s)
        for element_range in ranges:
            s = s.replace(element_range, '').replace('  ', ' ')
            element_range = element_range.split('-')
            element_indices += list(range(int(element_range[0]), int(element_range[1]) + 1))

        r_ranges = re.findall(r'\d+ r \d+ \d+', s)
        for element_range in r_ranges:
            s = s.replace(element_range, '').replace('  ', ' ')
            element_range = element_range.split(' ')
            element_indices += list(range(int(element_range[0]),
                                          int(element_range[2]) + 1,
                                          int(element_range[3])
                                          )
                                    )

        for element in s.split(' '):
            if len(element) > 0:
                element_indices.append(int(element))

        return element_indices

    @staticmethod
    def scad_repeat_line_operator(s: str) -> tuple:
        try:
            s = re.search(r'\d[\d\s]+:[\d\s.\-e]+', s).group()
        except AttributeError as e:
            raise e

        n, k = s.split(':')
        n = n.strip()
        k = k.strip()

        n_list = [int(n_i) for n_i in n.split(' ') if len(n_i) > 0]
        k_list = [float(k_i) for k_i in k.split(' ') if len(k_i) > 0]

        return n_list, k_list
