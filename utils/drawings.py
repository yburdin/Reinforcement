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

        for location in scheme.reinforcement_zones:
            doc.layers.add(location, color=randint(10, 230))

            for zone in scheme.reinforcement_zones[location]:  # type: ReinforcementZone
                points = zone.bounding_rectangle
                for i in range(1, len(points)):
                    msp.add_line(tuple(points[i-1]), tuple(points[i]), dxfattribs={'layer': location})
                msp.add_line(tuple(points[-1]), tuple(points[0]), dxfattribs={'layer': location})

        doc.saveas(save_path)
