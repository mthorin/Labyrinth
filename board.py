#!/usr/bin/env python
import random
from itertools import product

from tile import *
from player import all_player_colours

all_tokens = set(["genie", "skull", "sword", "scarab", "beetle", "rat",
                           "dragonfly", "gold", "keys", "gem", "lizard", "helmet",
                           "princess", "book", "crown", "treasure", "candlestick",
                           "ghost", "spider", "owl", "map", "ring", "man", "bat"])

class TileMovement: # Represent as (Edge, Row) i.e. (T, M) for Top Middle
    # WARNING: Chaning these values will break the offset in the slide_tiles function
    T = 0 # Top
    M = 1 # Middle
    B = 2 # Bottom
    L = -3 # Left
    R = 4 # Right

class GameBoard:
    def __init__(self, dynamic_placement=None):
        def static_tile(tile, rotation=0, token=None):
            tile.token = token
            tile.rotate(rotation)
            tile.can_move = False
            return tile

        def random_placement(empty_coords, tile):
            return random.choice(empty_coords)

        if dynamic_placement is None:
            dynamic_placement = random_placement

        # Create an empty board
        self._board = [[None for x in range(7)] for y in range(7)]

        # Add in the player bases
        self._board[0][0] = static_tile(CornerTile(), 90,  "red base")
        self._board[0][6] = static_tile(CornerTile(), 180, "blue base")
        self._board[6][6] = static_tile(CornerTile(), 270, "green base")
        self._board[6][0] = static_tile(CornerTile(), 0,   "yellow base")

        # Add in outside static tiles
        self._board[0][2] = static_tile(TriTile(), 180, "skull")
        self._board[0][4] = static_tile(TriTile(), 180, "sword")
        self._board[2][0] = static_tile(TriTile(), 90,  "gold")
        self._board[4][0] = static_tile(TriTile(), 90,  "book")
        self._board[6][2] = static_tile(TriTile(), 0,   "map")
        self._board[6][4] = static_tile(TriTile(), 0,   "ring")
        self._board[2][6] = static_tile(TriTile(), 270, "helmet")
        self._board[4][6] = static_tile(TriTile(), 270, "candlestick")

        # Add in inside static tiles
        self._board[2][2] = static_tile(TriTile(), 90,  "keys")
        self._board[2][4] = static_tile(TriTile(), 180, "gem")
        self._board[4][2] = static_tile(TriTile(), 0,   "crown")
        self._board[4][4] = static_tile(TriTile(), 270, "treasure")

        # Create set of dynamic tiles
        dynamic_tiles = list(batch_create_tiles(CornerTile, 16,
                        ["scarab", "beetle", "rat", "dragonfly", "spider", "owl"]).union(
                            batch_create_tiles(TriTile, 6,
                            ["genie", "lizard", "princess", "ghost", "man", "bat"])).union(
                                batch_create_tiles(StraightTile, 12, [])
                                ))
        random.shuffle(list(dynamic_tiles))
        for tile in dynamic_tiles:
            empty_coords = [(x, y) for x, y, t in self.iterate() if not t]
            if empty_coords != []:
                x, y = dynamic_placement(empty_coords, tile)
                assert(0 <= x < 7 and 0 <= y < 7)
                assert(not self._board[y][x])
                self._board[y][x] = tile
            elif not hasattr(self, "floating_tile"):
                self.floating_tile = tile
                self.last_slide = None
            else:
                assert(False) # For some reason we have 2 (or more) tiles floating

    def iterate(self):
        i = 0
        it = iter(self._board)
        for y, row in enumerate(self._board):
            for x, tile in enumerate(row):
                yield (x, y, tile)

    def is_valid(self):
        """Some assertions to try an make sure the board makes sense"""

        # Check that we have a floating tile
        assert(hasattr(self, "floating_tile"))
        found_tokens = set()
        if self.floating_tile.token:
            found_tokens.add(self.floating_tile.token)

        # Check that there are no duplicate tokens on the board
        for x, y, tile in self.iterate():
            if tile and tile.token:
                if tile.token in found_tokens:
                    print("There are at least two {} tokens (one is at {}, {})".format(tile.token, x, y))
                    assert(False)
                else:
                    found_tokens.add(tile.token)

        # Check all tokens are valid
        everything = all_tokens.union(set(p + " base" for p in all_player_colours))
        missing_tokens = everything - found_tokens
        incorrect_tokens = found_tokens - everything
        if not(len(missing_tokens) == 0 and len(incorrect_tokens) == 0):
            print("Missing: {}\nInvalid: {}".format(missing_tokens, incorrect_tokens))
            assert(False)

    def slide_tiles(self, direction):
        assert(self.last_slide is None or self.last_slideS != direction)
        edge, row = direction
        if edge == TileMovement.T:
            assert(row in [TileMovement.L, TileMovement.M, TileMovement.R])
            offset = ((edge - 1) / 2) + 2
            #TODO: Move tiles down

        elif edge == TileMovement.L:
            assert(row in [TileMovement.T, TileMovement.M, TileMovement.B])
            offset = (edge * 2) + 1
            #TODO: Move tiles right

        elif edge == TileMovement.B:
            assert(row in [TileMovement.L, TileMovement.M, TileMovement.R])
            offset = ((edge - 1) / 2) + 2
            # TODO: Move tiles up

        elif edge == TileMovement.R:
            assert(row in [TileMovement.T, TileMovement.M, TileMovement.B])
            offset = (edge * 2) + 1
            # TODO: Move tiles left

        else:
            assert(False) # Invalid edge
        self.last_slide = direction # Need to invert direction
