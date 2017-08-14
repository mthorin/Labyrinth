#!/usr/bin/env python
from labyrinth import *
from player import *
from tile import *
import time

class InteractivePlayer(Player):
    def __init__(self, colour):
        super().__init__(colour)

    def decide_move(self, gameboard):
        assert(all(hasattr(self, a) for a in ["home_x", "home_y", "x", "y"]))

        if gameboard.last_slide is not None:
            print("Do not choose {}".format(TileMovement.to_str(gameboard.last_slide)))

        print("Your cards are {}".format(self.cards))
        slide_direction = input("Slide Direction (top/bottom/left/right): ").lower()[0]
        assert(slide_direction in ["t", "b", "l", "r"])

        if slide_direction in ["t", "b"]:
            slide_slot = input("Slide Slot (left/middle/right): ").lower()[0]
            assert(slide_slot in ["l", "m", "r"])
        else:
            slide_slot = input("Slide Slot (top/middle/bottom): ").lower()[0]
            assert(slide_slot in ["t", "m", "b"])

        slide = TileMovement.from_str(slide_direction, slide_slot)

        slide_orientation = int(input("Tile Orientation (0/90/180/270) CW: "))
        assert(slide_orientation in [0, 90, 180, 270])

        new_board = gameboard.slide_tiles(slide, slide_orientation)
        print(new_board)

        print("Slide has been applied")

        path = []
        running = True
        player = new_board.players[new_board.turn]
        print("Your cards are {}".format(player.cards))
        while True:
            direction = input("Move player (w/a/s/d/end): ").lower()[0]
            assert(direction in ["w", "a", "s", "d", "e"])
            if direction == "w":
                step = PlayerMovement.UP
            elif direction == "a":
                step = PlayerMovement.LEFT
            elif direction == "s":
                step = PlayerMovement.DOWN
            elif direction == "d":
                step = PlayerMovement.RIGHT
            elif direction == "e":
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

    num_humans = int(input("Number of human players (max 4): "))
    assert(0 <= num_humans <= 4)

    num_ai = int(input("Number of ai players (max {}): ".format(4 - num_humans)))
    assert(0 <= num_ai <= 4)
    assert(1 <= num_humans + num_ai <= 4)

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
