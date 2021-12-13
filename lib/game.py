from lib.math import Vector2, dist


class State(object):
    def __init__(self):
        self.tracs = []
        self.shutter = {}
        self.stacker = {}
        self.sensor_cost = -1
        self.bans = {}

    def add_trac(self, x1, x2, y1, y2, step):
        self.tracs.append(Trac(x1, x2, y1, y2, step))

    def add_shutter(self, name, speed):
        self.shutter[name] = Shutter(name, speed)

    def get_shutter(self, name):
        if name in self.shutter:
            return self.shutter[name]
        else:
            raise ValueError()

    def add_stacker(self, name, speed, max_detectors):
        self.stacker[name] = Stacker(name, speed, max_detectors)

    def get_stacker(self, name):
        if name in self.stacker:
            return self.stacker[name]
        else:
            raise ValueError()

    def set_sensor_cost(self, sensor_cost):
        self.sensor_cost = sensor_cost

    def set_shutter_cost(self, name, cost):
        if name in self.shutter:
            self.shutter[name].cost = cost
        else:
            raise ValueError()

    def set_stacker_cost(self, name, cost):
        if name in self.stacker:
            self.stacker[name].cost = cost
        else:
            raise ValueError()

    def add_bans(self, num, start, end):
        if num not in self.bans:
            self.bans[num] = []
        self.bans[num].append(Vector2(start, end))

    def find_trac(self, start, end):
        for t in self.tracs:
            if dist(t.start, start) == 0 and dist(t.end, end) == 0 or dist(t.start, end) == 0 and dist(t.end, start) == 0 :
                return t
        raise Exception("trac not find")


TRAC_STATUS_EMPTY = 0
TRAC_STATUS_FULL = 1
TRAC_STATUS_END = 2

class Trac(object):
    def __init__(self, x1, y1, x2, y2, step):
        self.start = Vector2(x1, y1)
        self.end = Vector2(x2, y2)
        self.step = step
        self.status = {}

    def do1_filling(self, t):
        self.status[TRAC_STATUS_EMPTY] = t

    def do2_fireing(self, t):
        self.status[TRAC_STATUS_FULL] = t

    def do3_getting(self, t):
        self.status[TRAC_STATUS_END] = t

    def validate(self):
        assert self.status[TRAC_STATUS_EMPTY] <= self.status[TRAC_STATUS_FULL] and self.status[TRAC_STATUS_FULL] <= self.status[TRAC_STATUS_END], "trac round not complite"


TYPE_SHIP_SHUTTER = 0
TYPE_SHIP_STACKER = 1

class Ship(object):
    def __init__(self, name, speed):
        self.name = name
        self.speed = speed
        self.cost = -1

    def is_shutter(self):
        return self.type == TYPE_SHIP_SHUTTER

class Shutter(Ship):
    def __init__(self, name, speed):
        super().__init__(name, speed)
        self.type = TYPE_SHIP_SHUTTER


class Stacker(Ship):
    def __init__(self, name, speed, max_detectors):
        super().__init__(name, speed)
        self.max_detectors = max_detectors
        self.type = TYPE_SHIP_STACKER

