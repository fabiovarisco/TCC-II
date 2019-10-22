
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
        trafficLight = tl.TrafficLight(id, TrafficLightControllerQLearningFPVCL)
        tlController = TrafficLightControllerQLearningFPVCL(trafficLight)
        tlController.setQLearningAlgorithm(ControllerAlgorithmDeepQLearning(tlController))
        trafficLight.setController(tlController)
        #trafficLight.controller.setRewardFunction(RewardCumulativeDelay(tl.controller))
        trafficLight.controller.setRewardFunction(RewardThroughput(trafficLight.controller))
        trafficLight.controller.setStateRepresentation(StateQueueLength(trafficLight.controller),
                                                                stateComponent = StateCurrentStage(trafficLight.controller))
        return trafficLight