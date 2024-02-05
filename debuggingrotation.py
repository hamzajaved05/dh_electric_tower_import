import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from glob import glob
import matplotlib

paths = "/home/hamzawlptp/Downloads"
paths = glob(paths + "/3.csv")
csvs = []

def plot(csv, rowst, rowend):
    """
     Plots data from csv file. This is a function to be called from plot_csv. py.
     
     @param csv - csv file from which data is read. Should be a pandas dataframe
     @param rowst - row to start from ( inclusive )
     @param rowend - row to end from ( inclusive ).
     
     @return True if successful False otherwise. The plot is saved to csv file and can be retrieved by get_plot
    """
    cmap = matplotlib.cm.get_cmap('hot')

    data = csv[["Longitude", "Latitude", "Yaw"]].iloc[6250: 6500]
    # plt.scatter(data["Longitude"], data["Latitude"], s = 2)
    angle = lambda x: (np.radians(90 - x))
    d = 0.00005
    x, y = d * np.cos(angle(data["Yaw"])), d * np.sin(angle(data["Yaw"]))
    # plt.scatter(x + data["Longitude"], y + data["Latitude"], s = 2, c= "r")

    xd, yd = data["Longitude"].to_numpy(), data["Latitude"].to_numpy()
    xt, yt = (data["Longitude"] + x).to_numpy(), (data["Latitude"] + y).to_numpy()
    yaws = data["Yaw"].to_numpy()
    yaws = yaws % 360
    
    yaws = (yaws - yaws.min()) / (yaws.max() - yaws.min())

    # Plot the data for each row in data.
    for r in range(data.shape[0]):
        plt.plot([xd[r], xt[r]], [yd[r], yt[r]], c= cmap(yaws[r])[:3])

    plt.show()

    return ""


# Plot the csv files in the given paths
for path in paths:
    csv = pd.read_csv(path)
    plot(csv, 0, -1)
    print("asd")