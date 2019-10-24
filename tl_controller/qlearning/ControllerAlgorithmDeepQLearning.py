# -*- coding: utf-8 -*-
from pyqlearning.deepqlearning.deep_q_network import DeepQNetwork
import numpy as np

class ControllerAlgorithmDeepQLearning(DeepQNetwork):
    '''
    Deep Q-Network as controller algorithm
    '''
    def __init__(self, function_approximator, controller):
        super().__init__(function_approximator)

        #self._function_approximator = function_approximator
        self.controller = controller

        self.t = 0
        self.lastAction = 0
        self.lastPredictedQ = None

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
        actions = self.controller.getPossibleActions(state_arr)
        actions_arr = np.zeros((28, 4))
        state_length = len(state_arr)
        for i, a in enumerate(actions):
            actions_arr[i][:state_length] = state_arr
            actions_arr[i][-1] = a
        return actions_arr
        #np.array([state_arr, [float(i)]]).ravel() for i in actions])

        #return np.array([[1, 1, float(i)] for i in range(sm.SimulationManager.getCurrentSimulation().config.getInt(TLC_QLEARNING_ACTION_MIN_GREEN),
        #            sm.SimulationManager.getCurrentSimulation().config.getInt(TLC_QLEARNING_ACTION_MAX_GREEN))])
        #r[2] = actions
        #print(r)
        #print(r.shape)
        #return r



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
        if (self.lastPredictedQ is not None):
            reward_value = self.observe_reward_value(self.lastState, self.lastAction)

            new_state = self.controller.getCurrentState()

            # Inference the Max-Q-Value in next action time.
            next_action_list = self.extract_possible_actions(new_state)
            next_max_q = self.function_approximator.inference_q(next_action_list).max()
            print('===Next Max Q===')
            print(next_max_q)
            # Update real Q-Values.
            real_q_selected = self.update_q(
                    np.array([self.lastPredictedQ]),
                    np.array([reward_value]),
                    np.array([next_max_q])
                )

            real_q_arr = np.copy(self.lastPredictedQArr)
            real_q_arr[self.lastActionKey] = real_q_selected[0]

            print('last key')
            print(self.lastActionKey)
            print('last predicted q arr')
            print(self.lastPredictedQArr)
            print('real q arr')
            print(real_q_arr)
            print('===== Learning ======')
            print('last predicted q')
            print(self.lastPredictedQArr[self.lastActionKey])
            print('real q')
            print(real_q_arr[self.lastActionKey])
            '''
            if self.q_logs_arr.shape[0] > 0:
                self.q_logs_arr = np.r_[
                    self.q_logs_arr,
                    np.array([self.lastPredictedQ, real_q]).reshape(1, 2)
                ]
            else:
                self.q_logs_arr = np.array([self.lastPredictedQ, real_q]).reshape(1, 2)
            '''
            # Learn Q-Values.
            self.learn_q(self.lastPredictedQArr, real_q_arr)

        # ========================================
        # Take next action
        # ========================================

        state_arr = self.controller.getCurrentState()
        # Draw samples of next possible actions from any distribution.
        next_action_arr = self.extract_possible_actions(state_arr)
        print('next_action_arr')
        print(next_action_arr)
        # Inference Q-Values.
        predicted_q_arr = self.function_approximator.inference_q(next_action_arr)
        self.lastPredictedQArr = predicted_q_arr
        print('predicted_q_arr')
        print(predicted_q_arr)
        # Select action.
        self.lastActionKey = self.select_action_key(next_action_arr, predicted_q_arr)
        #action_arr, predicted_q = self.select_action(next_action_arr, predicted_q_arr)
        action_arr = next_action_arr[self.lastActionKey]
        predicted_q = predicted_q_arr[self.lastActionKey]
        print('===Action arr===')
        print(action_arr)
        print('====Predicted Q====')
        print(predicted_q)

        self.lastPredictedQ = predicted_q
        self.lastAction = action_arr

        # Take next action
        self.controller.takeAction(self.lastAction[-1], step)

        # Episode.
        self.t += 1

    @staticmethod
    def createLSTMApproximator(state_array_length, hidden_neuron_count = 40):
        # Conv LSTM as a Function Approximator.
        from pyqlearning.functionapproximator.lstm_fa import LSTMFA
        # LSTM model.
        from pydbm.rnn.lstm_model import LSTMModel
        # LSTM Graph which is-a `Synapse`.
        from pydbm.synapse.recurrenttemporalgraph.lstm_graph import LSTMGraph
        # Adam optimizer.
        from pydbm.optimization.optparams.adam import Adam
        # Cost function.
        from pydbm.loss.mean_squared_error import MeanSquaredError

        from pydbm.activation.tanh_function import TanhFunction
        from pydbm.activation.logistic_function import LogisticFunction
        # Verification.
        from pydbm.verification.verificate_function_approximation import VerificateFunctionApproximation

        #Init.
        lstm_graph = LSTMGraph()

        # Activation function in LSTM.
        lstm_graph.observed_activating_function = TanhFunction()
        lstm_graph.input_gate_activating_function = LogisticFunction()
        lstm_graph.forget_gate_activating_function = LogisticFunction()
        lstm_graph.output_gate_activating_function = LogisticFunction()
        lstm_graph.hidden_activating_function = TanhFunction()
        lstm_graph.output_activating_function = TanhFunction()

        # Initialization strategy.
        # This method initialize each weight matrices and biases in Gaussian distribution: `np.random.normal(size=hoge) * 0.01`.
        lstm_graph.create_rnn_cells(
            input_neuron_count=state_array_length + 1,
            hidden_neuron_count=hidden_neuron_count,
            output_neuron_count=1
        )

        # Optimizer for Encoder.
        lstm_opt_params = Adam()
        lstm_opt_params.weight_limit = 0.5
        lstm_opt_params.dropout_rate = 0.5

        lstm_model = LSTMModel(
            # Delegate `graph` to `LSTMModel`.
            graph=lstm_graph,
            # The number of epochs in mini-batch training.
            epochs=100,
            # The batch size.
            batch_size=1,
            # Learning rate.
            learning_rate=1e-05,
            # Attenuate the `learning_rate` by a factor of this value every `attenuate_epoch`.
            learning_attenuate_rate=0.1,
            # Attenuate the `learning_rate` by a factor of `learning_attenuate_rate` every `attenuate_epoch`.
            attenuate_epoch=50,
            # Refereed maxinum step `t` in BPTT. If `0`, this class referes all past data in BPTT.
            bptt_tau=5,
            # Size of Test data set. If this value is `0`, the validation will not be executed.
            test_size_rate=0,
            # Loss function.
            computable_loss=MeanSquaredError(),
            # Optimizer.
            opt_params=lstm_opt_params,
            # Verification function.
            verificatable_result=VerificateFunctionApproximation(),
            # Tolerance for the optimization.
            # When the loss or score is not improving by at least tol
            # for two consecutive iterations, convergence is considered
            # to be reached and training stops.
            tol=0.0
        )

        # CNN as a function approximator.
        function_approximator = LSTMFA(
            # Batch size.
            batch_size=1,
            # Delegate LSTM Model.
            lstm_model=lstm_model,
            # The length of sequences.
            seq_len=5,
            # Learning rate.
            learning_rate=1e-05,
            # is-a `pydbm.loss.interface.computable_loss.ComputableLoss`.
            computable_loss=None,
            # is-a `pydbm.optimization.opt_params.OptParams`.
            opt_params=None,
            # is-a `pydbm.verification.interface.verificatable_result.VerificatableResult`.
            verificatable_result=None,
            # Verbose mode or not.
            verbose_mode=True
        )
        return function_approximator
