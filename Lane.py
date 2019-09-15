from traci import lane as tLane
import numpy as np

class Lane(object):

    """Represents a link of a road"""
    def __init__(self, id):
        super(Lane, self).__init__()
        self.id = id
        self.previousStepVehicleIDs = []
        #self.detectorid = detectorid

    def getQueueLength(self):
        return tLane.getLastStepHaltingNumber(self.id)

    def getMaxSpeed(self):
        return tLane.getMaxSpeed(self.id)

    def getWaitingTime(self):
        return tLane.getWaitingTime(self.id)

    def getLastStepOccupancy(self):
        return tLane.getLastStepOccupancy(self.id)

    def getLastStepVehicleIDs(self):
        return tLane.getLastStepVehicleIDs(self.id)

    def getVehicleDeltaNumber(self):
        return self.deltaNumber

    def step(self, step):
        newVehicleIDs = self.getLastStepVehicleIDs()
        self.deltaNumber = np.sum(np.isin(newVehicleIDs, self.previousStepVehicleIDs))
        self.previousStepVehicleIDs = newVehicleIDs

    def getWidth(self):
        return tLane.getWidth(self.id)

    