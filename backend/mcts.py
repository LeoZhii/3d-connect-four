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
        valid_moves = game.get_valid_moves(root_state)
        opponent = game.get_opponent(player)

        # 1. FAST CHECK: Immediate Winning Move (1-ply)
        for move in valid_moves:
            # Check if this move leads to an immediate win for the AI
            temp_state = game.make_move(copy.deepcopy(root_state), move, player)
            if game.get_result(move['x'], move['y'], move['z'], player, grid=temp_state) == 1: 
                # Found the winning move, return it immediately
                return move 
        
        # 2. FAST CHECK: Immediate Losing Threat (2-ply)
        losing_moves = [] # Moves that allow the opponent to win on their next turn
        
        for move in valid_moves:
            # AI makes a potential move
            temp_state = game.make_move(copy.deepcopy(root_state), move, player)
            
            # Check every subsequent move the opponent can make
            for opponent_move in game.get_valid_moves(temp_state):
                final_state = game.make_move(copy.deepcopy(temp_state), opponent_move, opponent)
                
                # If opponent wins on their next turn, the AI's initial 'move' is bad
                if game.get_result(opponent_move['x'], opponent_move['y'], opponent_move['z'], opponent, grid=final_state) == 1:
                    losing_moves.append(move)
                    break # Stop checking responses to this AI move, it's identified as a threat enabler

        # 3. Handle Forced Block Scenario
        # If there is only *one* move that is NOT a losing move, that must be the block.
        safe_moves = [m for m in valid_moves if m not in losing_moves]
        
        if len(safe_moves) == 1:
            # If a unique move exists that prevents the opponent from winning, use it
            return safe_moves[0]
            
        # If all moves are losing, MCTS must still run to find the 'least bad' move.
        # If the number of safe moves is small (e.g., 2), MCTS will quickly converge.

        # 4. MCTS Simulation Phase (Standard)
        root = Node(state=copy.deepcopy(root_state), player=player)
        
        for _ in range(self.simulations):
            node = self._select(root, game)
            reward = self._simulate(node.state, node.player, game)
            self._backpropagate(node, reward)

        # 5. Determine Final Move
        
        # Filter the children to only include safe moves if safe moves exist
        children_to_evaluate = root.children
        if safe_moves:
            children_to_evaluate = [child for child in root.children if child.move in safe_moves]
            # If filtering left no children (e.g., due to low simulation count), use all children
            if not children_to_evaluate and root.children:
                 children_to_evaluate = root.children

        # If the root is empty (very rare), just pick a random valid move
        if not children_to_evaluate:
            return random.choice(valid_moves)

        # Return the move with the most visits among the chosen set of children
        return max(children_to_evaluate, key=lambda child: child.visits).move

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