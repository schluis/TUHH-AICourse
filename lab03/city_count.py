from typing import List
from enum import Enum


class TouristAction(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3

    def inverse(self):
        if self == TouristAction.UP:
            return TouristAction.DOWN
        elif self == TouristAction.DOWN:
            return TouristAction.UP
        elif self == TouristAction.LEFT:
            return TouristAction.RIGHT
        else:
            return TouristAction.LEFT
        

class TouristState:
    def __init__(self, ave: int, street: str):
        self.ave: int = ave
        self.street: str = street

    def as_tuple(self):
        return (self.ave, self.street)

    def __eq__(self, other):
        return self.as_tuple() == other.as_tuple()

    def __hash__(self):
        return self.as_tuple().__hash__()

    def __repr__(self):
        return self.as_tuple().__repr__()


# initial_state = TouristState(1, "A")
initial_state = TouristState(1, "C")
stun_states = set([TouristState(2, "A"), TouristState(2, "C"), TouristState(4, "B")])
bad_restaurants = [
    ((2, "A"), (3, "A")),
    ((1, "B"), (1, "C")),
    ((4, "B"), (4, "C")),
]
good_restaurants = [
    ((4, "A"), (4, "B")),
    ((2, "C"), (3, "C")),
]
bad_restaurants += [(b, a) for (a, b) in bad_restaurants]
good_restaurants += [(b, a) for (a, b) in good_restaurants]


def available_actions(state: TouristState):

    return [
        x
        for x in [
            TouristAction.UP if state.street != "A" else None,
            TouristAction.DOWN if state.street != "C" else None,
            TouristAction.LEFT if state.ave != 1 else None,
            TouristAction.RIGHT if state.ave != 4 else None,
        ]
        if x is not None
    ]


def _move_deterministic(state: TouristState, action: TouristAction):
    if action == TouristAction.UP:
        new_street = chr(ord(state.street) - 1)
        return TouristState(state.ave, new_street)
    elif action == TouristAction.DOWN:
        new_street = chr(ord(state.street) + 1)
        return TouristState(state.ave, new_street)
    elif action == TouristAction.LEFT:
        return TouristState(state.ave - 1, state.street)
    elif action == TouristAction.RIGHT:
        return TouristState(state.ave + 1, state.street)


def resulting_states(state, action):
    assert action in available_actions(state), "Invalid action"

    results = set()
    if state in stun_states:
        for actions in available_actions(state):
            results.add(_move_deterministic(state, actions))
    else:
        results.add(_move_deterministic(state, action))

    return results


def or_search(state, path: List):
    if len(path) > 0:
        if (state.as_tuple(), path[0].as_tuple()) in good_restaurants:
            return []
        elif (state.as_tuple(), path[0].as_tuple()) in bad_restaurants:
            return None
    
    if state in path:
        return None

    # actions = available_actions(state)
    actions = [TouristAction.RIGHT]
    for action in actions:
        print(action)
        plan = and_search(resulting_states(state, action), [state] + path, action)
        if plan:
            return [action, plan]
    return None


def and_search(states, path: List, previous_action: TouristAction, previous_state: TouristState):
    plans = {}
    print(states)
    
    for state in states:
        if len(path) > 0:
            if (state.as_tuple(), path[0].as_tuple()) in good_restaurants:
                plans[state] = []
            elif (state.as_tuple(), path[0].as_tuple()) in bad_restaurants:
                return None

        if state in path:
            if previous_state in stun_states:
             
                plan = and_search(resulting_states(state, action), [state] + path, action, state)
                if plan:
                    plans[state] = [action, plan]
                                
            else:
                return None

        for action in available_actions(state):
            if action == previous_action.inverse():
                print(action, previous_action)
                if state in stun_states:
                    continue
                else:
                    continue
            else:
                # print(action)
                plan = and_search(resulting_states(state, action), [state] + path, action, state)
                if plan:
                    plans[state] = [action, plan]

    return plans


def and_or_search():
    return or_search(initial_state, [])


def print_plan(plan, depth=0):
    if plan == []:
        print(2 * depth * " " + "SUCCESS")
        return
    elif plan == None:
        print(2 * depth * " " + "FAILURE")
        return

    for step in plan:
        if isinstance(step, TouristAction):
            print(2 * depth * " " + step.name)
        else:
            for i, s in enumerate(step.keys()):
                pref = "el" if i > 0 else ""
                print(2 * depth * " " + pref + "if state == " + str(s.as_tuple()) + ":")
                print_plan(step[s], depth=depth + 1)


plan = and_or_search()
print_plan(plan)

