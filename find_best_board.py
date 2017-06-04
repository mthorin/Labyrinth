#!/usr/bin/env python
import labyrinth, player, tile
import time

def main():
    for i in range(100):
        tile.tile_id = 0
        ruleset = labyrinth.RuleSet()
        players = [player.Player(colour) for colour in player.all_player_colours]

        lab = labyrinth.Labyrinth(ruleset, players)
        lab.deal_cards(3)

        turns = 0
        while lab.who_won() is None:
            lab.make_turn()
            turns += 1

        print("Winner: {} in {} turns".format(lab.who_won(), turns))

if __name__ == '__main__':
    main()
