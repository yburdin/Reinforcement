from typing import Iterable
import numpy as np


class ReinforcementZone:
    def __init__(self):
        self.elements = np.array([])
        self.nodes = np.array([])

    def add_one_element_to_zone(self, element: int, nodes: Iterable):
        if element not in self.elements:
            self.elements = np.append(self.elements, element)
            self.nodes = np.union1d(self.nodes, nodes)

    def add_multiple_elements_to_zone(self, elements: Iterable, nodes: Iterable):
        self.elements = np.union1d(self.elements, elements)
        self.nodes = np.union1d(self.nodes, nodes)