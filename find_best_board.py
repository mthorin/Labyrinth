#!/usr/bin/env python
import labyrinth, player, tile
import time
import utils

def main():
    global best_board
    TIMEOUT_LENGTH = 10
    RANGE_LIMIT = 5

    utils.enable_colours(True)
    best_board = None
    best_avg = 0

    for i in range(100):
        tile.tile_id = 0
        ruleset = labyrinth.RuleSet()
        players = [player.Player(colour) for colour in player.all_player_colours]

        lab = labyrinth.Labyrinth(ruleset, players)
        lab.deal_cards(3)

        for p in lab.gameboard.players:
            p.turns = 0

        start_gameboard = lab.gameboard
        start_time = time.time()
        timeout = False
        while lab.gameboard.turn is not None and not timeout:
            lab.gameboard.players[lab.gameboard.turn].turns += 1
            lab.make_turn()
            if time.time() - start_time > TIMEOUT_LENGTH:
                timeout = True

        if timeout:
            print("Aborted Execution")
        else:
            players = sorted(lab.gameboard.players, key=lambda p: p.turns)
            min_turns = players[0].turns
            max_turns = players[3].turns
            avg_turns = sum(map(lambda p: p.turns, players)) / 4.0
            print("min: {} with {} moves, max: {} with {} moves, avg: {} moves".format(
                players[0], min_turns, players[3], max_turns, avg_turns))

            # New best board
            if max_turns - min_turns <= RANGE_LIMIT and best_avg < avg_turns:
                best_board = start_gameboard
                best_avg = avg_turns

if __name__ == '__main__':
    global best_board
    try:
        main()
    except KeyboardInterrupt:
        print(best_board)
