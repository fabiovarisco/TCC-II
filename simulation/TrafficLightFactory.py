
from simulation import TrafficLight as tl

from tl_controller import TrafficLightStatic as tlcStatic
from tl_controller.TrafficLightControllerFXM import TrafficLightControllerFXM
from tl_controller.TrafficLightControllerWebsterLike import TrafficLightControllerWebsterLike
from tl_controller.TrafficLightControllerQLearning import TrafficLightControllerQLearning
from tl_controller.TrafficLightControllerQLearningFPVCL import TrafficLightControllerQLearningFPVCL
from tl_controller.qlearning.RewardFunction import RewardCumulativeDelay, RewardThroughput
from tl_controller.qlearning.StateRepresentation import StateQueueLengthDiscretized, StateCurrentStage

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
        trafficLight = tl.TrafficLight(id, TrafficLightStatic)
        trafficLight.controller.setProgram(programId)
        return trafficLight

    #@staticmethod
    #def createTrafficLightSimpleQLearning(id):
    #    return TrafficLight(id, TrafficLightControllerQLearning)

    @staticmethod
    def createTrafficLightQLearningFPVCL(id):
        trafficLight = tl.TrafficLight(id, TrafficLightControllerQLearningFPVCL)
        #trafficLight.controller.setRewardFunction(RewardCumulativeDelay(tl.controller))
        trafficLight.controller.setRewardFunction(RewardThroughput(trafficLight.controller, 90))
        trafficLight.controller.setStateRepresentation(StateQueueLengthDiscretized(trafficLight.controller, discretizeByValue = 3.0,
                                                                stateComponent = StateCurrentStage(trafficLight.controller)))
        return trafficLight
