#!/usr/bin/python
from board import *
from player import *

def main():
    gameboard = GameBoard()
    gameboard.is_valid()

    players = [Player(colour, gameboard) for colour in all_player_colours]

    new_board = slide_tiles(gameboard, (TileMovement.T, TileMovement.L))
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
