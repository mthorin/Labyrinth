#!/usr/bin/env python
from tile import TileMovement


all_player_colours = ["red", "blue", "green", "yellow"]

class PlayerMovement:
    UP = -1
    DOWN = 1
    LEFT = -2
    RIGHT = 2

class Player:
    def __init__(self, colour, cards=[]):
        self.colour = colour
        self.cards = cards

    def decide_move(self, gameboard):
        assert(all(hasattr(self, a) for a in ["home_x", "home_y", "x", "y"]))

        # TODO: Choose a better move
        return (TileMovement.T, TileMovement.L), 90, [PlayerMovement.UP]

    def __str__(self):
        return "{}({},{},{})".format(self.colour,self.x,self.y,self.cards)

    __repr__ = __str__
