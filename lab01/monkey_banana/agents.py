from random import sample
from copy import deepcopy
import numpy as np

from  . banana_environment import MonkeyBananaEnvironmentTask
from  . banana_environment import MonkeyBananaFOEnvironmentTask, MonkeyBananaPOEnvironmentTask
from . banana_environment import MonkeyBananaAction
from . banana_environment import MonkeyBananaPartialObservation
from . banana_environment import MonkeyBananaState



class Agent:
    """
    General abstract class for an agent.
    """
    
    def choose_action(self, env: MonkeyBananaEnvironmentTask, verbose:str = True):
        """
        (Abstract) Implements the choice of action for the specific agent. 

        Parameters
        ----------
        env : MonkeyBananaEnvironmentTask
            Current environment.
        verbose : str, optional
            Allow logs. The default is True.

        Returns
        -------
        action: MonkeyBananaAction
            Returns the optimal action.

        """
        pass
    
    
    
    def run(self, env: MonkeyBananaEnvironmentTask, n_steps : int, verbose: str = True):
        """
        Runs the agent for a sequence of several steps

        Parameters
        ----------
        env : MonkeyBananaEnvironmentTask
            Current environment.
        n_steps : int
            Maximal number of steps to run the agent.
        verbose : str, optional
            Allow logs. The default is True.

        Returns
        -------
        env : MonkeyBananaEnvironmentTask
            Final environment.

        """
        if verbose: env.visualize()
        
        for n in range(n_steps):
            if verbose: print("\n======= Step", n)
            action = self.choose_action(env, verbose)     
            if verbose: print("\nAction:", action, "\n")
            
            res = env.perform_action(action)
            if res:
                print("Victory!")
                print("Total score:", env.performance())
                break
            if verbose: env.visualize()
            
        return env





class RandomAgent(Agent):
    """
    Random agent (Section 3)
    """
    
    def choose_action(self, env: MonkeyBananaEnvironmentTask):
        available_actions = env.available_actions()
        action = sample(available_actions, 1)[0]
        return action
        
    

    

class RuleBasedAgent(Agent):
    """
    Reflex rule-based agent (Section 4)
    """
    
    def choose_action(self, env: MonkeyBananaFOEnvironmentTask):
        
        observation = env.perceive()

        if observation.box_position < observation.banana_position:
            return MonkeyBananaAction.MOVE_BOX_RIGHT
        elif observation.box_position > observation.banana_position:
            return MonkeyBananaAction.MOVE_BOX_LEFT
        else:
            if not observation.is_monkey_up:
                return MonkeyBananaAction.CLIMB
            else:
                return MonkeyBananaAction.GRAB


class PlanningAgent(Agent):
    """
    Planning agent (Section 5)
    """
    
    def _launch_planning(self, env: MonkeyBananaFOEnvironmentTask, max_search_depth: int):
        """
        Method used to launch the planning. To be used only withing choose_action

        Parameters
        ----------
        env : MonkeyBananaFOEnvironmentTask
            Environment in the initial state.

        Returns
        -------
        plan_found: bool
            Shows whether the planning was succesful.
        action: MonkeyBananaAction
            Returns the optimal action

        """
        encountered_states = set()
        return self._plan(env, encountered_states, max_search_depth)
        
        
    
    def _plan(self, env: MonkeyBananaFOEnvironmentTask, encountered_states: set, max_search_depth: int):
        """
        Private method used to execute the planning recursively

        Parameters
        ----------
        env : MonkeyBananaFOEnvironmentTask
            Environment.
        encountered_states : set
            States that have already been explored by the search.

        Returns
        -------
        plan_found: bool
            Shows whether the planning was succesful.
        action: MonkeyBananaAction
            Returns the optimal action.

        """

        if max_search_depth == 0:
            return False, None
        
        perceived_state_representation = env.perceive().vector_representation()
        
        encountered_states.add(perceived_state_representation)
        
        
        available_actions = env.available_actions()
        
        for action in available_actions:
            # Makes a copy of the environment => This copy is used to then execute
            # the planning recursively from the new state reached after playing
            # the explored action
            env_copy = deepcopy(env)
            
            # Execute the action within the copied environment. 
            victory = env_copy.perform_action(action)
            
            if victory:
                # This action led to victory => planning is over!
                print(action)
                return True, action
            
            new_state = env_copy.perceive().vector_representation()
            
            encountered_states_copy = deepcopy(encountered_states)
            encountered_states_copy.add(new_state)

            # Execute the search recursively from the new state
            plan_found, _ = self._plan(env_copy, encountered_states_copy, max_search_depth - 1)
                
            if plan_found: 
                print(action)
                return True, action
        
        return False, None
    
    
    def choose_action(self, env: MonkeyBananaFOEnvironmentTask, max_search_depth: int):
        plan_found, action = self._launch_planning(env, max_search_depth)
        
        if plan_found:
            return action
        else:
            available_actions = env.available_actions()
            action = sample(available_actions, 1)[0]
            return action



class BeliefAgent(Agent):
    """
    Bayesian rule-based agent (Section 6)
    """
    
    def __init__(self, env_size: int):
        self.env_size = env_size
        self.beliefs = np.ones(env_size) / env_size


    def update_belief(self, obs: MonkeyBananaPartialObservation):
        if not(obs.is_monkey_up): 
            # Monkey is not on the box => no update
            return 
        
        # TODO: Question 15: Implement Bayesian belief update here
        self.beliefs = self.beliefs 

    
    def choose_action(self, env: MonkeyBananaPOEnvironmentTask, verbose:str):
        # TODO: Question 16
        if np.any(self.beliefs > 0.7):
            return None
        return None


