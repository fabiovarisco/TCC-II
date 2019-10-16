from abc import ABC, abstractmethod

class Statistics(ABC):

    """docstring for Statistics."""
    def __init__(self, runID, filePrefix = "stats"):
        super(Statistics, self).__init__()
        self.runID = runID
        self.filePrefix = filePrefix
        self.statistics = []

    @abstractmethod
    def update(self, step, callingObject):
        pass

    @abstractmethod
    def createPlot(self):
        pass

    def save(self):
        with open(f"output/{self.runID}_{self.filePrefix}.csv", "w") as statsFile:
            print(",".join(cN for cN in self.columns), file=statsFile)
            for s in self.statistics:
                print(",".join(str(sI) for sI in s), file=statsFile)


class ObserverStatistics(Statistics):

    """docstring for Statistics."""
    def __init__(self, runID, filePrefix = "stats"):
        super(ObserverStatistics, self).__init__(runID, filePrefix)


import pandas as pd
from matplotlib import pyplot as plt

class StatisticsAggregator(object):

    """docstring for Statistics."""
    def __init__(self):
        super(StatisticsAggregator, self).__init__()

    @staticmethod
    def aggregateDataframes(dataframes, onColumns):
        if (len(dataframes) == 0): raise Exception("No dataframes were passed.")
        df = dataframes[0]
        for i in range(1, len(dataframes)):
            df = pd.merge(df, dataframes[i], on=onColumns)
        return df

    @staticmethod
    def aggregate(df, aggregationOptions):
        return df.groupby('step').agg(aggregationOptions)

    @staticmethod
    def plot(df, x_column, y_columns, kinds):
        for i in range(0, len(y_columns)):
            df.plot(kind=kinds[i], x='step', y=y_columns[i])

    @staticmethod
    def plotAndSaveFigure(figureName, df, x_column, y_columns, kinds):
        plt.figure(figureName)
        StatisticsAggregator.plot(df, x_column, y_columns, kinds)
        plt.savefig(f"out_plots/{figureName}.png")

