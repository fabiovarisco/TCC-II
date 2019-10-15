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

class RewardCumulativeDelay(RewardFunction):

    def __init__(self, controller):
        super().__init__(controller)
        self.currentStepCumulativeDelay = 0
        self.previousStepWaitingVehicles = 0

    def step(self, step):
        self.previousStepCumulativeDelay = self.currentStepCumulativeDelay
        self.currentStepCumulativeDelay = self.controller.trafficLight.getTotalCumulativeDelay()

    def getReward(self):
        return self.previousStepCumulativeDelay - self.currentStepCumulativeDelay

class RewardWaitingVehicles(RewardFunction):

    def __init__(self, controller):
        super().__init__(controller)
        self.previousStepWaitingVehicles = 0
        self.currentStepWaitingVehicles = 0

    def step(self, step):
        waitingVehicles = 0
        for s in self.controller.trafficLight.getStages():
            for sl in s.getSignalLanes():
                waitingVehicles += sl.incoming.getQueueLength()
        self.previousStepWaitingVehicles = self.currentStepWaitingVehicles
        self.currentStepWaitingVehicles = waitingVehicles

    def getReward(self):
        return self.previousStepWaitingVehicles - self.currentStepWaitingVehicles

from SimulationConfig import QLEARNING_REWARD_WEIGHT_THROUGHPUT, QLEARNING_REWARD_WEIGHT_QUEUE_RATIO, CONSTANT_SATURATION_FLOW, TLC_STAGE_MAX_LENGTH
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
            lane = s.getSignalLanes()[maxLengthIndex].incoming
            if (lane.getLastStepLength() > 0):
                laneAceptableQueueLength = (lane.getLength() / lane.getLastStepLength() * 
                                            sm.SimulationManager.getCurrentSimulation().config.getInt(LANE_MAX_ACCEPTABLE_QUEUE_OCCUPANCY))
            else:
                laneAceptableQueueLength = (lane.getLength() / sm.SimulationManager.getCurrentSimulation().config.getInt(VEHICLE_AVG_LENGTH) 
                                            * sm.SimulationManager.getCurrentSimulation().config.getInt(LANE_MAX_ACCEPTABLE_QUEUE_OCCUPANCY))
            queueRatio += maxLength / laneAceptableQueueLength
        queueRatio = 1 - (queueRatio / len(self.controller.trafficLight.getStages()))
        return queueRatio

    def getReward(self):
        return (self.weight_throughput * self._getThroughputForCurrentStage()) + 
                (self.weight_queue_ratio * self._getQueueRatio())
