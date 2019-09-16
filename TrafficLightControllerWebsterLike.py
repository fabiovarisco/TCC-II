sl.lane.sl.lane.
from TrafficLightController import TrafficLightController
import time

TLC_CYCLE_ADJUSTMENT_TIME_WEBSTER = 1000
TLC_CYCLE_STARTUP_TIME_WEBSTER = 30
TL_TOTAL_LOST_TIME = (4 * 2) + 4 # (4s * no. of stages) + all_red_time

class TrafficLightControllerWebsterLike(TrafficLightController):

    startStageStep = 0
    startCycleStep = 0
    lastCycleAdjustmentStep = 0

    totalLostTime = TL_TOTAL_LOST_TIME

    vehicleFlow = {}
    vehicleNumber = {}
    vehicleFlow = {}
    queueLength = {}
    laneWidth = {}
    saturationFlow = {}
    flowFactor = {}
    stageFlowFactors = []
    cycleLength = TLC_CYCLE_STARTUP_TIME_WEBSTER
    stageLengths = []
    # currentPhase = 0 #to_be_deleted

    """docstring for TrafficLightControllerWebsterLike."""
    def __init__(self, trafficLight):
        super(TrafficLightControllerWebsterLike, self).__init__(trafficLight)

        print('Phase number: ', self.trafficLight.getPhaseNumber())
        i = 0
        for l in self.trafficLight.getCompleteRedYellowGreenDefinition():
            print('Logic: ', i)
            print(l)
            for p in l.getPhases():
                print(p)
            print(l.getParameters())
        self._initBaseIndicators()

    def step(self, step):
        self._gatherLaneStats(step)

        if (step - self.lastCycleAdjustmentStep > TLC_CYCLE_ADJUSTMENT_TIME_WEBSTER):
            self._adjustCycle(step)

        if (step - self.startCycleStep) > self.cycleLength:
            self._startCycle(step)
        elif (step - self.startStageStep) > self.stageLengths[self.trafficLight.getCurrentStage()]:
            self._advanceStage(step)

    def _initBaseIndicators(self):
        for s in self.trafficLight.getStages():
            for sl in s.getSignalLanes():
                self.vehicleNumber[sl.lane.id] = 0
                self.queueLength[sl.lane.id] = 0
                laneWidth = sl.lane.getWidth()
                self.saturationFlow[sl.lane.id] = 525 * laneWidth
                self.laneWidth[sl.lane.id] = laneWidth
                self.vehicleFlow[sl.lane.id] = 0
            self.stageLengths.append(self.cycleLength / len(self.trafficLight.getStages()))


    def _startCycle(self, step):
        self.startCycleStep = step
        self._advanceStage()

    def _advanceStage(self, step):
        self.startStageStep = step
        self.trafficLight.advanceStage()

    def _gatherLaneStats(self, step):
        for s in self.trafficLight.getStages():
            for sl in s.getSignalLanes():
                self.vehicleNumber[sl.lane.id] += sl.lane.getVehicleDeltaNumber()
                self.queueLength[sl.lane.id] += sl.lane.getQueueLength()

    def _adjustCycle(self, step):
        elapsedTime = step - self.lastCycleAdjustmentStep

        totalFlowFactor = 0

        for s in self.trafficLight.getStages():
            stageFlowFactor = 0
            for sl in s.getSignalLanes():
                self.vehicleFlow[sl.lane.id] = self.vehicleNumber[sl.lane.id] * 3600 / elapsedTime
                self.flowFactor[sl.lane.id] = self.vehicleFlow[sl.lane.id] - self.saturationFlow[sl.lane.id]
                stageFlowFactor = max(stageFlowFactor, self.flowFactor[sl.lane.id])
            self.stageFlowFactors[s.getPhaseIndex()] = stageFlowFactor
            totalFlowFactor += stageFlowFactor

        eq1 = (1.5 * self.totalLostTime) + 5
        eq2 = 1 - totalFlowFactor

        if (eq2 != 0):
            self.cycleLength = eq1 / eq2
        else:
            self.cycleLength = 30

        for s in self.trafficLight.getStages():
            self.stageLengths[s.getPhaseIndex()] = (self.stageFlowFactors[p] * (self.cycleLength - TL_TOTAL_LOST_TIME)) / totalFlowFactor

        self.lastCycleAdjustmentStep = step
        print(f"New Cycle Length: {self.cycleLength}")
        for s in self.trafficLight.getStages():
            print(f"Stage {s.getPhaseIndex()}: {self.stageLengths[s.getPhaseIndex()]}")
