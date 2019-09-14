
from TrafficLightController import TrafficLightController
import time

class TrafficLightControllerWebsterLike(TrafficLightController):

    """docstring for TrafficLightControllerWebsterLike."""
    def __init__(self, trafficLight):
        super(TrafficLightControllerWebsterLike, self).__init__(trafficLight)
        
        self.startPhaseStep = 0
        self.startCycleStep = 0
        
        self.totalLostTime = (4 * 2) + 4 # (4s * no. of stages) + all_red_time

        self.vehicleFlow = {}
        self.vehicleNumber = {}
        self.vehicleFlow = {}
        self.queueLength = {}
        self.laneWidth = {}
        self.saturationFlow = {}
        self.flowFactor = {}
        self.phaseFlowFactors = []
        print('Phase number: ', self.trafficLight.getPhaseNumber())
        for p in range(0, self.trafficLight.getPhaseNumber()):
            for l in self.trafficLight.incoming[p]:
                self.lanewidth = l.getLaneWidth()
                self.vehicleNumber[l.id] = 0
                self.queueLength[l.id] = 0
                laneWidth = l.getLaneWidth()
                self.saturationFlow[l.id] = 525 * laneWidth
                self.laneWidth[l.id] = laneWidth
                self.vehicleFlow[l.id] = 0
        self.cycleLength = 30
        self.phaseLengths = []


    def step(self, step):

        self._gatherLaneStats(step)

        if (step - self.startCycleStep) > self.cycleLength:
            self._startCycle(step)
        elif (step - self.startPhaseStep) > self.phaseLengths[self.currentPhase]:
            self.startPhaseStep = step
            self.trafficLight.advancePhase()
            self.currentPhase += 1

    def _gatherLaneStats(self, step):
        for p in range(0, self.trafficLight.getPhaseNumber()):
            for l in self.trafficLight.incoming[p]:
                self.vehicleNumber[l.id] += l.getVehicleDeltaNumber()
                self.queueLength[l.id] += l.getQueueLength()

    def _startCycle(self, step):

        elapsedTime = step - self.startCycleStep

        totalFlowFactor = 0
        for p in range(0, self.trafficLight.getPhaseNumber()):
            phaseFlowFactor = 0
            for l in self.trafficLight.incoming[p]:
                self.vehicleFlow[l.id] = self.vehicleNumber[l.id] * 3600 / elapsedTime
                self.flowFactor[l.id] = self.vehicleFlow[l.id] - self.saturationFlow[l.id]
                phaseFlowFactor = max(phaseFlowFactor, self.flowFactor[l.id])
            self.phaseFlowFactors[p] = phaseFlowFactor
            totalFlowFactor += phaseFlowFactor
        
        eq1 = (1.5 * self.totalLostTime) + 5
        eq2 = 1 - totalFlowFactor

        if (eq2 != 0):
            self.cycleLength = eq1 / eq2
        else:
            self.cycleLength = 30

        for p in range(0, self.trafficLight.getPhaseNumber()):
            self.phaseLengths[p] = (self.phaseFlowFactors[p] * (self.cycleLength - self.totalLostTime)) / totalFlowFactor

        self.startCycleStep = step
        self.currentPhase = 0
        self.trafficLight.advancePhase()
        self.startPhaseStep = step
        print(f"New Cycle Length: {self.cycleLength}")
