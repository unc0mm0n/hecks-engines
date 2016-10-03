"""
This engine plays random moves. The only legality check being that they weren't played before.
"""
import itertools
import random
import logging


def main():
    move_list = prepare_moves()
    played_moves = {}

    while True:
        command = input()
        logging.info("Got command: {}".format(command))
        if "quit" in command:
            logging.info("Quitting..")
            print("=")
            exit(0)
        elif "clear_board" in command:
            logging.info("Resetting the board..")
            played_moves = {}
            move_list = prepare_moves()
            print("=")
        elif "play" in command:
            move = command.rsplit(" ", maxsplit=1)[-1].strip()
            logging.info("Playing move {}".format(move))
            if move not in ("pass", "resign"):
                played_moves[move] = True
            print("=")
        elif "genmove" in command:
            try:
                next_move = move_list.pop()
                while next_move in played_moves:
                    next_move = move_list.pop()
                played_moves[next_move] = True
            except IndexError:
                next_move = "pass"
            logging.info("Sending move: {}".format(next_move))
            print("= {}".format(next_move))
        else:
            logging.warning("Unknown command {}".format(command))
            print("? Unknown command. ")


def prepare_moves():
    moves = []
    for row in range(5):
        for col in range(1, 9 + 2*row):
            row_letter = chr(ord('a') + row)
            htp_vertex = "{}{}".format(row_letter, col)
            moves.append(htp_vertex)

            reflected_row_letter = chr(ord('a') + (9 - row))
            htp_reflected_vertex = "{}{}".format(reflected_row_letter, col)
            moves.append(htp_reflected_vertex)
    random.shuffle(moves)
    logging.debug("Moves: {}".format(moves))
    return moves

if __name__ == "__main__":
    import os

    os.makedirs("logs", exist_ok=True)

    logging.basicConfig(filename='logs/engine.log', level=logging.DEBUG,
                        format='%(asctime)s : %(name)s : %(levelname)s : %(message)s')
    logging = logging.getLogger(__name__)
    # End of necessary evil

    main()