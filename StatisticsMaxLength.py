
from Statistics import Statistics

class StatisticsMaxLength(Statistics):

    """docstring for StatisticsWaitingTime."""
    def __init__(self, runID, filePrefix = "wtime"):
        super(StatisticsMaxLength, self).__init__(runID, filePrefix)

    def gather(self, step, trafficLight):
        self.statistics.append([step, trafficLight.getId(), trafficLight.getMaxLength()])
