import numpy as np

from utils.scad_data import SCADData
from utils.reinforcement_data import ReinforcementData
from structures.reinforcement_scheme import ReinforcementScheme
import unittest
import pandas as pd


class ImportTest(unittest.TestCase):
    def test_import_elements_from_txt(self):
        data = '(1/2 15 3 10/ r 1 5: 0 0 1 1/ 51 21 12/ 31 2 34 35 40 41 22 23 28 29/ 21 1 11 14 18 19/ 12 1 12 15 27/)'
        element_table = SCADData().import_elements_from_txt_data(data)

        self.assertEqual(len(element_table), 10)
        self.assertEqual(element_table.Element_type.to_list(), [2, 2, 2, 2, 2, 2, 51, 31, 21, 12])
        self.assertEqual(element_table.Stiffness.to_list(), [15, 15, 15, 15, 15, 15, 21, 2, 1, 1])
        self.assertEqual(element_table.loc[1, 'Nodes'], [3, 10])
        self.assertEqual(element_table.loc[2, 'Nodes'], [4, 11])
        self.assertEqual(element_table.loc[3, 'Nodes'], [5, 12])
        self.assertEqual(element_table.loc[4, 'Nodes'], [6, 13])
        self.assertEqual(element_table.loc[5, 'Nodes'], [7, 14])
        self.assertEqual(element_table.loc[6, 'Nodes'], [8, 15])
        self.assertEqual(element_table.loc[7, 'Nodes'], [12])
        self.assertEqual(element_table.loc[8, 'Nodes'], [34, 35, 40, 41, 22, 23, 28, 29])
        self.assertEqual(element_table.loc[9, 'Nodes'], [11, 14, 18, 19])
        self.assertEqual(element_table.loc[10, 'Nodes'], [12, 15, 27])

    def test_get_elements_from_txt(self):
        with self.subTest(msg='Testcase 1'):
            string = '1-5'
            result = [1, 2, 3, 4, 5]
            self.assertEqual(SCADData.get_element_list_from_string(string), result)

        with self.subTest(msg='Testcase 2'):
            string = '1 r 17 4'
            result = [1, 5, 9, 13, 17]
            self.assertEqual(SCADData.get_element_list_from_string(string), result)

        with self.subTest(msg='Testcase 3'):
            string = '1 2 3'
            result = [1, 2, 3]
            self.assertEqual(SCADData.get_element_list_from_string(string), result)

        with self.subTest(msg='Testcase 4'):
            string = '1-5 6 r 12 3 13 14'
            result = [1, 2, 3, 4, 5, 6, 9, 12, 13, 14]
            self.assertEqual(SCADData.get_element_list_from_string(string), result)

    def test_get_nodes_from_txt(self):
        with self.subTest(msg='Testcase 1'):
            string = '(4/1.5 2.8/ 2.3 3.7 8.8/ 5/r 1 5: 0 0 2/)'
            nodes_table = SCADData().import_nodes_form_txt_data(string)

            self.assertEqual(len(nodes_table), 8)
            self.assertEqual(nodes_table.index.tolist(), list(range(1, 9)))
            self.assertEqual(nodes_table.X.tolist(), [1.5, 2.3, 5, 5, 5, 5, 5, 5])
            self.assertEqual(nodes_table.Y.tolist(), [2.8, 3.7, 0, 0, 0, 0, 0, 0])
            self.assertEqual(nodes_table.Z.tolist(), [0, 8.8, 0, 2, 4, 6, 8, 10])

    def test_scad_repeat_line_operator(self):
        with self.subTest('Testcase 1'):
            string = 'r 1 5: 0 0 2'
            result = ([1, 5], [0, 0, 2])

            self.assertEqual(SCADData.scad_repeat_line_operator(string), result)

        with self.subTest('Testcase 2'):
            string = 'r 1 5: 0 0 1 1'
            result = ([1, 5], [0, 0, 1, 1])

            self.assertEqual(SCADData.scad_repeat_line_operator(string), result)

        with self.subTest('Testcase 2'):
            string = 'r 1 5: 0 0 1 1'
            result = ([1, 5], [0, 0, 1, 1])

            self.assertEqual(SCADData.scad_repeat_line_operator(string), result)

    def test_calculate_element_center(self):
        with self.subTest('Testcase 1'):
            element_series = pd.Series(data=[[1, 2, 3, 4]], dtype=object, name='Nodes')
            nodes_table = pd.DataFrame(data={'X': [0, 50, 50, 0], 'Y': [0, 0, 100, 100], 'Z': [0, 0, 0, 0]},
                                       index=[1, 2, 3, 4])
            centers = ReinforcementScheme.calculate_element_centers(element_series, nodes_table)

            self.assertEqual(centers.loc[0].Element_center_X, 25)
            self.assertEqual(centers.loc[0].Element_center_Y, 50)
            self.assertEqual(centers.loc[0].Element_center_Z, 0)

    def test_import_polygons(self):
        data = 'GL POLY 4\n   1.313   8.849   9.990\n   0.713   8.849   9.990\n   0.713   6.949   9.990\n   1.313   ' \
               '6.949   9.990\nGL POLY 4\n   0.963   4.769   9.990\n   0.713   4.769   9.990\n   0.713   4.369   ' \
               '9.990\n   0.963   4.369   9.990\nGP KNOT 50'
        expected_result = [
            np.array([[1.313, 8.849, 9.990],
                      [0.713, 8.849, 9.990],
                      [0.713, 6.949, 9.990],
                      [1.313, 6.949, 9.990]
                      ]),
            np.array([[0.963, 4.769, 9.990],
                      [0.713, 4.769, 9.990],
                      [0.713, 4.369, 9.990],
                      [0.963, 4.369, 9.990]
                      ]),
        ]

        for n in range(len(expected_result)):
            for k in range(len(expected_result[n])):
                with self.subTest(f'{n=}, {k=}'):
                    self.assertCountEqual(ReinforcementData.import_polygons(data)[n][k], expected_result[n][k])


if __name__ == '__main__':
    unittest.main()
