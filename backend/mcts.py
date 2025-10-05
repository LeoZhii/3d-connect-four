### implements monte carlo tree search algorithm
###    
### returns best move after running all simulations

import math, random, copy
import game

class Node: 
    def __init__(self, state, parent=None, move=None, player=None):
        self.state = state      #game board state
        self.parent = parent
        self.move = move        #move that led to this node
        self.player = player    #which player made this move
        self.children = []      #possible future moves/next states
        self.visits = 0         #times this node was explored
        self.wins = 0           #wins recorded from simulations

    def is_fully_expanded(self):
        return len(self.children) == len(game.get_valid_moves(self.state))

    def best_child(self, exploration_constant):
        return max(
            self.children,
            key = lambda child: child.wins / child.visits + exploration_constant * math.sqrt(math.log(self.visits) / child.visits)
        )

class MCTS: 
    def __init__(self, simulations = 1000, exploration_constant=math.sqrt(2)):
        self.simulations = simulations
        self.c = exploration_constant

    def best_move(self, root_state, player, game):
        root = Node(state=copy.deepcopy(root_state), player = player)

        for _ in range(self.simulations):
            node = self._select(root, game)
            reward = self._simulate(node.state, node.player, game)
            self._backpropagate(node, reward)

        #Return move with the most visits
        return max(root.children, key=lambda child: child.visits).move

    def _select(self, node, game):
        #traverse down until unexpanded or terminal
        while not game.is_terminal(node.state):
            valid_moves = game.get_valid_moves(node.state)
            if len(node.children) < len(valid_moves):
                self._expand(node, game)
                return node.children[-1]
            else:
                node = node.best_child(self.c)
        return node

    def _expand(self, node, game):
        valid_moves = game.get_valid_moves(node.state)
        tried_moves = [c.move for c in node.children]

        untried_moves = [m for m in valid_moves if m not in tried_moves]
        move = random.choice(untried_moves)

        new_state = game.make_move(copy.deepcopy(node.state), move, node.player)
        next_player = game.get_opponent(node.player) 

        child = Node(state=new_state, parent=node, move=move, player=next_player)
        node.children.append(child)

    def _simulate(self, state, player, game):
        #simulate random play until terminal
        current_player = player
        sim_state = copy.deepcopy(state)
        while not game.is_terminal(sim_state):
            moves = game.get_valid_moves(sim_state)
            move = random.choice(moves)
            sim_state = game.make_move(sim_state, move, current_player)
            current_player = game.get_opponent(current_player)
        return game.get_result(sim_state, player)

    def _backpropagate(self, node, reward):
        while node:
            node.visits += 1
            node.wins += reward
            node = node.parent

## for testing algor should return a move
if __name__ == "__main__":
    game = game.DummyGame()
    board = [0] * 9
    mcts = MCTS(simulations=100)
    move = mcts.best_move(board, player=1, game=game)
    print(f"Best move chosen: {move}") 