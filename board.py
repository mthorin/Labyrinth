#!/usr/bin/env python

all_players = set(["red", "blue", "green", "yellow"])

all_elements = set(["ghost", "skull", "sword", "scarab", "beetle", "rat",
                    "dragonfly", "gold", "keys", "gem", "lizard", "helmet",
                    "princess", "book", "crown", "treasure", "candlestick",
                    "ghost", "spider", "owl", "map", "ring", "man"])

class Tile:
    def __init__(self, rotation=0):
        self.NORTH = False
        self.EAST = False
        self.SOUTH = False
        self.WEST = False
        self.element = None
        self.can_move = True
        self.rotate(rotation)

    def rotate(self, angle=90):
        # angle is clockwise and must be a multiple of 90 degrees
        angle = int(angle) % 360
        assert(angle in [0, 90, 180, 270])
        assert(angle == 0 or self.can_move)
        while angle > 0:
            tmp = self.NORTH
            self.NORTH = self.WEST
            self.WEST = self.SOUTH
            self.SOUTH = self.EAST
            self.EAST = tmp
            angle -= 90

    def __str__(self):
        path = ("N" if self.NORTH else "")
        path = path + ("E" if self.EAST else "")
        path = path + ("S" if self.SOUTH else "")
        path = path + ("W" if self.WEST else "")
        return "Tile(path=\"{}\",can_move={},element=\"{}\")".format(path, self.can_move, self.element)

    __repr__ = __str__

class CornerTile(Tile):
    def __init__(self, rotation=0):
        Tile.__init__(self, rotation)
        self.NORTH = True
        self.EAST = True

class StraightTile(Tile):
    def __init__(self, rotation=0):
        Tile.__init__(self, rotation)
        self.EAST = True
        self.WEST = True

class TriTile(Tile):
    def __init__(self, rotation=0):
        Tile.__init__(self, rotation)
        self.EAST = True
        self.NORTH = True
        self.WEST = True

class GameBoard:
    def __init__(self):
        def static_tile(tile, rotation=0, element=None):
            tile.element = element
            tile.rotate(rotation)
            tile.can_move = False
            return tile

        # Create an empty board
        self._board = [[None for x in range(7)] for y in range(7)]

        # Add in the player bases
        self._board[0][0] = static_tile(CornerTile(), 90,  "red base")
        self._board[6][0] = static_tile(CornerTile(), 180, "blue base")
        self._board[6][6] = static_tile(CornerTile(), 270, "green base")
        self._board[0][6] = static_tile(CornerTile(), 0,   "yellow base")

        # Add in outside static tiles
        self._board[2][0] = static_tile(TriTile(), 180, "skull")
        self._board[4][0] = static_tile(TriTile(), 180, "sword")
        self._board[0][2] = static_tile(TriTile(), 90,  "gold")
        self._board[0][4] = static_tile(TriTile(), 90,  "book")
        self._board[2][6] = static_tile(TriTile(), 0,   "map")
        self._board[4][6] = static_tile(TriTile(), 0,   "ring")
        self._board[6][2] = static_tile(TriTile(), 270, "helmet")
        self._board[6][4] = static_tile(TriTile(), 270, "candlestick")

        # Add in inside static tiles
        self._board[2][2] = static_tile(TriTile(), 90,  "keys")
        self._board[4][2] = static_tile(TriTile(), 180, "gem")
        self._board[2][4] = static_tile(TriTile(), 0,   "crown")
        self._board[4][4] = static_tile(TriTile(), 270, "treasure")

    def is_valid(self):
        # Some assertions to try an make sure the board makes sense
        found_elements = set()
        for x, row in enumerate(self._board):
            for y, tile in enumerate(row):
                if tile:
                    if tile.element in found_elements:
                        print("There are at least two {} elements (one is at {}, {})".format(tile.element, x, y))
                        assert(False)
                    else:
                        found_elements.add(tile.element)
        everything = all_elements.union(set(p + " base" for p in all_players))
        missing_elements = everything - found_elements
        incorrect_elements = found_elements - everything
        print("Missing: {}\nInvalid: {}".format(missing_elements, incorrect_elements))
        # TODO: Add missing elements and enable this assert
        # assert(len(missing_elements) == 0 and len(incorrect_elements) == 0)

if __name__ == '__main__':
    gameboard = GameBoard()
    gameboard.is_valid()
    print("Done")
