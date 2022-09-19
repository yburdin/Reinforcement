from typing import List


class ReinforcementZone:
    def __init__(self):
        self.elements = []
        self.nodes = []

    def add_to_zone(self, element: int, nodes: List[int]):
        if element not in self.elements:
            self.elements.append(element)

        for node in nodes:
            if node not in self.nodes:
                self.nodes.append(node)
