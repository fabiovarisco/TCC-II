import re

class Stage(object):

    """Represents a link of a road"""
    def __init__(self, definition, phaseIndex):
        super(Stage, self).__init__()
        self.definition = definition
        self.phaseIndex = phaseIndex
        self.signalLanes = []

    def addSignalLane(self, signalIndex, incoming, outgoing):
        self.signalLanes.append(SignalLane(signalIndex, incoming, outgoing))

    def getDefinition(self):
        return self.definition

    def getSignalLanes(self):
        return self.signalLanes

    def getPhaseIndex(self):
        return self.phaseIndex

    def getMaxLaneLength(self):
        maxLength = 0
        for sl in self.getSignalLanes():
            qL = sl.incoming.getQueueLength()
            print(f"Lane: {sl.incoming.id}; Queue Length: {qL}.")
            maxLength = max(maxLength, qL)
        return maxLength

    def getMaxVehicleNumber(self):
        maxNumber = 0
        for sl in self.getSignalLanes():
            vehNumber = sl.incoming.getVehicleNumber()
            print(f"Lane: {sl.incoming.id}; Vehicle Number: {vehNumber}.")
            maxNumber = max(maxNumber, vehNumber)
        return maxNumber

    @staticmethod
    def resolveStages(phases, incomingLanes, outgoingLanes):
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
                    s.addSignalLane(m.start(), incomingLanes[m.start()], outgoingLanes[m.start()])
                    print(f"Signal Lane: {m.start()}")
                stages.append(s)
            i += 1
        return stages

class SignalLane(object):

    """Represents a link of a road"""
    def __init__(self, signalIndex, incoming, outgoing):
        super(SignalLane, self).__init__()
        self.signalIndex = signalIndex
        self.incoming = incoming
        self.outgoing = outgoing
