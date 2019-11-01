

from pyqlearning.qlearning.greedy_q_learning import GreedyQLearning

import SimulationManager as sm
from simulation.event_constants import EVENT_QLEARNING_DECISION
import numpy as np

class ControllerAlgorithmQLearning(GreedyQLearning):

    """docstring for ControllerAlgorithmQLearning."""
    def __init__(self):
        super(ControllerAlgorithmQLearning, self).__init__()
        self.t = 0
        self.lastAction = {}
        self.lastState = {}
        np.seed(42)

    def extract_possible_actions(self, state_key):
        '''
        Extract the list of the possible action in `self.t+1`.

        Abstract method for concreate usecases.

        Args:
            state_key       The key of state in `self.t+1`.

        Returns:
            `list` of the possible actions in `self.t+1`.

        '''
        return self.controller.getPossibleActions(state_key)

    def observe_reward_value(self, state_key, action_key):
        '''
        Compute the reward value.

        Args:
            state_key:              The key of state.
            action_key:             The key of action.

        Returns:
            Reward value.
        '''
        reward_value = self.controller.getReward()
        self.save_r_df(state_key, reward_value)
        return reward_value


    def update_state(self, state_key, action_key):
        '''
        Update state.

        This method can be overrided for concreate usecases.

        Args:
            state_key:    The key of state in `self.t`.
            action_key:   The key of action in `self.t`.

        Returns:
            The key of state in `self.t+1`.
        '''
        return self.controller.getCurrentState()

    def check_the_end_flag(self, state_key):
        '''
        Check the end flag.

        If this return value is `True`, the learning is end.

        As a rule, the learning can not be stopped.
        This method should be overrided for concreate usecases.

        Args:
            state_key:    The key of state in `self.t`.

        Returns:
            bool
        '''
        # As a rule, the learning can not be stopped.
        return False

    def visualize_learning_result(self, state_key):
        '''
        Visualize learning result.
        This method should be overrided for concreate usecases.

        This method is called in last learning steps.

        Args:
            state_key:    The key of state in `self.t`.
        '''
        print("===== Learning =====")
        for i, c in self.q_df.iterrows():
            print(f"I: {i}; S: {c['state_key']}; A: {c['action_key']}; R: {c['q_value']}.")



    def step(self, step, controller):
        self.controller = controller
        tlID = controller.trafficLight.getId()

        # ========================================
        # Update Q-values based on previous action
        # ========================================
        if tlID in self.lastState:
            lastState = self.lastState[tlID]
            lastAction = self.lastAction[tlID]

            reward_value = self.observe_reward_value(lastState, lastAction)

            state = controller.getCurrentState()
            next_action_list = self.extract_possible_actions(state)

            sm.SimulationManager.getCurrentSimulation().notify(EVENT_QLEARNING_DECISION,
                        tl_id=tlID, previous_state=lastState,
                        current_state=state, action=lastAction, reward=reward_value)

            if len(next_action_list):
                # Max-Q-Value in next action time.
                next_action = self.predict_next_action(state, next_action_list)
                next_max_q = self.extract_q_df(state, next_action)
                #print(f"State: {self.lastStateKey}; Action: {self.lastActionKey}; Reward: {reward_value}.")
                # Update Q-Value.
                self.update_q(
                    state_key=lastState,
                    action_key=lastAction,
                    reward_value=reward_value,
                    next_max_q=next_max_q
                )
        else:
            state = controller.getCurrentState()
            next_action_list = self.extract_possible_actions(state)
            next_action = self.predict_next_action(state, next_action_list)
            next_max_q = self.extract_q_df(state, next_action)

        # Normalize.
        self.normalize_q_value()
        self.normalize_r_value()

        # Vis.
        #self.visualize_learning_result(state_key)
        # Check.
        #if self.check_the_end_flag(state_key) is True:
        #    break

        action = self.select_action(
            state_key=state,
            next_action_list=next_action_list
        )

        self.controller.takeAction(action, step)

        self.lastState[tlID] = state
        self.lastAction[tlID] = action

        # Episode.
        self.t += 1

        if (self.t % 50 == 0):
            self.epsilon_greedy_rate *= 0.9
