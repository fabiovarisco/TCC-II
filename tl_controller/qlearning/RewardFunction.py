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
from simulation.event_constants import EVENT_ADAPTIVE_REWARD_FUNCTION_WEIGHT, EVENT_REWARD_FUNCTION

class AdaptiveRewardFunction(RewardFunction, ABC):

    @staticmethod
    def activationLinear(x, **kwargs):
        return x

    @staticmethod
    def activationAdaptedSigmoid(x, **kwargs):
        x = (x * 2) - 1
        return 1 / (1 + math.exp(-kwargs['steepness'] * (x - kwargs['inf_point'])))

    def __init__(self, controller, activationFunction = activationLinear, steepness = 15, inf_point = -0.2):
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
        dynamicWeightAA = self.activationFunction( self.getDynamicWeight(), **self.kwargs)
        for f in self.functions:
            dw = 1 - dynamicWeightAA if f[2] else dynamicWeightAA
            reward += dw * f[1] * f[0].getReward()

        sm.SimulationManager.getCurrentSimulation().notify(EVENT_ADAPTIVE_REWARD_FUNCTION_WEIGHT,
                    tl_id=self.controller.trafficLight.getId(), dynamic_weight=dynamicWeight,
                    dynamic_weight_activation=dynamicWeightAA, reward=reward)

        return reward

class RewardWithPenalty(RewardFunction, ABC):

    def __init__(self, controller, baseRewardFunction):
        RewardFunction.__init__(self, controller)
        self.controller = controller
        self.baseRF = baseRewardFunction

    def step(self, step):
        self.baseRF.step(step)

    @abstractmethod
    def getPenalty(self):
        pass

    def getReward(self):
        baseReward = self.baseRF.getReward()
        penalty = self.getPenalty()
        reward = baseReward - penalty

        sm.SimulationManager.getCurrentSimulation().notify(EVENT_REWARD_FUNCTION,
                    tl_id=self.controller.trafficLight.getId(),
                    reward_type='reward_with_penalty', previous=baseReward,
                    current=baseReward, max=penalty, reward=reward)
        return reward

class RewardAdditionalStopsPenalty(RewardWithPenalty):

    def getPenalty(self):
        numberOfStops = 0
        max = 0
        for l in self.controller.trafficLight.incoming:
            numberOfStops += l.getNumberOfExtraStops()
            #numberOfStops += l.getNumberOfStops()
            max += (l.getMaxAcceptableQueueLength() / 2)
        return (numberOfStops / max)

class RewardResidualQueuePenalty(RewardWithPenalty):

    def getPenalty(self):
        residual_queue_total = self.controller.trafficLight.vehicles_not_dispatched_total
        max = self.controller.trafficLight.getMaxAcceptableQueueLengthForStage(self.controller.trafficLight.getPreviousStage()) / 2
        return residual_queue_total / max

class RewardWastedTimePenalty(RewardWithPenalty):

    def __init__(self, controller, baseRewardFunction):
        RewardWithPenalty.__init__(self, controller, baseRewardFunction)
        self.maxStageLength = (sm.SimulationManager.getCurrentSimulation().config.getInt(TLC_QLEARNING_ACTION_MAX_GREEN) *
                         sm.SimulationManager.getCurrentSimulation().config.getInt(TLC_QLEARNING_ACTION_UNIT_LENGTH))

    def getPenalty(self):
        return self.controller.trafficLight.wastedTimeLastStage / self.maxStageLength

class RewardWastedTimePenaltyLogistic(RewardWastedTimePenalty):

    def _adaptedLogistic(self, x):
        x = (x * 2) - 1
        return 1 / (1 + math.exp(-5 * (x + 0.4)))

    def getPenalty(self):
        return self._adaptedLogistic(super().getPenalty())

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
        previous = self.previousStepCumulativeDelay
        current = self.currentStepCumulativeDelay
        reward = (previous - current) / self.maxPossibleDelay

        sm.SimulationManager.getCurrentSimulation().notify(EVENT_REWARD_FUNCTION,
                    tl_id=self.controller.trafficLight.getId(),
                    reward_type='cumulative_delay', previous=previous,
                    current=current, max=self.maxPossibleDelay, reward=reward)

        return reward

class RewardCumulativeVehicleDelay(RewardFunction):

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
        #self.maxPossibleDelay *= (maxStageLength / 2)
        self.maxPossibleDelay *= maxStageLength

    def step(self, step):
        self.previousStepCumulativeDelay = self.currentStepCumulativeDelay
        self.currentStepCumulativeDelay = self.controller.trafficLight.getCumulativeVehicleDelay()

    def getReward(self):

        reward = 1 - (self.currentStepCumulativeDelay / self.maxPossibleDelay)

        sm.SimulationManager.getCurrentSimulation().notify(EVENT_REWARD_FUNCTION,
                    tl_id=self.controller.trafficLight.getId(),
                    reward_type='vehicle_cumulative_delay', previous=self.previousStepCumulativeDelay,
                    current=self.currentStepCumulativeDelay, max=self.maxPossibleDelay, reward=reward)

        return reward

class RewardCumulativeVehicleDelayDiff(RewardCumulativeVehicleDelay):

    def getReward(self):

        reward = ((self.previousStepCumulativeDelay - self.currentStepCumulativeDelay)
                        / self.maxPossibleDelay)

        sm.SimulationManager.getCurrentSimulation().notify(EVENT_REWARD_FUNCTION,
                    tl_id=self.controller.trafficLight.getId(),
                    reward_type='vehicle_cumulative_delay', previous=self.previousStepCumulativeDelay,
                    current=self.currentStepCumulativeDelay, max=self.maxPossibleDelay, reward=reward)

        return reward

class RewardNumberOfStops(RewardFunction):

    def __init__(self, controller):
        super().__init__(controller)
        self.previousNumberOfStops = 0
        self.currentNumberOfStops = 0

        self.maxNumberOfStops = 0
        for s in self.controller.trafficLight.getStages():
            for sl in s.getSignalLanes():
                self.maxNumberOfStops += sl.incoming.getMaxPossibleQueueLength()
        #self.maxNumberOfStops *= 2
        self.maxNumberOfStops *= 0.25


    def step(self, step):
        self.previousNumberOfStops = self.currentNumberOfStops
        self.currentNumberOfStops = self.controller.trafficLight.getTotalNumberOfStops()

    def getReward(self):

        reward = 1 - (self.currentNumberOfStops / self.maxNumberOfStops)

        sm.SimulationManager.getCurrentSimulation().notify(EVENT_REWARD_FUNCTION,
                    tl_id=self.controller.trafficLight.getId(),
                    reward_type='vehicle_number_of_stops', previous=self.previousNumberOfStops,
                    current=self.currentNumberOfStops, max=self.maxNumberOfStops, reward=reward)

        return reward

class RewardNumberOfStopsDiff(RewardNumberOfStops):

    def getReward(self):

        reward = ((self.previousNumberOfStops - self.currentNumberOfStops)
                        / self.maxNumberOfStops)

        sm.SimulationManager.getCurrentSimulation().notify(EVENT_REWARD_FUNCTION,
                    tl_id=self.controller.trafficLight.getId(),
                    reward_type='vehicle_number_of_stops', previous=self.previousNumberOfStops,
                    current=self.currentNumberOfStops, max=self.maxNumberOfStops, reward=reward)

        return reward

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
        previous = self.previousStepWaitingVehicles
        current = self.currentStepWaitingVehicles
        reward = (previous - current) / self.maxReward

        sm.SimulationManager.getCurrentSimulation().notify(EVENT_REWARD_FUNCTION,
                    tl_id=self.controller.trafficLight.getId(),
                    reward_type='waiting_vehicles', previous=previous,
                    current=current, max=self.maxReward, reward=reward)

        return reward

class RewardAverageQueueLength(RewardFunction):

    def __init__(self, controller):
        super().__init__(controller)

    def step(self, step):
        pass

    def getReward(self):
        averageQueueLength = 0
        averageMaxAcceptableQueueLength = 0

        n = 0
        for s in self.controller.trafficLight.getStages():
            for sl in s.getSignalLanes():
                averageQueueLength += sl.incoming.getQueueLength()
                averageMaxAcceptableQueueLength += sl.incoming.getMaxAcceptableQueueLength()
                n += 1
        averageQueueLength = averageQueueLength / n
        averageMaxAcceptableQueueLength = averageMaxAcceptableQueueLength / n

        reward = 1 - (averageQueueLength / averageMaxAcceptableQueueLength)

        sm.SimulationManager.getCurrentSimulation().notify(EVENT_REWARD_FUNCTION,
                    tl_id=self.controller.trafficLight.getId(),
                    reward_type='avg_queue_length', previous=averageQueueLength,
                    current=averageQueueLength, max=averageMaxAcceptableQueueLength, reward=reward)

        return reward

class RewardAverageVehicleNumber(RewardFunction):

    def __init__(self, controller):
        super().__init__(controller)

    def step(self, step):
        pass

    def getReward(self):
        averageVehicleNumber= 0
        averageMaxAcceptableQueueLength = 0

        n = 0
        for s in self.controller.trafficLight.getStages():
            for sl in s.getSignalLanes():
                averageVehicleNumber += sl.incoming.getVehicleNumber()
                averageMaxAcceptableQueueLength += sl.incoming.getMaxAcceptableQueueLength()
                n += 1

        averageVehicleNumber = averageVehicleNumber / n
        averageMaxAcceptableQueueLength = averageMaxAcceptableQueueLength / n

        reward = 1 - (averageVehicleNumber / averageMaxAcceptableQueueLength)

        sm.SimulationManager.getCurrentSimulation().notify(EVENT_REWARD_FUNCTION,
                    tl_id=self.controller.trafficLight.getId(),
                    reward_type='avg_vehicle_number', previous=averageVehicleNumber,
                    current=averageVehicleNumber, max=averageMaxAcceptableQueueLength, reward=reward)

        return reward


from SimulationConfig import QLEARNING_REWARD_WEIGHT_THROUGHPUT, QLEARNING_REWARD_WEIGHT_QUEUE_RATIO, CONSTANT_SATURATION_FLOW, TLC_STAGE_MAX_LENGTH, LANE_MAX_ACCEPTABLE_QUEUE_OCCUPANCY, VEHICLE_AVG_LENGTH, TLC_QLEARNING_ACTION_MAX_GREEN, TLC_QLEARNING_ACTION_UNIT_LENGTH
import SimulationManager as sm

class RewardThroughput(RewardFunction):

    def __init__(self, controller):
        super().__init__(controller)
        self.weight_throughput = sm.SimulationManager.getCurrentSimulation().config.getInt(QLEARNING_REWARD_WEIGHT_THROUGHPUT)
        self.weight_queue_ratio = sm.SimulationManager.getCurrentSimulation().config.getInt(QLEARNING_REWARD_WEIGHT_QUEUE_RATIO)
        self.maxStageLength = sm.SimulationManager.getCurrentSimulation().config.getInt(TLC_STAGE_MAX_LENGTH)
        self.saturationFlowConstant = sm.SimulationManager.getCurrentSimulation().config.getInt(CONSTANT_SATURATION_FLOW)

    def step(self, step):
        pass

    def _getThroughputForPreviousStage(self):
        s = self.controller.trafficLight.getStages()[self.controller.trafficLight.getPreviousStage()]
        stageLength = self.controller.lastStageTime
        throughput = 0
        maxThroughput = 0
        for sl in s.getSignalLanes():
            saturationFlow = self.saturationFlowConstant * sl.incoming.getWidth()
            throughput += (saturationFlow / 3600) * stageLength
            maxThroughput += (saturationFlow / 3600) * self.maxStageLength
        return throughput / maxThroughput

    def _getQueueRatio(self):
        queueRatio = 0
        for s in self.controller.trafficLight.getStages():
            maxLength = 0
            maxLengthIndex = 0
            for i, sl in enumerate(s.getSignalLanes()):
                qL = sl.incoming.getQueueLength()
                if (qL > maxLength):
                    maxLength = qL
                    maxLengthIndex = i
            laneAceptableQueueLength = s.getSignalLanes()[maxLengthIndex].incoming.getMaxAcceptableQueueLength()
            queueRatio += maxLength / laneAceptableQueueLength

        queueRatio = 1 - (queueRatio / len(self.controller.trafficLight.getStages()))
        return queueRatio

    def getReward(self):
        throughput = self._getThroughputForPreviousStage()
        queue_ratio = self._getQueueRatio()
        totalWeight = self.weight_throughput + self.weight_queue_ratio
        reward = (((self.weight_throughput * throughput)
                + (self.weight_queue_ratio * queue_ratio)) / totalWeight)

        sm.SimulationManager.getCurrentSimulation().notify(EVENT_REWARD_FUNCTION,
                    tl_id=self.controller.trafficLight.getId(),
                    reward_type='throughput_queueratio', previous=throughput,
                    current=queue_ratio, max=totalWeight, reward=reward)
        return reward

class RewardActualThroughput(RewardThroughput):

    def _getThroughputForPreviousStage(self):
        s = self.controller.trafficLight.getStages()[self.controller.trafficLight.getPreviousStage()]
        throughput = 0
        maxThroughput = 0

        totalVehicleNumber = 0
        for sl in s.getSignalLanes():
            totalVehicleNumber += sl.incoming.getVehicleNumberAtBeginningOfStage()
            throughput += sl.incoming.getVehicleThroughput()
        totalVehicleNumber += (totalVehicleNumber * 0.4)
        if (totalVehicleNumber == 0):
            return 1
        else:
            return throughput / totalVehicleNumber

class RewardActualThroughputMaxQueueRatio(RewardActualThroughput):

    def _getQueueRatio(self):
        queueRatio = 0
        maxQueueRatio = 0
        for l in self.controller.trafficLight.incoming:
            maxQueueRatio = max(maxQueueRatio, (l.getQueueLength() / l.getMaxAcceptableQueueLength()))
        queueRatio = 1 - maxQueueRatio
        return queueRatio


class AdaptiveLaneOccupancyReward(AdaptiveRewardFunction):

    def getDynamicWeight(self):
        maxOccupancy = self.controller.trafficLight.getMaxLaneccupancy()
        #print(f"Max occupancy: {maxOccupancy}")
        return maxOccupancy

class AdaptiveArrivalToCapacityRatioReward(AdaptiveRewardFunction):

    def getDynamicWeight(self):
        maxRatio = self.controller.trafficLight.getMaxArrivalToCapacityRatio()
        print(f"Max ratio: {maxRatio}")
        return maxRatio
