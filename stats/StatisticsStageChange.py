
from stats.Statistics import ObserverStatistics
import matplotlib.pyplot as plt
import pandas as pd
from simulation.TrafficLight import TrafficLight

class StatisticsStageChange(ObserverStatistics):

    """docstring for StatisticsStageChange."""
    def __init__(self, runID, filePrefix = "state_change"):
        super(StatisticsStageChange, self).__init__(runID, ['step', 'tl_id', 'new_state'], filePrefix)

    def update(self, step, **kwargs):
        traffic_light = kwargs['traffic_light']
        if (isinstance(traffic_light, TrafficLight)):
            self.statistics.append([step, traffic_light.getId(), traffic_light.getCurrentStage()])
        else:
            raise Exception("StatisticsStageChange expects stage object to be a TrafficLight")

    def createPlot(self):
        df_raw = pd.DataFrame(data=self.statistics, columns=self.columns)
        df_raw["tl_id"] = pd.to_numeric(df_raw["tl_id"])
        plt.figure(f"{self.filePrefix} - {self.runID}")
        df_raw.plot(kind='scatter', x='step', y='tl_id')
        plt.savefig(f"out_plots/{self.filePrefix}-{self.runID}.png")
