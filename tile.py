#!/usr/bin/env python

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
    def is_valid(cls, direction):
        edge, row = direction
        assert(edge in [cls.T, cls.B, cls.L, cls.R])
        if edge == cls.T or edge == cls.B:
            assert(row in [cls.L, cls.M, cls.R])
        elif edge == L or edge == cls.R:
            assert(row in [cls.T, cls.M, cls.B])
        else:
            assert(False)

    @classmethod
    def invert(cls, direction):
        cls.is_valid(direction)
        edge, row = direction
        if edge == cls.T:
            edge = cls.B
        elif edge == cls.B:
            edge = cls.T
        elif edge == cls.L:
            edge = cls.R
        elif edge == cls.R:
            edge = cls.L
        return (edge, row)


class Tile:
    def __init__(self, rotation=0):
        global tile_id
        # Unique ID for each tile
        self.id = tile_id
        tile_id += 1

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
        assert(angle == 0 or self.can_move)
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

        path = "┌" if self.can_move else "⬤"
        path = path + ("┐     ┌" if self.NORTH else "───────")
        path = path + ("┐\n" if self.can_move else "⬤\n")

        path = path + ("└" if self.WEST else "│")
        path = path + " %s " % token[:5]
        path = path + ("┘\n" if self.EAST else "│\n")

        path = path + (" " if self.WEST else "│")
        path = path + " %s " % token[5:10]
        path = path + (" \n" if self.EAST else "│\n")

        path = path + ("┌" if self.WEST else "│")
        path = path + " %s " % token[10:15]
        path = path + ("┐\n" if self.EAST else "│\n")

        path = path + ("└" if self.can_move else "⬤")
        path = path + ("┘     └" if self.SOUTH else "───────")
        path = path + ("┘" if self.can_move else "⬤")

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
