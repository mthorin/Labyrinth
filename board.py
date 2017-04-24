#!/usr/bin/env python
import copy
import random
from itertools import product

from tile import *
from player import all_player_colours, Player
from labyrinth import RuleSet

all_tokens = set(["genie", "skull", "sword", "scarab", "beetle", "rat",
                           "dragonfly", "gold", "keys", "gem", "lizard", "helmet",
                           "princess", "book", "crown", "treasure", "candlestick",
                           "ghost", "spider", "owl", "map", "ring", "man", "bat"])

class GameBoard:
    def __init__(self, players=[], dynamic_placement=None):
        def static_tile(tile, rotation=0, token=None):
            tile.token = token
            tile.rotate(rotation)
            tile.can_move = False
            return tile

        def random_placement(empty_coords, tile):
            return (random.choice(empty_coords), random.choice([0, 90, 180, 270]))

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
        random.shuffle(dynamic_tiles)
        for tile in dynamic_tiles:
            empty_coords = [(x, y) for x, y, t in self.iterate() if not t]
            if empty_coords != []:
                (x, y), theta = dynamic_placement(empty_coords, tile)
                assert(0 <= x < 7 and 0 <= y < 7 and theta in [0, 90, 180, 270])
                assert(not self._board[y][x])
                tile.rotate(theta)
                self._board[y][x] = tile
            elif not hasattr(self, "floating_tile"):
                self.floating_tile = tile
                self.last_slide = None
            else:
                assert(False) # For some reason we have 2 (or more) tiles floating

        # Add all the players to the board
        self.players = []
        for player in players:
            for x, y, tile in self.iterate():
                if tile and tile.token == player.colour + " base":
                    player.home_x = x
                    player.home_y = y
                    player.x = x
                    player.y = y
                    break
            self.players.append(player)

    def iterate(self):
        i = 0
        it = iter(self._board)
        for y, row in enumerate(self._board):
            for x, tile in enumerate(row):
                yield (x, y, tile)

    def clone(self):
        new_board = copy.deepcopy(self)
        return new_board

    def is_valid(self):
        """Some assertions to try an make sure the board makes sense"""

        # Check that we have a floating tile
        assert(hasattr(self, "floating_tile"))
        found_tokens = set()
        found_ids = set([self.floating_tile.id])
        if self.floating_tile.token:
            found_tokens.add(self.floating_tile.token)

        for x, y, tile in self.iterate():
            # Check all tiles have unique ids
            assert(tile.id not in found_ids)
            found_ids.add(tile.id)

            # Check that there are no duplicate tokens on the board
            if tile.token:
                assert(tile.token not in found_tokens)
                found_tokens.add(tile.token)

        # Check that we have all the tiles we are supposed to
        assert(found_ids == set([i for i in range(50)]))

        # Check all tokens are valid
        everything = all_tokens.union(set(p + " base" for p in all_player_colours))
        missing_tokens = everything - found_tokens
        incorrect_tokens = found_tokens - everything
        if not(len(missing_tokens) == 0 and len(incorrect_tokens) == 0):
            print("Missing: {}\nInvalid: {}".format(missing_tokens, incorrect_tokens))
            assert(False)

    def __str__(self):
        def tile_to_lines(tile):
            return tile.__str__().split("\n")
        output = ""

        for x, y, tile in self.iterate():
            tile._colour = None

        for player in self.players:
            self._board[player.y][player.x]._colour = player.colour

        for row in self._board:
            tile_lines = map(tile_to_lines, row)
            board_line = [" ".join(t) for t in list(zip(*list(tile_lines)))]
            output = output + "\n".join(board_line) + "\n"

        return output[:-1]

    __repr__ = __str__
