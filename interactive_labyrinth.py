#!/usr/bin/env python
from labyrinth import *
from player import *
from tile import *
from utils import checked_input
import utils
import time

class InteractivePlayer(Player):
    def __init__(self, colour):
        super().__init__(colour)

    def decide_move(self, gameboard):
        assert(all(hasattr(self, a) for a in ["home_x", "home_y", "x", "y"]))

        if gameboard.last_slide is not None:
            print("Do not choose {}".format(TileMovement.to_str(gameboard.last_slide)))

        print("Your cards are {}".format(self.cards))

        slide = gameboard.last_slide
        while slide == gameboard.last_slide:
            slide_direction = checked_input("Slide Direction (top/bottom/left/right): ",
                                            lambda x: x in ["t", "b", "l", "r"],
                                            lambda x: x.lower()[0])

            if slide_direction in ["t", "b"]:
                slide_slot = checked_input("Slide Slot (left/middle/right): ",
                                           lambda x: x in ["l", "m", "r"],
                                           lambda x: x.lower()[0])
            else:
                slide_slot = checked_input("Slide Slot (top/middle/bottom): ",
                                           lambda x: x in ["t", "m", "b"],
                                           lambda x: x.lower()[0])

            slide = TileMovement.from_str(slide_direction, slide_slot)

            if slide == gameboard.last_slide:
                print("Cannot slide the tile in that direction")

        slide_orientation = checked_input("Tile Orientation (0/90/180/270) CW: ",
                                          lambda x: x in [0, 90, 180, 270],
                                          lambda x: int(x) % 360)

        new_board = gameboard.slide_tiles(slide, slide_orientation)
        print(new_board)

        print("Slide has been applied")

        path = []
        running = True
        player = new_board.players[new_board.turn]
        print("Your cards are {}".format(player.cards))
        while True:
            direction = checked_input("Move player (w/a/s/d/end): ",
                                      lambda x: x in ["w", "a", "s", "d", "end"],
                                      lambda x: x.lower())
            if direction == "w":
                step = PlayerMovement.UP
            elif direction == "a":
                step = PlayerMovement.LEFT
            elif direction == "s":
                step = PlayerMovement.DOWN
            elif direction == "d":
                step = PlayerMovement.RIGHT
            elif direction == "end":
                break # no more input
            else:
                assert(False) # impossible case

            if PlayerMovement.move(step, new_board._board, player):
                path.append(step)
                print(new_board)
            else:
                print("Cannot move in that direction")

        return slide, slide_orientation, path

def main():
    ruleset = RuleSet()
    utils.enable_colours(True)

    # Print title in colours
    title = "Labyrinth"
    colours = ["red", "blue", "yellow", "green"]
    for i, letter in enumerate(iter(title)):
        print(colourise(colours[i % 4], letter), end='')

    # Can terminal print colours?
    colours = checked_input("\nDid the title render correctly? (yes/no)? ",
                            lambda x: x == "yes" or x == "no",
                            lambda x: x.lower())
    if colours == "yes":
        utils.enable_colours(True)
    elif colours == "no":
        utils.enable_colours(False)
    print("")

    # Get number of human and ai players
    num_humans = checked_input("Number of human players (max 4): ",
                               lambda x: 0 <= x <= 4, int)

    max_ai = 4 - num_humans
    num_ai = 0
    if max_ai > 0:
        num_ai = checked_input("Number of ai players (max {}): ".format(max_ai),
                                   lambda x: 0 <= x <= max_ai, int)

    # Create the players
    players = []
    if num_humans > 0:
        players += [InteractivePlayer(colour) for colour in all_player_colours[0:num_humans]]
    if num_ai > 0:
        players += [Player(colour) for colour in all_player_colours[num_humans:num_humans + num_ai]]

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
