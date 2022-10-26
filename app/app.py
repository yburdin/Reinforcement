import tkinter.messagebox
from tkinter import filedialog as fd
from tkinter import Menu, Tk, Label
from json import loads
from typing import List
import os
from structures.reinforcement_scheme import ReinforcementScheme
from utils.reinforcement_data import ReinforcementData
from utils.scad_data import SCADData
from utils.drawings import Drawer


class App:
    def __init__(self, master: Tk):
        self.working_directory = None
        self.json_path = None
        self.settings = None

        self.master = master
        self.master.geometry('520x30')
        self.master.resizable(False, False)

        main_menu = Menu(self.master)
        self.master.config(menu=main_menu)

        main_menu.add_command(label='Load settings json', command=self.load_json)
        main_menu.add_command(label='Create dxf', command=self.create_dxf)

    def load_json(self):
        try:
            if self.working_directory is None:
                initial_dir = os.getcwd()
            else:
                initial_dir = self.working_directory

            filename = fd.askopenfilename(
                title='Open json',
                initialdir=initial_dir,
            )

            if filename:
                self.json_path = filename

                try:
                    with open(self.json_path, encoding='utf-8') as f:
                        settings = loads(f.read())
                        self.working_directory = '/'.join(self.json_path.split('/')[0:-1]) + '/'
                except FileNotFoundError:
                    raise AssertionError('JSON file not found')

                assert 'path_to_asf_folder' in settings, 'Path to asf folder not found in JSON file'
                assert 'path_to_txt_file' in settings, 'Path to txt file not found in JSON file'
                assert 'path_to_csv_file' in settings, 'Path to csv file not found in JSON file'
                assert 'path_to_dxf_output_folder' in settings, 'Path to dxf folder not found in JSON file'
                assert 'background_reinforcement_intensity' in settings, 'Background reinforcement not ' \
                                                                         'found in JSON file'
                assert 'reinforcement_groups' in settings, 'Reinforcement groups not found in JSON file'

                self.settings = settings

                self.place_settings_labels(self.master, self.settings)

        except AssertionError as e:
            tkinter.messagebox.showerror(title=None, message=e)

    def create_dxf(self):
        try:
            asf_files = self.get_asf_files()

            txt_path = self.settings['path_to_txt_file']
            scad_data = SCADData()
            scad_data.import_txt(txt_path)

            background_reinforcement_intensity = self.settings['background_reinforcement_intensity']
            reinforcement_groups = self.settings['reinforcement_groups']

            for group in reinforcement_groups:
                asf_file_index = None
                for i, asf_file in enumerate(asf_files):
                    if f'{group}.asf' in asf_file:
                        asf_file_index = i
                        break

                if asf_file_index is None:
                    raise AssertionError(f'Group {group} not found in asf files')

                reinforcement = ReinforcementData()
                reinforcement.import_asf(asf_files[asf_file_index])

                reinforcement_scheme = ReinforcementScheme()

                if 'possible_steps' in self.settings and 'possible_diameters' in self.settings:
                    possible_steps = self.settings['possible_steps']
                    possible_diameters = self.settings['possible_diameters']
                    reinforcement_scheme.calculator.set_possible_reinforcement(steps=possible_steps,
                                                                               diameters=possible_diameters)

                reinforcement_scheme.load_reinforcement_data(reinforcement)
                reinforcement_scheme.set_background_reinforcement(auto=False,
                                                                  intensity=background_reinforcement_intensity)

                reinforcement_scheme.load_scad_data(scad_data, group)
                try:
                    reinforcement_scheme.load_anchorage_lengths(self.settings['path_to_csv_file'])
                except FileNotFoundError:
                    raise AssertionError('CSV file not found')
                reinforcement_scheme.make_combined_table()

                for loc in ['Top_X', 'Top_Y', 'Bot_X', 'Bot_Y']:
                    reinforcement_scheme.find_reinforcement_zones(loc)
                    reinforcement_scheme.transfer_reinforcement_direction_to_zones()
                    reinforcement_scheme.set_zones_reinforcement()

                drawer = Drawer()
                dxf_file = f'{self.settings["path_to_dxf_output_folder"]}/{group}.dxf'
                drawer.dxf_draw_zones(reinforcement_scheme, dxf_file)

            tkinter.messagebox.showinfo(message='Drawings are done')

        except AssertionError as e:
            tkinter.messagebox.showerror(title=None, message=e)

    def get_asf_files(self) -> List[str]:
        asf_folder = self.settings['path_to_asf_folder']
        asf_files = [f'{asf_folder}/{file}' for file in os.listdir(asf_folder) if '.asf' in file]

        if len(asf_files) < 1:
            raise AssertionError('*.asf files not found')

        return asf_files

    @staticmethod
    def place_settings_labels(master: Tk, settings: dict):
        line_height = 21
        height = line_height * 11
        row_n = 0

        Label(master, text='Путь к папке с asf файлами:', anchor="nw", width=500).grid(row=row_n, column=0)
        Label(master, text=f'\t{settings["path_to_asf_folder"]}', anchor="nw", width=500).grid(row=row_n+1, column=0)

        Label(master, text='Путь к txt файлу:', anchor="nw", width=500).grid(row=row_n+2, column=0)
        Label(master, text=f'\t{settings["path_to_txt_file"]}', anchor="nw", width=500).grid(row=row_n+3, column=0)

        Label(master, text='Путь к csv-таблице длин анкеровки:', anchor="nw", width=500).grid(row=row_n+4, column=0)
        Label(master, text=f'\t{settings["path_to_csv_file"]}', anchor="nw", width=500).grid(row=row_n+5, column=0)

        Label(master, text='Путь для сохранения dxf файлов:', anchor="nw", width=500).grid(row=row_n+6, column=0)
        Label(master, text=f'\t{settings["path_to_dxf_output_folder"]}', anchor="nw", width=500).grid(row=row_n+7,
                                                                                                      column=0)

        Label(master, text=f'Интенсивность фонового армирования: {settings["background_reinforcement_intensity"]}',
              anchor="nw", width=500).grid(row=row_n+8, column=0)

        row_n = 8
        if 'possible_steps' in settings:
            Label(master, text=f'Возможные шаги армирования: {settings["possible_steps"]}',
                  anchor="nw", width=500).grid(row=row_n+1, column=0)
            row_n += 1
            height += line_height

        if 'possible_diameters' in settings:
            Label(master, text=f'Возможные диаметры арматуры: {settings["possible_diameters"]}',
                  anchor="nw", width=500).grid(row=row_n+1, column=0)
            row_n += 1
            height += line_height

        Label(master, text='Названия групп армирования из txt файла\n'
                           '(должны соответствовать именам файлов из папки с asf):',
              anchor="nw", width=500, justify='left').grid(row=row_n+2, column=0)
        row_n += 2

        for n, group in enumerate(settings["reinforcement_groups"]):
            row_n += 1
            Label(master, text=f'\t{group}', anchor="nw", width=500, justify='left').grid(row=row_n+n, column=0)
            height += line_height

        master.geometry(f'520x{height}')


if __name__ == '__main__':
    root = Tk()
    app = App(root)
    root.title('Reinpycement 0.7')
    if 'icon.ico' in os.listdir():
        root.iconbitmap("icon.ico")

    root.mainloop()
