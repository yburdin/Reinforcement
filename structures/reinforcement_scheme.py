from utils.reinforcement_calculator import ReinforcementCalculator
from structures.reinforcement_zone import ReinforcementZone
from utils.reinforcement_data import ReinforcementData
from utils.scad_data import SCADData
from utils.decorators import Decorators
from typing import List, Optional
from numpy import intersect1d
import pandas as pd
import numpy as np


class ReinforcementScheme:
    def __init__(self):
        self.nodes_table = None
        self.elements_table = None
        self.calculator = ReinforcementCalculator()
        self.reinforcement_data = None
        self.reinforcement_zones = {'Top_X': [],
                                    'Top_Y': [],
                                    'Bot_X': [],
                                    'Bot_Y': [],
                                    'Lat_X': [],
                                    'Lat_Y': [],
                                    }
        self.scad_data = SCADData()
        self.background_reinforcement = {'diameter': 0,
                                         'step': 0}
        self.anchorage_lengths = None

    @Decorators.timed
    def load_reinforcement_data(self, reinforcement_data: ReinforcementData):
        self.reinforcement_data = reinforcement_data

    def load_anchorage_lengths(self, path: str):
        if '.csv' in path:
            self.anchorage_lengths = pd.read_csv(path, sep=';', index_col=0, header=0)
            self.anchorage_lengths.columns = ['Length']
        else:
            raise TypeError('Wrong file type')

    def load_scad_data(self, scad_data: SCADData, name: str):
        self.scad_data = SCADData()
        self.scad_data.elements_table = scad_data.elements_table.loc[scad_data.reinforcement_groups[name]]
        self.scad_data.nodes_table = scad_data.nodes_table

    @Decorators.timed
    def find_reinforcement_zones(self, location, min_value=None):
        assert isinstance(self.elements_table, pd.DataFrame), 'No reinforcement data'

        if min_value is None:
            min_value = self.background_reinforcement_intensity

        reinforced_elements = self.elements_table.query(f'{location} > {min_value}')
        reinforced_elements_indices = reinforced_elements.index.to_list()

        while len(reinforced_elements_indices) > 0:
            first_element = reinforced_elements_indices.pop(0)
            first_element_nodes = self.elements_table.loc[first_element].Nodes

            zone = ReinforcementZone()
            zone.add_one_element_to_zone(first_element, first_element_nodes)

            while True:
                next_elements = self.find_elements_with_nodes(self.elements_table, zone.nodes)
                next_elements = intersect1d(next_elements, reinforced_elements_indices)

                if len(next_elements) > 0:
                    nodes = np.stack(self.elements_table.loc[next_elements].Nodes.values).flatten()
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

    @Decorators.timed
    def transfer_reinforcement_direction_to_zones(self):
        for location in self.reinforcement_zones.keys():
            for zone in self.reinforcement_zones[location][:]:
                zone_directions = self.elements_table.loc[zone.elements, ['Rotation_type', 'Direction']]

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
                        new_zone_elements = new_zone_indices.to_list()
                        new_zone_nodes = np.stack(self.elements_table.loc[new_zone_elements].Nodes.values)
                        new_zone_nodes = np.unique(new_zone_nodes)

                        new_zone = ReinforcementZone()
                        new_zone.add_multiple_elements_to_zone(new_zone_elements, new_zone_nodes)

                        if rotation_type == 'EX':
                            new_zone.set_reinforcement_direction(*direction)

                        new_zone.set_bounding_rectangle(self.get_zone_bounding_rectangle(new_zone))

                        self.reinforcement_zones[location].append(new_zone)

                    self.reinforcement_zones[location].remove(zone)

    def get_zone_bounding_rectangle(self, zone: ReinforcementZone) -> np.array:
        zone_nodes = self.nodes_table.loc[zone.nodes]

        rotation_matrix = self.make_rotation_matrix_2d(*zone.reinforcement_direction[:2])
        zone_nodes_coordinates = zone_nodes.loc[:, ['X', 'Y']]
        local_coordinates = (np.linalg.inv(rotation_matrix) @ zone_nodes_coordinates.values.T).T

        min_x_local, min_y_local = local_coordinates[:, 0].min(), local_coordinates[:, 1].min()
        max_x_local, max_y_local = local_coordinates[:, 0].max(), local_coordinates[:, 1].max()

        points_local = np.array([[min_x_local, min_y_local],
                                 [min_x_local, max_y_local],
                                 [max_x_local, max_y_local],
                                 [max_x_local, min_y_local],
                                 ])
        points_global = rotation_matrix @ points_local.T
        return points_global

    def set_background_reinforcement(self, reinforcement_data: Optional[ReinforcementData] = None, auto: bool = True,
                                     reinforcement: Optional[dict] = None, intensity: Optional[float] = 0.):

        if auto:
            quantiles = reinforcement_data.reinforcement_table.loc[:, ['Top_X', 'Top_Y',
                                                                       'Bot_X', 'Bot_Y']].quantile(0.8)
            self.background_reinforcement = self.calculator.reinforcement_from_intensity(quantiles.max())
        else:
            if reinforcement is not None and intensity == 0:
                assert 'diameter' in reinforcement, 'No diameter in manual background reinforcement'
                assert 'step' in reinforcement, 'No step in manual background reinforcement'

                self.background_reinforcement = {'diameter': reinforcement['diameter'],
                                                 'step': reinforcement['step']}
            elif reinforcement is None and intensity > 0:
                self.background_reinforcement = self.calculator.reinforcement_from_intensity(intensity)
            else:
                raise ValueError('Manual background reinforcement error')

    def set_zones_reinforcement(self):
        for location in self.reinforcement_zones:
            for zone in self.reinforcement_zones[location]:  # type: ReinforcementZone
                max_intensity = self.elements_table.loc[zone.elements, location].max()

                zone.max_intensity = max_intensity
                zone.background_reinforcement = self.background_reinforcement
                zone.background_reinforcement_intensity = self.background_reinforcement_intensity

                if self.anchorage_lengths is not None:
                    zone.anchorage_lengths = self.anchorage_lengths

    @Decorators.timed
    def make_combined_table(self):
        elements_table = self.reinforcement_data.elements_table
        direction_series = pd.Series(name='Direction', dtype=object)

        centers_table = self.calculate_element_centers(self.scad_data.elements_table.Nodes, self.scad_data.nodes_table)
        self.scad_data.elements_table = pd.concat([self.scad_data.elements_table, centers_table], axis=1)

        for element in elements_table.index:
            element_center = elements_table.loc[element, ['Element_center_X',
                                                          'Element_center_Y',
                                                          'Element_center_Z']].values

            x_con = abs(self.reinforcement_data.reinforcement_table.loc[:, 'Element_center_X'] -
                        element_center[0]) < 1e-3
            y_con = abs(self.reinforcement_data.reinforcement_table.loc[:, 'Element_center_Y'] -
                        element_center[1]) < 1e-3
            z_con = abs(self.reinforcement_data.reinforcement_table.loc[:, 'Element_center_Z'] -
                        element_center[2]) < 1e-3

            reinforcement_index = self.reinforcement_data.reinforcement_table.loc[x_con & y_con & z_con].iloc[0].name
            for column in ['Top_X', 'Top_Y', 'Lat_X', 'Bot_X', 'Bot_Y', 'Lat_Y']:
                elements_table.loc[element, column] = self.reinforcement_data.reinforcement_table.loc[
                    reinforcement_index, column]

            x_con = abs(self.scad_data.elements_table.loc[:, 'Element_center_X'] - element_center[0]) < 1e-3
            y_con = abs(self.scad_data.elements_table.loc[:, 'Element_center_Y'] - element_center[1]) < 1e-3
            z_con = abs(self.scad_data.elements_table.loc[:, 'Element_center_Z'] - element_center[2]) < 1e-3
            scad_element = self.scad_data.elements_table.loc[x_con & y_con & z_con].iloc[0]
            scad_index = scad_element.name
            elements_table.loc[element, 'Rotation_type'] = self.scad_data.elements_table.loc[scad_index,
                                                                                             'Rotation_type']
            direction_series.loc[element] = self.scad_data.elements_table.loc[scad_index, 'Direction']

        elements_table = pd.concat([elements_table, direction_series], axis=1)

        self.elements_table = elements_table
        self.nodes_table = self.reinforcement_data.nodes_table

        self.reinforcement_data = None
        self.scad_data = None

    @Decorators.timed
    def make_combined_table_test(self):
        centers_table = self.calculate_element_centers(self.scad_data.elements_table.Nodes, self.scad_data.nodes_table)
        self.scad_data.elements_table = pd.concat([self.scad_data.elements_table, centers_table], axis=1)

        scad_index = self.scad_data.elements_table.sort_values(by=['Element_center_X',
                                                                   'Element_center_Y',
                                                                   'Element_center_Z']).index
        reinforcement_index = self.reinforcement_data.reinforcement_table.sort_values(by=['Element_center_X',
                                                                                          'Element_center_Y',
                                                                                          'Element_center_Z']).index
        asf_index = self.reinforcement_data.elements_table.sort_values(by=['Element_center_X',
                                                                           'Element_center_Y',
                                                                           'Element_center_Z']).index

        asf_columns = self.reinforcement_data.elements_table.columns
        # scad_columns = self.scad_data.elements_table.columns
        scad_columns = ['Rotation_type', 'Direction']
        reinforcement_columns = [column for column in self.reinforcement_data.reinforcement_table.columns
                                 if column not in asf_columns]

        self.elements_table = pd.concat(
            [
                self.reinforcement_data.elements_table.loc[asf_index].reset_index(drop=True),
                self.reinforcement_data.reinforcement_table.loc[reinforcement_index,
                                                                reinforcement_columns].reset_index(drop=True),
                self.scad_data.elements_table.loc[scad_index, scad_columns].reset_index(drop=True),
            ], axis=1)

        # self.nodes_table = self.scad_data.nodes_table
        self.nodes_table = self.reinforcement_data.nodes_table

        # self.reinforcement_data = None
        # self.scad_data = None

    @staticmethod
    def make_rotation_matrix_2d(x, y) -> np.array:
        tan_alpha = y / (x + 1e-9)
        alpha = np.arctan(tan_alpha)

        return np.array([[np.cos(alpha), -np.sin(alpha)],
                         [np.sin(alpha), np.cos(alpha)]])

    @property
    def background_reinforcement_intensity(self) -> float:
        return self.calculator.intensity_from_diameter_and_step(self.background_reinforcement['diameter'],
                                                                self.background_reinforcement['step'])

    @staticmethod
    @Decorators.timed
    def calculate_element_centers(element_nodes: pd.Series, nodes_table: pd.DataFrame) -> pd.DataFrame:
        centers_table = pd.DataFrame(columns=('Element_center_X', 'Element_center_Y', 'Element_center_Z',))

        for n, element in enumerate(element_nodes.index):
            nodes = element_nodes.loc[element]
            nodes_coordinates = nodes_table.loc[nodes, ['X', 'Y', 'Z']]
            centers_table.loc[element] = nodes_coordinates.mean().values

        return centers_table
