
from stats.Statistics import ObserverStatistics
import matplotlib.pyplot as plt
import pandas as pd
from TrafficLight import TrafficLight

class StatisticsStageChange(ObserverStatistics):

    """docstring for StatisticsWaitingTime."""
    def __init__(self, runID, filePrefix = "state_change"):
        self.columns = ['step', 'tl_id', 'new_state']
        super(StatisticsMaxLength, self).__init__(runID, filePrefix)

    def update(self, step, callingObject):
        if (isinstance(callingObject, TrafficLight)):
            self.statistics.append([step, callingObject.getId(), callingObject.getCurrentStage()])
        else:
            raise Exception("StatisticsStageChange expects stage object to be a TrafficLight")

    def createPlot(self):
        df_raw = pd.DataFrame(data=self.statistics, columns=self.columns)
        plt.figure(f"{self.filePrefix} - {self.runID}")
        df_agg.plot(kind='scatter')
        plt.savefig(f"out_plots/{self.filePrefix}-{self.runID}.png")
