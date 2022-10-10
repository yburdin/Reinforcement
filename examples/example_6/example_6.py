from utils.scad_data import SCADData

if __name__ == '__main__':
    example_name = 'example_6'

    txt_path = f'examples/{example_name}/{example_name}.txt'
    scad_data = SCADData()
    scad_data.import_txt(txt_path)

