import click
import logging
import sys

from lib.game import State

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
        except (ValueError):
            error(i, line)


if __name__ == '__main__':
    main()
