
from tl_controller import TrafficLightControllerQLearning as tlcQLearning
import time
import math
import numpy as np

import SimulationManager as sm
from SimulationConfig import TL_STAGE_LOST_TIME, TLC_STAGE_INITIAL_LENGTH, TLC_QLEARNING_ACTION_MIN_GREEN, TLC_QLEARNING_ACTION_MAX_GREEN, TLC_QLEARNING_ACTION_UNIT_LENGTH


class TrafficLightControllerQLearningFPVCL(tlcQLearning.TrafficLightControllerQLearning):

    """docstring for TrafficLightControllerQLearning."""
    def __init__(self, trafficLight):
        super(TrafficLightControllerQLearningFPVCL, self).__init__(trafficLight)

        self.nextStepIn = sm.SimulationManager.getCurrentSimulation().config.getInt(TLC_STAGE_INITIAL_LENGTH)
        self.isStageSwitchInProgress = False

    def getPossibleActions(self, state_key):
        return range(sm.SimulationManager.getCurrentSimulation().config.getInt(TLC_QLEARNING_ACTION_MIN_GREEN),
                    sm.SimulationManager.getCurrentSimulation().config.getInt(TLC_QLEARNING_ACTION_MAX_GREEN))

    def takeAction(self, action, step):
        self.nextStepIn = action * sm.SimulationManager.getCurrentSimulation().config.getInt(TLC_QLEARNING_ACTION_UNIT_LENGTH)
        self.resetActionStep = step

    def step(self, step):
        if (step - self.resetActionStep > self.nextStepIn and not self.isStageSwitchInProgress):
            self.trafficLight.advanceStage()
            self.isStageSwitchInProgress = True

        if (step - self.resetActionStep > self.nextStepIn + sm.SimulationManager.getCurrentSimulation().config.getInt(TL_STAGE_LOST_TIME)):
            super().step(step)
            self.isStageSwitchInProgress = False
