from enum import Enum


class State(int, Enum):
    CONTINUE = 0,
    PLAYER_1_WIN = 1,
    PLAYER_2_WIN = 2,
    DRAW = 3
