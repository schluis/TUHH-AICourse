import math
import random
from typing import Tuple

from game import Player, GameState, OtherAction, Game


class TicTacToeState(GameState):
    def __init__(self, cells: Tuple[Tuple[int, ...], ...], turn: Player):
        super().__init__(turn)
        self.cells = cells

    def __copy__(self):
        return TicTacToeState(self.cells, self.turn)


class TicTacToeAction(OtherAction):
    def __init__(self, r, c):
        self.r = r
        self.c = c


class TicTacToeGame(Game):
    def __init__(self):
        super().__init__(TicTacToeState(((-1, -1, -1),) * 3, Player.MAX))

    def perform_action(self, action: TicTacToeAction):
        self.state = result(self.state, action)
        if is_goal(self.state):
            self.done = True
            if _has_won(self.state):
                print(f"== Player {Player(1 - self.state.turn.value).name} won! ==")
            else:
                print(f"== Draw ==")

    def render(self):
        # MAX has x, MIN has o
        sym = {-1: " ", 0: "x", 1: "o"}
        print("")
        print("+" + "-" * 3 + "+")
        for r in self.state.cells:
            out = ["|"]
            for x in r:
                out.append(sym[x])
            out.append("|")
            print("".join(out))
        print("+" + "-" * 3 + "+")
        print("")


def _has_won(state: TicTacToeState):
    for r in range(3):
        if (
            state.cells[r][0] >= 0
            and state.cells[r][0] == state.cells[r][1] == state.cells[r][2]
        ):
            return True
    for c in range(3):
        if (
            state.cells[0][c] >= 0
            and state.cells[0][c] == state.cells[1][c] == state.cells[2][c]
        ):
            return True
    if (
        state.cells[0][0] >= 0
        and state.cells[0][0] == state.cells[1][1] == state.cells[2][2]
    ):
        return True
    if (
        state.cells[0][2] >= 0
        and state.cells[0][2] == state.cells[1][1] == state.cells[2][0]
    ):
        return True
    return False


def is_goal(state: TicTacToeState):
    return _has_won(state) or all(all(x > -1 for x in row) for row in state.cells)


def available_actions(state: TicTacToeState) -> list[TicTacToeAction]:
    actions: list[TicTacToeAction] = []
    for i, row in enumerate(state.cells):
        for j, col in enumerate(row):
            if col < 0:
                actions.append(TicTacToeAction(i, j))
    return actions


def result(state: TicTacToeState, action: TicTacToeAction) -> TicTacToeState:
    cells = list(list(x for x in r) for r in state.cells)
    cells[action.r][action.c] = state.turn.value
    return TicTacToeState(cells, Player(1 - state.turn.value))


def utility(state: TicTacToeState) -> float:
    if not _has_won(state):
        return 0
    if state.turn == Player.MAX:
        return (
            -1
        )  # If it's MAX's turn, it means that MIN drew the winning circle/cross --> MAX loses.
    else:
        return 1


count = 0


def interactive_game():
    global count
    """
    Play a round of tic-tac-toe against MAX with an optimal strategy given by `minimax_decision`.
    """
    game = TicTacToeGame()
    game.render()
    while not game.done:
        if game.state.turn == Player.MAX:
            action = alpha_beta_search(game.state)
            assert action is not None 
            print("Explored nodes:", count)
        else:
            while True:
                nums = input(
                    "Where do you want to place your symbol? (Format: row col) "
                )
                a, b = [int(x) - 1 for x in nums.split()]
                if (0 <= a <= 2) and (0 <= b <= 2) and game.state.cells[a][b] < 0:
                    break
                print(f"Please choose a valid non-empty cell.")
            action = TicTacToeAction(a, b)
        game.perform_action(action)
        game.render()




def alpha_beta_search(state: TicTacToeState) -> TicTacToeAction | None:
    # Used for counting the number of explored nodes => do not modify!
    global count
    count = 0

    v = -math.inf
    best_action = None

    for action in available_actions(state):
        new_v = min_value(result(state, action), -math.inf, math.inf)

        if new_v >= v:
            v = new_v
            best_action = action
    
    return best_action


def max_value(
    state: TicTacToeState, alpha: float, beta: float
    ) -> float:
    # Used for counting the number of explored nodes => do not modify!
    global count
    count += 1

    if is_goal(state):
        return utility(state)
    
    v = -math.inf
    actions = available_actions(state)
    random.shuffle(actions)
    for action in actions:
        v = max(v, min_value(result(state, action), alpha, beta))

        if v >= beta:
            return v
        
        alpha = max(alpha, v)

    return v


def min_value(
    state: TicTacToeState, alpha: float, beta: float
) -> float:
    # Used for counting the number of explored nodes => do not modify!
    global count
    count += 1

    if is_goal(state):
        return utility(state)
    
    v = math.inf
    actions = available_actions(state)
    random.shuffle(actions)
    for action in actions:
        v = min(v, max_value(result(state, action), alpha, beta))

        if v <= alpha:
            return v

        beta = min(beta, v)

    return v


interactive_game()
