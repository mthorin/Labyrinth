#!/usr/bin/env python

all_player_colours = set(["red", "blue", "green", "yellow"])

class Player:
    def __init__(self, colour, gameboard, cards=[]):
        self.colour = colour
        self._board = gameboard
        for x, y, tile in self._board.iterate():
            if tile and tile.token == colour + " base":
                self.home_x = x
                self.home_y = y
                break
        # Assert that this Player has a base on the GameBoard
        assert(hasattr(self, 'home_x') and hasattr(self, 'home_y'))
        self.x = self.home_x
        self.y = self.home_y
        self.cards = cards
