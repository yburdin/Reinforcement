from utils.imports import ReinforcementData
from utils.plots import Plotter


if __name__ == '__main__':
    asf_path = 'examples/example_1/example_1_reinforcement.asf'
    reinforcement = ReinforcementData()
    reinforcement.import_asf(asf_path)

    plotter = Plotter()
    for loc in ['Top_X', 'Top_Y', 'Bot_X', 'Bot_Y', ]:
        plotter.plot_reinforcement_2d(reinforcement, loc, min_value=1.41)
