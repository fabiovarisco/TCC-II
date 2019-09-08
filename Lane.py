from traci import lane as tLane

class Lane(object):

    """Represents a link of a road"""
    def __init__(self, id):
        super(Lane, self).__init__()
        self.id = id
        #self.detectorid = detectorid

    def getQueueLength(self):
        return tLane.getLastStepHaltingNumber(self.id)

    def getMaxSpeed(self):
        return tLane.getMaxSpeed(self.id)

    def getWaitingTime(self):
        return tLane.getWaitingTime(self.id)

    def getLastStepOccupancy(self):
        return tLane.getLastStepOccupancy(self.id)
