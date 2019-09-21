
from traci import trafficlight as tTL
from Lane import Lane, LaneFactory
from Stage import Stage

from TrafficLightStatic import TrafficLightStatic
from TrafficLightControllerFXM import TrafficLightControllerFXM
from TrafficLightControllerWebsterLike import TrafficLightControllerWebsterLike

class TrafficLight(object):

    
    """docstring for Junction."""
    def __init__(self, id, TrafficLightController):
        super(TrafficLight, self).__init__()
        self.id = id
        
        self._initVariables()
        self._initLinks()
        self._initStages()

        self.controller = TrafficLightController(self);

    def _initVariables(self):
        self.incoming = []
        self.outgoing = []
        self.currentStage = 0
    
    def _initLinks(self):
        links = tTL.getControlledLinks(self.id)
        phaseId = 0
        print(links)
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

        for l in self.incoming:
            print(f"Lane: {l.id}")

        self.stages = Stage.resolveStages(self.logic.getPhases(), self.incoming, self.outgoing)
        for i, s in enumerate(self.stages):
            print(f"Stage {i}")
            for sl in s.getSignalLanes():
                print(f"Lane {sl.lane.id}")

    def getId(self):
        return self.id

    def getPhaseNumber(self):
        return self.phaseNumber

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
        tTL.setPhase(self.id, (tTL.getPhase(self.id) + 1) % self.getPhaseNumber())

    def advanceStage(self):
        self.currentStage = (self.currentStage + 1) % len(self.stages)
        self._advancePhase()

    def getMaxPhaseLength(self, phaseId):
        lanes = self.incoming[phaseId]
        maxLength = 0
        for l in lanes:
            maxLength = max(maxLength, l.getQueueLength())
        return maxLength

    def getMaxStageLength(self, stageIndex):
        maxLength = 0
        for sl in self.stages[stageIndex].getSignalLanes():
            maxLength = max(maxLength, sl.lane.getQueueLength())
        return maxLength

    def getMaxLength(self):
        maxLength = 0
        for i in range(0, len(self.stages)):
            maxLength = max(maxLength, self.getMaxStageLength(i))
        return maxLength

    def step(self, step):
        for l in self.incoming:
            l.step(step)
        self.controller.step(step)

    def getCompleteRedYellowGreenDefinition(self):
        return tTL.getCompleteRedYellowGreenDefinition(self.id)



class TrafficLightFactory(object): 

    """docstring for Junction."""
    def __init__(self):
        super(TrafficLightFactory, self).__init__()

    @staticmethod
    def createTrafficLightWebsterLike(id):
        return TrafficLight(id, TrafficLightControllerWebsterLike)

    @staticmethod
    def createTrafficLightFXM(id):
        return TrafficLight(id, TrafficLightControllerFXM)

    @staticmethod
    def createTrafficLightStatic(id, programId):
        tl = TrafficLight(id, TrafficLightStatic)
        tl.controller.setProgram(programId)
        return tl