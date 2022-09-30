from structures.reinforcement_scheme import ReinforcementScheme
from utils.reinforcement_data import ReinforcementData
from utils.scad_data import SCADData
from utils.plots import Plotter
from utils.drawings import Drawer


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

    if example_name == 'example_4':
        reinforcement_scheme.load_scad_data(scad_data, 'Перекрытие 1-го этажа')
    else:
        reinforcement_scheme.load_scad_data(scad_data, 'Плита')

    reinforcement_scheme.load_anchorage_lengths(f'examples/{example_name}/{example_name}_anchorage_lengths.csv')
    reinforcement_scheme.make_combined_table()

    plotter = Plotter()

    for loc in [
        'Top_X',
        'Top_Y',
        'Bot_X',
        'Bot_Y'
    ]:
        reinforcement_scheme.find_reinforcement_zones(loc)
        reinforcement_scheme.transfer_reinforcement_direction_to_zones()
        reinforcement_scheme.set_zones_reinforcement()

        # plotter.plot_reinforcement_2d(reinforcement, loc,
        #                               min_value=reinforcement_scheme.background_reinforcement_intensity)
        # plotter.plot_reinforcement_zones_2d(reinforcement_scheme, loc, plot_directions=True)

    drawer = Drawer()
    drawer.dxf_draw_zones(reinforcement_scheme, f'examples/{example_name}/{example_name}.dxf')
