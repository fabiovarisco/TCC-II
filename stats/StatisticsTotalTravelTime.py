
from stats.Statistics import Statistics
from traci import simulation

class StatisticsTotalTravelTime(Statistics):

    """docstring for StatisticsTotalTravelTime."""
    def __init__(self, runID, folder, filePrefix = "travel_time"):
        super(StatisticsTotalTravelTime, self).__init__(runID,  folder, ['step', 'veh_id', 'ttime'], filePrefix)

        self.vehiclesDeparture = {}

    def update(self, step, **kwargs):

        for id in simulation.getDepartedIDList():
            self.vehiclesDeparture[id] = step

        for id in simulation.getArrivedIDList():
            self.statistics.append([step, id, step - self.vehiclesDeparture[id]])       

    def createPlot(self):
        pass
