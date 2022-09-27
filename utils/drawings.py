from structures.reinforcement_scheme import ReinforcementScheme
from structures.reinforcement_scheme import ReinforcementZone
from numpy.random import randint
import ezdxf


class Drawer:
    def __init__(self):
        pass

    @staticmethod
    def dxf_draw_zones(scheme: ReinforcementScheme, save_path: str):
        doc = ezdxf.new()
        msp = doc.modelspace()

        doc.layers.add('TEXT', color=randint(10, 230))
        diameter, step = scheme.background_reinforcement["diameter"], scheme.background_reinforcement["step"]
        msp.add_text(f'Фон {diameter} шаг {step}', dxfattribs={'layer': 'TEXT', 'height': 0.2}).set_placement((0, 0))

        for location in scheme.reinforcement_zones:
            doc.layers.add(location, color=randint(10, 230))
            doc.layers.add(f'TEXT_{location}', color=randint(10, 230))

            for zone in scheme.reinforcement_zones[location]:  # type: ReinforcementZone
                points = zone.bounding_rectangle
                points_adj = zone.bounding_rectangle_adjusted
                for i in range(1, len(points)):
                    msp.add_line(tuple(points[i-1]), tuple(points[i]), dxfattribs={'layer': location, 'color': 9})
                    msp.add_line(tuple(points_adj[i-1]), tuple(points_adj[i]), dxfattribs={'layer': location})
                msp.add_line(tuple(points[-1]), tuple(points[0]), dxfattribs={'layer': location, 'color': 9})
                msp.add_line(tuple(points_adj[-1]), tuple(points_adj[0]), dxfattribs={'layer': location})

                zone_diameter = zone.additional_reinforcement['diameter']
                zone_step = zone.additional_reinforcement['step']
                zone_dim = zone.dimensions_adjusted
                msp.add_text(f'{zone_diameter} шаг {zone_step}',
                             dxfattribs={'layer': f'TEXT_{location}',
                                         'height': 0.2}).set_placement(zone.midpoint)
                msp.add_text(f'({zone_dim[0] * 1000:.4g}x{zone_dim[1] * 1000:.4g})',
                             dxfattribs={'layer': f'TEXT_{location}',
                                         'height': 0.2}).set_placement((zone.midpoint[0], zone.midpoint[1] - 0.25))

        doc.saveas(save_path)
