from __future__ import annotations

import math
import operator
import random
from copy import deepcopy
from functools import reduce
from itertools import permutations
from math import factorial
from typing import List, Tuple
import json
import numpy as np

from game import EnumAction, Game, GameState


def prod(iterable):
    return reduce(operator.mul, iterable, 1)


cheating = False
verbose = True
expected_player1_value = 0
expected_player2_value = 0


class CardAction(EnumAction):
    PLAY = 0
    REFUSE = 1


class CardState(GameState):
    def __init__(
        self,
        player_turn: int,
        deck: List[int],
        alpha: int,
        choices: List[CardAction],
        cards: List[List[int]],
    ):
        super().__init__(player_turn)
        assert alpha >= 0
        self.deck = deck
        self.alpha = alpha
        self.choices = choices
        self.cards = cards

    def available_actions(self) -> List[CardAction]:
        return [CardAction.PLAY, CardAction.REFUSE]

    def result(self, action: CardAction) -> CardState:
        new_choices = self.choices
        new_choices[self.player_turn] = action
        new_deck = deepcopy(self.deck)
        new_cards = deepcopy(self.cards)
        if (
            self.player_turn == 1 and action == CardAction.PLAY
        ):  # P2 can choose a card from the deck
            if len(new_deck) > 0:
                new_card = new_deck[0]
                new_deck = new_deck[1:]
                new_cards[1].append(new_card)

        return CardState(
            1 - self.player_turn, new_deck, self.alpha, new_choices, new_cards
        )

    def is_goal(self) -> bool:
        return None not in self.choices

    def utilities(self) -> Tuple[int, int] | None:
        if self.choices[0] == CardAction.REFUSE:
            return (-1, 1)
        if self.choices[1] == CardAction.REFUSE:
            return (1, -1)
        if self.choices[1] == CardAction.PLAY:
            maxs = [max(c) for c in self.cards]
            if maxs[0] > maxs[1]:
                return (self.alpha, -self.alpha)
            else:
                return (-self.alpha, self.alpha)


class CardGame(Game):
    def __init__(self, deck: List[int], k: int, alpha: float):
        assert len(deck) >= 2 * k
        cards = [deck[:k], deck[k : (2 * k)]]
        deck = deck[(2 * k) :]
        self.state = CardState(0, deck, alpha, [None, None], cards)

    def perform_action(self, action: CardAction):
        self.state = self.state.result(action)


def solve_MC(N: int, α: int, k: int, p: int):  # p is the number of shuffles to sample
    return (
        expected_value_va(CardAction.PLAY, N, α, k, p),
        expected_value_va(CardAction.REFUSE, N, α, k, p),
    )


def expected_value_va(action: CardAction, N: int, α: int, k: int, p=None):
    assert k <= N / 2
    if p is None:
        p = factorial(N)

    sum = 0
    shuffelings = list(permutations(list(range(1, N + 1))))
    random.shuffle(shuffelings)
    reduced_shuffelings = shuffelings[:p]

    for σ in reduced_shuffelings:
        sum += value(action, σ, N, α, k, True)[0]

    return sum / len(reduced_shuffelings)


def value(
    action: CardAction, σ: tuple[int, ...], N: int, α: int, k: int, do_simulation=False
):  # assuming, that N is known to both players. Otherwise this is random
    if action == CardAction.REFUSE:  # player refuses
        return -1, -1

    max_player1_deck = 0
    max_player2_deck = 0
    max_player2_deck_simulation = 0
    unknown_cards_to_player1 = list(range(1, N + 1))
    unknown_cards_to_player2 = list(range(1, N + 1))
    for number, card in enumerate(σ):
        if number < k:  # first k belong to player1
            unknown_cards_to_player1.remove(card)
            max_player1_deck = max(max_player1_deck, card)
        elif number < 2 * k:  # second k belong to player2
            unknown_cards_to_player2.remove(card)
            max_player2_deck = max(max_player2_deck, card)
            max_player2_deck_simulation = max(max_player2_deck_simulation, card)
        elif number == 2 * k + 1:
            max_player2_deck_simulation = max(max_player2_deck_simulation, card)

    # player 1
    number_of_lower_cards = sum(
        [1 for card in unknown_cards_to_player1 if card < max_player1_deck]
    )
    probability_of_player_2_having_only_lower_cards = math.comb(
        number_of_lower_cards, k + 1
    ) / math.comb(len(unknown_cards_to_player1), k + 1)

    probability_of_player2_having_at_least_one_higher_card = (
        1 - probability_of_player_2_having_only_lower_cards
    )

    # player 2
    number_of_lower_cards = sum(
        [1 for card in unknown_cards_to_player2 if card < max_player2_deck]
    )
    probability_of_player_1_having_only_lower_cards = math.comb(
        number_of_lower_cards, k
    ) / math.comb(len(unknown_cards_to_player2), k)
    probability_of_player1_having_at_least_one_higher_card = (
        1 - probability_of_player_1_having_only_lower_cards
    )

    number_of_cards_higher_than_expected_player1_highest_card = sum(
        [
            1
            for card in unknown_cards_to_player2
            if (card > expected_player1_value and card > max_player2_deck)
        ]
    )
    probability_of_drawing_high_enough_card = (
        number_of_cards_higher_than_expected_player1_highest_card
        / len(unknown_cards_to_player2)
    )

    if verbose:
        print(
            "Probability of player 1 having higher card: ",
            probability_of_player1_having_at_least_one_higher_card,
        )
        print(
            "Probability of player 2 having higher card: ",
            probability_of_player2_having_at_least_one_higher_card,
        )
        print(
            "Probability of player 2 drawing high enough card to win: ",
            probability_of_drawing_high_enough_card,
            "\n",
        )

    if do_simulation:  # do simulation
        if max_player1_deck > max_player2_deck_simulation:
            return α, -α
        else:
            return -α, α
    else:  # simulate the game without knowing the other players cards per player
        probable_value_player1 = (
            probability_of_player2_having_at_least_one_higher_card * -α
            + (1 - probability_of_player2_having_at_least_one_higher_card) * α
        )

        if cheating:
            if σ[k] > max_player1_deck:  # cheat and observe one card of player 2
                probable_value_player1 = -α

        probable_value_player2 = (
            probability_of_player1_having_at_least_one_higher_card * -α
            + (1 - probability_of_player1_having_at_least_one_higher_card) * α
        ) + probability_of_drawing_high_enough_card * α

    return (probable_value_player1, probable_value_player2)


def approximate_other_players_max(N: int, k: int):
    results_dict = {}

    try:
        with open("approximated_other_players_max.json", "r+") as fp:
            saved_results = json.load(fp)
    except FileNotFoundError:
        saved_results = {}

    results_dict.update(saved_results)

    stored_result = results_dict.get(f"({N}, {k})")
    if stored_result != None:
        return stored_result

    R = round(10 / N)
    expected_value = 0

    for _ in range(R):
        shufflings = list(permutations(list(range(1, N + 1))))
        random.shuffle(shufflings)

        for σ in shufflings:
            max_player_deck = 0
            for number, card in enumerate(σ):
                if number < k:  # first k belong to player
                    max_player_deck = max(max_player_deck, card)

            expected_value += max_player_deck

    result = expected_value / (factorial(N) * R)

    results_dict[f"({N}, {k})"] = result
    with open("approximated_other_players_max.json", "w+") as fp:
        json.dump(results_dict, fp)

    return result


def plot_solve_MC(N, k, p):
    import pandas as pd
    import plotly.express as px

    results_play = []
    results_refuse = []

    my_range = np.linspace(1, 30)
    for α in my_range:
        print(f"testing for α={α}")
        result = solve_MC(N, α, k, p)
        print(result)
        results_play.append(result[0])
        results_refuse.append(result[1])

    data = pd.DataFrame({"α": my_range, "Play": results_play, "Refuse": results_refuse})

    fig = px.line(
        data,
        x="α",
        y=["Play", "Refuse"],
        title=f"Impact of α (N = {N}, k = {k})",
        log_x=True,
    )
    fig.show()


def plot_average_game(N, k, p):
    import pandas as pd
    import plotly.express as px

    results_player1 = []
    results_player2 = []

    my_range = np.linspace(1.0, 3.0, num=10)
    for α in my_range:
        print(f"\ntesting for α={α}")

        average_utilies = [0, 0]

        for _ in range(p):
            deck = list(range(1, N + 1))
            random.shuffle(deck)

            game = CardGame(deck, k, α)
            action1, action2 = solve(game.state)
            game.perform_action(action1)
            game.perform_action(action2)

            average_utilies[0] += game.state.utilities()[0]
            average_utilies[1] += game.state.utilities()[1]

        results_player1.append(average_utilies[0] / p)
        results_player2.append(average_utilies[1] / p)

        print(
            "Average utilities: ",
            results_player1[-1],
            results_player2[-1],
        )

    data = pd.DataFrame(
        {"α": my_range, "Player 1": results_player1, "Player 2": results_player2}
    )

    fig = px.line(
        data,
        x="α",
        y=["Player 1", "Player 2"],
        title=f"Impact of α (N = {N}, k = {k})",
        log_x=False,
    )
    fig.show()


def solve(state: CardState) -> tuple[CardAction, CardAction]:
    value_play = value(
        CardAction.PLAY,
        tuple(list(state.cards[0]) + list(state.cards[1])),
        N,
        state.alpha,
        len(state.cards[0]),
    )
    value_refuse = value(
        CardAction.REFUSE,
        tuple(list(state.cards[0]) + list(state.cards[1])),
        N,
        state.alpha,
        len(state.cards[0]),
    )

    if verbose:
        print("Value play: ", value_play)
        print("Value refuse: ", value_refuse, "\n")

    action_player_1 = (
        CardAction.PLAY if value_play[0] > value_refuse[0] else CardAction.REFUSE
    )
    action_player_2 = (
        CardAction.PLAY if value_play[1] > value_refuse[1] else CardAction.REFUSE
    )

    return (action_player_1, action_player_2)


if __name__ == "__main__":
    repetitions = 100000
    verbose = False
    cheating = False
    run_simple_game = True
    run_plot_average_game = False
    run_plot_solve_MC = False

    N = 10
    k = 2
    α = 2.2

    if run_plot_average_game:
        plot_average_game(N, k, 100000)

    if run_plot_solve_MC:
        plot_solve_MC(N, k, 1000000)

    if run_simple_game:
        print("Calculating expected max value of other players: ")
        expected_player1_value = approximate_other_players_max(N, k)
        expected_player2_value = approximate_other_players_max(
            N, k if cheating else k + 1
        )  # if player 1 cheats, player 2 has k unknown cards, otherwise k+1 unknown cards

        print(
            "Expected max value of other players: ",
            (expected_player1_value, expected_player2_value),
            "\n",
        )

        deck = list(range(1, N + 1))
        random.shuffle(deck)

        game = CardGame(deck, k, α)
        action1, action2 = solve(game.state)
        game.perform_action(action1)
        game.perform_action(action2)

        print("Deck: ", deck, "\n")
        print("Player 1 chooses: ", action1)
        print("Player 2 chooses: ", action2, "\n")
        print("Utilities: ", game.state.utilities())
