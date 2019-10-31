
from abc import ABC, abstractmethod
import math
import numpy as np

class StateRepresentation(ABC):

    STATE_REPRESENTATION_STRING = 1
    STATE_REPRESENTATION_NP_ARRAY = 2

    def _stateToArray(self, state):
        return np.array(state)

    def _stateToString(self, state):
        return '_'.join(map(str, state))

    def _concatStateArrays(self, arr1, arr2):
        return np.concatenate((arr1, arr2))

    def _concatStateString(self, str1, str2):
        return f"{str1}_{str2}"

    def __init__(self, controller, stateComponent = None, stateRepresentationType = STATE_REPRESENTATION_STRING ):
        super().__init__()
        self.controller = controller
        self.stateComponent = stateComponent
        if (stateRepresentationType == StateRepresentation.STATE_REPRESENTATION_STRING):
            self.stateToRepresentation = self._stateToString
            self.concatStateRepresentation = self._concatStateString
        else:
            self.stateToRepresentation = self._stateToArray
            self.concatStateRepresentation = self._concatStateArrays

    @abstractmethod
    def getCurrentState(self):
        currentState = self.stateToRepresentation(self.stateArr)
        if (self.stateComponent is not None):
            currentState = self.concatStateRepresentation(currentState, self.stateComponent.getCurrentState())
        return currentState


class StateQueueLength(StateRepresentation):

    def getCurrentState(self):
        self.stateArr = []
        for s in self.controller.trafficLight.getStages():
            self.stateArr.append(s.getMaxLaneLength())
        return super().getCurrentState()

class StateVehicleNumber(StateRepresentation):

    def getCurrentState(self):
        self.stateArr = []
        for s in self.controller.trafficLight.getStages():
            self.stateArr.append(s.getMaxVehicleNumber())
        return super().getCurrentState()

class StateVehicleNumberDiscretized(StateRepresentation):

    def __init__(self, controller, discretizeByValue = 1, stateComponent = None):
        super().__init__(controller, stateComponent)
        self.discretizeByValue = discretizeByValue

    def getCurrentState(self):
        self.stateArr = []
        for s in self.controller.trafficLight.getStages():
            self.stateArr.append(math.ceil(s.getMaxVehicleNumber() / self.discretizeByValue))
        return super().getCurrentState()


class StateApproachingVehicleNumber(StateRepresentation):

    def getCurrentState(self):
        self.stateArr = []
        for s in self.controller.trafficLight.getStages():
            self.stateArr.append(s.getMaxVehicleNumber() - s.getMaxLaneLength())
        return super().getCurrentState()

class StateApproachingVehicleNumberDiscretized(StateRepresentation):

    def __init__(self, controller, discretizeByValue = 1, stateComponent = None):
        super().__init__(controller, stateComponent)
        self.discretizeByValue = discretizeByValue

    def getCurrentState(self):
        self.stateArr = []
        for s in self.controller.trafficLight.getStages():
            self.stateArr.append(math.ceil((s.getMaxVehicleNumber() - s.getMaxLaneLength()) / self.discretizeByValue))
        return super().getCurrentState()


class StateQueueLengthDiscretized(StateRepresentation):

    def __init__(self, controller, discretizeByValue = 1, stateComponent = None):
        super().__init__(controller, stateComponent)
        self.discretizeByValue = discretizeByValue

    def getCurrentState(self):
        self.stateArr = []
        for s in self.controller.trafficLight.getStages():
            self.stateArr.append(math.ceil(s.getMaxLaneLength() / self.discretizeByValue))
        return super().getCurrentState()

class StateCurrentStage(StateRepresentation):

    def getCurrentState(self):
        self.stateArr = [ self.controller.trafficLight.getCurrentStage() ]
        return super().getCurrentState()

class StateNextStage(StateRepresentation):

    def getCurrentState(self):
        self.stateArr = [ self.controller.trafficLight.getNextStage() ]
        return super().getCurrentState()
