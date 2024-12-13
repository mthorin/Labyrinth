from player import *
import torch

class Theseus(Player):
    def __init__(self, colour, network, exploration_weight=0):
        super().__init__(colour)
        self.network = network
        self.exploration_weight = exploration_weight

    def decide_move(self, gameboard):
        assert(all(hasattr(self, a) for a in ["home_x", "home_y", "x", "y"]))

        # TODO: Decay exploration_weight after 30 turns?

        direction, orientation = self._search(gameboard.clone(), iterations=1000)

        tensor = convert_gameboard_to_tensor(gameboard)
        p, _ = self.network(tensor)

        action_index = TileMovement.all_moves().index(direction)
        orientation_index = [0, 90, 180, 270].index(orientation)

        destination = torch.argmax(p[action_index, orientation_index])

        new_board = gameboard.slide_tiles(direction, orientation)
        player = new_board.players[new_board.turn]
        
        # TODO Smart Path
        _, path = gameboard.shortest_path_to_closest((player.x, player.y), destination)

        # TODO Return/save gamestate tensor, pi / pi_max

        return direction, orientation, path
    
    def _search(self, initial_state, iterations=1000):
        root = Node(self.network, self.cards, self.colour, initial_state)

        for _ in range(iterations):
            node = self._select(root)
            reward = node.value
            self._backpropagate(node, reward)

        pi_max = max(root.children, 
                     key=lambda child: child.visits**(1/self.exploration_weight) / (1000 - child.visits)**(1/self.exploration_weight))
        return pi_max.action

    def _select(self, node):
        """Select a node to expand."""
        while 1:
            if not node.is_fully_expanded():
                return node.expand()
            else:
                node = node.best_child()
        return node

    def _backpropagate(self, node, reward):
        """Propagate the reward back through the tree."""
        while node is not None:
            node.visits += 1
            node.value += reward
            node = node.parent


class Node:
    def __init__(self, network, cards, colour, state, action, probability=0, parent=None):
        self.state = state
        self.parent = parent
        self.children = []
        self.visits = 0
        self.probability = probability
        self.network = network
        self.action = action
        self.cards = cards
        self.colour = colour

        tensor = convert_gameboard_to_tensor(state, cards, colour)
        p, x = self.network(tensor)
        self.p_logits = self._convert_tensor_to_probabilities(p)
        self.value = x.item()

    def is_fully_expanded(self):
        return len(self.p_logits) <= 0

    def best_child(self):
        """Select the best child using the formula used by AlphaGo Zero."""
        choices_weights = [
            (child.value / child.visits) +
            child.probability / 1 + child.visits
            for child in self.children
        ]
        return self.children[choices_weights.index(max(choices_weights))]

    def expand(self):
        """Expand the tree by adding a new child node."""
        highest_prob = max(self.p_logits)
        action = self.p_logits.pop(highest_prob)
        if action:
            next_state = self.state.slide_tiles(action[0], action[1])

            # Select random cards for next opponent (same number of cards as self)
            next_cards = random.sample([item for item in card_list if item not in self.cards], len(self.cards))
            # Increment color 
            next_colour = (all_player_colours.index(self.colour) + 1) % len(all_player_colours)
            
            child_node = Node(self.network, next_cards, next_colour, next_state, action, highest_prob, parent=self)
            self.children.append(child_node)
            return child_node
        return None
    
    def _convert_tensor_to_probabilities(self, logits):
        """Converts probability distribution of all moves dictionary ."""
        combined_probs = torch.sum(logits, dim=2)

        actions = TileMovement.all_moves()
        orientations = [0, 90, 180, 270]

        probability_dist = {combined_probs[i, j].item(): tuple([actions[i], orientations[j]]) 
                            for i in range(combined_probs.shape[0]) 
                            for j in range(combined_probs.shape[1])}

        return probability_dist
    

card_list = ["genie", "skull", "sword", "scarab", "beetle", "rat",
            "dragonfly", "gold", "keys", "gem", "lizard", "helmet",
            "princess", "book", "crown", "treasure", "candlestick",
            "ghost", "spider", "owl", "map", "ring", "man", "bat"]

dynamic_card_list = ["genie", "scarab", "beetle", "rat", 
                     "dragonfly", "lizard", "princess", 
                     "ghost", "spider", "owl", "man", "bat"]

def convert_gameboard_to_tensor(gameboard, cards, colour):
        """Convert game state to tensor for input into network."""
        state_tensor = torch.zeros(53, 58)

        # Set current player
        state_tensor[0, all_player_colours.index(colour)] = 1

        # Set card info
        row = 50
        for card in cards:
            index = card_list.index(card)
            state_tensor[row, index] = 1
            row += 1

        # Set player location information
        for player in gameboard.players:
            state_tensor[1 + player.x + (player.y * 7), all_player_colours.index(player.colour)] = 1

        # set board info
        for x in range(7):
            for y in range(7):
                if x in [0, 2, 4, 6] and y in [0, 2, 4, 6]:
                    continue
                tile = gameboard._board[x][y]

                rotation_offset = 0
                index_offset = 0

                path_count = sum([tile.NORTH, tile.SOUTH, tile.EAST, tile.WEST])

                if path_count == 2 and tile.EAST and tile.WEST:
                    rotation_offset = 1
                else:
                    if tile.token:
                        index_offset = 6
                        index_offset += dynamic_card_list.index(tile.token) * 4
                    if path_count == 2:
                        if tile.EAST and tile.SOUTH:
                            rotation_offset = 1
                        if tile.SOUTH and tile.WEST:
                            rotation_offset = 2
                        if tile.WEST and tile.NORTH:
                            rotation_offset = 3
                    else:
                        if tile.NORTH and tile.EAST and tile.SOUTH:
                            rotation_offset = 1
                        if tile.EAST and tile.SOUTH and tile.WEST:
                            rotation_offset = 2
                        if tile.SOUTH and tile.WEST and tile.NORTH:
                            rotation_offset = 3

                state_tensor[1 + x + (7 * y), 4 + index_offset + rotation_offset] = 1

        return state_tensor