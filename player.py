#!/usr/bin/env python
from Labyrinth.tile import TileMovement
from Labyrinth.utils import colourise
import random, math

all_player_colours = ["red", "blue", "green", "yellow"]

class PlayerMovement:
    UP = -1
    DOWN = 1
    LEFT = -2
    RIGHT = 2

    @classmethod
    def all_moves(self):
        l = [self.UP, self.DOWN, self.LEFT, self.RIGHT]
        random.shuffle(l)
        return l

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

        # See if player picks up token
        if len(player.cards) > 0:
            token = next_tile.token
            if ((player.ruleset.CARDS_IN_ORDER and token == player.cards[0])
            or (not player.ruleset.CARDS_IN_ORDER and token in player.cards)):
                player.cards.remove(token)

                # TODO: Might need to end turn here
                #if not self.ruleset.MOVE_AFTER_PICKUP:
                #    return True

        return True

class Player:
    def __init__(self, colour):
        self.colour = colour
        self.cards = []

    def decide_move(self, gameboard):
        assert(all(hasattr(self, a) for a in ["home_x", "home_y", "x", "y"]))
        return self.one_lookahead_move(gameboard)

    def random_move(self, gameboard):
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
        player = new_board.players[new_board.turn]
        for i in range(100): # Make 100 attempts at a step
            step = random.choice([PlayerMovement.UP, PlayerMovement.LEFT,
                           PlayerMovement.DOWN, PlayerMovement.RIGHT])
            if PlayerMovement.move(step, new_board._board, player):
                path.append(step)


        return direction, orientation, path

    def one_lookahead_move(self, gameboard):
        best_slide = None
        best_path = None
        best_score = math.inf
        best_orientation = 0

        orientations = [0, 90, 180, 270]
        random.shuffle(orientations)

        # For each possible slide
        for slide in TileMovement.all_moves():
            # For each possible tile orientation
            for orientation in orientations:
                if gameboard.last_slide is None or slide != gameboard.last_slide:
                    # Slide tile to a temporary board
                    new_board = gameboard.slide_tiles(slide, orientation)
                    player = new_board.players[new_board.turn]

                    # Find out what player is targeting
                    targets = []
                    if player.cards == []:
                        targets = [(player.home_x, player.home_y)]
                    else:
                        num_cards = len(player.cards)
                        for i in range(num_cards):
                            card_loc = new_board.find_card(player.cards[i])
                            if card_loc:
                                targets.append(card_loc)

                    # Find best path by checking each target in turn
                    player_start = (player.x, player.y)
                    best_target_score = math.inf
                    best_target_path = None
                    for target_x, target_y in [targets[0]] if self.ruleset.CARDS_IN_ORDER else targets:
                        # Try to calculate the shortest path
                        (end_x, end_y), path = new_board.shortest_path_to_closest((player.x, player.y), (target_x, target_y))

                        # Calculate how good the move is
                        score = abs(end_x - target_x) + abs(end_y - target_y)

                        if self.ruleset.CARDS_IN_ORDER and score == 0 and self.ruleset.MOVE_AFTER_PICKUP:
                            # Made it to the first card, should try to get to the next one
                            keep_chaining = True
                            target_index = 1
                            while keep_chaining and target_index <= len(targets):
                                (start_x, start_y) = (end_x, end_y)
                                if target_index < len(targets):
                                    target_x, target_y = targets[target_index]
                                else:
                                    target_x, target_y = (player.home_x, player.home_y)
                                (end_x, end_y), path2 = new_board.shortest_path_to_closest((start_x, start_y), (target_x, target_y))
                                path += path2
                                keep_chaining = end_x == target_x and end_y == target_y
                                target_index += 1

                        # Save if it is a better score
                        if score < best_target_score:
                            best_target_score = score
                            best_target_path = path

                    # Check if this slide is better than the previous
                    if best_target_score < best_score:
                        best_slide = slide
                        best_path = best_target_path
                        best_score = best_target_score
                        best_orientation = orientation

        return best_slide, best_orientation, best_path

    def has_finished(self):
        return self.cards == [] and self.x == self.home_x and self.y == self.home_y

    def __str__(self):
        if self.ruleset.SEE_ALL_CARDS:
            cards = self.cards
        else:
            cards = len(self.cards)
        return colourise(self.colour, "{}({},{}) has {} cards".format(self.colour,self.x,self.y,cards))

    __repr__ = __str__
