import re

class Stage(object):

    """Represents a link of a road"""
    def __init__(self, definition, phaseIndex):
        super(Stage, self).__init__()
        self.definition = definition
        self.phaseIndex = phaseIndex
        self.signalLanes = []

    def addSignalLane(self, signalIndex, lane):
        self.signalLanes.append(SignalLane(signalIndex, lane))

    def getDefinition(self):
        return self.definition

    def getSignalLanes(self):
        return self.signalLanes

    def getPhaseIndex(self):
        return self.phaseIndex

    @staticmethod
    def resolveStages(phases, incomingLanes):
        stages = []
        i = 0
        for phase in phases:
            # Stage definition example: GrGr
            # If the Phase contains a green stage, keep track of Lanes composing the stage
            # Create a stage with the lanes that are Green for this stage
            if (re.search('G', phase.state)):
                s = Stage(phase.state, i)
                print(f"Stage {i}: {phase.state}. Dur: {phase.duration}")
                matches = re.finditer('G', phase.state)
                for m in matches:
                    s.addSignalLane(m.start(), incomingLanes[m.start()])
                    print(f"Signal Lane: {m.start()}")
                stages.append(s)
            i += 1
        return stages

class SignalLane(object):

    """Represents a link of a road"""
    def __init__(self, signalIndex, lane):
        super(SignalLane, self).__init__()
        self.signalIndex = signalIndex
        self.lane = lane
