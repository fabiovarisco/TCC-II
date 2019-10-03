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
