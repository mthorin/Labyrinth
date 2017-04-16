#!/usr/bin/python
from board import *
from player import *

class RuleSet:
    def __init__(self):
        self.SEE_ALL_CARDS = True
        self.CARDS_IN_ORDER = False
        self.MOVE_BEFORE_TURN = False
        self.MOVE_AFTER_PICKUP = False
        self.END_AT_HOME = True
        self.NUMBER_OF_TOKENS = 3
        self.NUMBER_OF_SLIDES = 1
        self.MOVE_TILE_LIMIT = 0

class Labyrinth:
    def __init__(self, ruleset, players):
        self.ruleset = ruleset
        self.gameboard = GameBoard(players)
        self.turn = 0

    def make_turn(self):
        # Get the player who's turn it is
        player = self.gameboard.players[self.turn]

        # Let them decide a move
        (direction, orientation, move_path) = player.decide_move(self.gameboard)

        # Execute the slide
        board = self.slide_tiles(direction, orientation)
        player = board.players[self.turn]

        # If there is a move limit, enforce it
        if self.ruleset.MOVE_TILE_LIMIT > 0:
            move_path[self.ruleset.MOVE_TILE_LIMIT:]

        # Execute the move
        for step in move_path:
            px, py = player.x, player.y
            current_tile = board._board[py][px]
            next_tile = None
            if abs(step) == 2:
                # Left/Right movement
                step = step / 2
                next_tile = board._board[py][px + step]
                # Check move is valid and then move
                if step > 0:
                    can_move = current_tile.EAST and next_tile.WEST
                else:
                    can_move = current_tile.WEST and next_tile.EAST
                assert(can_move)
                player.x += step
            elif abs(step) == 1:
                # Up/Down movement
                next_tile = board._board[py + step][px]
                # Check move is valid and then move
                if step > 0:
                    can_move = current_tile.SOUTH and next_tile.NORTH
                else:
                    can_move = current_tile.NORTH and next_tile.SOUTH
                assert(can_move)
                player.y += step
            else:
                assert(False)

            # See if player picks up token
            token = next_tile.token
            if token in player.cards:
                player.cards.remove(token)

                # Might need to end turn here
                if not self.ruleset.MOVE_AFTER_PICKUP:
                    break

        # Save the changes
        self.gameboard = board
        self.turn = (self.turn + 1) % len(board.players)

    def slide_tiles(self, direction, orientation):
        #TODO: Move players
        assert(self.gameboard.last_slide is None or self.gameboard.last_slide != direction)
        TileMovement.is_valid(direction)

        # Create new board to apply slide to
        new_board = self.gameboard.clone()
        floating_tile = new_board.floating_tile
        floating_tile.rotate(orientation)

        edge, row = direction
        if edge == TileMovement.T:
            offset = (edge * 2) + 1
            # Create a temporary column for easy shifting
            column = [t for x, y, t in new_board.iterate() if x == offset]
            if edge == TileMovement.T:
                # Move tiles down
                column = [floating_tile] + column
                new_board.floating_tile = column[len(column) - 1]
                column = column[:-1]
            elif edge == TileMovement.B:
                # Move tiles up
                column.add(floating_tile)
                new_board.floating_tile = column[0]
                column = column[1:]
            # Put temporary column back into board representation
            for y in range(7):
                new_board._board[y][offset] = column[y]

        elif edge == TileMovement.L or edge == TileMovement.R:
            offset = ((edge - 1) / 2) + 2
            row = new_board._board[offset]
            if edge == TileMovement.L:
                #Move tiles right
                row = [floating_tile] + row
                new_board.floating_tile = row[len(row) - 1]
                new_board._board[offset] = row[:-1]
            elif edge == TileMovement.R:
                # Move tiles left
                row.add(floating_tile)
                new_board.floating_tile = row[0]
                new_board._board[offset] = row[1:]

        else:
            assert(False) # Invalid edge
        new_board.last_slide = TileMovement.invert(direction)
        new_board.is_valid() # Check the changes haven't broken the board
        return new_board

    def __str__(self):
        return "{}\n{}\n{}\n\n".format(self.gameboard, self.gameboard.players, self.gameboard.floating_tile)

    __repr__ = __str__

def main():
    ruleset = RuleSet()
    players = [Player(colour) for colour in all_player_colours]

    lab = Labyrinth(ruleset, players)
    print(lab)

    for i in range(3):
        lab.make_turn()
        print(lab)

    print("Done")

if __name__ == '__main__':
    main()
