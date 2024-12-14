from player import *
import torch

class Theseus(Player):
    def __init__(self, colour, network, exploration_weight=0.001, data_bank=None):
        super().__init__(colour)
        self.network = network
        self.exploration_weight = exploration_weight
        self.turns = 0
        self.data_bank = data_bank

    def decide_move(self, gameboard):
        assert(all(hasattr(self, a) for a in ["home_x", "home_y", "x", "y"]))

        self.turns += 1
        if self.exploration_weight != 0.001 and self.turns > 30:
            self.exploration_weight = 0.001

        tensor = convert_gameboard_to_tensor(gameboard)

        # Slide space search
        pi_max, pi_slide = self._search_slide_space(gameboard.clone(), iterations=1000)
        direction, orientation = pi_max

        new_board = gameboard.slide_tiles(direction, orientation)
        player = new_board.players[new_board.turn]

        # Move space search
        destination, pi_move = self._search_move_space(new_board.clone(), iterations=1000)
        
        # TODO Smart Path
        _, path = new_board.shortest_path_to_closest((player.x, player.y), destination)

        self.data_bank.append(tuple([tensor, pi_slide, pi_move]))

        return direction, orientation, path
    
    def _search_slide_space(self, initial_state, iterations=1000):
        root = SlideNode(self.network, self.cards, self.colour, self.cards, self.colour, initial_state)

        for _ in range(iterations):
            node = self._select(root)
            reward = node.value
            self._backpropagate(node, reward)

        pi = root.generate_pi()

        sorted_children = sorted(
                            root.children, 
                            key=lambda child: child.visits**(1/self.exploration_weight) / (1000 - child.visits)**(1/self.exploration_weight),
                            reverse=True  # Sort in descending order
                        )
        pi_max = sorted_children[0]
        if pi_max.action[0] == initial_state.last_slide:
            pi_max = sorted_children[1]
        return pi_max.action, pi
    
    def _search_move_space(self, initial_state, iterations=1000):
        root = MoveNode(self.network, self.cards, self.colour, self.cards, self.colour, initial_state)

        for _ in range(iterations):
            node = self._select(root)
            reward = node.value
            self._backpropagate(node, reward)

        pi = root.generate_pi()

        pi_max = torch.argmax(pi)
        return (pi_max % 7, pi_max // 7), pi

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


class MoveNode:
    def __init__(self, network, cards, colour, org_cards, org_colour, state, destination=None, probability=0, parent=None):
        self.state = state
        self.parent = parent
        self.children = []
        self.visits = 0
        self.probability = probability
        self.network = network
        self.destination = destination
        self.cards = cards
        self.colour = colour
        self.org_cards = org_cards
        self.org_colour = org_colour

        tensor = convert_gameboard_to_tensor(state, cards, colour)
        _, m, x = self.network(tensor)
        self.m_logits = self._convert_tensor_to_probabilities(m)

        if colour == org_colour:
            self.value = x.item()
        else:
            new_tensor = convert_gameboard_to_tensor(state, org_cards, org_colour)
            _, _, x = self.network(new_tensor)
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
        highest_prob = max(self.m_logits)
        action = self.m_logits.pop(highest_prob)
        if action:
            next_state = self.state.clone()
            next_state.players[next_state.turn].x = action[0]
            next_state.players[next_state.turn].y = action[1]

            # Select random cards for next opponent (same number of cards as self)
            next_cards = random.sample([item for item in card_list if item not in self.cards], len(self.cards))
            # Increment color 
            next_colour = (all_player_colours.index(self.colour) + 1) % len(all_player_colours)
            
            child_node = MoveNode(self.network, next_cards, next_colour, self.org_cards, self.org_colour, next_state, 
                                   destination=action, probability=highest_prob, parent=self)
            self.children.append(child_node)
            return child_node
        return None
    
    def generate_pi(self, exploration_weight):
        pi = torch.zeros(49)

        for child in self.children:
            pi[child.action[0] + (7 * child.action[1])] = child.visits**(1/exploration_weight)

        return pi / pi.sum()
    
    def _convert_tensor_to_probabilities(self, logits):
        """Converts probability distribution of all moves dictionary."""

        probability_dist = {logits[i + (7 * j)].item(): tuple([i, j])
                            for i in range(7) 
                            for j in range(7)}

        return probability_dist
    

class SlideNode:
    def __init__(self, network, cards, colour, org_cards, org_colour, state, action=None, probability=0, parent=None):
        self.state = state
        self.parent = parent
        self.children = []
        self.visits = 0
        self.probability = probability
        self.network = network
        self.action = action
        self.cards = cards
        self.colour = colour
        self.org_cards = org_cards
        self.org_colour = org_colour

        tensor = convert_gameboard_to_tensor(state, cards, colour)
        p, m, x = self.network(tensor)

        self.p_logits = self._convert_tensor_to_probabilities(p)

        if colour == org_colour:
            self.value = x.item()
        else:
            new_tensor = convert_gameboard_to_tensor(state, org_cards, org_colour)
            _, _, x = self.network(new_tensor)
            self.value = x.item()

        self.destination = torch.argmax(m)

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
            next_state.players[next_state.turn].x = self.destination % 7
            next_state.players[next_state.turn].y = self.destination // 7

            # Select random cards for next opponent (same number of cards as self)
            next_cards = random.sample([item for item in card_list if item not in self.cards], len(self.cards))
            # Increment color 
            next_colour = (all_player_colours.index(self.colour) + 1) % len(all_player_colours)
            
            child_node = SlideNode(self.network, next_cards, next_colour, self.org_cards, self.org_colour, next_state, 
                                   action=action, probability=highest_prob, parent=self)
            self.children.append(child_node)
            return child_node
        return None
    
    def generate_pi(self, exploration_weight):
        pi = torch.zeros(48)

        for child in self.children:
            actions = TileMovement.all_moves()
            orientations = [0, 90, 180, 270]

            direction_index = actions.index(child.action[0])
            orientation_index = orientations.index(child.action[1])

            pi[direction_index + (orientation_index * 12)] = child.visits**(1/exploration_weight)

        return pi / pi.sum()
    
    def _convert_tensor_to_probabilities(self, logits):
        """Converts probability distribution of all moves dictionary."""
        actions = TileMovement.all_moves()
        orientations = [0, 90, 180, 270]

        probability_dist = {logits[i + (j * 12)].item(): tuple([actions[i], orientations[j]]) 
                            for i in range(12) 
                            for j in range(4)}

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
        def set_tensor_for_tile(tensor, tile, row):
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

            tensor[row, 4 + index_offset + rotation_offset] = 1

            return tensor

        state_tensor = torch.zeros(54, 58)

        # Set current player
        state_tensor[0, all_player_colours.index(colour)] = 1

        # Set card info
        row = 51
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
                state_tensor = set_tensor_for_tile(state_tensor, tile, 1 + x + (7 * y))

        # free tile
        state_tensor = set_tensor_for_tile(state_tensor, gameboard.floating_tile, 50)

        return state_tensor