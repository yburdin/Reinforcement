from utils.reinforcement_data import ReinforcementData
from utils.scad_data import SCADData
from utils.plots import Plotter
from structures.reinforcement_scheme import ReinforcementScheme


if __name__ == '__main__':
    asf_path = 'examples/example_1/example_1_reinforcement.asf'
    reinforcement = ReinforcementData()
    reinforcement.import_asf(asf_path)

    txt_path = 'examples/example_1/example_1_result_force_directions.txt'
    scad_data = SCADData()
    scad_data.import_txt(txt_path)

    reinforcement_scheme = ReinforcementScheme()
    reinforcement_scheme.load_reinforcement_data(reinforcement)
    reinforcement_scheme.load_scad_data(scad_data, 'Плита тест армир')

    plotter = Plotter()

    for loc in ['Top_X', 'Top_Y', 'Bot_X', 'Bot_Y']:
        plotter.plot_reinforcement_2d(reinforcement, loc, min_value=1.41)
        reinforcement_scheme.find_reinforcement_zones(loc, min_value=1.41)
        plotter.plot_reinforcement_zones_2d(reinforcement_scheme, loc)
