
from tl_controller.qlearning.ControllerAlgorithmQLearning import ControllerAlgorithmQLearning
from tl_controller.qlearning.ControllerAlgorithmDeepQLearning import ControllerAlgorithmDeepQLearning

class QLearningAlgorithmFactory(object):

    qlearning_algorithm = None
    deep_qlearning_algorithm = None

    """docstring for QLearningAlgorithmFactory."""
    def __init__(self):
        super(QLearningAlgorithmFactory, self).__init__()

    @staticmethod
    def getQLearningAlgorithm():

        if QLearningAlgorithmFactory.qlearning_algorithm is None:
            QLearningAlgorithmFactory.qlearning_algorithm = ControllerAlgorithmQLearning()

        return QLearningAlgorithmFactory.qlearning_algorithm

    @staticmethod
    def getDeepQLearningAlgorithmLSTM(state_array_length, epsilon_greedy_rate=0.7, learning_rate=1e-05, discounting_rate=0.1, hidden_neuron_count=40):

        if QLearningAlgorithmFactory.deep_qlearning_algorithm is None:
            deep_qlearning_algorithm = ControllerAlgorithmDeepQLearning(
                ControllerAlgorithmDeepQLearning.createLSTMApproximator(state_array_length, hidden_neuron_count=hidden_neuron_count))
            deep_qlearning_algorithm.epsilon_greedy_rate = epsilon_greedy_rate
            # Learning rate.
            deep_qlearning_algorithm.alpha_value = learning_rate
            # Discounting rate.
            deep_qlearning_algorithm.gamma_value = discounting_rate
            QLearningAlgorithmFactory.deep_qlearning_algorithm = deep_qlearning_algorithm

        return QLearningAlgorithmFactory.deep_qlearning_algorithm

    @staticmethod
    def resetFactory():
        QLearningAlgorithmFactory.deep_qlearning_algorithm = None
        QLearningAlgorithmFactory.qlearning_algorithm = None
