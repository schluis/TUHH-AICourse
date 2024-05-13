from __future__ import annotations
from enum import Enum
from abc import ABC, abstractmethod
from typing import Union, List
import math
import random


class EnumAction(Enum):
    pass


class OtherAction(ABC):
    pass


Action = Union[OtherAction, OtherAction, int]


class GameState(ABC):
    def __init__(self, player_turn: int):
        self.player_turn = player_turn

    @abstractmethod
    def is_goal(self) -> bool:
        pass

    @abstractmethod
    def available_actions(self) -> List[Action]:
        pass

    @abstractmethod
    def result(self, action: Action) -> GameState:
        pass

    @abstractmethod
    def utilities(self) -> tuple[int, int] | None:
        pass


class Game(ABC):
    def __init__(self, state):
        self.state = state
        self.done = False

    @abstractmethod
    def perform_action(self, action: Action):
        pass


def solve(state: GameState) -> Action:
    v = tuple(-math.inf for _ in range(2))
    best_action = None

    actions = state.available_actions()
    if type(actions) == list:
        random.shuffle(actions)

    for action in actions:
        values = max_values(state.result(action))

        if values[state.player_turn] > v[state.player_turn]:
            v = values
            best_action = action

        elif values[state.player_turn] == v[state.player_turn]:
            if (
                values[(state.player_turn + 1) % 2] < v[(state.player_turn + 1) % 2]
            ):  # maximize other players utility if that doesn't affect our utility
                v = values
                best_action = action

    return best_action


def max_values(state: GameState) -> tuple[float, float] | None:
    if state.is_goal():
        return state.utilities()

    v = tuple(-math.inf for _ in range(2))
    actions = state.available_actions()
    for action in actions:
        values = max_values(state.result(action))
        if values[state.player_turn] > v[state.player_turn]:
            v = values

    return v
