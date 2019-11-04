from simulation import TrafficLight as tl

from tl_controller.TrafficLightStatic import TrafficLightStatic
from tl_controller.TrafficLightControllerFXM import TrafficLightControllerFXM
from tl_controller.TrafficLightControllerWebsterLike import TrafficLightControllerWebsterLike
from tl_controller.TrafficLightControllerQLearning import TrafficLightControllerQLearning
from tl_controller.TrafficLightControllerQLearningFPVCL import TrafficLightControllerQLearningFPVCL
from tl_controller.qlearning.ControllerAlgorithmQLearning import ControllerAlgorithmQLearning
from tl_controller.qlearning.ControllerAlgorithmDeepQLearning import ControllerAlgorithmDeepQLearning
from tl_controller.qlearning.RewardFunction import * #RewardCumulativeDelay, RewardThroughput, AdaptiveRewardFunction, AdaptiveLaneOccupancyReward, RewardWaitingVehicles, RewardAverageQueueLength
from tl_controller.qlearning.StateRepresentation import * # StateRepresentation, StateQueueLengthDiscretized, StateQueueLength, StateCurrentStage
from tl_controller.qlearning.QLearningAlgorithmFactory import QLearningAlgorithmFactory

from SimulationConfig import *

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
        trafficLight = tl.TrafficLight(id)
        trafficLight.setController(TrafficLightControllerWebsterLike(trafficLight))
        return trafficLight

    @staticmethod
    def createTrafficLightFXM(id):
        trafficLight = tl.TrafficLight(id)
        trafficLight.setController(TrafficLightControllerFXM(trafficLight))
        return trafficLight


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

        epsilon_greedy_rate = sm.SimulationManager.getCurrentSimulation().config.getFloat(QLEARNING_EPSILON_GREEDY_RATE)
        gamma_value = sm.SimulationManager.getCurrentSimulation().config.getFloat(QLEARNING_GAMMA_VALUE)
        alpha_value = sm.SimulationManager.getCurrentSimulation().config.getFloat(QLEARNING_LEARNING_RATE)

        qlearning_algorithm = QLearningAlgorithmFactory.getQLearningAlgorithm(
                                                epsilon_greedy_rate = epsilon_greedy_rate,
                                                gamma_value = gamma_value,
                                                alpha_value = alpha_value)

        tlController.setQLearningAlgorithm(qlearning_algorithm)
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

        state_length = sm.SimulationManager.getCurrentSimulation().config.getInt(QLEARNING_STATE_LENGTH)

        epsilon_greedy_rate = sm.SimulationManager.getCurrentSimulation().config.getFloat(QLEARNING_EPSILON_GREEDY_RATE)
        learning_rate = sm.SimulationManager.getCurrentSimulation().config.getFloat(QLEARNING_LEARNING_RATE)
        sequence_length = sm.SimulationManager.getCurrentSimulation().config.getInt(DEEP_QLEARNING_SEQUENCE_LENGTH)
        discounting_rate = sm.SimulationManager.getCurrentSimulation().config.getFloat(DEEP_QLEARNING_DISCOUNTING_RATE)
        hidden_neuron_count = sm.SimulationManager.getCurrentSimulation().config.getInt(DEEP_QLEARNING_HIDDEN_NEURON_COUNT)

        qlearning_algorithm = QLearningAlgorithmFactory.getDeepQLearningAlgorithmLSTM(
                                                state_length,
                                                hidden_neuron_count=hidden_neuron_count,
                                                epsilon_greedy_rate=epsilon_greedy_rate,
                                                learning_rate=learning_rate,
                                                discounting_rate=discounting_rate,
                                                sequence_length=sequence_length)

        tlController.setQLearningAlgorithm(qlearning_algorithm)

        trafficLight.setController(tlController)
        #trafficLight.controller.setRewardFunction(RewardCumulativeDelay(tl.controller))
        trafficLight.controller.setRewardFunction(RewardThroughput(trafficLight.controller))
        trafficLight.controller.setStateRepresentation(StateQueueLength(trafficLight.controller,
                                                                stateComponent = StateCurrentStage(trafficLight.controller, stateRepresentationType = StateRepresentation.STATE_REPRESENTATION_NP_ARRAY),
                                                                stateRepresentationType = StateRepresentation.STATE_REPRESENTATION_NP_ARRAY))

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

        state_length = sm.SimulationManager.getCurrentSimulation().config.getInt(QLEARNING_STATE_LENGTH)

        epsilon_greedy_rate = sm.SimulationManager.getCurrentSimulation().config.getFloat(QLEARNING_EPSILON_GREEDY_RATE)
        learning_rate = sm.SimulationManager.getCurrentSimulation().config.getFloat(QLEARNING_LEARNING_RATE)
        sequence_length = sm.SimulationManager.getCurrentSimulation().config.getInt(DEEP_QLEARNING_SEQUENCE_LENGTH)
        discounting_rate = sm.SimulationManager.getCurrentSimulation().config.getFloat(DEEP_QLEARNING_DISCOUNTING_RATE)
        hidden_neuron_count = sm.SimulationManager.getCurrentSimulation().config.getInt(DEEP_QLEARNING_HIDDEN_NEURON_COUNT)

        qlearning_algorithm = QLearningAlgorithmFactory.getDeepQLearningAlgorithmLSTM(
                                                state_length,
                                                hidden_neuron_count=hidden_neuron_count,
                                                epsilon_greedy_rate=epsilon_greedy_rate,
                                                learning_rate=learning_rate,
                                                discounting_rate=discounting_rate,
                                                sequence_length=sequence_length)

        tlController.setQLearningAlgorithm(qlearning_algorithm)


        trafficLight.setController(tlController)
        return trafficLight

    @staticmethod
    def createBasicTrafficLightQLearningFPVCL(id):

        trafficLight = TrafficLightFactory.createTrafficLight(id)
        tlController = TrafficLightFactory.createTrafficLightController(trafficLight, TrafficLightControllerQLearningFPVCL)

        epsilon_greedy_rate = sm.SimulationManager.getCurrentSimulation().config.getFloat(QLEARNING_EPSILON_GREEDY_RATE)
        gamma_value = sm.SimulationManager.getCurrentSimulation().config.getFloat(QLEARNING_GAMMA_VALUE)
        alpha_value = sm.SimulationManager.getCurrentSimulation().config.getFloat(QLEARNING_LEARNING_RATE)

        qlearning_algorithm = QLearningAlgorithmFactory.getQLearningAlgorithm(
                                                epsilon_greedy_rate = epsilon_greedy_rate,
                                                gamma_value = gamma_value,
                                                alpha_value = alpha_value)

        tlController.setQLearningAlgorithm(qlearning_algorithm)
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
    def createRewardFunction(rewardFunctionParams, controller):
        if (rewardFunctionParams[0] in TLC_QLEARNING_REWARDS_WITH_PENALTY):
            if (len(rewardFunctionParams) < 2):
                raise Exception("The Reward Functions with penalty require a base reward function to be specified last.")
            baseRF = TrafficLightFactory.createRewardFunction(
                rewardFunctionParams[1:],
                controller)
            return TLC_QLEARNING_REWARD_FUNCTION[rewardFunctionParams[0]](controller, baseRF)
        else:
            return TLC_QLEARNING_REWARD_FUNCTION[rewardFunctionParams[0]](controller)

    @staticmethod
    def createStateRepresentation(stateRepresentationParams, discretizeValueParams, controller, stateRepresentationType = StateRepresentation.STATE_REPRESENTATION_NP_ARRAY):
        stateComponent = None
        for i in range(len(stateRepresentationParams) - 1, -1, -1):
            s = stateRepresentationParams[i]
            d = int(discretizeValueParams[i])
            #print(s, d)
            if (d <= 1):
                cur = TLC_QLEARNING_STATE_REPRESENTATION[s](controller,
                                    stateComponent = stateComponent,
                                    stateRepresentationType = stateRepresentationType)
            else:
                cur = TLC_QLEARNING_STATE_REPRESENTATION[s](controller,
                                    stateComponent = stateComponent,
                                    discretizeByValue = d,
                                    stateRepresentationType = stateRepresentationType)
            stateComponent = cur
        return stateComponent

    @staticmethod
    def createTrafficLightQLearningFPVCLFromRFandSR(id, rewardFunctionParams, stateRepresentationParams, discretizeValueParams):

        trafficLight = TrafficLightFactory.createBasicTrafficLightQLearningFPVCL(id)
        rf = TrafficLightFactory.createRewardFunction(rewardFunctionParams, trafficLight.controller)
        sc = TrafficLightFactory.createStateRepresentation(stateRepresentationParams, discretizeValueParams, trafficLight.controller,
                                                            stateRepresentationType = StateRepresentation.STATE_REPRESENTATION_STRING)

        trafficLight.controller.setRewardFunction(rf)
        trafficLight.controller.setStateRepresentation(sc)

        return trafficLight

    @staticmethod
    def createTrafficLightQLearningFPVCLFromParams(id):

        rfList = TrafficLightFactory.getRewardFunctionParams()
        srList, discretizeList = TrafficLightFactory.getStateRepresentationParams()

        return TrafficLightFactory.createTrafficLightQLearningFPVCLFromRFandSR(id, rfList, srList, discretizeList)

    @staticmethod
    def createTrafficLightDeepQLearningFPVCLFromRFandSR(id, rewardFunctionParams, stateRepresentationParams, discretizeValueParams):
        trafficLight = TrafficLightFactory.createBasicTrafficLightDeepQLearningFPVCL(id)

        rf = TrafficLightFactory.createRewardFunction(rewardFunctionParams, trafficLight.controller)
        sc = TrafficLightFactory.createStateRepresentation(stateRepresentationParams, discretizeValueParams, trafficLight.controller)

        trafficLight.controller.setRewardFunction(rf)
        trafficLight.controller.setStateRepresentation(sc)
        return trafficLight

    @staticmethod
    def createTrafficLightDeepQLearningFPVCLFromParams(id):
        rfList = TrafficLightFactory.getRewardFunctionParams()
        srList, discretizeList = TrafficLightFactory.getStateRepresentationParams()
        return TrafficLightFactory.createTrafficLightDeepQLearningFPVCLFromRFandSR(id,
                                        rfList, srList, discretizeList)

    @staticmethod
    def getStateRepresentationParams():
        srParams = sm.SimulationManager.getCurrentSimulation().config.get(QLEARNING_STATE_PARAMS)
        discretizeParams = sm.SimulationManager.getCurrentSimulation().config.get(QLEARNING_STATE_DISCRETIZE_PARAMS)
        srList = srParams.split(',')
        discretizeList = discretizeParams.split(',')
        return srList, discretizeList

    @staticmethod
    def getRewardFunctionParams():
        rfParams = sm.SimulationManager.getCurrentSimulation().config.get(QLEARNING_REWARD_PARAM)
        rfList = rfParams.split(',')
        return rfList

    @staticmethod
    def createTrafficLightDeepQLearningFPVCLWaitingVehiclesRF(id):
        return TrafficLightFactory.createTrafficLightDeepQLearningFPVCLFromRF(id, RewardWaitingVehicles)

    @staticmethod
    def createTrafficLightDeepQLearningFPVCLAvgQueueLengthRF(id):
        return TrafficLightFactory.createTrafficLightDeepQLearningFPVCLFromRF(id, RewardAverageQueueLength)

    @staticmethod
    def createTrafficLightDeepQLearningFPVCLThroughputRF(id):
        return TrafficLightFactory.createTrafficLightDeepQLearningFPVCLFromRF(id, RewardThroughput)

TLC_TYPE_FUNCTIONS = {'DeepQLearningAdaptiveLaneOccupancyRF': TrafficLightFactory.createTrafficLightDeepQLearningFPVCLAdaptiveLaneOccupancyRF,
                       'DeepQLearningWaitingVehiclesRF': TrafficLightFactory.createTrafficLightDeepQLearningFPVCLWaitingVehiclesRF,
                       'DeepQLearningAvgQueueLengthRF': TrafficLightFactory.createTrafficLightDeepQLearningFPVCLAvgQueueLengthRF,
                       'DeepQLearningThroughputRF': TrafficLightFactory.createTrafficLightDeepQLearningFPVCLThroughputRF,
                       'DeepQLearning' : TrafficLightFactory.createTrafficLightDeepQLearningFPVCLFromParams,
                       'QLearning': TrafficLightFactory.createTrafficLightQLearningFPVCLFromParams,
                       'FixedTime' : TrafficLightFactory.createTrafficLightFXM,
                       'WebsterLike': TrafficLightFactory.createTrafficLightWebsterLike
                       }

TLC_QLEARNING_REWARD_FUNCTION = {'AverageVehicleNumber' : RewardAverageVehicleNumber,
                            'Throughput': RewardThroughput,
                            'ActualThroughput': RewardActualThroughput,
                            'CumulativeVehicleDelay' : RewardCumulativeVehicleDelay,
                            'CumulativeVehicleDelayDiff': RewardCumulativeVehicleDelayDiff,
                            'AverageQueueLength': RewardAverageQueueLength,
                            'NumberOfStops': RewardNumberOfStops,
                            'NumberOfStopsDiff': RewardNumberOfStopsDiff,
                            'AdditionalStopsPenalty': RewardAdditionalStopsPenalty,
                            'ResidualQueuePenalty': RewardResidualQueuePenalty,
                            'WastedTimePenalty': RewardWastedTimePenalty,
                            'WastedTimePenaltyLogistic': RewardWastedTimePenaltyLogistic,
                            'ActualThroughputMaxQueueRatio': RewardActualThroughputMaxQueueRatio }

TLC_QLEARNING_REWARDS_WITH_PENALTY = ['ResidualQueuePenalty', 'AdditionalStopsPenalty', 'WastedTimePenalty', 'WastedTimePenaltyLogistic']

TLC_QLEARNING_STATE_REPRESENTATION = {'QueueLength' : StateQueueLength,
                                        'VehicleNumber' : StateVehicleNumber,
                                        'CurrentStage': StateCurrentStage,
                                        'ApproachingVehicles': StateApproachingVehicleNumber,
                                        'QueueLengthDiscretized': StateQueueLengthDiscretized,
                                        'VehicleNumberDiscretized': StateVehicleNumberDiscretized }
