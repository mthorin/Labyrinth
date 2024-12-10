from player import *

class Theseus(Player):
    def __init__(self, colour):
        super().__init__(colour)

    def decide_move(self, gameboard):
        assert(all(hasattr(self, a) for a in ["home_x", "home_y", "x", "y"]))

        # TODO

        return slide, slide_orientation, path