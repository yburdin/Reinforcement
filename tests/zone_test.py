import unittest
import numpy as np
import pandas as pd

from structures.reinforcement_zone import ReinforcementZone


class ZoneTest(unittest.TestCase):
    def test_dimensions(self):
        with self.subTest('Testcase 1'):
            zone = ReinforcementZone()
            zone.bounding_rectangle = np.array([[0, 0],
                                                [5, 0],
                                                [5, 10],
                                                [0, 10]
                                                ])
            zone.reinforcement_direction = [0, 3, 0]

            self.assertAlmostEqual(zone.dimensions[0], 10)
            self.assertAlmostEqual(zone.dimensions[1], 5)

        with self.subTest('Testcase 2'):
            zone = ReinforcementZone()
            zone.bounding_rectangle = np.array([[5, 0],
                                                [5, 10],
                                                [0, 10],
                                                [0, 0],
                                                ])
            zone.reinforcement_direction = [0, 3, 0]

            self.assertAlmostEqual(zone.dimensions[0], 10)
            self.assertAlmostEqual(zone.dimensions[1], 5)

        with self.subTest('Testcase 3'):
            zone = ReinforcementZone()
            zone.bounding_rectangle = np.array([[5, 10],
                                                [0, 10],
                                                [0, 0],
                                                [5, 0],
                                                ])
            zone.reinforcement_direction = [0, 3, 0]

            self.assertAlmostEqual(zone.dimensions[0], 10)
            self.assertAlmostEqual(zone.dimensions[1], 5)

        with self.subTest('Testcase 3'):
            zone = ReinforcementZone()
            zone.bounding_rectangle = np.array([[0, 10],
                                                [0, 0],
                                                [5, 0],
                                                [5, 10],
                                                ])
            zone.reinforcement_direction = [0, 3, 0]

            self.assertAlmostEqual(zone.dimensions[0], 10)
            self.assertAlmostEqual(zone.dimensions[1], 5)

    def test_additional_reinforcement(self):
        zone = ReinforcementZone()

        with self.subTest('Testcase 1'):
            zone.background_reinforcement_intensity = 3.93
            zone.background_reinforcement = {'diameter': 10, 'step': 200}

            zone.max_intensity = 3.93 + 1.40

            self.assertEqual(zone.additional_reinforcement['diameter'], 6)
            self.assertEqual(zone.additional_reinforcement['step'], 200)

        with self.subTest('Testcase 2'):
            zone.background_reinforcement_intensity = 3.93
            zone.background_reinforcement = {'diameter': 10, 'step': 200}

            zone.max_intensity = 3.93 + 2.82

            self.assertEqual(zone.additional_reinforcement['diameter'], 6)
            self.assertEqual(zone.additional_reinforcement['step'], 100)

    def test_adjusted_dimensions(self):
        with self.subTest('Testcase 1'):
            zone = ReinforcementZone()
            zone.bounding_rectangle = np.array([[0, 0],
                                                [0.1, 0],
                                                [0.1, 10],
                                                [0, 10]
                                                ])
            zone.reinforcement_direction = [0, 3, 0]

            zone.anchorage_lengths = pd.DataFrame(index=[6, 8, 10], data=[2000, 2000, 2000], columns=('Length',))

            zone.background_reinforcement_intensity = 3.93
            zone.background_reinforcement = {'diameter': 10, 'step': 200}
            zone.max_intensity = 3.93 + 1.40

            self.assertAlmostEqual(zone.dimensions_adjusted[0], 14, delta=0.1)
            self.assertAlmostEqual(zone.dimensions_adjusted[1], 0.2, delta=0.01)

    def test_bounding_rectangle_adjusted(self):
        with self.subTest('Testcase 1'):
            zone = ReinforcementZone()
            zone.bounding_rectangle = np.array([[0, 0],
                                                [0.1, 0],
                                                [0.1, 1],
                                                [0, 1]
                                                ])
            zone.reinforcement_direction = [0, 3, 0]

            zone.anchorage_lengths = pd.DataFrame(index=[6, 8, 10], data=[1000, 1000, 1000], columns=('Length',))

            zone.background_reinforcement_intensity = 3.93
            zone.background_reinforcement = {'diameter': 10, 'step': 200}
            zone.max_intensity = 3.93 + 1.40

            self.assertAlmostEqual(zone.bounding_rectangle_adjusted[0, 0], -0.05, delta=0.01)
            self.assertAlmostEqual(zone.bounding_rectangle_adjusted[0, 1], -1, delta=0.1)

            self.assertAlmostEqual(zone.bounding_rectangle_adjusted[1, 0], 0.15, delta=0.01)
            self.assertAlmostEqual(zone.bounding_rectangle_adjusted[1, 1], -1, delta=0.1)

            self.assertAlmostEqual(zone.bounding_rectangle_adjusted[2, 0], 0.15, delta=0.01)
            self.assertAlmostEqual(zone.bounding_rectangle_adjusted[2, 1], 2, delta=0.1)

            self.assertAlmostEqual(zone.bounding_rectangle_adjusted[3, 0], -0.05, delta=0.01)
            self.assertAlmostEqual(zone.bounding_rectangle_adjusted[3, 1], 2, delta=0.1)

        with self.subTest('Testcase 2'):
            zone = ReinforcementZone()
            zone.bounding_rectangle = np.array([[0.1, 0],
                                                [0.1, 1],
                                                [0, 1],
                                                [0, 0],
                                                ])
            zone.reinforcement_direction = [0, 3, 0]

            zone.anchorage_lengths = pd.DataFrame(index=[6, 8, 10], data=[1000, 1000, 1000], columns=('Length',))

            zone.background_reinforcement_intensity = 3.93
            zone.background_reinforcement = {'diameter': 10, 'step': 200}
            zone.max_intensity = 3.93 + 1.40

            self.assertAlmostEqual(zone.bounding_rectangle_adjusted[0, 0], 0.15, delta=0.01)
            self.assertAlmostEqual(zone.bounding_rectangle_adjusted[0, 1], -1, delta=0.1)

            self.assertAlmostEqual(zone.bounding_rectangle_adjusted[1, 0], 0.15, delta=0.01)
            self.assertAlmostEqual(zone.bounding_rectangle_adjusted[1, 1], 2, delta=0.1)

            self.assertAlmostEqual(zone.bounding_rectangle_adjusted[2, 0], -0.05, delta=0.01)
            self.assertAlmostEqual(zone.bounding_rectangle_adjusted[2, 1], 2, delta=0.1)

            self.assertAlmostEqual(zone.bounding_rectangle_adjusted[3, 0], -0.05, delta=0.01)
            self.assertAlmostEqual(zone.bounding_rectangle_adjusted[3, 1], -1, delta=0.1)

        with self.subTest('Testcase 3'):
            zone = ReinforcementZone()
            zone.bounding_rectangle = np.array([[0.1, 1],
                                                [0, 1],
                                                [0, 0],
                                                [0.1, 0],
                                                ])
            zone.reinforcement_direction = [0, 3, 0]

            zone.anchorage_lengths = pd.DataFrame(index=[6, 8, 10], data=[1000, 1000, 1000], columns=('Length',))

            zone.background_reinforcement_intensity = 3.93
            zone.background_reinforcement = {'diameter': 10, 'step': 200}
            zone.max_intensity = 3.93 + 1.40

            self.assertAlmostEqual(zone.bounding_rectangle_adjusted[0, 0], 0.15, delta=0.01)
            self.assertAlmostEqual(zone.bounding_rectangle_adjusted[0, 1], 2, delta=0.1)

            self.assertAlmostEqual(zone.bounding_rectangle_adjusted[1, 0], -0.05, delta=0.01)
            self.assertAlmostEqual(zone.bounding_rectangle_adjusted[1, 1], 2, delta=0.1)

            self.assertAlmostEqual(zone.bounding_rectangle_adjusted[2, 0], -0.05, delta=0.01)
            self.assertAlmostEqual(zone.bounding_rectangle_adjusted[2, 1], -1, delta=0.1)

            self.assertAlmostEqual(zone.bounding_rectangle_adjusted[3, 0], 0.15, delta=0.01)
            self.assertAlmostEqual(zone.bounding_rectangle_adjusted[3, 1], -1, delta=0.1)

        with self.subTest('Testcase 4'):
            zone = ReinforcementZone()
            zone.bounding_rectangle = np.array([[2.25, 1.25],
                                                [3.75, 2.75],
                                                [5.25, 1.25],
                                                [3.75, -0.25]])

            zone.reinforcement_direction = [3.0, 3.0, 0]

            zone.anchorage_lengths = pd.DataFrame(index=[6, 8, 10], data=[310, 350, 400], columns=('Length',))

            zone.background_reinforcement_intensity = 1.413716694115407
            zone.background_reinforcement = {'diameter': 6, 'step': 200}
            zone.max_intensity = 4.61

            self.assertAlmostEqual(zone.bounding_rectangle_adjusted[0, 0], 1.936, delta=0.01)
            self.assertAlmostEqual(zone.bounding_rectangle_adjusted[0, 1], 0.992, delta=0.01)

            self.assertAlmostEqual(zone.bounding_rectangle_adjusted[1, 0], 4.008, delta=0.01)
            self.assertAlmostEqual(zone.bounding_rectangle_adjusted[1, 1], 3.063, delta=0.01)

            self.assertAlmostEqual(zone.bounding_rectangle_adjusted[2, 0], 5.563, delta=0.01)
            self.assertAlmostEqual(zone.bounding_rectangle_adjusted[2, 1], 1.508, delta=0.01)

            self.assertAlmostEqual(zone.bounding_rectangle_adjusted[3, 0], 3.492, delta=0.01)
            self.assertAlmostEqual(zone.bounding_rectangle_adjusted[3, 1], -0.564, delta=0.01)




if __name__ == '__main__':
    unittest.main()
