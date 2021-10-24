from lib.math import Vector2


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

    def add_stacker(self, name, speed, max_detectors):
        self.stacker[name] = Stacker(name, speed, max_detectors)

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

class Trac(object):
    def __init__(self, x1, y1, x2, y2, step):
        self.start = Vector2(x1, y1)
        self.end = Vector2(x2, y2)
        self.step = step


class Ship(object):
    def __init__(self, name, speed):
        self.name = name
        self.speed = speed
        self.cost = -1


class Shutter(Ship):
    def __init__(self, name, speed):
        super().__init__(name, speed)


class Stacker(Ship):
    def __init__(self, name, speed, max_detectors):
        super().__init__(name, speed)
        self.max_detectors = max_detectors

