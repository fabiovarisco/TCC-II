
from stats.Statistics import Statistics
from traci import simulation

class StatisticsTotalTravelTime(Statistics):

    """docstring for StatisticsTotalTravelTime."""
    def __init__(self, runID, filePrefix = "travel_time"):
        self.columns = ['step', 'veh_id', 'ttime']
        super(StatisticsTotalTravelTime, self).__init__(runID, filePrefix)

        self.vehiclesDeparture = {}

    def update(self, step, callingObject):

        for id in simulation.getDepartedIDList():
            self.vehiclesDeparture[id] = step

        for id in simulation.getArrivedIDList():
            self.statistics.append([step, id, step - self.vehiclesDeparture[id]])       

    def createPlot(self):
        pass
