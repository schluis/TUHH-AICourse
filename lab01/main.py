from monkey_banana.agents import RandomAgent, RuleBasedAgent, PlanningAgent
from monkey_banana.banana_environment import MonkeyBananaEnvironmentTask
from monkey_banana.banana_environment import MonkeyBananaFOEnvironmentTask, MonkeyBananaPOEnvironmentTask
from monkey_banana.banana_environment import MonkeyBananaAction

import plotly.express as px


if __name__ == "__main__":
    # Question 1
    initial_banana_position = 7
    initial_box_position = 2
    room_size = 10

    if True:
        environment = MonkeyBananaFOEnvironmentTask(initial_banana_position, initial_box_position, room_size)
        
        # Question 2
        probability_of_actions = 1 / len(environment.available_actions())
        environment.perform_action(MonkeyBananaAction.MOVE_BOX_RIGHT)
        
        probability_of_actions *= 1 / len(environment.available_actions())
        environment.perform_action(MonkeyBananaAction.MOVE_BOX_RIGHT)
        
        probability_of_actions *= 1 / len(environment.available_actions())
        environment.perform_action(MonkeyBananaAction.MOVE_BOX_RIGHT)
        
        probability_of_actions *= 1 / len(environment.available_actions())
        environment.perform_action(MonkeyBananaAction.MOVE_BOX_RIGHT)
        
        probability_of_actions *= 1 / len(environment.available_actions())
        environment.perform_action(MonkeyBananaAction.MOVE_BOX_RIGHT)
        
        probability_of_actions *= 1 / len(environment.available_actions())
        environment.perform_action(MonkeyBananaAction.CLIMB)
        
        probability_of_actions *= 1 / len(environment.available_actions())
        environment.perform_action(MonkeyBananaAction.GRAB)

        environment.visualize()
        print(f"Score: {environment.score}\n")

        # Question 4
        # print(probability_of_actions)

    # question10()
    if False:
        print("\n\nRandom agent:\n")
        agents_with_optimal_solution = 0
        executions = 10000
        steps_needed = 0
        steps_needed_list = [0] * executions
        score_list = [0] * executions

        for i in range(executions):
            steps_needed = 0
            environment = MonkeyBananaFOEnvironmentTask(initial_banana_position, initial_box_position, room_size)
            agent = RandomAgent()
            action = agent.choose_action(environment)
            steps_needed += 1
            
            while not environment.perform_action(action):
                action = agent.choose_action(environment)
                steps_needed += 1

            score_list[i] = environment.score
            if environment.score == 4.4:
                agents_with_optimal_solution += 1
            steps_needed_list[i] = steps_needed

        print(f"Average score: {sum(score_list)/executions}")
        print(f"Average steps needed: {sum(steps_needed_list)/executions}")
        print(f"Agents with optimal solution: {agents_with_optimal_solution}\n")

        fig = px.histogram(x=steps_needed_list, title="Score distribution", labels={"x": "Steps needed"}, nbins=1000)
        fig.show()



    # question11()
    if False:
        print("\n\nRule-based agent:\n")
        environment = MonkeyBananaFOEnvironmentTask(initial_banana_position, initial_box_position, room_size)
        
        steps_needed = 0
        agent = RuleBasedAgent()
        action = agent.choose_action(environment)
        steps_needed += 1
        
        while not environment.perform_action(action):
            action = agent.choose_action(environment)
            steps_needed += 1

        print(f"Score: {environment.score}")
        print(f"Steps needed: {steps_needed}\n")


    # question12()
    if True:
        print("\n\nPlanning agent:\n")
        environment = MonkeyBananaFOEnvironmentTask(initial_banana_position, initial_box_position, room_size)
        
        steps_needed = 0
        agent = PlanningAgent()
        max_search_depth = 8
        action = agent.choose_action(environment, max_search_depth)
        print(action)
        environment.visualize()
        steps_needed += 1
        
        while not environment.perform_action(action):
            environment.visualize()
            print(action)
            action = agent.choose_action(environment, max_search_depth)
            steps_needed += 1

        print(f"Score: {environment.score}")
        print(f"Steps needed: {steps_needed}\n")



    # question15()
    # question16()

