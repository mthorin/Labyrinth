#!/usr/bin/python
from board import *
from player import *

class RuleSet:
    def __init__(self):
        self.SEE_ALL_CARDS = True
        self.CARDS_IN_ORDER = False
        self.MOVE_BEFORE_TURN = False
        self.MOVE_AFTER_PICKUP = False
        self.END_AT_HOME = True
        self.NUMBER_OF_TOKENS = 3
        self.NUMBER_OF_SLIDES = 1
        self.MOVE_TILE_LIMIT = 0

def main():
    ruleset = RuleSet()
    gameboard = GameBoard(ruleset)
    gameboard.is_valid()

    players = [Player(colour, gameboard) for colour in all_player_colours]

    new_board = slide_tiles(gameboard, (TileMovement.T, TileMovement.L), 90)
    print(gameboard)
    print("\n")
    print(gameboard.floating_tile)
    print("\n\n")
    print(new_board)
    print("\n")
    print(new_board.floating_tile)
    print("Done")

if __name__ == '__main__':
    main()
