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

    def add_one_element_to_zone(self, element: int, nodes: Iterable):
        if element not in self.elements:
            self.elements = np.append(self.elements, element)
            self.nodes = np.union1d(self.nodes, nodes)

    def add_multiple_elements_to_zone(self, elements: Iterable, nodes: Iterable):
        self.elements = np.union1d(self.elements, elements)
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
        p1 = complex(*self.bounding_rectangle[0])
        p2 = complex(*self.bounding_rectangle[1])
        p3 = complex(*self.bounding_rectangle[2])

        return abs(p2-p1), abs(p3-p2)

    @property
    def additional_reinforcement(self) -> dict:
        calculator = ReinforcementCalculator()
        additional_intensity = self.max_intensity - self.background_reinforcement_intensity
        additional_reinforcement_dict = {}

        step = self.background_reinforcement['step']
        for _ in range(3):
            if step in calculator.possible_steps:
                additional_reinforcement = calculator.reinforcement_from_intensity(additional_intensity,
                                                                                   step)
                diameter, step = additional_reinforcement['diameter'], additional_reinforcement['step']
                intensity = calculator.intensity_from_diameter_and_step(diameter, step)
                additional_reinforcement_dict[intensity] = additional_reinforcement

                step //= 2

        min_intensity = min(additional_reinforcement_dict.keys())

        return additional_reinforcement_dict[min_intensity]

    @property
    def midpoint(self) -> tuple:
        return np.average(self.bounding_rectangle[:, 0]), np.average(self.bounding_rectangle[:, 1])
