

from stats.Statistics import Statistics
from simulation import TrafficLight as tl

class StatisticsQueueLength(Statistics):

    """docstring for StatisticsQueueLength."""
    def __init__(self, runID, filePrefix = "queue_length"):
        super(StatisticsQueueLength, self).__init__(runID, ['step', 'tl_id', 'lane_id' 'queue_length'], filePrefix)

    def update(self, step, callingObject):
        if (isinstance(callingObject, tl.TrafficLight)):
            s_qls = [[step, callingObject.getId(), ql['lane_id'], ql['queue_length']] for ql in callingObject.getQueueLengthAllLanes()]
            self.statistics.extend(s_qls)
        else:
            raise Exception("StatisticsQueueLength expects stage object to be a TrafficLight")

    def createPlot(self):
        pass