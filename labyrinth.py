#!/usr/bin/python
from board import GameBoard
from player import Player
from tile import *

def main():
    gameboard = GameBoard()
    gameboard.is_valid()
    print("Done")

if __name__ == '__main__':
    main()
