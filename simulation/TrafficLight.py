
from traci import trafficlight as tTL
from simulation.Lane import Lane, LaneFactory
from simulation.Stage import Stage
from simulation.event_constants import EVENT_STAGE_CHANGE

import SimulationManager as sm

class TrafficLight(object):

    """docstring for Junction."""
    def __init__(self, id):
        super(TrafficLight, self).__init__()
        self.id = id

        self._initVariables()
        self._initLinks()
        self._initStages()
        
        #self.controller = TrafficLightController(self)
    
    def setController(self, controller):
        self.controller = controller

    def _initVariables(self):
        self.incoming = []
        self.outgoing = []
        self.currentStage = 0
        self.cumulativeDelay = 0

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
        self.currentStage = self.getNextStage()
        self._advancePhase()
        sm.SimulationManager.getCurrentSimulation().notify(EVENT_STAGE_CHANGE, self)

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
        self.cumulativeDelay += self.getTotalDelayAtCurrentTimeStep()
        self.controller.step(step)

    def getCompleteRedYellowGreenDefinition(self):
        return tTL.getCompleteRedYellowGreenDefinition(self.id)

    def getTotalCumulativeDelay(self):
        return self.cumulativeDelay

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
