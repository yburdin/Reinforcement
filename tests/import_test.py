from utils.scad_data import SCADData
import unittest


class ImportTest(unittest.TestCase):
    def test_import_elements_from_txt(self):
        data = '(1/2 15 3 10/ r 1 5: 0 0 1 1/ 51 21 12/ 31 2 34 35 40 41 22 23 28 29/ 21 1 11 14 18 19/ 12 1 12 15 27/)'
        element_table = SCADData.import_elements_from_txt_data(data)

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

    def test_get_elements_from_string(self):
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


if __name__ == '__main__':
    unittest.main()
