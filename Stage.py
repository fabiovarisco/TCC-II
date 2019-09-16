

class Stage(object):

    signalLanes = []

    """Represents a link of a road"""
    def __init__(self, definition, phaseIndex):
        super(Lane, self).__init__()
        self.definition = definition
        self.phaseIndex = phaseIndex

    def addSignalLane(self, signalIndex, lane):
        self.signalLanes.append(SignalLane(signalIndex, lane))


    def getDefinition(self):
        return self.definition

    def getSignalLanes(self):
        return self.signalLanes

    def getPhaseIndex(self):
        return self.phaseIndex

    @staticmethod
    def resolveStages(phases):
        stages = []
        i = 0
        for phase in phases:
            # Stage definition example: GrGr
            matches = re.findall('G', phase.stage)
            # If the Phase contains a green stage, keep track of Lanes composing the stage
            if (matches):
                # Create a stage with the lanes that are Green for this stage
                s = Stage(phase.stage, i)
                for m in matches:
                    s.addSignalLane(m.start(), self.incoming(m.start()))
                stages.append(s)
            i += 1
        return stages

class SignalLane(object):

    """Represents a link of a road"""
    def __init__(self, signalIndex, lane):
        super(SignalLane, self).__init__()
        self.signalIndex = signalIndex
        self.lane = lane
