from traci import lane as tLane
import SimulationManager as sm #import SimulationManager as simulationMgr
from simulation.Vehicle import VehicleFactory
import numpy as np
from SimulationConfig import VEHICLE_AVG_LENGTH, LANE_MAX_ACCEPTABLE_QUEUE_OCCUPANCY
import SimulationManager as sm

class Lane(object):

    """Represents a link of a road"""
    def __init__(self, id):
        super(Lane, self).__init__()
        self.id = id
        self.previousStepVehicleIDs = []
        self.queueLength = 0
        self.queueLengthStep = 0
        self.cumulativeVehicleDelay = {}
        self.vehicleNumberOfStops = {}
        self.vehicleLastSpeed = {}
        self.vehicleThroughput = 0
        self.queueLengthAtBeginningOfStage = 0

    def getQueueLength(self):
        if (self.queueLengthStep != sm.SimulationManager.getCurrentSimulationStep()):
            self.calculateLaneVehicleIndicators(sm.SimulationManager.getCurrentSimulationStep())
        return self.queueLength

    def getLastStepHaltingNumber(self):
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

    def getVehicleNumber(self):
        return tLane.getLastStepVehicleNumber(self.id)

    def startActiveStage(self):
        self.vehicleNumberAtBeginningOfStage = self.getVehicleNumber()
        self.queueLengthAtBeginningOfStage = self.getQueueLength()
        self.vehicleThroughput = 0

    def getVehicleNumberAtBeginningOfStage(self):
        return self.vehicleNumberAtBeginningOfStage

    def getQueueLengthAtBeginningOfStage(self):
        return self.queueLengthAtBeginningOfStage

    def getVehicleThroughput(self):
        return self.vehicleThroughput

    def step(self, step):
        newVehicleIDs = self.getLastStepVehicleIDs()
        self.deltaNumber = np.sum(~np.isin(newVehicleIDs, self.previousStepVehicleIDs))
        self.vehicleThroughput += np.sum(~np.isin(self.previousStepVehicleIDs, newVehicleIDs))
        self.previousStepVehicleIDs = newVehicleIDs

        self.calculateLaneVehicleIndicators(step)
        '''
        if (self.id == '2i_0'):
            print(newVehicleIDs)
            print(self.previousStepVehicleIDs)
            print(~np.isin(newVehicleIDs, self.previousStepVehicleIDs))
            print(self.deltaNumber)
            '''

    def calculateLaneVehicleIndicators(self, step):
        length = 0
        cumulativeVehicleDelay = {}
        vehicleNumberOfStops = {}
        vehicleLastSpeed = {}
        for id in self.getLastStepVehicleIDs():
            vehSpeed = VehicleFactory.getVehicleSpeed(id)
            if (vehSpeed < 2):
                length += 1
                cumulativeVehicleDelay[id] = self.cumulativeVehicleDelay.get(id, 0) + 1
                if (self.vehicleLastSpeed.get(id, 3) > 2):
                    vehicleNumberOfStops[id] = self.vehicleNumberOfStops.get(id, 0) + 1
            else:
                vehicleNumberOfStops[id] = self.vehicleNumberOfStops.get(id, 0)
                cumulativeVehicleDelay[id] = self.cumulativeVehicleDelay.get(id, 0)
            vehicleLastSpeed[id] = vehSpeed

        self.vehicleNumberOfStops = vehicleNumberOfStops
        self.vehicleLastSpeed = vehicleLastSpeed
        self.cumulativeVehicleDelay = cumulativeVehicleDelay
        self.queueLength = length
        self.queueLengthStep = step

    def getWidth(self):
        return tLane.getWidth(self.id)

    def getLength(self):
        return tLane.getLength(self.id)

    def getLastStepLength(self):
        return tLane.getLastStepLength(self.id)

    def getMaxPossibleQueueLength(self):
        if (self.getLastStepLength() > 0):
            maxQueueLength = self.getLength() / self.getLastStepLength()
        else:
            maxQueueLength = self.getLength() / sm.SimulationManager.getCurrentSimulation().config.getInt(VEHICLE_AVG_LENGTH)
        return maxQueueLength

    def getMaxAcceptableQueueLength(self):
        return (self.getMaxPossibleQueueLength()
            * sm.SimulationManager.getCurrentSimulation().config.getFloat(LANE_MAX_ACCEPTABLE_QUEUE_OCCUPANCY))

    def getNumberOfStops(self):
        numberOfStops = 0
        for _, n in self.vehicleNumberOfStops.items():
            numberOfStops += n
        return numberOfStops

    def getNumberOfExtraStops(self):
        numberOfStops = 0
        for _, n in self.vehicleNumberOfStops.items():
            if (n > 1):
                numberOfStops += (n - 1)
        return numberOfStops

    def getCumulativeVehicleDelay(self):
        delay = 0
        for _, vehicleDelay in self.cumulativeVehicleDelay.items():
            delay += vehicleDelay
        return delay

class LaneFactory(object):

    lanes = {}

    """Represents a link of a road"""
    def __init__(self):
        super(LaneFactory, self).__init__()

    @staticmethod
    def getLane(laneId):
        if (laneId in LaneFactory.lanes):
            return LaneFactory.lanes[laneId]
        else:
            LaneFactory.lanes[laneId] = Lane(laneId)
            return LaneFactory.lanes[laneId]
