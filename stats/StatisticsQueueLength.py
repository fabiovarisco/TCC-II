

from stats.Statistics import Statistics
from simulation import TrafficLight as tl

class StatisticsQueueLength(Statistics):

    """docstring for StatisticsQueueLength."""
    def __init__(self, runID, folder, filePrefix = "queue_length"):
        super(StatisticsQueueLength, self).__init__(runID, folder, ['step', 'tl_id', 'lane_id' 'queue_length'], filePrefix)

    def update(self, step, **kwargs):
        traffic_light = kwargs['traffic_light']
        if (isinstance(traffic_light, tl.TrafficLight)):
            s_qls = [[step, traffic_light.getId(), ql['lane_id'], ql['queue_length']] for ql in traffic_light.getQueueLengthAllLanes()]
            self.statistics.extend(s_qls)
        else:
            raise Exception("StatisticsQueueLength expects stage object to be a TrafficLight")

    def createPlot(self):
        pass