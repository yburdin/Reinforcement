from utils.reinforcement_data import ReinforcementData
import os

if __name__ == '__main__':
    example_name = 'example_7'

    if example_name in os.getcwd():
        asf_path = f'{os.getcwd()}/Перекрытие 2-го этажа.asf'
    else:
        asf_path = f'examples/{example_name}/Перекрытие 2-го этажа.asf'

    reinforcement = ReinforcementData()
    reinforcement.import_asf(asf_path)
