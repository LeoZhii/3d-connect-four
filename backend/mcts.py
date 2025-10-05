### implements monte carlo tree search algorithm
###    
### returns best move after running all simulations

import math, random, copy
from game_funcs import game_data

class Node: 
    def __init__(self, state, parent=None, move=None, player=None):
        self.state = state      #game board state
        self.parent = parent
        self.move = move        #move that led to this node
        self.player = player    #which player made this move
        self.children = []      #possible future moves/next states
        self.visits = 0         #times this node was explored
        self.wins = 0           #wins recorded from simulations

    def is_fully_expanded(self, game):
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
        # The player who started the MCTS tree search is 'player' (the AI)
        sim_state = copy.deepcopy(state)
        # The player whose turn it is to make the FIRST move in the simulation
        current_player = game.get_opponent(player) 
        
        # Keep track of the last move made and by whom, needed for get_result
        last_move = None
        
        while True:
            valid_moves = game.get_valid_moves(sim_state)

            # --- Check for Terminal State (Win or Draw) based on the LAST move ---
            # If a move was made, check the result of that move
            if last_move:
                # 'result' is 1 (current_player won), 0.5 (draw), or None (game continues)
                result = game.get_result(last_move['x'], last_move['y'], last_move['z'], 
                                         game.get_opponent(current_player), grid=sim_state)
                
                if result is not None:
                    # Game is terminal (Win or Draw)
                    break 

            # --- Handle No Valid Moves (Pre-emptive Draw Check) ---
            if not valid_moves:
                # This should be covered by get_result checking for grid full,
                # but serves as a safety break.
                result = 0.5 
                break

            # --- Random Move and State Update ---
            move = random.choice(valid_moves)
            sim_state = game.make_move(sim_state, move, current_player)
            last_move = move
            
            # Switch to the next player
            current_player = game.get_opponent(current_player)

        # --- Backpropagate the Final Reward ---
        # If the loop broke, the game is terminal. 'result' holds the outcome (1 or 0.5).
        
        if result == 1:
            # A win (1) means the player who just finished their move (the opponent of current_player) won.
            winner = game.get_opponent(current_player)
            
            if winner == player:
                return 1  # AI player won: Full Reward
            else:
                return 0  # AI player lost: Zero Reward
                
        elif result == 0.5:
            return 0.5 # Draw Reward
        
        # Fallback: Should not be reached if get_result logic is correct
        return 0.5 

    def _backpropagate(self, node, reward):
        while node:
            node.visits += 1
            node.wins += reward
            node = node.parent

## for testing algor should return a move
if __name__ == "__main__":
    game = game_data
    board = game.grid
    mcts = MCTS(simulations=800)
    move = mcts.best_move(board, player=1, game=game)
    print(f"Best move chosen: {move}")