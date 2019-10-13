
from abc import ABC, abstractmethod
import math

class StateRepresentation(ABC):

    def __init__(self, controller, stateComponent = None):
        super().__init__()
        self.controller = controller
        self.stateComponent = stateComponent

    @abstractmethod
    def getCurrentState(self):
        if (self.stateComponent is not None):
            self.currentState = f"{self.currentState}_{self.stateComponent.getCurrentState()}"
        return self.currentState


class StateQueueLength(StateRepresentation):

    def getCurrentState(self):
        state = []
        for s in self.controller.trafficLight.getStages():
            state.append(s.getMaxLaneLength())
            #state.append(math.ceil(s.getMaxVehicleNumber() / 2.0))
        self.currentState = '_'.join(map(str, state))
        return super().getCurrentState()


class StateQueueLengthDiscretized(StateRepresentation):

    def __init__(self, controller, discretizeByValue = 1, stateComponent = None):
        super().__init__(controller, stateComponent)
        self.discretizeByValue = discretizeByValue

    def getCurrentState(self):
        state = []
        for s in self.controller.trafficLight.getStages():
            state.append(math.ceil(s.getMaxLaneLength() / self.discretizeByValue))
        self.currentState = '_'.join(map(str, state))
        return super().getCurrentState()

class StateCurrentStage(StateRepresentation):

    def getCurrentState(self):
        self.currentState = str(self.controller.trafficLight.getCurrentStage())
        return super().getCurrentState()

class StateNextStage(StateRepresentation):

    def getCurrentState(self):
        self.currentState = str(self.controller.trafficLight.getNextStage())
        return super().getCurrentState()
