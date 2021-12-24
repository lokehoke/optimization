from lib.math import Vector2, dist

TRAC_STATUS_NOT_INIT = -1
TRAC_STATUS_EMPTY = 0
TRAC_STATUS_FULL = 1
TRAC_STATUS_END = 2

class State(object):
    def __init__(self):
        self.tracs = []
        self.shutter = {}
        self.stacker = {}
        self.sensor_cost = -1
        self.bans = {}
        self.game_end = False

    def availableTrack(self, ship, trac):
        t1 = ship.time + dist(self.tracs[trac].start, ship.coor) / ship.speed
        t2 = t1 + dist(self.tracs[trac].start, self.tracs[trac].end) / ship.speed

        if self.tracs[trac].status[self.tracs[trac].last_status] > t1:
            return [False, t1, t2]

        if ship.is_shutter() and self.tracs[trac].last_status == TRAC_STATUS_EMPTY:
            if trac in self.bans:
                for b in self.bans[trac]:
                    if b.x <= t1 and b.y >= t1 or b.x <= t2 and b.y >= t2:
                        return [False, t1, t2]
            return [True, t1, t2]
        if ship.is_stacker() and self.tracs[trac].last_status in (TRAC_STATUS_NOT_INIT, TRAC_STATUS_FULL):
            if trac in self.bans:
                for b in self.bans[trac]:
                    if b.x <= t1 and b.y >= t1 or b.x <= t2 and b.y >= t2:
                        return [False, t1, t2]
            if self.tracs[trac].last_status == TRAC_STATUS_NOT_INIT and self.tracs[trac].detectors > ship.detectors:
                return [False, t1, t2]
            return [True, t1, t2]
        return [False, t1, t2]


    def add_trac(self, x1, x2, y1, y2, step):
        self.tracs.append(Trac(x1, x2, y1, y2, step))

    def add_shutter(self, name, speed):
        self.shutter[name] = Shutter(name, speed)

    def get_shutter(self, name):
        if name in self.shutter:
            return self.shutter[name]
        else:
            raise ValueError()

    def add_stacker(self, name, speed, detectors):
        self.stacker[name] = Stacker(name, speed, detectors)

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



class Trac(object):
    def __init__(self, x1, y1, x2, y2, step):
        self.start = Vector2(x1, y1)
        self.end = Vector2(x2, y2)
        self.step = step
        self.status = {}
        self.status[TRAC_STATUS_NOT_INIT] = 0
        self.last_status = TRAC_STATUS_NOT_INIT
        self.detectors = dist(self.start, self.end) // self.step

    def do1_filling(self, t):
        self.status[TRAC_STATUS_EMPTY] = t
        self.last_status = TRAC_STATUS_EMPTY

    def do2_fireing(self, t):
        self.status[TRAC_STATUS_FULL] = t
        self.last_status = TRAC_STATUS_FULL

    def do3_getting(self, t):
        self.status[TRAC_STATUS_END] = t
        self.last_status = TRAC_STATUS_END

    def update_status(self, t):
        if self.last_status == TRAC_STATUS_NOT_INIT:
            self.do1_filling(t)
        elif self.last_status == TRAC_STATUS_EMPTY:
            self.do2_fireing(t)
        elif self.last_status == TRAC_STATUS_FULL:
            self.do3_getting(t)

    def validate(self):
        assert self.status[TRAC_STATUS_EMPTY] <= self.status[TRAC_STATUS_FULL] and self.status[TRAC_STATUS_FULL] <= self.status[TRAC_STATUS_END], "trac round not complite"


TYPE_SHIP_SHUTTER = 0
TYPE_SHIP_STACKER = 1

class Ship(object):
    def __init__(self, name, speed):
        self.name = name
        self.speed = speed
        self.cost = -1
        self.coor = Vector2(0, 0)
        self.time = 0
        self.history = []

    def is_shutter(self):
        return self.type == TYPE_SHIP_SHUTTER

    def is_stacker(self):
        return self.type == TYPE_SHIP_STACKER

class Shutter(Ship):
    def __init__(self, name, speed):
        super().__init__(name, speed)
        self.type = TYPE_SHIP_SHUTTER


class Stacker(Ship):
    def __init__(self, name, speed, detectors):
        super().__init__(name, speed)
        self.detectors = detectors
        self.type = TYPE_SHIP_STACKER

