#!/usr/bin/python
from board import *
from player import *

def main():
    gameboard = GameBoard()
    gameboard.is_valid()

    players = [Player(colour, gameboard) for colour in all_player_colours]
    print("Done")

if __name__ == '__main__':
    main()
