from player import *
import torch

class Theseus(Player):
    def __init__(self, colour):
        super().__init__(colour)

    def decide_move(self, gameboard):
        assert(all(hasattr(self, a) for a in ["home_x", "home_y", "x", "y"]))

        # convert gameboard to tensor
        self.convert_gameboard_to_tensor(gameboard)

        # send tensor to theseus (should I do monte carlo sampling? yes)

        # turn result of tensor into action

        direction = (TileMovement.T, TileMovement.L)
        orientation = random.choice([0, 90, 180, 270])
        path = []

        return direction, orientation, path
    
    def convert_gameboard_to_tensor(self, gameboard):

        state = torch.rand(53,62)

        return state