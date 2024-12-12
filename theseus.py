from player import *
import torch

class Theseus(Player):
    def __init__(self, colour, network, exploration_weight):
        super().__init__(colour)
        self.mcts = MCTS(network, exploration_weight)

    def decide_move(self, gameboard):
        assert(all(hasattr(self, a) for a in ["home_x", "home_y", "x", "y"]))

        direction, orientation = self.mcts.search(gameboard, iterations=1000)

        #direction = (TileMovement.T, TileMovement.L)
        #orientation = random.choice([0, 90, 180, 270])
        path = []

        return direction, orientation, path

class Node:
    def __init__(self, network, state, action, probability=0, parent=None):
        self.state = state
        self.parent = parent
        self.children = []
        self.visits = 0
        self.probability = probability
        self.network = network
        self.action = action

        tensor = self._convert_gameboard_to_tensor(state)
        p, x = self.network(tensor)
        self.p_logits = self._convert_tensor_to_probabilities(p)
        self.value = x.item()

    def is_fully_expanded(self):
        return len(self.children) == len(self.state.get_legal_actions())

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
        actions = self.state.get_legal_actions()
        for action in actions:
            if not any(child.state == self.state.perform_action(action) for child in self.children):
                next_state = self.state.perform_action(action)
                child_node = Node(self.network, next_state, action, self.p_logits[action], parent=self)
                self.children.append(child_node)
                return child_node
        return None
    
    def _convert_gameboard_to_tensor(self, gameboard):
        """Convert game state to tensor for input into network."""
        # TODO:
        state = torch.rand(53,62)

        return state
    
    def _convert_tensor_to_probabilities(self, logits):
        probability_dist = {}
        # TODO:

        return probability_dist


class MCTS:
    def __init__(self, network, exploration_weight=1):
        self.exploration_weight = exploration_weight
        self.network = network

    def search(self, initial_state, iterations=1000):
        root = Node(self.network, initial_state)

        for _ in range(iterations):
            node = self._select(root)
            reward = node.value
            self._backpropagate(node, reward)

        pi_max = max(root.children, 
                     key=lambda child: child.visits**(1/self.exploration_weight) / (1000 - child.visits)**(1/self.exploration_weight))
        return pi_max.action

    def _select(self, node):
        """Select a node to expand."""
        while not node.state.is_terminal():
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


# Example game state for testing
class GameState:
    def __init__(self, data):
        self.data = data

    def get_legal_actions(self):
        """Returns possible actions from this state."""
        # Replace with actual logic
        return []

    def perform_action(self, action):
        """Returns the new state after performing an action."""
        # Replace with actual logic
        return GameState(self.data)

    def is_terminal(self):
        """Returns True if the state is terminal."""
        # Replace with actual logic
        return False