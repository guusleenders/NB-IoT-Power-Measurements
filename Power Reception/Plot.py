
import pandas as pd
import matplotlib.pyplot as plt
from numpy import trapz
import numpy as np
import seaborn as sns
import glob
import LatexifyMatplotlib

SPINE_COLOR = 'gray'
FORMAT = "pdf"
MARKER = "+"


    # Boot       Search        RA + Join     Network       Message       EDRX end
times = [

]

# RSSI: An integer indicating the received signal strength. These parameters are
#       available for GSM and LTE mode respectively.
# RSRP: An integer indicating the reference signal received power (RSRP). This
#       parameter is available for LTE mode.
# SINR: An integer indicating the signal to interference plus noise ratio (SINR).
#       Logarithmic value of SINR. Values are in 1/5th of a dB. The range is 0-250
#       which translates to -20dB - +30dB.
# RSRQ: An integer indicating the reference signal received quality (RSRQ) in dB.

#   RSSI, RSRP, SINR, RSRQ

# properties =
#     [0, -71, -74, 156, 0],
#     [0, -71, -75, 157, 0],
#     [0, -72, -75, 155, 0],
#     [0, -73, -78, 143, -5],
#     [0, -100, -104, 146, 0]
#     [0, -105, -107, 135, 0]
# ]

filenames = glob.glob("Metingen 3/*.csv")

dataCollection = []

i = 0
for filename in filenames:
    tempDictionary = {}

    filename = filename.replace(".csv","")

    df = pd.read_csv(filename+".csv")

    inc = df["Increment"][df.index[0]]
    start = df["Start"][df.index[0]]
    df = df.drop(df.index[0])

    df["CH1"] = df["CH1"].astype(float)
    df["CH2"] = df["CH2"].astype(float)
    df["CH3"] = df["CH3"].astype(float)

    df["trigger"] = df["CH3"].diff()
    triggerDataFrame = df[abs(df["trigger"]) >= 2]

    df["time"] = df.index*inc
    df = df.drop(columns=["Start", "Increment"])
    df['current'] = (abs(df['CH1'] - df['CH2']))*1000#*3.98
    df['power'] = df['current']*df['CH1']


    df.drop(columns=['CH1', 'CH2', 'Unnamed: 5', 'trigger'], inplace=True)
    try:
        tempDictionary["data"] = df
        tempDictionary["times"] = [[triggerDataFrame.index[0], triggerDataFrame.index[1]], [triggerDataFrame.index[2], triggerDataFrame.index[3]], [triggerDataFrame.index[4], triggerDataFrame.index[5]], [triggerDataFrame.index[6], triggerDataFrame.index[7]]]

        propertiesString = filename.replace("Metingen 3\\Meting met pin ", "")
        tempDictionary["properties"] = np.array(propertiesString.split(" ")).astype(np.int16).tolist()
        dataCollection.append(tempDictionary)
    except:
        print("Not valid: ")
        print(filename)

    i = i+1

energyDataFrame = pd.DataFrame(columns = ['boot', 'connect', 'network', 'packet', 'rsrp', 'rssi', 'sinr', 'rsrq', 'celevel'])

for dataDictionary in dataCollection:
    bootEnergy = trapz(dataDictionary["data"]["power"][dataDictionary["times"][0][0]:dataDictionary["times"][0][1]],
                       x=dataDictionary["data"]["time"][dataDictionary["times"][0][0]:dataDictionary["times"][0][1]])
    connectEnergy = trapz(dataDictionary["data"]["power"][dataDictionary["times"][1][0]:dataDictionary["times"][1][1]],
                          x=dataDictionary["data"]["time"][dataDictionary["times"][1][0]:dataDictionary["times"][1][1]])
    networkEnergy = trapz(dataDictionary["data"]["power"][dataDictionary["times"][2][0]:dataDictionary["times"][2][1]],
                          x=dataDictionary["data"]["time"][dataDictionary["times"][2][0]:dataDictionary["times"][2][1]])
    packetEnergy = trapz(dataDictionary["data"]["power"][dataDictionary["times"][3][0]:dataDictionary["times"][3][1]],
                         x=dataDictionary["data"]["time"][dataDictionary["times"][3][0]:dataDictionary["times"][3][1]])
    try:
        cdrxEnd = dataDictionary["data"].index[round(dataDictionary["data"]["time"],1) == round(dataDictionary["data"]["time"][dataDictionary["times"][3][1]],1)+10].tolist()[0]
        cdrxEnergy = trapz(dataDictionary["data"]["power"][dataDictionary["times"][3][1]:cdrxEnd],
                           x=dataDictionary["data"]["time"][dataDictionary["times"][3][1]:cdrxEnd])
    except:
        cdrxEnergy = 0

    if packetEnergy < 1500 and dataDictionary["properties"][0] == 2:
        print(dataDictionary["properties"])
        fig, ax1 = plt.subplots()
        plt.plot("time", "power", data=dataDictionary["data"])

        ax2 = ax1.twinx()
        plt.plot("time", "CH3", data=dataDictionary["data"], color="tab:red")
        plt.show()
        #dataDictionary["data"].plot(x="time", y="power")

    if bootEnergy != 0 and connectEnergy != 0 and networkEnergy != 0 and packetEnergy != 0 and cdrxEnergy != 0:
        energyDataFrame = energyDataFrame.append({
            'boot': bootEnergy,
            'connect': connectEnergy,
            'network': networkEnergy,
            'packet': packetEnergy,
            'cdrx': cdrxEnergy,
            'packetCdrx': packetEnergy + cdrxEnergy,
            'total': connectEnergy + networkEnergy + packetEnergy + cdrxEnergy,
            'celevel': 'A' if dataDictionary["properties"][0] == 0 else 'B' if dataDictionary["properties"][0] == 1 else 'C',
            'rssi': dataDictionary["properties"][1],
            'rsrp': dataDictionary["properties"][2],
            'sinr': dataDictionary["properties"][3],
            'rsrq': dataDictionary["properties"][4]
        }, ignore_index=True)


energyDataFrame = energyDataFrame.sort_values(by=['rsrp'])



# sns.scatterplot(x="rsrp", y="boot", hue="celevel", data=energyDataFrame)
# plt.show()
sns.scatterplot(x="rsrp", y="connect", hue="celevel", data=energyDataFrame)
plt.show()
sns.scatterplot(x="rsrp", y="network", hue="celevel", data=energyDataFrame)
plt.show()
sns.scatterplot(x="rsrp", y="packet", hue="celevel", data=energyDataFrame)
plt.show()
sns.scatterplot(x="rsrp", y="cdrx", hue="celevel", data=energyDataFrame)
plt.show()
sns.scatterplot(x="rsrp", y="packetCdrx", hue="celevel", data=energyDataFrame)
plt.show()


# with plt.style.context('seaborn-muted'): #dark_background
#     plt.rcParams.update({'font.family': 'CMU Serif', 'font.size': 12, 'figure.figsize': '8,5'})
#     ax = plt.gca()
#
#     #df.plot(x="time", y="current", ax=ax)
#     sns.scatterplot(x="rsrp", y="total", hue="celevel", data=energyDataFrame, ax=ax)
#     ax.spines['right'].set_visible(False)
#     ax.spines['top'].set_visible(False)
#     #ax.get_legend().remove()
#     plt.xlabel(r"Time (s)")
#     plt.ylabel(r"Energy (mJ)")
#     plt.savefig("total.svg", bbox_inches='tight')

fig, ax = plt.subplots()
sns.scatterplot(x="rsrp", y="total", hue="celevel", data=energyDataFrame, ax=ax)
LatexifyMatplotlib.save("total.tex", plt=plt, show=True)



sns.scatterplot(x="rsrp", y="total", hue="celevel", data=energyDataFrame)
plt.show()

# -- Boxplots --
boxplotData = [energyDataFrame.loc[energyDataFrame['celevel'] == "A"]["connect"],
               energyDataFrame.loc[energyDataFrame['celevel'] == "B"]["connect"],
               energyDataFrame.loc[energyDataFrame['celevel'] == "C"]["connect"]]
fig7, ax7 = plt.subplots()
ax7.set_title('Connect celevel')
ax7.boxplot(boxplotData)

boxplotData = [energyDataFrame.loc[energyDataFrame['celevel'] == "A"]["network"],
               energyDataFrame.loc[energyDataFrame['celevel'] == "B"]["network"],
               energyDataFrame.loc[energyDataFrame['celevel'] == "C"]["network"]]
fig7, ax7 = plt.subplots()
ax7.set_title('Network celevel')
ax7.boxplot(boxplotData)

boxplotData = [energyDataFrame.loc[energyDataFrame['celevel'] == "A"]["packet"],
               energyDataFrame.loc[energyDataFrame['celevel'] == "B"]["packet"],
               energyDataFrame.loc[energyDataFrame['celevel'] == "C"]["packet"]]
fig7, ax7 = plt.subplots()
ax7.set_title('Packet celevel')
ax7.boxplot(boxplotData)

boxplotData = [energyDataFrame.loc[energyDataFrame['celevel'] == "A"]["packetCdrx"],
               energyDataFrame.loc[energyDataFrame['celevel'] == "B"]["packetCdrx"],
               energyDataFrame.loc[energyDataFrame['celevel'] == "C"]["packetCdrx"]]
fig7, ax7 = plt.subplots()
ax7.set_title('Packetcdrx celevel')
ax7.boxplot(boxplotData)

boxplotData = [energyDataFrame.loc[energyDataFrame['celevel'] == "A"]["total"],
               energyDataFrame.loc[energyDataFrame['celevel'] == "B"]["total"],
               energyDataFrame.loc[energyDataFrame['celevel'] == "C"]["total"]]
fig7, ax7 = plt.subplots()
ax7.set_title('Total celevel')
ax7.boxplot(boxplotData)

plt.show()
#LatexifyMatplotlib.save(filename+".tex", plt = plt, show = True)
