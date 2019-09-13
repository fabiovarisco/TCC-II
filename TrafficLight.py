
from traci import trafficlight as tTL
from Lane import Lane


class TrafficLight(object):

    """docstring for Junction."""
    def __init__(self, id, TrafficLightController):
        super(TrafficLight, self).__init__()
        self.id = id
        links = tTL.getControlledLinks(self.id)
        self.incoming = {}
        self.outgoing = {}
        phaseId = 0
        print(links)
        for phase in links:
            self.incoming[phaseId] = []
            self.outgoing[phaseId] = []
            # Incoming links
            print(phase)
            for l in phase:
                print(f"Incoming lane: {l[0]}")
                self.incoming[phaseId].append(Lane(l[0]))
                self.outgoing[phaseId].append(Lane(l[1]))
            #for l in directions[1]:
            #    self.outgoing[phaseId].append(Lane(l))

            if (len(self.incoming[phaseId]) == 0): raise Exception(f"No incoming lanes for phase {phaseId} in traffic light {self.id}")
            if (len(self.outgoing[phaseId]) == 0): raise Exception(f"No outgoing lanes for phase {phaseId} in traffic light {self.id}")

            phaseId += 1
        self.controller = TrafficLightController(self);


    def getId(self):
        return self.id

    def getPhaseNumber(self):
        return len(self.incoming)

    def getPhase(self):
        return tTL.getPhase(self.id)

    def setPhase(self, phaseIndex):
        tTL.setPhase(self.id, phaseIndex)

    def advancePhase(self):
        tTL.setPhase(self.id, tTL.getPhase(self.id) + 1)

    def getMaxPhaseLength(self, phaseId):
        lanes = self.incoming[phaseId]
        max = 0
        for l in lanes:
            laneQueueLength = l.getQueueLength()
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
