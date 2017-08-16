#!/usr/bin/python
from board import *
from player import *
import time, random, copy

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
        self.deck = list(copy.deepcopy(all_tokens))
        self.show_colours = True
        random.shuffle(self.deck)

    def deal_cards(self, num=1):
        for i in range(num):
            for p in self.gameboard.players:
                p.cards.append(self.deck[0])
                self.deck = self.deck[1:]

    def make_turn(self, gameboard=None, save=True):
        # Use current gameboard by default
        if gameboard is None:
            gameboard = self.gameboard

        if gameboard.turn is None:
            raise Exception("Game is over, nobody has a turn")

        # Get the player who's turn it is
        player = gameboard.players[gameboard.turn]

        # Let them decide a move
        (direction, orientation, move_path) = player.decide_move(gameboard)

        # Execute the slide
        board = gameboard.slide_tiles(direction, orientation)
        player = board.players[board.turn]

        # If there is a move limit, enforce it
        if self.ruleset.MOVE_TILE_LIMIT > 0:
            move_path[self.ruleset.MOVE_TILE_LIMIT:]

        # Execute the move
        for step in move_path:
            assert(PlayerMovement.move(step, board._board, player))

        # Next person's turn
        start_turn = board.turn
        skip_player = True
        while skip_player:
            board.turn = (board.turn + 1) % len(board.players)
            if not board.players[board.turn].has_finished() or start_turn == board.turn:
                skip_player = False
        # Set turn to None if there are no players have a move left
        if start_turn == board.turn and board.players[board.turn].has_finished():
            board.turn = None

        # Save the changes
        if save:
            self.gameboard = board

        return board

    def who_won(self, gameboard=None):
        # Use current gameboard by default
        if gameboard is None:
            gameboard = self.gameboard

        players = gameboard.players
        num_players = len(players)
        turn = gameboard.turn

        # If no players have a turn left, then start from the begining
        if turn is None:
            turn = 0

        # Check every player
        for i in range(num_players):
            # Start from the last player who played
            p = gameboard.players[(i + turn - 1) % num_players]

            # If they have no cards and are at home, then they have won
            if len(p.cards) == 0 and p.x == p.home_x and p.y == p.home_y:
                return p
        # Nobody has won yet
        return None


    def __str__(self):
        return "{}\n{}\n{}\n\n".format(self.gameboard, self.gameboard.players, self.gameboard.floating_tile)

    __repr__ = __str__

def main():
    ruleset = RuleSet()
    players = [Player(colour) for colour in all_player_colours]

    lab = Labyrinth(ruleset, players)
    lab.deal_cards(3)
    print(lab)

    turns = 0
    while lab.who_won() is None:
        lab.make_turn()
        print(lab)
        time.sleep(0.1)
        turns += 1

    print("Done")
    print("Winner: {} in {} turns".format(lab.who_won(), turns))

if __name__ == '__main__':
    main()
