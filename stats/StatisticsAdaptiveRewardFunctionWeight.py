
from stats.Statistics import ObserverStatistics


class StatisticsAdaptiveRewardFunctionWeight(ObserverStatistics):

    """docstring for StatisticsAdaptiveRewardFunctionWeight."""
    def __init__(self, runID, filePrefix = "adaptive_rw_function"):
        super(StatisticsAdaptiveRewardFunctionWeight, self).__init__(runID, ['step', 'tl_id', 'dynamic_weight', 'dynamic_weight_activation', 'reward'], filePrefix)

    def update(self, step, **kwargs):
        self.statistics.append([step, kwargs['tl_id'], kwargs['dynamic_weight'], kwargs['dynamic_weight_activation'], kwargs['reward']])

    def createPlot(self):
        pass