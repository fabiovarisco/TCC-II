
from TrafficLightController import TrafficLightController
import time

class TrafficLightControllerWebsterLike(TrafficLightController):



    """docstring for TrafficLightControllerWebsterLike."""
    def __init__(self, trafficLight):
        super(TrafficLightControllerWebsterLike, self).__init__(trafficLight)
        #self.lastPhase = 1
        #self.trafficLight.setPhase(self.lastPhase)
        self.startPhaseStep = 0
        self.startCycleStep = 0
        self.vehicleFlow = {}
        self.queueLength = {}
        for p in range(0, self.trafficLight.getPhaseNumber()):
            for l in self.trafficLight.incoming[p]:
                self.vehicleFlow[l.id] = 0
                self.queueLength[l.id] = 0
        self.cycleLength = 30

    def step(self, step):
        if (step - self.startCycleStep) > self.cycleLength:
            self._startCycle(step)
        if (step - self.startPhaseStep) > 15:
            self.startPhaseStep = step
            self.trafficLight.advancePhase()
            #self.lastPhase = (self.lastPhase + 1) % self.trafficLight.getPhaseNumber()
            #self.trafficLight.setPhase(self.lastPhase)

    def _gatherLaneStats(self, step):
        for p in range(0, self.trafficLight.getPhaseNumber()):
            for l in self.trafficLight.incoming[p]:
                self.vehicleFlow[l.id] += l.getVehicleDeltaNumber()
                self.queueLength[l.id] += l.getQueueLength()

    def _startCycle(self, step):

        elapsedTime = step - self.startCycleStep

        eq1 = (1.5 * sum(self.queueLength.values())) + 5
        eq2 = 1 - (sum(self.vehicleFlow.values()) / elapsedTime)

        self.cycleLength = eq1 / eq2
        self.startCycleStep = step
        print(f"New Cycle Length: {self.cycleLength}")
