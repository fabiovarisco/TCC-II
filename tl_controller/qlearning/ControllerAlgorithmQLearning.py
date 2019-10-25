

from pyqlearning.qlearning.greedy_q_learning import GreedyQLearning

import SimulationManager as sm
from simulation.event_constants import EVENT_QLEARNING_DECISION

class ControllerAlgorithmQLearning(GreedyQLearning):

    """docstring for ControllerAlgorithmQLearning."""
    def __init__(self, controller):
        super(ControllerAlgorithmQLearning, self).__init__()
        self.controller = controller
        self.t = 0
        self.lastActionKey = 0
        #self.lastStateKey = self.controller.getCurrentState()

    def initState(self, state_key):
        self.lastStateKey = state_key

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



    def step(self, step):
        # Implement learning

        reward_value = self.observe_reward_value(self.lastStateKey, self.lastActionKey)

        state_key = self.controller.getCurrentState()
        next_action_list = self.extract_possible_actions(state_key)

        sm.SimulationManager.getCurrentSimulation().notify(EVENT_QLEARNING_DECISION, 
                    tl_id=self.controller.trafficLight.getID(), previous_state=self.lastStateKey,
                    current_state=state_key, action=self.lastActionKey, reward=reward_value)
            
        if len(next_action_list):
            # Max-Q-Value in next action time.

            next_next_action_list = self.extract_possible_actions(state_key)
            next_action_key = self.predict_next_action(state_key, next_next_action_list)
            next_max_q = self.extract_q_df(state_key, next_action_key)
            #print(f"State: {self.lastStateKey}; Action: {self.lastActionKey}; Reward: {reward_value}.")
            # Update Q-Value.
            self.update_q(
                state_key=self.lastStateKey,
                action_key=self.lastActionKey,
                reward_value=reward_value,
                next_max_q=next_max_q
            )


        # Normalize.
        self.normalize_q_value()
        self.normalize_r_value()

        # Vis.
        #self.visualize_learning_result(state_key)
        # Check.
        #if self.check_the_end_flag(state_key) is True:
        #    break

        self.lastActionKey = self.select_action(
            state_key=state_key,
            next_action_list=next_action_list
        )
        self.lastStateKey = state_key

        self.controller.takeAction(self.lastActionKey, step)

        # Episode.
        self.t += 1
