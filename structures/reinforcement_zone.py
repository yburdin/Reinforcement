from typing import Iterable
import numpy as np


class ReinforcementZone:
    def __init__(self):
        self.elements = np.array([])
        self.nodes = np.array([])
        self.reinforcement_direction = [0, 0, 0]
        self.bounding_rectangle = None

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

