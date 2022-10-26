from structures.reinforcement_scheme import ReinforcementScheme
from utils.reinforcement_data import ReinforcementData
from utils.scad_data import SCADData
from utils.plots import Plotter
from utils.drawings import Drawer
import os


if __name__ == '__main__':
    example_name = 'example_1'

    if example_name in os.getcwd():
        work_dir = f'{os.getcwd()}'
    else:
        work_dir = f'examples/{example_name}'

    asf_path = f'{work_dir}/{example_name}.asf'
    reinforcement = ReinforcementData()
    reinforcement.import_asf(asf_path)

    txt_path = f'{work_dir}/{example_name}.txt'
    scad_data = SCADData()
    scad_data.import_txt(txt_path)

    reinforcement_scheme = ReinforcementScheme()
    reinforcement_scheme.load_reinforcement_data(reinforcement)
    reinforcement_scheme.set_background_reinforcement(reinforcement)
    reinforcement_scheme.load_scad_data(scad_data, 'Плита')

    csv_file = [file for file in os.listdir(f'{work_dir}') if '.csv' in file][0]
    reinforcement_scheme.load_anchorage_lengths(f'{work_dir}/{csv_file}')
    reinforcement_scheme.make_combined_table()

    for loc in [
        'Top_X',
        'Top_Y',
        'Bot_X',
        'Bot_Y'
    ]:
        reinforcement_scheme.find_reinforcement_zones(loc)
        reinforcement_scheme.transfer_reinforcement_direction_to_zones()
        reinforcement_scheme.set_zones_reinforcement()

    drawer = Drawer()
    drawer.dxf_draw_zones(reinforcement_scheme, f'{work_dir}/{example_name}.dxf')
