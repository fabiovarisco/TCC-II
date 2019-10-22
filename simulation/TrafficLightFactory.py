
from simulation import TrafficLight as tl

from tl_controller.TrafficLightStatic import TrafficLightStatic
from tl_controller.TrafficLightControllerFXM import TrafficLightControllerFXM
from tl_controller.TrafficLightControllerWebsterLike import TrafficLightControllerWebsterLike
from tl_controller.TrafficLightControllerQLearning import TrafficLightControllerQLearning
from tl_controller.TrafficLightControllerQLearningFPVCL import TrafficLightControllerQLearningFPVCL
from tl_controller.qlearning.ControllerAlgorithmDeepQLearning import ControllerAlgorithmDeepQLearning
from tl_controller.qlearning.RewardFunction import RewardCumulativeDelay, RewardThroughput
from tl_controller.qlearning.StateRepresentation import StateQueueLengthDiscretized, StateQueueLength, StateCurrentStage

class TrafficLightFactory(object):

    """docstring for Junction."""
    def __init__(self):
        super(TrafficLightFactory, self).__init__()

    @staticmethod
    def createTrafficLightWebsterLike(id):
        return tl.TrafficLight(id, TrafficLightControllerWebsterLike)

    @staticmethod
    def createTrafficLightFXM(id):
        return tl.TrafficLight(id, TrafficLightControllerFXM)

    @staticmethod
    def createTrafficLightStatic(id, programId):
        trafficLight = tl.TrafficLight(id)
        trafficLight.setController(TrafficLightStatic(trafficLight))
        trafficLight.controller.setProgram(programId)
        return trafficLight

    #@staticmethod
    #def createTrafficLightSimpleQLearning(id):
    #    return TrafficLight(id, TrafficLightControllerQLearning)

    @staticmethod
    def createTrafficLightQLearningFPVCL(id):
        from SimulationConfig import TLC_QLEARNING_DISCRETIZE_QUEUE_LENGTH
        import SimulationManager as sm
        trafficLight = tl.TrafficLight(id)
        trafficLight.setController(TrafficLightControllerQLearningFPVCL(trafficLight))
        #trafficLight.controller.setRewardFunction(RewardCumulativeDelay(tl.controller))
        trafficLight.controller.setRewardFunction(RewardThroughput(trafficLight.controller))
        trafficLight.controller.setStateRepresentation(StateQueueLengthDiscretized(trafficLight.controller, discretizeByValue = sm.SimulationManager.getCurrentSimulation().config.getInt(TLC_QLEARNING_DISCRETIZE_QUEUE_LENGTH),
                                                                stateComponent = StateCurrentStage(trafficLight.controller)))
        return trafficLight

    @staticmethod
    def createTrafficLightDeepQLearningFPVCL(id):
        import SimulationManager as sm
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
        # Verification.
        from pydbm.verification.verificate_function_approximation import VerificateFunctionApproximation
        
        # Init.
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
            input_neuron_count=3,
            hidden_neuron_count=40,
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
            batch_size=100,
            # Learning rate.
            learning_rate=1e-05,
            # Attenuate the `learning_rate` by a factor of this value every `attenuate_epoch`.
            learning_attenuate_rate=0.1,
            # Attenuate the `learning_rate` by a factor of `learning_attenuate_rate` every `attenuate_epoch`.
            attenuate_epoch=50,
            # Refereed maxinum step `t` in BPTT. If `0`, this class referes all past data in BPTT.
            bptt_tau=5,
            # Size of Test data set. If this value is `0`, the validation will not be executed.
            test_size_rate=0.3,
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
            batch_size=100,
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

        trafficLight = tl.TrafficLight(id, TrafficLightControllerQLearningFPVCL)
        tlController = TrafficLightControllerQLearningFPVCL(trafficLight)

        deep_q_learning = ControllerAlgorithmDeepQLearning(
            # is-a `FunctionApproximator`.
            function_approximator,
            tlController
        )
        # Epsilon greedy rate.
        deep_q_learning.epsilon_greedy_rate = 0.7
        # Learning rate.
        deep_q_learning.alpha_value = 1e-05
        # Discounting rate.
        deep_q_learning.gamma_value = 0.1
        
        tlController.setQLearningAlgorithm(deep_q_learning)

        trafficLight.setController(tlController)
        #trafficLight.controller.setRewardFunction(RewardCumulativeDelay(tl.controller))
        trafficLight.controller.setRewardFunction(RewardThroughput(trafficLight.controller))
        trafficLight.controller.setStateRepresentation(StateQueueLength(trafficLight.controller),
                                                                stateComponent = StateCurrentStage(trafficLight.controller))
        return trafficLight