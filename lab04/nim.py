import math
from enum import Enum
from typing import Set

from game import Player, GameState, EnumAction, Game


class NimState(GameState):
    def __init__(self, count: int, turn: Player):
        super().__init__(turn)
        self.count = count


class NimAction(EnumAction):
    TAKE_ONE = 1
    TAKE_TWO = 2
    TAKE_THREE = 3


class NimGame(Game):
    def __init__(self, N):
        super().__init__(NimState(N, Player.MAX))

    def perform_action(self, action: NimAction):
        self.state = result(self.state, action)
        if is_goal(self.state):
            self.done = True
            print(f"== Player {Player(1 - self.state.turn.value).name} won! ==")


def is_goal(state: NimState):
    return state.count == 0


def available_actions(state: NimState) -> Set[NimAction]:
    actions = set([NimAction.TAKE_ONE])
    if state.count >= 2:
        actions.add(NimAction.TAKE_TWO)
    if state.count >= 3:
        actions.add(NimAction.TAKE_THREE)
    return actions


def result(state: NimState, action: NimAction) -> NimState:
    return NimState(state.count - action.value, Player(1 - state.turn.value))


def utility(state: NimState) -> int:
    if state.count > 0:
        return 0
    if state.turn == Player.MAX:
        return (
            -1
        )  # If it's MAX's turn, it means that MIN took the last object --> MAX loses.
    else:
        return 1


def interactive_game(N: int):
    """
    Plays a round of Nim against MAX with an optimal strategy given by `minimax_decision`.
    """
    game = NimGame(N)
    print(f"{game.state.count} objects left")
    while not game.done:
        if game.state.turn == Player.MAX:
            action = minimax_search(game.state)
        else:
            num = 0
            while True:
                num = input("How many objects would you like to remove? ")
                u = min(3, game.state.count)
                if num.isdigit() and 1 <= int(num) <= u:
                    break
                print(f"Please enter a number between 1 and {u}.")
            action = NimAction(int(num))
        print(
            f"Player {game.state.turn.name} removes {action.value} object{'' if action.value == 1 else 's'} from the pile"
        )
        game.perform_action(action)
        print(
            f"    ({game.state.count} object{'' if game.state.count == 1 else 's'} left)"
        )


def optimal_game(N: int):
    """
    Simulates a game of Nim with `N` objects, where both MIN and MAX play optimally.
    """
    game = NimGame(N)
    print(f"{game.state.count} objects left")
    while not game.done:
        action = (
            minimax_search(game.state)
            if game.state.turn == Player.MAX
            else maximin_search(game.state)
        )
        print(
            f"Player {game.state.turn.name} removes {action.value} object{'' if action.value == 1 else 's'} from the pile"
        )
        game.perform_action(action)
        print(
            f"    ({game.state.count} object{'' if game.state.count == 1 else 's'} left)"
        )


################################################################################


def minimax_search(state: NimState) -> NimAction:
    max_utility = -math.inf

    max_action = list(available_actions(state))[0]
    for action in available_actions(state):
        value = min_value(result(state, action))

        if value > max_utility:
            max_utility = value
            max_action = action

    return max_action


def maximin_search(state: NimState) -> NimAction:
    min_utility = math.inf

    min_action = list(available_actions(state))[0]
    for action in available_actions(state):
        value = max_value(result(state, action))

        if value < min_utility:
            min_utility = value
            min_action = action

    return min_action


def max_value(state: NimState) -> int:
    if is_goal(state):
        return utility(state)

    v = -math.inf
    for action in available_actions(state):
        v = max(v, min_value(result(state, action)))

    return int(v)


def min_value(state: NimState) -> int:
    if is_goal(state):
        return utility(state)

    v = math.inf
    for action in available_actions(state):
        v = min(v, max_value(result(state, action)))
    
    return int(v)


interactive_game(N=8)
# optimal_game(N=18)
