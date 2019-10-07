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

    def __init__(self, controller):
        super().__init__(controller)


    def step(self, step):
        pass

    def _getThroughputForCurrentStage(self):
        s = self.controller.trafficLight.getStages()[self.controller.trafficLight.getCurrentStage()]
        stageLength = self.controller.nextStepIn
        throughput = 0
        for sl in s.getSignalLanes():
            saturationFlow = 525 * sl.incoming.getWidth()
            throughput += (saturationFlow / 3600) * stageLength
        return throughput

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
            queueRatio += maxLength / (lane.getLength() / lane.getLastStepLength() * 0.7)
        queueRatio = queueRatio / len(self.controller.trafficLight.getStages())
        return queueRatio

    def getReward(self):
        # TODO

        return self.previousStepWaitingVehicles - self.currentStepWaitingVehicles
