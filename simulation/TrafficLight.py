
from traci import trafficlight as tTL
from simulation.Lane import Lane, LaneFactory
from simulation.Stage import Stage
from simulation.event_constants import EVENT_STAGE_CHANGE, EVENT_CYCLE_TIME

from SimulationConfig import *
import SimulationManager as sm

class TrafficLight(object):

    """docstring for Junction."""
    def __init__(self, id):
        super(TrafficLight, self).__init__()
        self.id = id
        
        self._initLinks()
        self._initStages()
        self._initVariables()

    def setController(self, controller):
        self.controller = controller

    def _initVariables(self):
        self.incoming = []
        self.outgoing = []
        self.currentStage = 0
        self.lastActiveStage = 0
        self.nextStageStartsAt = -1
        self.cumulativeDelay = 0
        self.vehicleCumulativeDelay = {}
        self.currentStageCumulativeDelay = 0
        self.arrivingVehiclesDuringLastStage = {}
        self.approachingVehiclesAtLastStageStart = {}
        self.vehicleNumberAtLastStageStart = {}
        for l in self.incoming:
            self.arrivingVehiclesDuringLastStage[l.id] = 0
            self.approachingVehiclesAtLastStageStart[l.id] = 0
            self.vehicleNumberAtLastStageStart[l.id] = 0

        self.stageTimes = [0 for i in range(0, self.stages)]
        self.lastStageTimes = self.stageTimes
        self.__stageLostTime = sm.SimulationManager.getCurrentSimulation().config.getInt(TL_STAGE_LOST_TIME)
        self.queueClearsAtStepForLane = {}
        self.lastCycleBeginAt = 0

    def _initLinks(self):
        links = tTL.getControlledLinks(self.id)
        phaseId = 0
        #print(links)
        for phase in links:
            for l in phase:
                self.incoming.append(LaneFactory.getLane(l[0]))
                self.outgoing.append(LaneFactory.getLane(l[1]))
            phaseId += 1

        if (len(self.incoming) == 0): raise Exception(f"No incoming lanes for phase {phaseId} in traffic light {self.id}")
        if (len(self.outgoing) == 0): raise Exception(f"No outgoing lanes for phase {phaseId} in traffic light {self.id}")

    def _initStages(self):
        logics = [l for l in self.getCompleteRedYellowGreenDefinition() if l.getSubID() == self.getProgramId()]
        if (len(logics) == 0): raise Exception(f"Not able to find program ID {self.getProgramId()}")
        self.logic = logics[0]

        self.phaseNumber = len(self.logic.getPhases())

        self.stages = Stage.resolveStages(self.logic.getPhases(), self.incoming, self.outgoing)

    def getId(self):
        return self.id

    def getPhaseNumber(self):
        return self.phaseNumber

    def getCurrentStage(self):
        return self.currentStage

    def getPreviousStage(self):
        return self.lastActiveStage

    def getNextStage(self):
        return (self.currentStage + 1) % len(self.stages)

    def getProgramId(self):
        return tTL.getProgram(self.id)

    def getPhase(self):
        return tTL.getPhase(self.id)

    def getStages(self):
        return self.stages

    def _setPhase(self, phaseIndex):
        tTL.setPhase(self.id, phaseIndex)

    def setPhaseByStage(self, stageIndex):
        tTL.setPhase(self.id, self.stages[stageIndex].getPhaseIndex())

    def _advancePhase(self):
        tTL.setPhase(self.id, (tTL.getPhase(self.id) + 1) % self.getPhaseNumber())

    def advanceStage(self):
        self.lastActiveStage = self.currentStage
        self.stageTimes[self.lastActiveStage] = sm.SimulationManager.getCurrentSimulationStep() - self.nextStageStartsAt
        
        wastedTime = -1
        residualQueue = -1
        if (len(self.queueClearsAtStepForLane) == len(self.stages[self.lastActiveStage].getSignalLanes())):
            queueClearsAt = max(self.queueClearsAtStepForLane.values())
            wastedTime = sm.SimulationManager.getCurrentSimulationStep() - queueClearsAt
        else:
            for sl in self.stages[self.lastActiveStage]:
                l_residual_queue = sl.incoming.getQueueLengthAtBeginningOfStage() - sl.incoming.getVehicleThroughput()
                residualQueue = max(residualQueue, l_residual_queue)

        self.nextStageStartsAt = (sm.SimulationManager.getCurrentSimulationStep() + self.__stageLostTime)
        self.notifyStageChange(tl_id = self.id,
                                start_at_step = self.nextStageStartsAt,
                                stage = self.lastActiveStage,
                                stage_time = self.stageTimes[self.lastActiveStage],
                                time_beyond_queue_clearance = wastedTime,
                                residual_queue = residualQueue)

        self.currentStage = self.getNextStage()

        if (self.currentStage == 0):
            self.lastCycleTime = 0
            for t in self.stageTimes:
                self.lastCycleTime += t
            self.lastCycleTime += self.__stageLostTime * len(self.stages)
            self.lastStageTimes = self.stageTimes 
            self.stageTimes = [0 for i in range(len(self.stages))]
            self.notifyCycleTime(tl_id = self.id,
                                start_at_step = self.nextStageStartsAt - self.lastCycleTime,
                                cycle_time = self.lastCycleTime)
            
            self.lastCycleBeginAt = self.nextStageStartsAt

        
        self._advancePhase()
        self.currentStageCumulativeDelay = 0
        self.notifyStageChange(traffic_light = self)
        sm.SimulationManager.getCurrentSimulation().notify(EVENT_STAGE_CHANGE, )

    def notifyStageChange(self, **kwargs):
        sm.SimulationManager.getCurrentSimulation().notify(EVENT_STAGE_CHANGE, **kwargs)

    def notifyCycleTime(self, **kwargs):
        sm.SimulationManager.getCurrentSimulation().notify(EVENT_CYCLE_TIME, **kwargs)

    def setStage(self, stageIndex):
        if (stageIndex >= len(self.stages)): raise Exception(f"Invalid Stage Index: {stageIndex}. Traffic light {self.id} has {len(self.stages)}.")

        self.advanceStage()

    def getMaxPhaseLength(self, phaseId):
        lanes = self.incoming[phaseId]
        maxLength = 0
        for l in lanes:
            maxLength = max(maxLength, l.getQueueLength())
        return maxLength

    def getMaxStageLength(self, stageIndex):
        maxLength = 0
        for sl in self.stages[stageIndex].getSignalLanes():
            maxLength = max(maxLength, sl.incoming.getQueueLength())
        return maxLength

    def getMaxLength(self):
        maxLength = 0
        for i in range(0, len(self.stages)):
            maxLength = max(maxLength, self.getMaxStageLength(i))
        return maxLength

    def getQueueLengthAllLanes(self):
        queueLengths = []
        for stage in self.stages:
            for sl in stage.getSignalLanes():
                queueLengths.append({"lane_id": sl.incoming.id, "queue_length": sl.incoming.getQueueLength()})
        return queueLengths

    def step(self, step):
        for l in self.incoming:
            l.step(step)

        delayAtCurrentStep = self.getTotalDelayAtCurrentTimeStep()
        self.cumulativeDelay += delayAtCurrentStep
        self.currentStageCumulativeDelay += delayAtCurrentStep
        
        for sl in self.stages[self.currentStage]:
            if sl.incoming.getVehicleThroughput() >= sl.incoming.getQueueLengthAtBeginningOfStage():
                self.queueClearsAtStepForLane[sl.incoming.id] = step

        if (step == self.nextStageStartsAt):
            self.calculateVehicleIndicatorsForLastStage()
            self.getVehicleIndicatorsAtStageStart()
            self.resetArrivingVehiclesIndicator()

        self.gatherArrivingVehiclesIndicator()

        self.controller.step(step)

        if (step == self.nextStageStartsAt):
            for sl in self.stages[self.currentStage]:
                sl.incoming.startActiveStage()

    def getCumulativeVehicleDelay(self):
        delay = 0 
        for l in self.incoming:
            delay += l.getCumulativeVehicleDelay()
        return delay

    def getTotalNumberOfStops(self):
        numberOfStops = 0
        for l in self.incoming:
            numberOfStops += l.getNumberOfStops()
        return numberOfStops

    def getCompleteRedYellowGreenDefinition(self):
        return tTL.getCompleteRedYellowGreenDefinition(self.id)

    def getTotalCumulativeDelay(self):
        return self.cumulativeDelay
    
    def getCurrentStageCumulativeDelay(self):
        return self.currentStageCumulativeDelay

    def getTotalDelayAtCurrentTimeStep(self):
        totalQueueLength = 0
        for l in self.incoming:
            totalQueueLength += l.getQueueLength()
        return totalQueueLength

    def getTotalWaitingTime(self):
        totalWaitingTime = 0
        for l in self.incoming:
            totalWaitingTime += l.getWaitingTime()
        return totalWaitingTime

    def getMaxLaneccupancy(self):
        maxOccupancy = 0
        for s in self.stages:
            for sl in s.getSignalLanes():
                maxOccupancy = max(maxOccupancy, sl.incoming.getLastStepOccupancy())
        return maxOccupancy

    def resetArrivingVehiclesIndicator(self):
        for l in self.incoming:
            self.arrivingVehiclesDuringLastStage[l.id] = 0 

    def gatherArrivingVehiclesIndicator(self):
        for l in self.incoming:
            self.arrivingVehiclesDuringLastStage[l.id] += l.getVehicleDeltaNumber()

    def getVehicleIndicatorsAtStageStart(self):
        for l in self.incoming:
            self.approachingVehiclesAtLastStageStart[l.id] = l.getVehicleNumber() - l.getQueueLength()
            self.vehicleNumberAtLastStageStart[l.id] = l.getVehicleNumber()

    def calculateVehicleIndicatorsForLastStage(self):
        veh_not_dispatched_max = 0
        veh_not_dispatched_total = 0
        veh_throughput_max = 0
        veh_throughput_total = 0
        for sl in self.stages[self.lastActiveStage].getSignalLanes():
            l_veh_not_dispatched = TrafficLight.calculateVehiclesNotDispatched(
                sl.incoming.getVehicleNumber(),
                self.approachingVehiclesAtLastStageStart[sl.incoming.id],
                self.arrivingVehiclesDuringLastStage[sl.incoming.id] 
            )
            veh_not_dispatched_max = max(veh_not_dispatched_max, l_veh_not_dispatched)
            veh_not_dispatched_total += l_veh_not_dispatched
            l_vehicle_throughput = TrafficLight.calculateActualThroughput(
                self.vehicleNumberAtLastStageStart[sl.incoming.id],
                l_veh_not_dispatched,
                self.approachingVehiclesAtLastStageStart[sl.incoming.id]
            )
            veh_throughput_max = max(veh_throughput_max, l_vehicle_throughput)
            veh_throughput_total += l_vehicle_throughput

        self.vehicles_not_dispatched_max = veh_not_dispatched_max
        self.vehicles_not_dispatched_total = veh_not_dispatched_total
        self.vehicles_throughput_max = veh_throughput_max
        self.vehicles_throughput_total = veh_throughput_total

    def getMaxAcceptableQueueLengthForStage(self, stage_index):
        acceptable_queue_length = 0
        for sl in self.controller.trafficLight.stages[stage_index].getSignalLanes:
            acceptable_queue_length += l.getMaxAcceptableQueueLength()
        return acceptable_queue_length
        
    @staticmethod
    def calculateVehiclesNotDispatched(veh_number_now, approaching_at_stage_start, arriving_current_stage):
        return veh_number_now - approaching_at_stage_start - arriving_current_stage

    @staticmethod
    def calculateActualThroughput(veh_number_previous, vehicles_not_dispatched, approaching_at_stage_start):
        return veh_number_previous - vehicles_not_dispatched - approaching_at_stage_start
