import numpy as np
from typing import List


class ReinforcementCalculator:
    def __init__(self):
        self.possible_diameters = [6, 8, 10, 12, 14, 16, 18, 20, 22, 25, 28, 32, 36, 40, 45, 50, 55, 60, 70, 80]
        self.possible_steps = [100, 125, 150, 200, 250, 300, 400, 500]

    def set_possible_reinforcement(self, diameters: List[int], steps: List[int]):
        self.possible_diameters = diameters
        self.possible_steps = steps

    def reinforcement_from_intensity(self, intensity: float, step=200, min_diameter=0) -> dict:
        diameter = 2 * np.sqrt(intensity * step / (np.pi * 1000)) * 10

        for result_diameter in self.possible_diameters:
            if result_diameter > diameter and result_diameter >= min_diameter:
                return {'diameter': result_diameter, 'step': step}

    @staticmethod
    def intensity_from_diameter_and_step(diameter: float, step: float) -> float:
        radius_mm = diameter / 2
        step_mm = step
        intensity_mm = np.pi * radius_mm ** 2 * 1000 / step_mm
        intensity_cm = intensity_mm * 0.01

        return intensity_cm
