#!/usr/bin/python
from board import *
from player import *
import time, random, copy
import utils
from utils import checked_input, str_bool

class RuleSet:
    def __init__(self):
        self.SEE_ALL_CARDS = False
        self.CARDS_IN_ORDER = False
        self.MOVE_BEFORE_TURN = False
        self.MOVE_AFTER_PICKUP = False
        self.END_AT_HOME = True
        self.NUMBER_OF_TOKENS = 3
        self.NUMBER_OF_SLIDES = 1
        self.MOVE_TILE_LIMIT = 0

    def configure(self):
        def request_bool(message, default):
            if default:
                yn = "YES/no"
            else:
                yn = "yes/NO"
            return checked_input("{} ({}): ".format(message, yn),
                                lambda x: x != None, str_bool, default)

        def request_int(message, default, min_val, max_val):
            return checked_input("{} [{}] ({}-{}): ".format(message, default, min_val, max_val),
                                lambda x: min_val <= x <= max_val, int, default)

        self.SEE_ALL_CARDS = request_bool("[RULESET] See all players cards", self.SEE_ALL_CARDS)
        self.CARDS_IN_ORDER = request_bool("[RULESET] Must collect cards in order", self.CARDS_IN_ORDER)
        self.MOVE_BEFORE_TURN = request_bool("[RULESET] Allow movement before slide", self.MOVE_BEFORE_TURN)
        self.MOVE_AFTER_PICKUP = request_bool("[RULESET] Allow movement after pickup", self.MOVE_AFTER_PICKUP)
        self.END_AT_HOME = request_bool("[RULESET] Game ends with players at home", self.END_AT_HOME)
        self.NUMBER_OF_TOKENS = request_int("[RULESET] Maximum number of cards", self.NUMBER_OF_TOKENS, 0, len(all_tokens))
        self.NUMBER_OF_SLIDES = request_int("[RULESET] Number of slides per turn", self.NUMBER_OF_SLIDES, 0, 100000)
        self.MOVE_TILE_LIMIT = request_int("[RULESET] Player move limit (0 is unlimited)", self.MOVE_TILE_LIMIT, 0, 100000)


class Labyrinth:
    def __init__(self, ruleset, players):
        self.ruleset = ruleset
        self.gameboard = GameBoard(players)
        self.deck = list(copy.deepcopy(all_tokens))
        self.show_colours = True
        random.shuffle(self.deck)

        # Work out how many cards to deal each player
        max_cards = int(len(self.deck) / len(self.gameboard.players))
        num = self.ruleset.NUMBER_OF_TOKENS
        if max_cards < num:
            num = max_cards

        # Deal the cards
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
        if self.ruleset.SEE_ALL_CARDS:
            return "{}\n{}\n{}\n\n".format(self.gameboard, self.gameboard.players, self.gameboard.floating_tile)
        else:
            return "{}\n\n{}\n\n".format(self.gameboard, self.gameboard.floating_tile)

    __repr__ = __str__

def main():
    ruleset = RuleSet()
    utils.enable_colours(True)

    players = [Player(colour) for colour in all_player_colours]

    lab = Labyrinth(ruleset, players)
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
