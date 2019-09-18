
from TrafficLightController import TrafficLightController
import time

TLC_CYCLE_ADJUSTMENT_TIME_WEBSTER = 180
TLC_CYCLE_STARTUP_TIME_WEBSTER = 60
TL_TOTAL_LOST_TIME = (2 * 2) + 4 # (2s amber period * no. of stages) + all_red_time

class TrafficLightControllerWebsterLike(TrafficLightController):

    """docstring for TrafficLightControllerWebsterLike."""
    def __init__(self, trafficLight):
        super(TrafficLightControllerWebsterLike, self).__init__(trafficLight)

        self._initVariables()
        self._initBaseIndicators()
        '''
        print('Phase number: ', self.trafficLight.getPhaseNumber())
        i = 0
        for l in self.trafficLight.getCompleteRedYellowGreenDefinition():
            print('Logic: ', i)
            print(l)
            for p in l.getPhases():
                print(p)
            print(l.getParameters())
        '''
        
    def step(self, step):
        self._gatherLaneStats(step)

        if (step - self.lastCycleAdjustmentStep > TLC_CYCLE_ADJUSTMENT_TIME_WEBSTER):
            self._adjustCycle(step)

        if (step - self.startCycleStep) > self.cycleLength:
            self._startCycle(step)
        elif (step - self.startStageStep) > self.stageLengths[self.trafficLight.getCurrentStage()]:
            self._advanceStage(step)

    def _initVariables(self):
        self.startStageStep = 0
        self.startCycleStep = 0
        self.lastCycleAdjustmentStep = 0

        self.totalLostTime = TL_TOTAL_LOST_TIME
        self.stageLostTime = self.totalLostTime / len(self.trafficLight.getStages())
        self.vehicleFlow = {}
        self.vehicleNumber = {}
        self.vehicleFlow = {}
        self.queueLength = {}
        self.laneWidth = {}
        self.saturationFlow = {}
        self.flowFactor = {}
        self.stageFlowFactors = []
        self.cycleLength = TLC_CYCLE_STARTUP_TIME_WEBSTER
        self.stageLengths = []

    def _initBaseIndicators(self):
        for s in self.trafficLight.getStages():
            for sl in s.getSignalLanes():
                self.vehicleNumber[sl.lane.id] = 0
                self.queueLength[sl.lane.id] = 0
                laneWidth = sl.lane.getWidth()
                self.saturationFlow[sl.lane.id] = 525 * laneWidth
                print(f"Lane {sl.lane.id}: width {laneWidth}; saturation flow: {self.saturationFlow[sl.lane.id]}")
                self.laneWidth[sl.lane.id] = laneWidth
                self.vehicleFlow[sl.lane.id] = 0
            self.stageFlowFactors.append(0)
            self.stageLengths.append(self.cycleLength / len(self.trafficLight.getStages()))


    def _startCycle(self, step):
        self.startCycleStep = step
        self._advanceStage(step)

    def _advanceStage(self, step):
        self.startStageStep = step + self.stageLostTime
        self.trafficLight.advanceStage()

    def _gatherLaneStats(self, step):
        for s in self.trafficLight.getStages():
            for sl in s.getSignalLanes():
                self.vehicleNumber[sl.lane.id] += sl.lane.getVehicleDeltaNumber()
                self.queueLength[sl.lane.id] += sl.lane.getQueueLength()
                #print(f"Lane Stats {sl.lane.id}: delta {sl.lane.getVehicleDeltaNumber()} total {self.vehicleNumber[sl.lane.id]}")

    def _resetLaneStats(self):
        for s in self.trafficLight.getStages():
            for sl in s.getSignalLanes():
                self.vehicleNumber[sl.lane.id] = sl.lane.getVehicleNumber()
                self.queueLength[sl.lane.id] = sl.lane.getQueueLength()

    def _adjustCycle(self, step):
        elapsedTime = step - self.lastCycleAdjustmentStep

        totalFlowFactor = 0

        for i, s in enumerate(self.trafficLight.getStages()):
            stageFlowFactor = 0
            for sl in s.getSignalLanes():
                self.vehicleFlow[sl.lane.id] = self.vehicleNumber[sl.lane.id] * 3600 / elapsedTime
                self.flowFactor[sl.lane.id] = self.vehicleFlow[sl.lane.id] / self.saturationFlow[sl.lane.id]
                stageFlowFactor = max(stageFlowFactor, self.flowFactor[sl.lane.id])
                print(f"Lane {sl.lane.id}: Veh No: {self.vehicleNumber[sl.lane.id]}. Flow:  {self.vehicleFlow[sl.lane.id]}. Factor: {self.flowFactor[sl.lane.id]}")
            print(f"Stage {i} Flow Factor: {stageFlowFactor}")
            self.stageFlowFactors[i] = stageFlowFactor
            totalFlowFactor += stageFlowFactor

        meanFlowFactor = totalFlowFactor / len(self.trafficLight.getStages())

        eq1 = (1.5 * self.totalLostTime) + 5
        
        if totalFlowFactor >= 1:
            totalFlowFactor = 0.9
        eq2 = 1 - totalFlowFactor
        #eq2 = 1 - meanFlowFactor

        if (eq2 != 0):
            self.cycleLength = eq1 / eq2
        else:
            self.cycleLength = 30

        print(f"New Cycle Length: {self.cycleLength}")

        for i, s in enumerate(self.trafficLight.getStages()):
            self.stageLengths[i] = ((self.stageFlowFactors[i] * (self.cycleLength - TL_TOTAL_LOST_TIME)) / totalFlowFactor)
            print(f"Stage {i}: {self.stageLengths[i]}")

        self._resetLaneStats()
        self.lastCycleAdjustmentStep = step
