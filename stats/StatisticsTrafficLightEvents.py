
from stats.Statistics import ObserverStatistics
import matplotlib.pyplot as plt
import pandas as pd
from simulation.TrafficLight import TrafficLight

class StatisticsStageChange(ObserverStatistics):

    """docstring for StatisticsStageChange."""
    def __init__(self, runID, folder, filePrefix = "state_change"):
        super(StatisticsStageChange, self).__init__(runID, folder, ['step', 'tl_id', 'new_state'], filePrefix)

    def update(self, step, **kwargs):
        if ('traffic_light' in kwargs):
            traffic_light = kwargs['traffic_light']
            if (isinstance(traffic_light, TrafficLight)):
                self.statistics.append([step, traffic_light.getId(), traffic_light.getCurrentStage()])
            else:
                raise Exception("StatisticsStageChange expects kwargs['traffic_light'] to be a TrafficLight object")

    def createPlot(self):
        df_raw = pd.DataFrame(data=self.statistics, columns=self.columns)
        df_raw["tl_id"] = pd.to_numeric(df_raw["tl_id"])
        plt.figure(f"{self.filePrefix} - {self.runID}")
        df_raw.plot(kind='scatter', x='step', y='tl_id')
        plt.savefig(f"out_plots/{self.filePrefix}-{self.runID}.png")

class StatisticsStageTime(ObserverStatistics):

    """docstring for StatisticsStageChange."""
    def __init__(self, runID, folder, filePrefix = "state_change"):
        super(StatisticsStageTime, self).__init__(runID, folder, ['step', 'tl_id', 'start_at_step', 'stage', 'stage_time', 'time_beyond_queue_clearance', 'residual_queue'], filePrefix)

    def update(self, step, **kwargs):
        if ('stage_time' in kwargs):
            self.statistics.append([step, kwargs['tl_id'], kwargs['start_at_step'], kwargs['stage'], kwargs['stage_time'], kwargs['time_beyond_queue_clearance'], kwargs['residual_queue']])

    def createPlot(self):
        pass

class StatisticsCycleTime(ObserverStatistics):

    """docstring for StatisticsStageChange."""
    def __init__(self, runID, folder, filePrefix = "state_change"):
        super(StatisticsCycleTime, self).__init__(runID, folder, ['step', 'tl_id', 'start_at_step', 'cycle_time'], filePrefix)

    def update(self, step, **kwargs):
        if ('cycle_time' in kwargs):
            self.statistics.append([step, kwargs['tl_id'], kwargs['start_at_step'], kwargs['cycle_time']])

    def createPlot(self):
        pass