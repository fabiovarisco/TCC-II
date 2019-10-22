# -*- coding: utf-8 -*-
from pyqlearning.deepqlearning.deep_q_network import DeepQNetwork


class ControllerAlgorithmDeepQLearning(DeepQNetwork):
    '''
    Deep Q-Network as controller algorithm
    '''
    def __init__(self, controller):
        super(ControllerAlgorithmDeepQLearning, self).__init__()
        self.controller = controller
        self.t = 0
        self.lastAction = 0
        
    def initState(self, state):
        self.lastState = state
    
    def inference(self, state_arr, limit=1):
        '''
        Infernce.
        
        Args:
            state_arr:    `np.ndarray` of state.
            limit:        The number of inferencing. Only 1 inference is supported
        
        Returns:
            next action to be taken
        '''
        next_action_arr = self.extract_possible_actions(state_arr)
        next_q_arr = self.function_approximator.inference_q(next_action_arr)
        action_arr, q = self.select_action(next_action_arr, next_q_arr)
        print('==Action Array==')
        print(action_arr)
        print('==Q Array==')
        print(q)
        return (action_arr[0], q[0])


    def extract_possible_actions(self, state_arr):
        '''
        Extract possible actions.
        This method is overrided.
        Args:
            state_arr:  `np.ndarray` of state.
        
        Returns:
            `np.ndarray` of actions.
        '''
        return self.controller.getPossibleActions(state_arr)

    def observe_reward_value(self, state_arr, action_arr):
        '''
        Compute the reward value.
        This method is overrided.
        Args:
            state_arr:              `np.ndarray` of state.
            action_arr:             `np.ndarray` of action.
        
        Returns:
            Reward value.
        '''
        #self.save_r_df(state_key, reward_value)
        return self.controller.getReward()

     def extract_now_state(self):
        '''
        Extract now state.
        
        Returns:
            `np.ndarray` of state.
        '''
        return self.controller.getCurrentState()

    def update_state(self, state_arr, action_arr):
        '''
        Update state.
        
        This method is overrided.
        Args:
            state_arr:    `np.ndarray` of state in `self.t`.
            action_arr:   `np.ndarray` of action in `self.t`.
        
        Returns:
            `np.ndarray` of state in `self.t+1`.
        '''
        pass
        #return self.controller.getCurrentState()

    def check_the_end_flag(self, state_arr):
        '''
        Check the end flag.
        
        If this return value is `True`, the learning is end.
        This method is overrided.
        As a rule, the learning can not be stopped.
        This method should be overrided for concreate usecases.
        Args:
            state_arr:    `np.ndarray` of state in `self.t`.
        Returns:
            bool
        '''
        # Your concrete functions.
        return False

    def step(self, step):
        # ========================================
        # Update Q-values based on previous action
        # ========================================
        reward_value = self.observe_reward_value(self.lastState, self.lastAction)

        new_state = self.controller.getCurrentState()
    
        # Inference the Max-Q-Value in next action time.
        next_action_list = self.extract_possible_actions(new_state)
        next_max_q = self.__function_approximator.inference_q(next_action_list).max()
        print('===Next Max Q===')
        print(next_max_q)
        lastPredictedQArr = np.array[self.lastPredictedQ]
        # Update real Q-Values.
        real_q_arr = self.update_q(
                lastPredictedQArr,
                np.array[reward_value],
                np.array[next_max_q]
            )
        print('last predicted q arr')
        print(lastPredictedQArr)
        print('real q arr')
        print(real_q_arr)
        # Maximum of predicted and real Q-Values.
        real_q = real_q_arr[0]
        if self.__q_logs_arr.shape[0] > 0:
            self.__q_logs_arr = np.r_[
                self.__q_logs_arr,
                np.array([self.lastPredictedQ, real_q]).reshape(1, 2)
            ]
        else:
            self.__q_logs_arr = np.array([self.lastPredictedQ, real_q]).reshape(1, 2)
        
        # Learn Q-Values.
        self.learn_q(lastPredictedQArr, real_q_arr)

        # ========================================
        # Take next action
        # ========================================

        # Draw samples of next possible actions from any distribution.
        next_action_arr = self.extract_possible_actions(state_arr)
        print('next_action_arr')
        print(next_action_arr)
        # Inference Q-Values.
        predicted_q_arr = self.__function_approximator.inference_q(next_action_arr)
        #self.lastPredictedQArr = predicted_q_arr
        print('predicted_q_arr')
        print(predicted_q_arr)
        # Select action.
        action_arr, predicted_q = self.select_action(next_action_arr, predicted_q_arr)
        print('===Action arr===')
        print(action_arr)
        print('====Predicted Q====')
        print(predicted_q)
        self.lastPredictedQ = predicted_q
        self.lastAction = action_arr    

        # Take next action
        self.controller.takeAction(self.lastActionKey, step)

        # Episode.
        self.t += 1
