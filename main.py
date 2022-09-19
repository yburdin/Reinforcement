from utils.imports import ReinforcementData
from utils.plots import Plotter
from structures.reinforcement_scheme import ReinforcementScheme


if __name__ == '__main__':
    asf_path = 'examples/example_1/example_1_reinforcement.asf'
    reinforcement = ReinforcementData()
    reinforcement.import_asf(asf_path)

    reinforcement_scheme = ReinforcementScheme()
    reinforcement_scheme.load_reinforcement_data(reinforcement)
    plotter = Plotter()

    for loc in ['Top_X', 'Top_Y', 'Bot_X', 'Bot_Y']:
        plotter.plot_reinforcement_2d(reinforcement, loc, min_value=1.41)
        reinforcement_scheme.find_reinforcement_zones(loc, min_value=1.41)
        plotter.plot_reinforcement_zones_2d(reinforcement_scheme, loc)
