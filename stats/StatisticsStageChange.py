
from stats.Statistics import ObserverStatistics
import matplotlib.pyplot as plt
import pandas as pd
from simulation.TrafficLight import TrafficLight

class StatisticsStageChange(ObserverStatistics):

    """docstring for StatisticsWaitingTime."""
    def __init__(self, runID, filePrefix = "state_change"):
        self.columns = ['step', 'tl_id', 'new_state']
        super(StatisticsStageChange, self).__init__(runID, filePrefix)

    def update(self, step, callingObject):
        if (isinstance(callingObject, TrafficLight)):
            self.statistics.append([step, callingObject.getId(), callingObject.getCurrentStage()])
        else:
            raise Exception("StatisticsStageChange expects stage object to be a TrafficLight")

    def createPlot(self):
        df_raw = pd.DataFrame(data=self.statistics, columns=self.columns)
        df_raw["tl_id"] = pd.to_numeric(df_raw["tl_id"])
        plt.figure(f"{self.filePrefix} - {self.runID}")
        df_raw.plot(kind='scatter', x='step', y='tl_id')
        plt.savefig(f"out_plots/{self.filePrefix}-{self.runID}.png")
