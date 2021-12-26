import click
import logging
import sys
import math

from lib.game import State
from lib.math import Vector2, dist


handler = logging.StreamHandler(stream=sys.stderr)
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)


TRAC_WORD = 'TRAC'
SHIP_WORD = 'SHIP'
MONE_WORD = 'MONE'
ICEE_WORD = 'ICEE'
PATH_WORD = 'PATH'
COMMENT_WORD = '--'
END_WORD = '/'
modes = (TRAC_WORD, SHIP_WORD, MONE_WORD, ICEE_WORD, PATH_WORD, COMMENT_WORD, END_WORD)

SHUTTER_KEY = 'S'
STACKER_KEY = 'H'

ACTION_STAND = 0
ACTION_MOVE = 1
ACTION_PUT = 2
ACTION_GET = 3
ACTION_FIRE = 4

def error(i, line):
    logging.error(f"error in {i} line: {line}")
    exit()


@click.command()
@click.option(
    'input_file',
    '--input-file',
    required=True,
    type=click.File('r'),
)
def main(input_file):
    logger.info(f"{input_file=}")

    mode = ''
    state = State()

    skip = False
    first_mone = True

    path_mode = ''
    path_ship = None
    path_rows = 0
    path_current_action = ACTION_STAND
    path_position = Vector2(0, 0)
    path_time = -1

    i = 0

    for line in input_file:
        try:
            i = i + 1
            line = line.strip()
            for m in modes:
                if line.startswith(m):
                    mode = m
                    skip = True
                    break

            if skip:
                skip = False
                continue

            info = line.split()

            if len(info) == 0:
                continue

            if mode == TRAC_WORD:
                if len(info) < 5:
                    error(i, line)

                state.add_trac(float(info[0]), float(info[1]), float(info[2]), float(info[3]), float(info[4]))
            elif mode == SHIP_WORD:
                if info[0] == SHUTTER_KEY:
                    state.add_shutter(info[1], float(info[2]))
                elif info[0] == STACKER_KEY:
                    state.add_stacker(info[1], float(info[2]), int(info[3]))
                else:
                    error(i, line)
            elif mode == MONE_WORD:
                if first_mone:
                    if float(info[0]) > 0:
                        state.set_sensor_cost(float(info[0]))
                        first_mone = False
                    else:
                        raise ValueError()
                else:
                    if float(info[2]) <= 0:
                        raise ValueError()

                    if info[0] == SHUTTER_KEY:
                        state.set_shutter_cost(info[1], float(info[2]))
                    else:
                        state.set_stacker_cost(info[1], float(info[2]))
            elif mode == ICEE_WORD:
                if int(info[1]) >= int(info[2]):
                    raise ValueError()
                state.add_bans(int(info[0]), int(info[1]), int(info[2]))
            elif mode == PATH_WORD:
                if path_rows == 0:
                    if info[0] in (SHUTTER_KEY, STACKER_KEY):
                        path_mode = info[0]
                    else:
                        error(i, line)
                    if path_mode == SHUTTER_KEY:
                        path_ship = state.get_shutter(info[1])
                    elif path_mode == STACKER_KEY:
                        path_ship = state.get_stacker(info[1])

                    path_rows = int(info[2])
                    path_time = -1
                else:
                    assert int(info[2]) >= path_time, f"time was expected to grow error: line: {i} \n {line}"
                    path_rows -= 1
                    d = dist(path_position, Vector2(info[0], info[1]))
                    if path_current_action == ACTION_STAND:
                        assert path_position.x == int(info[0]), f"move after stand error: line: {i} \n {line}"
                        assert path_position.y == int(info[1]), f"move after stand error: line: {i} \n {line}"
                    elif path_current_action == ACTION_MOVE:
                        assert path_ship.speed * (int(info[2]) - path_time - 1) - d < 0, f"so fast move: line: {i} \n {line}"
                    elif path_current_action == ACTION_PUT:
                        assert path_ship.speed * (int(info[2]) - path_time - 1) - d < 0, f"so fast move: line: {i} \n {line}"
                        assert not path_ship.is_shutter(), f"must be stacker: {i} \n {line}"
                        state.find_trac(path_position, Vector2(info[0], info[1])).do1_filling(int(info[2]))
                    elif path_current_action == ACTION_FIRE:
                        assert path_ship.speed * (int(info[2]) - path_time - 1) - d < 0, f"so fast move: line: {i} \n {line}"
                        assert path_ship.is_shutter(), f"must be shutter: {i} \n {line}"
                        state.find_trac(path_position, Vector2(info[0], info[1])).do2_fireing(int(info[2]))
                    elif path_current_action == ACTION_GET:
                        assert path_ship.speed * (int(info[2]) - path_time - 1) - d < 0, f"so fast move: line: {i} \n {line}"
                        assert not path_ship.is_shutter(), f"must be stacker: {i} \n {line}"
                        state.find_trac(path_position, Vector2(info[0], info[1])).do3_getting(int(info[2]))

                    path_position.x = int(info[0])
                    path_position.y = int(info[1])
                    path_time = int(info[2])
                    path_current_action = int(info[3])
        except Exception as e:
            print(e)
            error(i, line)


    # turn on for check
    for t in state.tracs:
        t.validate()
    return

    print("Good input.txt")

    while not state.game_end:
        min_t2 = -1
        min_t1 = -1
        min_sh = None
        min_trac = None

        for sh in state.shutter:
            for trac in range(len(state.tracs)):
                av, t1, t2 = state.availableTrack(state.shutter[sh], trac)
                if av and (min_t2 == -1 or min_t2 > t2):
                    min_t2 = t2
                    min_t1 = t1
                    min_sh = state.shutter[sh]
                    min_trac = trac
        for sh in state.stacker:
            for trac in range(len(state.tracs)):
                av, t1, t2 = state.availableTrack(state.stacker[sh], trac)
                if av and (min_t2 == -1 or min_t2 > t2):
                    min_t1 = t1
                    min_t2 = t2
                    min_sh = state.stacker[sh]
                    min_trac = trac


        trac_wrong_status = True
        for trac in range(len(state.tracs)):
            if state.tracs[trac].last_status != 2:
                trac_wrong_status = False

        if trac_wrong_status: # end of game
            for sh in state.shutter:
                sh = state.shutter[sh]
                if sh.coor.x != sh.coor.y or sh.coor.x != 0:
                    sh.history.append(f"{sh.coor.x} {sh.coor.y} {math.ceil(sh.time)} 1")
                    sh.time += dist(sh.coor, Vector2(0, 0)) / sh.speed
                    sh.coor = Vector2(0, 0)
                    sh.history.append(f"{sh.coor.x} {sh.coor.y} {math.ceil(sh.time)} 0")
            for sh in state.stacker:
                sh = state.stacker[sh]
                if sh.coor.x != sh.coor.y or sh.coor.x != 0:
                    sh.history.append(f"{sh.coor.x} {sh.coor.y} {math.ceil(sh.time)} 1")
                    sh.time += dist(sh.coor, Vector2(0, 0)) / sh.speed
                    sh.coor = Vector2(0, 0)
                    sh.history.append(f"{sh.coor.x} {sh.coor.y} {math.ceil(sh.time)} 0")
            break

        if min_t2 == -1:
            for sh in state.shutter:
                sh = state.shutter[sh]
                sh.history.append(f"{min_sh.coor.x} {min_sh.coor.y} {math.ceil(min_sh.time)} 0")
                sh.time += 1
            for sh in state.stacker:
                sh = state.stacker[sh]
                sh.history.append(f"{min_sh.coor.x} {min_sh.coor.y} {math.ceil(min_sh.time)} 0")
                sh.time += 1
            continue


        min_sh.history.append(f"{min_sh.coor.x} {min_sh.coor.y} {math.ceil(min_sh.time)} 1")
        if min_sh.is_stacker():
            if state.tracs[min_trac].last_status == -1:
                min_sh.detectors -= state.tracs[min_trac].detectors
                min_sh.history.append(f"{state.tracs[min_trac].start.x} {state.tracs[min_trac].start.y} {math.ceil(min_t1)} 2")
            else:
                min_sh.detectors += state.tracs[min_trac].detectors
                min_sh.history.append(f"{state.tracs[min_trac].start.x} {state.tracs[min_trac].start.y} {math.ceil(min_t1)} 3")
        else:
            min_sh.history.append(f"{state.tracs[min_trac].start.x} {state.tracs[min_trac].start.y} {math.ceil(min_t1)} 4")

        min_sh.coor = state.tracs[min_trac].end
        min_sh.time = min_t2
        state.tracs[min_trac].update_status(min_t2)


    max_t = 0
    pric_per_t = 0
    count_detector = 0

    for sh in state.shutter:
        sh = state.shutter[sh]
        max_t = max(max_t, sh.time)
        pric_per_t += sh.cost
        s = "S" if sh.is_shutter() else "H"
        print(f"{s} {sh.name} {len(sh.history)}")
        for h in sh.history:
            print(h)
    for sh in state.stacker:
        sh = state.stacker[sh]
        max_t = max(max_t, sh.time)
        pric_per_t += sh.cost
        count_detector += sh.detectors
        s = "S" if sh.is_shutter() else "H"
        print(f"{s} {sh.name} {len(sh.history)}")
        for h in sh.history:
            print(h)

    print(max_t * (pric_per_t + count_detector * state.sensor_cost) / 24 / 1000)

if __name__ == '__main__':
    main()
