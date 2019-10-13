
from tl_controller import TrafficLightController as tlc
import time

class TrafficLightControllerFXM(tlc.TrafficLightController):

    """docstring for TrafficLightControllerFXM."""
    def __init__(self, trafficLight):
        super(TrafficLightControllerFXM, self).__init__(trafficLight)
        #self.lastPhase = 1
        #self.trafficLight.setPhase(self.lastPhase)
        self.lastPhaseStep = 0

    def step(self, step):
        if (step - self.lastPhaseStep) > 30:
            self.lastPhaseStep = step
            self.trafficLight.advancePhase()
            #self.lastPhase = (self.lastPhase + 1) % self.trafficLight.getPhaseNumber()
            #self.trafficLight.setPhase(self.lastPhase)
