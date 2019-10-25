
from stats.Statistics import Statistics
import matplotlib.pyplot as plt
import pandas as pd
from simulation import TrafficLight as tl

class StatisticsMaxLength(Statistics):

    """docstring for StatisticsWaitingTime."""
    def __init__(self, runID, filePrefix = "max_length"):
        super(StatisticsMaxLength, self).__init__(runID,  ['step', 'tl_id', 'max_length'], filePrefix)

    def update(self, step, callingObject):
        if (isinstance(callingObject, tl.TrafficLight)):
            self.statistics.append([step, callingObject.getId(), callingObject.getMaxLength()])
        else:
            raise Exception("StatisticsStageChange expects stage object to be a TrafficLight")

    def createPlot(self):
        df_raw = pd.DataFrame(data=self.statistics, columns=self.columns)
        df_agg = df_raw.groupby('step').agg({'max_length' : 'mean'})
        plt.figure(f"{self.filePrefix} - {self.runID}")
        df_agg.plot(kind='line')
        plt.savefig(f"out_plots/{self.filePrefix}-{self.runID}.png")
