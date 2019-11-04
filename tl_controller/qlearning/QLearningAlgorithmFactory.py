
from tl_controller.qlearning.ControllerAlgorithmQLearning import ControllerAlgorithmQLearning
from tl_controller.qlearning.ControllerAlgorithmDeepQLearning import ControllerAlgorithmDeepQLearning

class QLearningAlgorithmFactory(object):

    qlearning_algorithm = None
    deep_qlearning_algorithm = None

    """docstring for QLearningAlgorithmFactory."""
    def __init__(self):
        super(QLearningAlgorithmFactory, self).__init__()

    @staticmethod
    def getQLearningAlgorithm(epsilon_greedy_rate = 0.7, gamma_value = 0.8, alpha_value = 0.1):

        print(f'Get QLearning algorithm with params: e-greedy-rate {epsilon_greedy_rate}; gamma_value {gamma_value}; alpha_value {alpha_value}.')
        if QLearningAlgorithmFactory.qlearning_algorithm is None:
            QLearningAlgorithmFactory.qlearning_algorithm = ControllerAlgorithmQLearning()

        QLearningAlgorithmFactory.qlearning_algorithm.epsilon_greedy_rate = epsilon_greedy_rate
        QLearningAlgorithmFactory.qlearning_algorithm.gamma_value = gamma_value
        QLearningAlgorithmFactory.qlearning_algorithm.alpha_value = alpha_value

        return QLearningAlgorithmFactory.qlearning_algorithm

    @staticmethod
    def getDeepQLearningAlgorithmLSTM(state_array_length, hidden_neuron_count=40, epsilon_greedy_rate=0.7, learning_rate=1e-05, discounting_rate=0.1, sequence_length=5):

        print(f'Get DeepQLearning algorithm with params:')
        print(f'state_length {state_array_length}; hidden_neuron_count {hidden_neuron_count}; e-greedy-rate {epsilon_greedy_rate};')
        print(f'learning_rate {learning_rate}; discounting_rate {discounting_rate}; sequence_length {sequence_length}.')
        
        if QLearningAlgorithmFactory.deep_qlearning_algorithm is None:
            QLearningAlgorithmFactory.deep_qlearning_algorithm = ControllerAlgorithmDeepQLearning(
                ControllerAlgorithmDeepQLearning.createLSTMApproximator(state_array_length,
                                                     hidden_neuron_count=hidden_neuron_count,
                                                     discounting_rate=discounting_rate,
                                                     learning_rate=learning_rate,
                                                     sequence_length=sequence_length ))

        QLearningAlgorithmFactory.deep_qlearning_algorithm.epsilon_greedy_rate = epsilon_greedy_rate
        # Learning rate.
        QLearningAlgorithmFactory.deep_qlearning_algorithm.alpha_value = learning_rate
        # Discounting rate.
        QLearningAlgorithmFactory.deep_qlearning_algorithm.gamma_value = discounting_rate
        
        return QLearningAlgorithmFactory.deep_qlearning_algorithm

    @staticmethod
    def resetFactory():
        QLearningAlgorithmFactory.deep_qlearning_algorithm = None
        QLearningAlgorithmFactory.qlearning_algorithm = None
