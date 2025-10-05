# Helper functions for the app.py + the MC algorithm
import random
import numpy as np
import itertools

class game_data:
    def __init__(self):
        self.terminal = False #is the game over
        self.grid = np.zeros((4, 4, 5), dtype=int)
        self.turn = 1
        self.moves = []

    # returns 1 for win, 0.5 for draw in perspective of the player
    def get_result(self, x, y, z, player_id):
        elements = [0, 1, -1]
        directions = list(itertools.product(elements, repeat=3))[1:]

        # check for draw
        if not np.any(self.grid==0):
            terminal = True
            return 0.5

        for dx, dy, dz in directions:
            count = 1

            for i in range(1, 4):
                nx, ny, nz = x + dx*i, y + dy*i, z + dz*i
                if 0 <= nx < 4 and 0 <= ny < 4 and 0 <= nz < 5:
                    if self.grid[nx, ny, nz] == player_id:
                        count += 1
                    else:
                        break
                else:
                    break

            for i in range(1, 4):
                nx, ny, nz = x - dx*i, y - dy*i, z - dz*i
                if 0 <= nx < 4 and 0 <= ny < 4 and 0 <= nz < 5:
                    if self.grid[nx, ny, nz] == player_id:
                        count += 1
                    else:
                        break
                else:
                    break

            if count >= 4:
                terminal = True 
                return 1 #win 

        return None 

    def is_terminal(self):
        return terminal 

    def get_opponent(self, current_player):
        return 1 if current_player == 2 else 2


    def get_valid_moves(self):
        # to be valid, coordinate must be empty and apease gravity
        zero_indices = np.argwhere(self.grid == 0)

        valid_moves = []
        for idx in zero_indices:
            x, y, z = idx[0], idx[1], idx[2]

            # check if z is 0 OR space directly below is NOT empty to be valid
            if z == 0 or self.grid[x, y, z-1] != 0:
                valid_moves.append({'x': int(x), 'y': int(y), 'z': int(z)})
            
        return valid_moves

    def make_move(self, state, move, player):
        state[move] = player
        return state

GAME_DATA = game_data() 


# class DummyGame:
#     def get_valid_moves(self, state):
#         return [i for i, x in enumerate(state) if x == 0]

#     def make_move(self, state, move, player):
#         state[move] = player
#         return state

#     def is_terminal(self, state): 
#         return all(x != 0 for x in state)

#     def get_opponent(self, player):
#         return 1 if player == 2 else 2

#     def get_result(self, state, player):
#         return random.choice([0,1]) 