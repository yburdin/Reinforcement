import pandas as pd


class ReinforcementData:
    def __init__(self):
        self.nodes_table = pd.DataFrame(columns=('X', 'Y', 'Z'))
        self.elements_table = pd.Series(name='Nodes', dtype=object)
        self.reinforcement_table = pd.DataFrame(columns=('Element_center_X', 'Element_center_Y', 'Element_center_Z',
                                                         'Top_X', 'Top_Y', 'Lat_X', 'Bot_X', 'Bot_Y', 'Lat_Y'))

    def import_asf(self, path: str) -> None:
        with open(path) as f:
            data = f.read().split('\n')

        assert data[0] == '1.0 Nemetschek ALLPLAN', 'Only 1.0 Nemetschek ALLPLAN files are supported'

        line_type = None
        for line in data:
            if len(line) < 5:
                pass
            elif 'GP KNOT' in line:
                line_type = 'node'
            elif 'GF ELEM' in line:
                line_type = 'element'
            elif line[0:2] == 'QM':
                self.import_reinforcement_line(line)
            elif line[0] != ' ':
                line_type = None
            else:
                if line_type == 'node':
                    self.import_node_line(line)
                elif line_type == 'element':
                    self.import_element_line(line)

        self.calculate_element_centers()
        self.compare_tables()

    def import_node_line(self, line: str):
        split_line = [item for item in line.split(' ') if item != '']
        assert len(split_line) == 4, 'Node line import error'

        self.nodes_table.loc[int(split_line[0])] = [float(item) for item in (split_line[1:4])]

    def import_element_line(self, line: str):
        split_line = [item for item in line.split(' ') if item != '']
        self.elements_table.loc[int(split_line[0])] = [int(item) for item in (split_line[1:])]

    def import_reinforcement_line(self, line: str):
        split_line = [item for item in line.split(' ') if item != '']
        self.reinforcement_table.loc[len(self.reinforcement_table)] = [float(item) for item in (split_line[3:12])]

    def calculate_element_centers(self):
        elements_centers = pd.DataFrame(columns=('Element_center_X', 'Element_center_Y', 'Element_center_Z'))

        for i in self.elements_table.index:
            element_nodes = self.elements_table.loc[i]
            n_nodes = len(element_nodes)
            element_center_x = 0
            element_center_y = 0
            element_center_z = 0

            for node in element_nodes:
                element_center_x += self.nodes_table.loc[node, 'X']
                element_center_y += self.nodes_table.loc[node, 'Y']
                element_center_z += self.nodes_table.loc[node, 'Z']

            elements_centers.loc[i] = (element_center_x / n_nodes,
                                       element_center_y / n_nodes,
                                       element_center_z / n_nodes)

        self.elements_table = pd.concat([self.elements_table, elements_centers], axis=1)

    def compare_tables(self):
        for element in self.elements_table.index:
            element_center = self.elements_table.loc[element, ['Element_center_X',
                                                               'Element_center_Y',
                                                               'Element_center_Z']].values

            x_con = abs(self.reinforcement_table.loc[:, 'Element_center_X'] - element_center[0]) < 1e-3
            y_con = abs(self.reinforcement_table.loc[:, 'Element_center_Y'] - element_center[1]) < 1e-3
            z_con = abs(self.reinforcement_table.loc[:, 'Element_center_Z'] - element_center[2]) < 1e-3

            reinforcement_index = self.reinforcement_table.loc[x_con & y_con & z_con].iloc[0].name

            self.elements_table.loc[element, 'Reinforcement_index'] = reinforcement_index
            self.reinforcement_table.loc[reinforcement_index, 'Element_index'] = element
