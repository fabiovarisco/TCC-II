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

class RewardThroughput(RewardFunction):

    WEIGHT_THROUGHPUT = 1
    WEIGHT_QUEUE_RATIO = 1

    def __init__(self, controller, maxStageLength):
        super().__init__(controller)
        self.maxStageLength = maxStageLength

    def step(self, step):
        pass

    def _getThroughputForCurrentStage(self):
        s = self.controller.trafficLight.getStages()[self.controller.trafficLight.getCurrentStage()]
        stageLength = self.controller.nextStepIn
        throughput = 0
        maxThroughput = 0
        for sl in s.getSignalLanes():
            saturationFlow = 525 * sl.incoming.getWidth()
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
                laneAceptableQueueLength = (lane.getLength() / lane.getLastStepLength() * 0.7)
            else:
                laneAceptableQueueLength = (lane.getLength() / 7 * 0.7)
            queueRatio += maxLength / laneAceptableQueueLength
        queueRatio = 1 - (queueRatio / len(self.controller.trafficLight.getStages()))
        return queueRatio

    def getReward(self):
        return (RewardThroughput.WEIGHT_THROUGHPUT * self._getThroughputForCurrentStage()) + (RewardThroughput.WEIGHT_QUEUE_RATIO * self._getQueueRatio())
