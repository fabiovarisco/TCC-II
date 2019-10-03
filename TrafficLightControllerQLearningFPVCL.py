
from TrafficLightControllerQLearning import TrafficLightControllerQLearning
from ControllerAlgorithmQLearning import ControllerAlgorithmQLearning
import time
import math

TL_YELLOW_RED_TIME = 4
TL_TOTAL_LOST_TIME = (2 * 2) + 4 # (2s amber period * no. of stages) + all_red_time
MIN_GREEN_TIME = 5
TLC_INITIAL_STAGE_LENGTH = 20

class TrafficLightControllerQLearningFPVCL(TrafficLightControllerQLearning):

    """docstring for TrafficLightControllerQLearning."""
    def __init__(self, trafficLight):
        super(TrafficLightControllerQLearningFPVCL, self).__init__(trafficLight)

        self.nextStepIn = TLC_INITIAL_STAGE_LENGTH

    def getPossibleActions(self, state_key):
        return range(2, 30)

    def takeAction(self, action, step):
        self.currentStageLength = action * 3
        self.trafficLight.advanceStage()
        self.resetCounterStep = step + TL_YELLOW_RED_TIME
