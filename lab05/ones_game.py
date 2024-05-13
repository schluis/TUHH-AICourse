from typing import List
from game import Game, GameState, solve

N_ROUNDS = 8


class OnesState(GameState):
    def __init__(self, player_turn: int, history: List[int]):
        self.player_turn = player_turn
        self.history = history

    def available_actions(self):
        return [0, 1]

    def result(self, action: int):
        return OnesState(1 - self.player_turn, self.history + [action])

    def is_goal(self):
        return len(self.history) >= 2 * N_ROUNDS

    def utilities(self):
        if not self.is_goal():
            return None
        i = 0
        hists = [[], []]
        for a in self.history:
            hists[i].append(a)
            i = 1 - i

        boni = []
        for hist in hists:
            bonus = 0
            for i in range(1, len(hist)):
                bonus += hist[i] != hist[i - 1]
            boni.append(bonus)

        utils = [sum(hists[0]), sum(hists[1])]

        for i in range(len(hist)):
            v1, v2 = hists[0][i], hists[1][i]
            if (v1, v2) == (1, 1):
                utils[0] -= 2
                utils[1] -= 2

        return tuple(utils[i] + boni[i] for i in [0, 1])


class OnesGame(Game):
    def __init__(self):
        self.state = OnesState(0, [])
        self.done = False

    def perform_action(self, action: int):
        self.state = self.state.result(action)
        if self.state.is_goal():
            self.done = True


game = OnesGame()
while not game.done:
    a = solve(game.state)
    print(f"Player {game.state.player_turn + 1}'s action: {a}")
    game.perform_action(a)
print("Utilities:", game.state.utilities())
