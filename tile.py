#!/usr/bin/env python
from Labyrinth.utils import colourise
import random
import math
import Labyrinth.utils as utils

global tile_id
tile_id = 0

class TileMovement: # Represent as (Edge, Row) i.e. (T, M) for Top Middle
    # WARNING: Chaning these values will break the offset in the slide_tiles function
    T = 0 # Top
    M = 1 # Middle
    B = 2 # Bottom
    L = -3 # Left
    R = 4 # Right

    @classmethod
    def is_valid(cls, movement):
        edge, row = movement
        assert(edge in [cls.T, cls.B, cls.L, cls.R])
        if edge == cls.T or edge == cls.B:
            assert(row in [cls.L, cls.M, cls.R])
        elif edge == cls.L or edge == cls.R:
            assert(row in [cls.T, cls.M, cls.B])
        else:
            assert(False)

    @classmethod
    def invert(cls, movement):
        cls.is_valid(movement)
        edge, row = movement
        if edge == cls.T:
            edge = cls.B
        elif edge == cls.B:
            edge = cls.T
        elif edge == cls.L:
            edge = cls.R
        elif edge == cls.R:
            edge = cls.L
        return (edge, row)

    @classmethod
    def all_moves(cls):
        l = [ (cls.T, cls.L)
            , (cls.T, cls.M)
            , (cls.T, cls.R)
            , (cls.B, cls.L)
            , (cls.B, cls.M)
            , (cls.B, cls.R)
            , (cls.L, cls.T)
            , (cls.L, cls.M)
            , (cls.L, cls.B)
            , (cls.R, cls.T)
            , (cls.R, cls.M)
            , (cls.R, cls.B)
            ]
        random.shuffle(l)
        return l

    @classmethod
    def from_str(cls, side, row):
        if side == "t":
            side_cls = cls.T
        elif side == "b":
            side_cls = cls.B
        elif side == "l":
            side_cls = cls.L
        elif side == "r":
            side_cls = cls.R
        else:
            assert(False) # side was not valid

        if row == "t":
            row_cls = cls.T
        elif row == "b":
            row_cls = cls.B
        elif row == "l":
            row_cls = cls.L
        elif row == "r":
            row_cls = cls.R
        elif row == "m":
            row_cls = cls.M
        else:
            assert(False) # row was not valid

        output = (side_cls, row_cls)
        TileMovement.is_valid(output)
        return output

    @classmethod
    def to_str(cls, pair):
        side, row = pair
        if side == cls.T:
            side_cls = "top"
        elif side == cls.B:
            side_cls = "bottom"
        elif side == cls.L:
            side_cls = "left"
        elif side == cls.R:
            side_cls = "right"
        else:
            assert(False) # side was not valid

        if row == cls.T:
            row_cls = "top"
        elif row == cls.B:
            row_cls = "bottom"
        elif row == cls.L:
            row_cls = "left"
        elif row == cls.R:
            row_cls = "right"
        elif row == cls.M:
            row_cls = "middle"
        else:
            assert(False) # row was not valid

        return "{} {}".format(side_cls, row_cls)


class Tile:
    def __init__(self, rotation=0):
        global tile_id
        # Unique ID for each tile
        self.id = tile_id
        tile_id += 1

        # Colour the tile should be when printing
        self._colours = []

        self.NORTH = False
        self.EAST = False
        self.SOUTH = False
        self.WEST = False
        self.token = None
        self.can_move = True
        self.rotate(rotation)

    def rotate(self, angle=90):
        # angle is clockwise and must be a multiple of 90 degrees
        angle = int(angle) % 360
        assert(angle in [0, 90, 180, 270])
        assert(self.can_move)
        while angle > 0:
            tmp = self.NORTH
            self.NORTH = self.WEST
            self.WEST = self.SOUTH
            self.SOUTH = self.EAST
            self.EAST = tmp
            angle -= 90

    def __str__(self):
        token = (self.token if self.token else "")
        token = token.ljust(15) if len(token) > 5 else token.center(15)

        if "red" in self._colours and not utils.SHOW_COLOURS:
            path = "R"
        else:
            path = "┌" if self.can_move else "X"
        path += ("┐     ┌" if self.NORTH else "───────")
        if "blue" in self._colours and not utils.SHOW_COLOURS:
            path += "B\n"
        else:
            path += ("┐\n" if self.can_move else "X\n")

        path += "└" if self.WEST else "│"
        path += " %s " % token[:5]
        path += "┘\n" if self.EAST else "│\n"

        path += " " if self.WEST else "│"
        path += " %s " % token[5:10]
        path += " \n" if self.EAST else "│\n"

        path += "┌" if self.WEST else "│"
        path += " %s " % token[10:15]
        path += "┐\n" if self.EAST else "│\n"

        if "yellow" in self._colours and not utils.SHOW_COLOURS:
            path += "Y"
        else:
            path += "└" if self.can_move else "X"
        path += "┘     └" if self.SOUTH else "───────"
        if "green" in self._colours and not utils.SHOW_COLOURS:
            path += "G"
        else:
            path += "┘" if self.can_move else "X"

        if self._colours:
            gap = math.ceil(len(path) / len(self._colours))
            split_path = [path[i*gap:(i+1)*gap] for i in range(len(self._colours))]
            for i, c in enumerate(self._colours):
                split_path[i] = colourise(c, split_path[i])
            path = "".join(split_path)
        return path

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

def batch_create_tiles(tile_type, number, tokens=[]):
    output = set()
    assert(len(tokens) <= number) # Check that no tokens would be missed
    for i in range(number):
        tile = tile_type()
        if i < len(tokens):
            tile.token = tokens[i]
        output.add(tile)
    return output
