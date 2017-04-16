#!/usr/bin/env python

all_player_colours = set(["red", "blue", "green", "yellow"])

class Player:
    def __init__(self, colour, cards=[]):
        self.colour = colour

    def decide_move(self, gameboard):
        assert(all(hasattr(self, a) for a in ["home_x", "home_y", "x", "y"]))

        # Return chosen move
        return None
