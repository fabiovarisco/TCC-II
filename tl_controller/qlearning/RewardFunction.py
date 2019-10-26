from abc import ABC, abstractmethod

class RewardFunction(ABC):

    def __init__(self, controller):
        super().__init__()
        self.controller = controller

    @abstractmethod
    def step(self, step):
        pass

    @abstractmethod
    def getReward(self):
        pass

import math
import SimulationManager as sm
from simulation.event_constants import EVENT_ADAPTIVE_REWARD_FUNCTION_WEIGHT

class AdaptiveRewardFunction(RewardFunction, ABC):

    @staticmethod
    def activationLinear(x, **kwargs):
        return x
    
    @staticmethod
    def activationAdaptedSigmoid(x, **kwargs):
        x = (x * 2) - 1
        return 1 / (1 + math.exp(-kwargs['steepness'] * (x - kwargs['inf_point'])))

    def __init__(self, controller, activationFunction = activationLinear, steepness = 5, inf_point = 0):
        RewardFunction.__init__(self, controller)
        self.functions = []
        self.activationFunction = activationFunction
        self.kwargs = {'steepness' : steepness, 'inf_point' : inf_point}
    
    def addFunction(self, rewardFunction, weight = 1, inverse = False):
        self.functions.append([rewardFunction, weight, inverse])

    @abstractmethod
    def getDynamicWeight(self):
        pass
    
    def step(self, step):
        for f in self.functions:
            f[0].step(step)

    def getReward(self):
        reward = 0
        dynamicWeight = self.getDynamicWeight()
        dynamicWeightAA = self.activationFunction( self.getDynamicWeight(), self.kwargs)
        for f in self.functions:
            dw = 1 - dynamicWeightAA if f[2] else dynamicWeightAA
            reward += dw * f[1] * f[0].getReward()
        
        sm.SimulationManager.getCurrentSimulation().notify(EVENT_ADAPTIVE_REWARD_FUNCTION_WEIGHT, 
                    tl_id=self.controller.trafficLight.getID(), dynamic_weight=dynamicWeight,
                    dynamic_weight_activation=dynamicWeightAA, reward=reward)
                    
        return reward

   
# On second thought, this measure seems problematic as the total cumulative delay is always increasing
class RewardCumulativeDelay(RewardFunction):

    def __init__(self, controller):
        super().__init__(controller)
        self.currentStepCumulativeDelay = 0
        self.previousStepWaitingVehicles = 0

        maxStageLength = (sm.SimulationManager.getCurrentSimulation().config.getInt(TLC_QLEARNING_ACTION_MAX_GREEN) *
                         sm.SimulationManager.getCurrentSimulation().config.getInt(TLC_QLEARNING_ACTION_UNIT_LENGTH))
        
        self.maxPossibleDelay = 0
        for s in self.controller.trafficLight.getStages():
            for sl in s.getSignalLanes():
                self.maxPossibleDelay += sl.incoming.getMaxPossibleQueueLength()
        self.maxPossibleDelay *= (maxStageLength / 2)     


    def step(self, step):
        self.previousStepCumulativeDelay = self.currentStepCumulativeDelay
        self.currentStepCumulativeDelay = self.controller.trafficLight.getTotalCumulativeDelay()

    def getReward(self):
        return (self.previousStepCumulativeDelay - self.currentStepCumulativeDelay) / self.maxPossibleDelay

class RewardWaitingVehicles(RewardFunction):

    def __init__(self, controller):
        super().__init__(controller)
        self.previousStepWaitingVehicles = 0
        self.currentStepWaitingVehicles = 0
        
        maxStageLength = (sm.SimulationManager.getCurrentSimulation().config.getInt(TLC_QLEARNING_ACTION_MAX_GREEN) *
                        sm.SimulationManager.getCurrentSimulation().config.getInt(TLC_QLEARNING_ACTION_UNIT_LENGTH))
        self.maxReward = 0 
        saturationFlowConstant = sm.SimulationManager.getCurrentSimulation().config.getInt(CONSTANT_SATURATION_FLOW)
        for s in self.controller.trafficLight.getStages():
            for sl in s.getSignalLanes():
                saturationFlow = saturationFlowConstant * sl.incoming.getWidth()
                self.maxReward += (saturationFlow / 3600) * maxStageLength


    def step(self, step):
        waitingVehicles = 0
        for s in self.controller.trafficLight.getStages():
            for sl in s.getSignalLanes():
                waitingVehicles += sl.incoming.getQueueLength()
        self.previousStepWaitingVehicles = self.currentStepWaitingVehicles
        self.currentStepWaitingVehicles = waitingVehicles

    def getReward(self):
        reward = (self.previousStepWaitingVehicles - self.currentStepWaitingVehicles) / self.maxReward
        
        # TODO Implement a statistics file to log rewards.

        return error_todo

from SimulationConfig import QLEARNING_REWARD_WEIGHT_THROUGHPUT, QLEARNING_REWARD_WEIGHT_QUEUE_RATIO, CONSTANT_SATURATION_FLOW, TLC_STAGE_MAX_LENGTH, LANE_MAX_ACCEPTABLE_QUEUE_OCCUPANCY, VEHICLE_AVG_LENGTH, TLC_QLEARNING_ACTION_MAX_GREEN, TLC_QLEARNING_ACTION_UNIT_LENGTH 
import SimulationManager as sm

class RewardThroughput(RewardFunction):

    def __init__(self, controller):
        super().__init__(controller)
        self.weight_throughput = sm.SimulationManager.getCurrentSimulation().config.getInt(QLEARNING_REWARD_WEIGHT_THROUGHPUT)
        self.weight_queue_ratio = sm.SimulationManager.getCurrentSimulation().config.getInt(QLEARNING_REWARD_WEIGHT_QUEUE_RATIO)
        self.maxStageLength = sm.SimulationManager.getCurrentSimulation().config.getInt(TLC_STAGE_MAX_LENGTH)

    def step(self, step):
        pass

    def _getThroughputForCurrentStage(self):
        s = self.controller.trafficLight.getStages()[self.controller.trafficLight.getCurrentStage()]
        stageLength = self.controller.nextStepIn
        throughput = 0
        maxThroughput = 0
        for sl in s.getSignalLanes():
            saturationFlow = sm.SimulationManager.getCurrentSimulation().config.getInt(CONSTANT_SATURATION_FLOW) * sl.incoming.getWidth()
            throughput += (saturationFlow / 3600) * stageLength
            maxThroughput += (saturationFlow / 3600) * self.maxStageLength
        return throughput / maxThroughput

    def _getQueueRatio(self):
        s = self.controller.trafficLight.getStages()[self.controller.trafficLight.getCurrentStage()]
        queueRatio = 0
        for s in self.controller.trafficLight.getStages():
            maxLength = 0
            maxLengthIndex = 0
            i = 0
            for sl in s.getSignalLanes():
                qL = sl.incoming.getQueueLength()
                if (qL > maxLength):
                    maxLength = qL
                    maxLengthIndex = i
                i += 1
            maxPossibleQueueLength = s.getSignalLanes()[maxLengthIndex].incoming.getMaxPossibleQueueLength()
            laneAceptableQueueLength *= sm.SimulationManager.getCurrentSimulation().config.getFloat(LANE_MAX_ACCEPTABLE_QUEUE_OCCUPANCY)
            queueRatio += maxLength / laneAceptableQueueLength
        
        queueRatio = 1 - (queueRatio / len(self.controller.trafficLight.getStages()))
        return queueRatio

    def getReward(self):
        return ((self.weight_throughput * self._getThroughputForCurrentStage())
                + (self.weight_queue_ratio * self._getQueueRatio())) / (self.weight_throughput + self.weight_queue_ratio)

class AdaptiveLaneOccupancyReward(AdaptiveRewardFunction):

    def getDynamicWeight(self):
        maxOccupancy = self.controller.trafficLight.getMaxLaneccupancy()
        #print(f"Max occupancy: {maxOccupancy}")
        return maxOccupancy
