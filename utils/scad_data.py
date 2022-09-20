from utils.decorators import Decorators
from typing import List
import pandas as pd
import re


class SCADData:
    def __init__(self):
        self.elements_table = pd.DataFrame(columns=('Rotation_type', 'Direction'))
        self.reinforcement_groups = {}

    @Decorators.timed
    def import_txt(self, path: str) -> None:
        with open(path) as f:
            data = f.read()

        self.import_force_directions_from_txt_data(data)
        self.import_reinforcement_groups_from_txt_data(data)

    def import_force_directions_from_txt_data(self, data: str) -> None:
        force_axis = re.search(r'\(33/[\s\w=:\-/.]+\)', data).group().split('\n')
        force_axis = [line.replace('  ', ' ').split(':') for line in force_axis if 'EX' in line or 'EY' in line]
        for line in force_axis:
            line_info, elements = line

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
            self.elements_table = pd.concat([self.elements_table, new_frame])

    def import_reinforcement_groups_from_txt_data(self, data: str) -> None:
        reinforcement_groups = re.search(r'\(53/[\w\s\d=\".:\-/]+\)', data).group().split('/')
        for line in reinforcement_groups:
            if 'Name' in line:
                name = re.search(r'Name="[\w\s\d]+"', line).group().split('"')[1]
                elements = line.split(':')[-1].replace('\n', '')

                element_indices = self.get_element_list_from_string(elements)
                self.reinforcement_groups[name] = element_indices

    @staticmethod
    def get_element_list_from_string(s: str) -> List[int]:
        element_indices = []

        for element in s.split(' '):
            if '-' in element:
                element_range = element.replace('/', '').split('-')
                element_indices += list(range(int(element_range[0]), int(element_range[1]) + 1))
            else:
                element_indices.append(int(element))

        return element_indices

