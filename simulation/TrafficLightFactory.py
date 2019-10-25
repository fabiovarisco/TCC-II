from simulation import TrafficLight as tl

from tl_controller.TrafficLightStatic import TrafficLightStatic
from tl_controller.TrafficLightControllerFXM import TrafficLightControllerFXM
from tl_controller.TrafficLightControllerWebsterLike import TrafficLightControllerWebsterLike
from tl_controller.TrafficLightControllerQLearning import TrafficLightControllerQLearning
from tl_controller.TrafficLightControllerQLearningFPVCL import TrafficLightControllerQLearningFPVCL
from tl_controller.qlearning.ControllerAlgorithmQLearning import ControllerAlgorithmQLearning
from tl_controller.qlearning.ControllerAlgorithmDeepQLearning import ControllerAlgorithmDeepQLearning
from tl_controller.qlearning.RewardFunction import RewardCumulativeDelay, RewardThroughput
from tl_controller.qlearning.StateRepresentation import StateRepresentation, StateQueueLengthDiscretized, StateQueueLength, StateCurrentStage
from tl_controller.qlearning.QLearningAlgorithmFactory import QLearningAlgorithmFactory

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
        tlController = TrafficLightControllerQLearningFPVCL(trafficLight)
        tlController.setQLearningAlgorithm(QLearningAlgorithmFactory.getQLearningAlgorithm())
        trafficLight.setController(tlController)
        #trafficLight.controller.setRewardFunction(RewardCumulativeDelay(tl.controller))
        trafficLight.controller.setRewardFunction(RewardThroughput(trafficLight.controller))
        trafficLight.controller.setStateRepresentation(StateQueueLengthDiscretized(trafficLight.controller, discretizeByValue = sm.SimulationManager.getCurrentSimulation().config.getInt(TLC_QLEARNING_DISCRETIZE_QUEUE_LENGTH),
                                                                stateComponent = StateCurrentStage(trafficLight.controller)))
        return trafficLight

    @staticmethod
    def createTrafficLightDeepQLearningFPVCL(id):

        trafficLight = tl.TrafficLight(id)
        tlController = TrafficLightControllerQLearningFPVCL(trafficLight)

        deep_q_learning = ControllerAlgorithmDeepQLearning(
            # is-a `FunctionApproximator`.
            ControllerAlgorithmDeepQLearning.createLSTMApproximator(3, hidden_neuron_count=40))
        # Epsilon greedy rate.
        deep_q_learning.epsilon_greedy_rate = 0.7
        # Learning rate.
        deep_q_learning.alpha_value = 1e-05
        # Discounting rate.
        deep_q_learning.gamma_value = 0.1

        tlController.setQLearningAlgorithm(
            QLearningAlgorithmFactory.getDeepQLearningAlgorithmLSTM(3, 
                                                        hidden_neuron_count=40))

        trafficLight.setController(tlController)
        #trafficLight.controller.setRewardFunction(RewardCumulativeDelay(tl.controller))
        trafficLight.controller.setRewardFunction(RewardThroughput(trafficLight.controller))
        trafficLight.controller.setStateRepresentation(StateQueueLength(trafficLight.controller,
                                                                stateComponent = StateCurrentStage(trafficLight.controller, stateRepresentationType = StateRepresentation.STATE_REPRESENTATION_NP_ARRAY),
                                                                stateRepresentationType = StateRepresentation.STATE_REPRESENTATION_NP_ARRAY
                                                                ))

        return trafficLight
