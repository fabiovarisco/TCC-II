
from tl_controller import TrafficLightController as tlc
from tl_controller.qlearning.ControllerAlgorithmQLearning import ControllerAlgorithmQLearning
from abc import ABC, abstractmethod

import SimulationManager as sm

from SimulationConfig import TL_STAGE_LOST_TIME, TL_STAGE_MIN_GREEN_TIME

class TrafficLightControllerQLearning(tlc.TrafficLightController, ABC):

    """docstring for TrafficLightControllerQLearning."""
    def __init__(self, trafficLight):
        tlc.TrafficLightController.__init__(self, trafficLight)

        self.resetCounterStep = 0
        self.nextStepIn = sm.SimulationManager.getCurrentSimulation().config.getInt(TL_STAGE_MIN_GREEN_TIME)

    def setQLearningAlgorithm(self, AlgorithmQLearning = ControllerAlgorithmQLearning):
        self.algorithm = AlgorithmQLearning(self)

    def setStateRepresentation(self, stateRepresentation):
        self.stateRepresentation = stateRepresentation
        self.algorithm.initState(self.stateRepresentation.getCurrentState())

    def setRewardFunction(self, rewardFunction):
        self.rewardFunction = rewardFunction

    def step(self, step):
        if (step - self.resetCounterStep > self.nextStepIn):
            self.rewardFunction.step(step)
            self.algorithm.step(step)

    def getReward(self):
        return self.rewardFunction.getReward()

    def getCurrentState(self):
        return self.stateRepresentation.getCurrentState()

    @abstractmethod
    def getPossibleActions(self, state_key):
        pass

    @abstractmethod
    def takeAction(self, action, step):
        self.resetCounterStep = step


'''

El-Thantawy 2010
class TrafficLightControllerQLearningVPVPL(TrafficLightController):

    """docstring for TrafficLightControllerQLearning."""
    def __init__(self, trafficLight):
        super(TrafficLightControllerQLearning, self).__init__(trafficLight)

        self.minStepGap = 4 + MIN_GREEN_TIME

        self.algorithm = ControllerAlgorithmQLearning(self)
        self.lastStageChangeStep = 0
        self.previousStepCumulativeDelay = 0
        self.currentStepCumulativeDelay = 0
        self.previousStepWaitingVehicles = 0
        self.currentStepWaitingVehicles = 0

        self.delayHistory = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.delayHistoryCurrent = 0


    def step(self, step):
        #if (step % 2 == 0):
        self.delayHistory[self.delayHistoryCurrent] = self.trafficLight.getTotalCumulativeDelay()
        if (step - self.lastStageChangeStep > self.minStepGap):
            self.previousStepCumulativeDelay = self.currentStepCumulativeDelay
            self.currentStepCumulativeDelay = self.trafficLight.getTotalCumulativeDelay()
            waitingVehicles = 0
            for s in self.trafficLight.getStages():
                for sl in s.getSignalLanes():
                    waitingVehicles += sl.incoming.getQueueLength()
            self.previousStepWaitingVehicles = self.currentStepWaitingVehicles
            self.currentStepWaitingVehicles = waitingVehicles
            #self.currentStepCumulativeDelay = self.trafficLight.getTotalWaitingTime()
            self.algorithm.step(step)
        self.delayHistoryCurrent = (self.delayHistoryCurrent + 1) % 9

    def getReward(self):
        self.currentImmediateReward = self.previousStepCumulativeDelay - self.currentStepCumulativeDelay
        return self.currentImmediateReward
        #return self.previousStepWaitingVehicles - self.currentStepWaitingVehicles
        #previousIndex = (self.delayHistoryCurrent + 1) % 9
        #return self.delayHistory[previousIndex] - self.delayHistory[self.delayHistoryCurrent]

    def getCurrentState(self):
        state = []
        for s in self.trafficLight.getStages():
            state.append(math.ceil(s.getMaxLaneLength()))
            #state.append(math.ceil(s.getMaxVehicleNumber() / 2.0))
        state.append(self.trafficLight.getCurrentStage())
        return '_'.join(map(str, state))
        #return state

    def getPossibleActions(self, state_key):
        return range(0, len(self.controller.trafficLight.getStages()))

    def takeAction(self, action, step):
        if (action != self.trafficLight.getCurrentStage()):
            self.lastStageChangeStep = step
            self.trafficLight.setStage(action)


'''
