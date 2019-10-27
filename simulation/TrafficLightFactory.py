from simulation import TrafficLight as tl

from tl_controller.TrafficLightStatic import TrafficLightStatic
from tl_controller.TrafficLightControllerFXM import TrafficLightControllerFXM
from tl_controller.TrafficLightControllerWebsterLike import TrafficLightControllerWebsterLike
from tl_controller.TrafficLightControllerQLearning import TrafficLightControllerQLearning
from tl_controller.TrafficLightControllerQLearningFPVCL import TrafficLightControllerQLearningFPVCL
from tl_controller.qlearning.ControllerAlgorithmQLearning import ControllerAlgorithmQLearning
from tl_controller.qlearning.ControllerAlgorithmDeepQLearning import ControllerAlgorithmDeepQLearning
from tl_controller.qlearning.RewardFunction import RewardCumulativeDelay, RewardThroughput, AdaptiveRewardFunction, AdaptiveLaneOccupancyReward, RewardWaitingVehicles, RewardAverageQueueLength
from tl_controller.qlearning.StateRepresentation import StateRepresentation, StateQueueLengthDiscretized, StateQueueLength, StateCurrentStage
from tl_controller.qlearning.QLearningAlgorithmFactory import QLearningAlgorithmFactory

class TrafficLightFactory(object):

    """docstring for Junction."""
    def __init__(self):
        super(TrafficLightFactory, self).__init__()

    @staticmethod
    def createTrafficLightFromType(id, type):
        if type not in TLC_TYPE_FUNCTIONS:
            raise Exception(f"Invalid function type {type}")
        return TLC_TYPE_FUNCTIONS[type](id)

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

    @staticmethod
    def createTrafficLight(id):
        return tl.TrafficLight(id)

    @staticmethod
    def createTrafficLightController(trafficLight, Controller):
        return Controller(trafficLight)


    @staticmethod
    def createBasicTrafficLightDeepQLearningFPVCL(id):

        trafficLight = TrafficLightFactory.createTrafficLight(id)
        tlController = TrafficLightFactory.createTrafficLightController(trafficLight, TrafficLightControllerQLearningFPVCL)

        tlController.setQLearningAlgorithm(
            QLearningAlgorithmFactory.getDeepQLearningAlgorithmLSTM(3,
                                                        hidden_neuron_count=40))

        trafficLight.setController(tlController)
        return trafficLight

    @staticmethod
    def createTrafficLightDeepQLearningFPVCLAdaptiveLaneOccupancyRF(id):

        trafficLight = TrafficLightFactory.createBasicTrafficLightDeepQLearningFPVCL(id)

        rf = AdaptiveLaneOccupancyReward(trafficLight.controller,
                activationFunction = AdaptiveRewardFunction.activationAdaptedSigmoid,
                steepness = 15, inf_point = -0.4)
        rf.addFunction(RewardAverageQueueLength(trafficLight.controller), weight = 1, inverse = True)
        rf.addFunction(RewardThroughput(trafficLight.controller), weight = 1, inverse = False)


        trafficLight.controller.setRewardFunction(rf)
        trafficLight.controller.setStateRepresentation(StateQueueLength(trafficLight.controller,
                                                                stateComponent = StateCurrentStage(trafficLight.controller, stateRepresentationType = StateRepresentation.STATE_REPRESENTATION_NP_ARRAY),
                                                                stateRepresentationType = StateRepresentation.STATE_REPRESENTATION_NP_ARRAY
                                                                ))
        return trafficLight

    @staticmethod
    def createTrafficLightDeepQLearningFPVCLFromRF(id, RewardFunction):
        trafficLight = TrafficLightFactory.createBasicTrafficLightDeepQLearningFPVCL(id)

        trafficLight.controller.setRewardFunction(RewardFunction(trafficLight.controller))
        trafficLight.controller.setStateRepresentation(StateQueueLength(trafficLight.controller,
                                                                stateComponent = StateCurrentStage(trafficLight.controller, stateRepresentationType = StateRepresentation.STATE_REPRESENTATION_NP_ARRAY),
                                                                stateRepresentationType = StateRepresentation.STATE_REPRESENTATION_NP_ARRAY
                                                                ))
        return trafficLight

    @staticmethod
    def createTrafficLightDeepQLearningFPVCLWaitingVehiclesRF(id):
        return TrafficLightFactory.createTrafficLightDeepQLearningFPVCLFromRF(id, RewardWaitingVehicles)

    @staticmethod
    def createTrafficLightDeepQLearningFPVCLAvgQueueLengthRF(id):
        return TrafficLightFactory.createTrafficLightDeepQLearningFPVCLFromRF(id, RewardAverageQueueLength)

TLC_TYPE_FUNCTIONS = {'DeepQLearningAdaptiveLaneOccupancyRF': TrafficLightFactory.createTrafficLightDeepQLearningFPVCLAdaptiveLaneOccupancyRF,
                       'DeepQLearningWaitingVehiclesRF': TrafficLightFactory.createTrafficLightDeepQLearningFPVCLWaitingVehiclesRF,
                       'DeepQLearningAvgQueueLengthRF': TrafficLightFactory.createTrafficLightDeepQLearningFPVCLAvgQueueLengthRF}
