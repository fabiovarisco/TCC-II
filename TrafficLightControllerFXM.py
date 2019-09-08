
from TrafficLightController import TrafficLightController
import time

class TrafficLightControllerFXM(TrafficLightController):



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
