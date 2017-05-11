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
        random.shuffle(self.deck)
        print(self.deck)

    def deal_cards(self, num=1):
        for i in range(num):
            for p in self.gameboard.players:
                p.cards.append(self.deck[0])
                self.deck = self.deck[1:]

    def make_turn(self):
        # Get the player who's turn it is
        player = self.gameboard.players[self.gameboard.turn]

        # Let them decide a move
        (direction, orientation, move_path) = player.decide_move(self.gameboard)

        # Execute the slide
        board = self.gameboard.slide_tiles(direction, orientation)
        player = board.players[self.gameboard.turn]

        # If there is a move limit, enforce it
        if self.ruleset.MOVE_TILE_LIMIT > 0:
            move_path[self.ruleset.MOVE_TILE_LIMIT:]

        # Execute the move
        for step in move_path:
            PlayerMovement.move(step, board._board, player)

        # Save the changes
        self.gameboard = board
        self.gameboard.turn = (self.gameboard.turn + 1) % len(board.players)

    def __str__(self):
        return "{}\n{}\n{}\n\n".format(self.gameboard, self.gameboard.players, self.gameboard.floating_tile)

    __repr__ = __str__

def main():
    ruleset = RuleSet()
    players = [Player(colour) for colour in all_player_colours]

    lab = Labyrinth(ruleset, players)
    lab.deal_cards(3)
    print(lab)

    for i in range(100):
        lab.make_turn()
        print(lab)
        time.sleep(0.1)

    print("Done")

if __name__ == '__main__':
    main()
