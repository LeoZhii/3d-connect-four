# dummy functions for testing mcts algo
import random

class DummyGame:
    def get_valid_moves(self, state):
        return [i for i, x in enumerate(state) if x == 0]

    def make_move(self, state, move, player):
        state[move] = player
        return state

    def is_terminal(self, state): 
        return all(x != 0 for x in state)

    def get_opponent(self, player):
        return 1 if player == 2 else 2

    def get_result(self, state, player):
        return random.choice([0,1]) 


