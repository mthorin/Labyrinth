from Labyrinth.player import *
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

        tensor = convert_gameboard_to_tensor(gameboard, self.cards, self.colour)

        # Slide space search
        pi_max, pi_slide = self._search_slide_space(gameboard.clone(), iterations=1000)
        direction, orientation = pi_max

        new_board = gameboard.slide_tiles(direction, orientation)

        # Move space search
        destination, pi_move = self._search_move_space(new_board.clone(), iterations=1000)
        
        # Smart Path
        path = self._smart_path(destination, new_board)

        self.data_bank.append(tuple([tensor, pi_slide, pi_move]))

        return direction, orientation, path
    
    def _search_slide_space(self, initial_state, iterations=1000):
        root = SlideNode(self.network, self.cards, self.colour, self.cards, self.colour, initial_state)

        for _ in range(iterations):
            node = None
            while not node:
                node = self._select(root)
            reward = node.value
            self._backpropagate(node, reward)

        pi = root.generate_pi(self.exploration_weight)

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
            node = None
            while not node:
                node = self._select(root)
            reward = node.value
            self._backpropagate(node, reward)

        pi = root.generate_pi(self.exploration_weight)

        pi_max = torch.argmax(pi).item()
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

    def _smart_path(self, destination, new_board):

        player = new_board.players[new_board.turn]
        player_start = (player.x, player.y)

        targets = []
        if player.cards == []:
            targets = [(player.home_x, player.home_y)]
        else:
            num_cards = len(player.cards)
            for i in range(num_cards):
                card_loc = new_board.find_card(player.cards[i])
                if card_loc:
                    targets.append(card_loc)
        
        if len(targets) == 0:
            _, path = new_board.shortest_path_to_closest((end_x, end_y), destination)
            return path

        target_x, target_y = targets[0]
        # Try to calculate the shortest path to first card
        (end_x, end_y), path = new_board.shortest_path_to_closest(player_start, targets[0])

        # Calculate how good the move is
        score = abs(end_x - target_x) + abs(end_y - target_y)

        if score == 0:
            if player.cards == []:
                return path
            # Made it to the first card, should try to get to the next one
            keep_chaining = True
            target_index = 1
            while keep_chaining and target_index <= len(targets):
                (start_x, start_y) = (end_x, end_y)
                if target_index < len(targets):
                    target_x, target_y = targets[target_index]
                else:
                    target_x, target_y = (player.home_x, player.home_y)
                (end_x, end_y), path2 = new_board.shortest_path_to_closest((start_x, start_y), (target_x, target_y))
                path += path2
                keep_chaining = end_x == target_x and end_y == target_y
                target_index += 1
            if keep_chaining:
                return path
            
        _, path2 = new_board.shortest_path_to_closest((end_x, end_y), destination)
        path += path2

        return path


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
        _, m, y = self.network(tensor, slide=False)
        self.m_logits = self._convert_tensor_to_probabilities(m)

        if colour == org_colour:
            self.value = y.item()
        else:
            new_tensor = convert_gameboard_to_tensor(state, org_cards, org_colour)
            _, _, y = self.network(new_tensor, slide=False, move=False)
            self.value = y.item()

    def is_fully_expanded(self):
        return len(self.m_logits) <= 0

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
            next_colour = all_player_colours[(all_player_colours.index(self.colour) + 1) % len(all_player_colours)]
            
            child_node = MoveNode(self.network, next_cards, next_colour, self.org_cards, self.org_colour, next_state, 
                                   destination=action, probability=highest_prob, parent=self)
            self.children.append(child_node)
            return child_node
        return None
    
    def generate_pi(self, exploration_weight):
        pi = torch.zeros(49)

        for child in self.children:
            pi[child.destination[0] + (7 * child.destination[1])] = child.visits**(1/exploration_weight)

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
        p, m, y = self.network(tensor)

        self.p_logits = self._convert_tensor_to_probabilities(p)

        if colour == org_colour:
            self.value = y.item()
        else:
            new_tensor = convert_gameboard_to_tensor(state, org_cards, org_colour)
            _, _, y = self.network(new_tensor, slide=False, move=False)
            self.value = y.item()

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
            if self.state.last_slide == action[0]:
                return None
            next_state = self.state.slide_tiles(action[0], action[1])
            next_state.players[next_state.turn].x = self.destination % 7
            next_state.players[next_state.turn].y = self.destination // 7

            # Select random cards for next opponent (same number of cards as self)
            next_cards = random.sample([item for item in card_list if item not in self.cards], len(self.cards))
            # Increment color 
            next_colour = all_player_colours[(all_player_colours.index(self.colour) + 1) % len(all_player_colours)]
            
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

def convert_gameboard_to_tensor(gameboard, cards, colour):
        """Convert game state to tensor for input into network."""
        def check_tile(tile):
            north = 0
            east = 0
            south = 0
            west = 0
            token = 0
            home = 0
            if cards != []:
                if tile.token is not None and tile.token in cards[0]:
                    token = 1
            if tile.token == str(colour) + " base":
                home = 1
            if tile.NORTH == True:
                north = 1
            if tile.EAST == True:
                east = 1
            if tile.SOUTH == True:
                south = 1
            if tile.WEST == True:
                west = 1
            return north, east, south, west, token, home
            
        state_tensor = torch.zeros(12, 7, 7) #player location, paths 4, is card, is home

        # Set player location information
        for player in gameboard.players:
            if player.colour == colour:
                state_tensor[0, player.x, player.y]

        float_north, float_east, float_south, float_west, float_token, _ = check_tile(gameboard.floating_tile)

        # set board info
        for x in range(7):
            for y in range(7):
                north, east, south, west, token, base = check_tile(gameboard._board[x][y])
                state_tensor[1, x, y] = north
                state_tensor[2, x, y] = east
                state_tensor[3, x, y] = south
                state_tensor[4, x, y] = west
                state_tensor[5, x, y] = token
                state_tensor[6, x, y] = base
                state_tensor[7, x, y] = float_north
                state_tensor[8, x, y] = float_east
                state_tensor[9, x, y] = float_south
                state_tensor[10, x, y] = float_west
                state_tensor[11, x, y] = float_token

        return state_tensor