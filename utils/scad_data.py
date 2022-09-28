from utils.decorators import Decorators
from typing import List
import pandas as pd
import re


class SCADData:
    def __init__(self):
        self.elements_table = None
        self.reinforcement_groups = {}

    @Decorators.timed
    def import_txt(self, path: str) -> None:
        with open(path) as f:
            data = f.read()

        self.elements_table = self.import_elements_from_txt_data(data)
        force_direction_table = self.import_force_directions_from_txt_data(data)
        self.elements_table = pd.concat([self.elements_table, force_direction_table], axis=1)

        self.reinforcement_groups = self.import_reinforcement_groups_from_txt_data(data)

    def import_force_directions_from_txt_data(self, data: str) -> pd.DataFrame:
        force_direction_table = pd.DataFrame(columns=('Rotation_type', 'Direction'))

        force_axis = re.search(r'\(33/[\s\w=:\-/.+"]+\)', data).group().replace('\n', ' ')
        force_axis = force_axis.split('/')
        force_axis = [line.replace('  ', ' ').strip() for line in force_axis if 'EX' in line or 'EY' in line]
        for line in force_axis:
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

    @staticmethod
    def import_elements_from_txt_data(data: str) -> pd.DataFrame:
        element_table = pd.DataFrame(columns=('Element_type', 'Stiffness'))
        element_series = pd.Series(name='Nodes', dtype=object)

        elements_data = re.search(r'\(1/[\d\s\w:/]+\)', data).group().replace('\n', ' ').replace('  ', ' ')
        elements_data = elements_data.split('/')
        for element_info in elements_data:
            element_info = element_info.strip()

            if ' ' not in element_info:
                continue

            if element_info[0] != 'r':
                element_info = element_info.split(' ')

                element_type = int(element_info[0])
                element_stiffness = int(element_info[1])
                nodes = [int(node) for node in element_info[2:] if len(node) > 0]

                element_table.loc[len(element_table)] = element_type, element_stiffness
                element_series.loc[len(element_series)] = nodes
            else:
                n, k = element_info[2:].split(':')
                n = n.strip()
                k = k.strip()

                n1 = int(n[0])
                n2 = 1 if len(n) < 3 else int(n[2])

                k_type = int(k[0])
                k_stiffness = int(k[2])
                k_nodes = [int(k_node) for k_node in k[4:].split(' ') if len(k_node) > 0]

                for _ in range(n2):
                    element_table.loc[len(element_table)] = (element_table.iloc[-1].Element_type + k_type,
                                                             element_table.iloc[-1].Stiffness + k_stiffness)
                    element_series.loc[len(element_series)] = [element_series.iloc[-1][i] + k_nodes[i]
                                                               for i in range(len(k_nodes))]

        element_table = pd.concat([element_table, element_series], axis=1)
        element_table.index = range(1, len(element_table) + 1)

        return element_table

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

