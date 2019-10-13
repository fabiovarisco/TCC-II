

from traci import vehicle as tVeh
import numpy as np

class Vehicle(object):

    def __init__(self, id):
        super(Vehicle, self).__init__()
        self.id = id



class VehicleFactory(object):

    vehicles = {}

    """Represents a link of a road"""
    def __init__(self):
        super(VehicleFactory, self).__init__()

    @staticmethod
    def getVehicle(vehicleId):
        if (vehicleId in VehicleFactory.vehicles):
            return VehicleFactory.vehicles[vehicleId]
        else:
            VehicleFactory.vehicles[vehicleId] = Vehicle(vehicleId)
            return VehicleFactory.vehicles[vehicleId]

    @staticmethod
    def getVehicleSpeed(vehicleId):
        return tVeh.getSpeed(vehicleId)
