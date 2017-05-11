#!/usr/bin/env python
from tile import TileMovement
from colours import colourise
import random

all_player_colours = ["red", "blue", "green", "yellow"]

class PlayerMovement:
    UP = -1
    DOWN = 1
    LEFT = -2
    RIGHT = 2

    @staticmethod
    def move(step, board, player):
        px, py = player.x, player.y
        current_tile = board[py][px]
        next_tile = None
        if abs(step) == 2:
            # Left/Right movement
            step = int(step / 2)
            # Check board bounds
            if px + step < 0 or px + step >= len(board[py]):
                return False
            next_tile = board[py][px + step]
            # Check move is valid and then move
            if step > 0:
                can_move = current_tile.EAST and next_tile.WEST
            else:
                can_move = current_tile.WEST and next_tile.EAST
            if not can_move:
                return False
            player.x += step
        elif abs(step) == 1:
            # Up/Down movement
            # Check board bounds
            if py + step < 0 or py + step >= len(board):
                return False
            next_tile = board[py + step][px]
            # Check move is valid and then move
            if step > 0:
                can_move = current_tile.SOUTH and next_tile.NORTH
            else:
                can_move = current_tile.NORTH and next_tile.SOUTH
            if not can_move:
                return False
            player.y += step
        else:
            assert(False) # Invalid step

        return True # TODO: Fix tokens below, and then remove this

        # See if player picks up token
        token = next_tile.token
        if token in player.cards:
            player.cards.remove(token)

            # Might need to end turn here
            if not self.ruleset.MOVE_AFTER_PICKUP:
                return True # TODO: Need to stop making more turns

class Player:
    def __init__(self, colour, cards=[]):
        self.colour = colour
        self.cards = cards

    def decide_move(self, gameboard):
        assert(all(hasattr(self, a) for a in ["home_x", "home_y", "x", "y"]))

        # Slide the tile in a random direction and orientation
        orientation = random.choice([0, 90, 180, 270])
        direction = gameboard.last_slide
        while direction == gameboard.last_slide or direction is None:
            side = random.choice([TileMovement.T, TileMovement.B, TileMovement.L, TileMovement.R])
            if side == TileMovement.T or side == TileMovement.B:
                row = random.choice([TileMovement.L, TileMovement.M, TileMovement.R])
            else:
                row = random.choice([TileMovement.T, TileMovement.M, TileMovement.B])
            direction = (side, row)

        new_board = gameboard.slide_tiles(direction, orientation)

        # Calculate a random path
        path = []
        player = new_board.players[(new_board.turn - 1) % len(new_board.players)]
        for i in range(100): # Make 100 attempts at a step
            step = random.choice([PlayerMovement.UP, PlayerMovement.LEFT,
                           PlayerMovement.DOWN, PlayerMovement.RIGHT])
            if PlayerMovement.move(step, new_board._board, player):
                path.append(step)


        return direction, orientation, path

    def __str__(self):
        return colourise(self.colour, "{}({},{},{})".format(self.colour,self.x,self.y,self.cards))

    __repr__ = __str__
