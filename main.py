from utils.reinforcement_data import ReinforcementData
from utils.scad_data import SCADData
from utils.plots import Plotter
from structures.reinforcement_scheme import ReinforcementScheme


if __name__ == '__main__':
    example_name = 'example_2'
    asf_path = f'examples/{example_name}/{example_name}.asf'
    reinforcement = ReinforcementData()
    reinforcement.import_asf(asf_path)

    txt_path = f'examples/{example_name}/{example_name}.txt'
    scad_data = SCADData()
    scad_data.import_txt(txt_path)

    reinforcement_scheme = ReinforcementScheme()
    reinforcement_scheme.load_reinforcement_data(reinforcement)
    reinforcement_scheme.load_scad_data(scad_data, 'Плита')

    plotter = Plotter()

    for loc in ['Top_X',
                # 'Top_Y', 'Bot_X', 'Bot_Y'
                ]:
        plotter.plot_reinforcement_2d(reinforcement, loc, min_value=1.41)
        reinforcement_scheme.find_reinforcement_zones(loc, min_value=1.41)
        reinforcement_scheme.transfer_reinforcement_direction_to_zones()
        plotter.plot_reinforcement_zones_2d(reinforcement_scheme, loc)
