
from tl_controller import TrafficLightController as tlc
import time
from SimulationConfig import SimulationConfig, TL_STAGE_GREEN_TIME
import SimulationManager as sm

class TrafficLightControllerFXM(tlc.TrafficLightController):

    """docstring for TrafficLightControllerFXM."""
    def __init__(self, trafficLight):
        super(TrafficLightControllerFXM, self).__init__(trafficLight)
        self.lastPhaseStep = 0
        self.nextStepIn = sm.SimulationManager.getCurrentSimulation().config.getInt(TL_STAGE_GREEN_TIME)

    def step(self, step):
        if (step - self.lastPhaseStep) > self.nextStepIn:
            self.lastPhaseStep = step
            self.trafficLight.advanceStage()
