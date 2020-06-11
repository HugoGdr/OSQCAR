import matplotlib.pyplot as plt

def plotElements():
    try:
        elemCharacsFile = open("elementPlotCharac.data", 'r')
    except FileNotFoundError:
        print("File elementPlotCharac.data not found")
    elementCharacs = dict()
    elemCharacsLines = elemCharacsFile.readlines() 
    for n,l in enumerate(elemCharacsLines):
        elementCharacs[n+1] = l.split()

    xs = list()
    ys = list()
    zs = list()
    for x,ec in elementCharacs.items():
        xs.append(x*2)
    plt.ion()
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d', facecolor="orange")
    for i,x in enumerate(xs):
        ax.scatter(x,0,0, c=elementCharacs[i+1][1], s=int(elementCharacs[i+1][2]), depthshade=False)
        ax.text(x,0,0.01,elementCharacs[i+1][0],'z')
    plt.show()
    plt.pause(0.001)
    input("Press Enter to continue")
    plt.close()
