from utils.imports import ReinforcementData


class ReinforcementScheme:
    def __init__(self):
        self.reinforcement_data = None
        self.reinforcement_zones = []
        self.background_reinforcement = 0

    def load_reinforcement_data(self, reinforcement_data: ReinforcementData):
        self.reinforcement_data = reinforcement_data

    def find_reinforcement_zones(self):
        pass
