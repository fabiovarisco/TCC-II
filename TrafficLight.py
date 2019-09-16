
import re

from traci import trafficlight as tTL
from Lane import Lane
from Stage import Stage

class TrafficLight(object):

    incoming = []
    outgoing = []
    currentStage = 0

    """docstring for Junction."""
    def __init__(self, id, TrafficLightController):
        super(TrafficLight, self).__init__()
        self.id = id

        self._initLinks()

        self._initStages()

        self.controller = TrafficLightController(self);

    def _initLinks(self):
        links = tTL.getControlledLinks(self.id)
        phaseId = 0
        print(links)
        for phase in links:
            for l in phase:
                self.incoming.append(Lane(l[0]))
                self.outgoing.append(Lane(l[1]))
            phaseId += 1

        if (len(self.incoming) == 0): raise Exception(f"No incoming lanes for phase {phaseId} in traffic light {self.id}")
        if (len(self.outgoing) == 0): raise Exception(f"No outgoing lanes for phase {phaseId} in traffic light {self.id}")

    def _initStages(self):
        logics = [l if l.getSubId() == self.getProgramId() for l in self.getCompleteRedYellowGreenDefinition()]
        if (len(logics) == 0): raise Exception(f"Not able to find program ID {self.getProgramId()}")
        self.logic = logics[0]

        self.stages = Stage.resolveStages(self.logic.getPhases())

    def getId(self):
        return self.id

    def getPhaseNumber(self):
        return len(self.incoming)

    def getCurrentStage(self):
        return self.currentStage

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
        tTL.setPhase(self.id, tTL.getPhase(self.id) + 1)

    def advanceStage(self):
        self.currentStage = (self.currentStage + 1) % len(self.stages)
        self._advancePhase(self)

    def getMaxPhaseLength(self, phaseId):
        lanes = self.incoming[phaseId]
        max = 0
        for l in lanes:
            laneQueueLength = l.getQueueLength()
            if (laneQueueLength > max):
                max = laneQueueLength
        return max

    def getMaxStageLength(self, stageIndex):
        max = 0
        for sl in self.stages[stageIndex].getSignalLanes():
            laneQueueLength = sl.lane.getQueueLength()
            if (laneQueueLength > max):
                max = laneQueueLength
        return max

    def getMaxLength(self):
        max = 0
        for p in self.incoming.keys():
            pMax = self.getMaxPhaseLength(p)
            if (pMax > max):
                max = pMax
        return max

    def step(self, step):
        for lanes in self.incoming.values():
            for l in lanes:
                l.step(step)
        self.controller.step(step)

    def getCompleteRedYellowGreenDefinition(self):
        return tTL.getCompleteRedYellowGreenDefinition(self.id)
