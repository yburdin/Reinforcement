from typing import Iterable
from utils.reinforcement_calculator import ReinforcementCalculator
import numpy as np


class ReinforcementZone:
    def __init__(self):
        self.elements = np.array([])
        self.nodes = np.array([])
        self.reinforcement_direction = [0, 0, 0]
        self.bounding_rectangle = None
        self.max_intensity = None
        self.background_reinforcement_intensity = None
        self.background_reinforcement = None
        self.anchorage_lengths = None

    def add_one_element_to_zone(self, element: int, nodes: Iterable):
        if element not in self.elements:
            self.elements = np.append(self.elements, element)

            nodes = [node for node in nodes if node != 0]
            self.nodes = np.union1d(self.nodes, nodes)

    def add_multiple_elements_to_zone(self, elements: Iterable, nodes: Iterable):
        self.elements = np.union1d(self.elements, elements)

        nodes = [node for node in nodes if node != 0]
        self.nodes = np.union1d(self.nodes, nodes)

    def set_reinforcement_direction(self, x: float, y: float, z: float):
        self.reinforcement_direction[0:3] = x, y, z

    def set_bounding_rectangle(self, points: Iterable):
        points = np.array(points)
        if len(points.shape) == 2:
            if points.shape[0] == 2:
                self.bounding_rectangle = points.T
            elif points.shape[1] == 2:
                self.bounding_rectangle = points
            else:
                raise ValueError('Wrong shape of bounding rectangle points array')
        else:
            raise ValueError('Bounding rectangle points array is not 2d')

    @property
    def dimensions(self):
        rotation_matrix = self.make_rotation_matrix_2d(*self.reinforcement_direction[:2])
        points = (np.linalg.inv(rotation_matrix) @ self.bounding_rectangle.T).T
        x_dim = abs(points[:, 0].max() - points[:, 0].min())
        y_dim = abs(points[:, 1].max() - points[:, 1].min())

        return x_dim, y_dim

    @property
    def additional_reinforcement(self) -> dict:
        calculator = ReinforcementCalculator()
        additional_intensity = self.max_intensity - self.background_reinforcement_intensity
        additional_reinforcement_dict = {}

        step = self.background_reinforcement['step']
        background_diameter = self.background_reinforcement['diameter']
        for _ in range(3):
            if step in calculator.possible_steps:
                additional_reinforcement = calculator.reinforcement_from_intensity(additional_intensity,
                                                                                   step,
                                                                                   min_diameter=background_diameter)
                diameter, step = additional_reinforcement['diameter'], additional_reinforcement['step']
                intensity = calculator.intensity_from_diameter_and_step(diameter, step)
                additional_reinforcement_dict[intensity] = additional_reinforcement

                step //= 2

        min_intensity = min(additional_reinforcement_dict.keys())

        return additional_reinforcement_dict[min_intensity]

    @property
    def midpoint(self) -> tuple:
        return np.average(self.bounding_rectangle[:, 0]), np.average(self.bounding_rectangle[:, 1])

    @property
    def dimensions_adjusted(self) -> tuple:
        diameter, step = [self.additional_reinforcement[value] for value in ['diameter', 'step']]
        x_m, y_m = self.dimensions
        x_mm, y_mm = x_m * 1000, y_m * 1000

        anchorage_length_mm = self.anchorage_lengths.loc[diameter, 'Length']

        x_mm_rounded = np.ceil(x_mm / 10) * 10
        x_mm_adjusted = x_mm_rounded + 2 * anchorage_length_mm

        y_mm_adjusted = ((y_mm // step) + 1) * step

        return x_mm_adjusted / 1000, y_mm_adjusted / 1000

    @property
    def bounding_rectangle_adjusted(self) -> np.array:
        scale = [self.dimensions_adjusted[i] / self.dimensions[i] for i in range(2)]

        rotation_matrix = self.make_rotation_matrix_2d(*self.reinforcement_direction[:2])

        scale_matrix = np.array([[scale[0], 0],
                                 [0, scale[1]]])
        transform_matrix = rotation_matrix @ scale_matrix @ np.linalg.inv(rotation_matrix)

        rect_scaled = (transform_matrix @ self.bounding_rectangle.T).T
        midpoint_scaled = np.average(rect_scaled[:, 0]), np.average(rect_scaled[:, 1])

        translation = np.array([[self.midpoint[i] - midpoint_scaled[i] for i in range(2)]
                                for _ in range(len(rect_scaled))])

        rect_scaled_translated = rect_scaled + translation

        return rect_scaled_translated

    @staticmethod
    def make_rotation_matrix_2d(x, y) -> np.array:
        tan_alpha = y / (x + 1e-9)
        alpha = np.arctan(tan_alpha)

        return np.array([[np.cos(alpha), -np.sin(alpha)],
                         [np.sin(alpha), np.cos(alpha)]])

    @property
    def alpha(self) -> float:
        x, y = self.reinforcement_direction[:2]
        tan_alpha = y / (x + 1e-9)
        return np.arctan(tan_alpha)
