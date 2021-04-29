import matplotlib.pyplot as plt
from matplotlib import collections  as mc
import sys


def plotElements():
    """Plot different elements to see what they look like"""
    try:
        elemCharacsFile = open("elementPlotCharac.data", 'r')
    except FileNotFoundError:
        print("File elementPlotCharac.data not found")
        sys.exit(1)
    elementCharacs = dict()
    elemCharacsLines = elemCharacsFile.readlines()
    for n, l in enumerate(elemCharacsLines):
        elementCharacs[n + 1] = l.split()

    xs = list()
    for x, ec in elementCharacs.items():
        xs.append(x*2)
    plt.ion()
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d', facecolor="orange")
    for i, x in enumerate(xs):
        ax.scatter(x, 0, 0, c=elementCharacs[i + 1][1],
                   s=int(elementCharacs[i + 1][2]), depthshade=False)
        ax.text(x, 0, 0.01, elementCharacs[i + 1][0], 'z')
    plt.show()
    plt.pause(0.001)
    input("Press Enter to continue")
    plt.close()


def plotStickSpectrum(freqs, ints, title):
    """Plot the stick spectrum, must be used after getSpectrum()
    and buildHarmSpecLists() or buildAnharmSpecLists()"""
    plt.ion()
    plt.stem(freqs, ints, markerfmt=' ', basefmt=' ', use_line_collection=True)
    plt.show()
    plt.pause(0.001)
    input("Press Enter to continue")
    plt.close()


def plotSpectrum(freqs, ints, fwhm, title, step=1,
                 norm=True, funcs="Lorentzian"):
    """Plot the spectrum, must be used after getSpectrum() and
    buildHarmSpecLists() or buildAnharmSpecLists()"""
    plt.ion()
    plt.title(title)
    plt.xlabel(r'Frequency (cm$^{-1}$)')
    if norm:
        plt.ylabel('Relative intensity')
    else:
        plt.ylabel('Intensity (a.u.)')
    for k in freqs:
        minFreq = sorted(freqs[k])[0]
        maxFreq = sorted(freqs[k])[-1]
        xMin = int(minFreq - 100)
        if xMin < 0:
            xMin = 0
        xMax = int(maxFreq + 200)
        xs = range(xMin, xMax, step)
        if norm:
            maxInt = sorted(ints[k])[-1]
            for i in range(0, len(ints[k])):
                ints[k][i] /= maxInt
        ys = list()
        for x in xs:
            y = 0
            for i, f in enumerate(freqs[k]):
                if funcs == "Lorentzian":
                    y += ints[k][i] / (1 + (2 * (f - x) / fwhm) ** 2)
                else:
                    print("Unknown function type for plotting the spectrum")
                    sys.exit(1)
            ys.append(y)
        plt.plot(xs, ys)
    plt.legend(freqs.keys())
    plt.show()
    plt.pause(0.001)
    input("Press Enter to continue")
    plt.close()


def tkPlotSpectrum(freqs, ints, fwhm, title,
                   step=1, norm=True, funcs="Lorentzian"):
    """Plot spectra in a tkinter window"""
    specFig, specAx = plt.subplots()
    specAx.set_title(title)
    specAx.set_xlabel(r'Frequency (cm$^{-1}$)')
    if norm:
        specAx.set_ylabel('Relative intensity')
    else:
        specAx.set_ylabel('Intensity (a.u.)')
    for k in freqs:
        minFreq = sorted(freqs[k])[0]
        maxFreq = sorted(freqs[k])[-1]
        xMin = int(minFreq - 100)
        if xMin < 0:
            xMin = 0
        xMax = int(maxFreq + 200)
        xs = range(xMin, xMax, step)
        if norm:
            maxInt = sorted(ints[k])[-1]
        else:
            maxInt = 1
        ys = list()
        for x in xs:
            y = 0
            for i, f in enumerate(freqs[k]):
                if funcs == "Lorentzian":
                    y += ints[k][i] / (maxInt*(1+(2*(f-x)/fwhm)**2))
                else:
                    print("Unknown function type for plotting the spectrum")
                    sys.exit(1)
            ys.append(y)
        specAx.plot(xs, ys)
    specAx.legend(freqs.keys())
    plt.show()


def plotEnergy(energies):
    """plot energy convergence in matplotlib"""
    plt.ion()
    plt.xlabel('Iteration')
    plt.ylabel(r'Energy (a.u.)')
    plt.plot(energies)
    plt.show()
    plt.pause(0.001)
    input("Press Enter to continue")
    plt.close()


def tkPlotEnergy(energies, title):
    """Plot energy convergence in a tkinter window"""
    specFig, specAx = plt.subplots()
    specAx.set_title(title)
    specAx.set_xlabel('Iteration')
    specAx.set_ylabel('Energy (a.u.)')
    specAx.plot(energies)
    plt.show()


def plotGeo(geo):
    try:
        elemCharacsFile = open("elementPlotCharac.data", 'r')
    except FileNotFoundError:
        print("File elementPlotCharac.data not found")
        sys.exit(1)
    elementCharacs = dict()
    elemCharacsLines = elemCharacsFile.readlines()
    for n, l in enumerate(elemCharacsLines):
        elementCharacs[n + 1] = l.split()
    xs = dict()
    ys = dict()
    zs = dict()
    for g in geo[-1].values():
        if not g[0] in xs:
            xs[g[0]] = list()
        xs[g[0]].append(float(g[1][0]))
        if not g[0] in ys:
            ys[g[0]] = list()
        ys[g[0]].append(float(g[1][1]))
        if not g[0] in zs:
            zs[g[0]] = list()
        zs[g[0]].append(float(g[1][2]))
    bounds_x, bounds_y, bounds_z = spotBounds(xs, ys, zs)
    plt.ion()
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d', facecolor="orange")
    for t in xs:
        ax.scatter(xs[t], ys[t], zs[t], c=elementCharacs[t][1],
                   s=int(elementCharacs[t][2]), depthshade=False)
    for i in range(0, len(bounds_x), 2):
        ax.plot(bounds_x[i:i+2], bounds_y[i:i+2], bounds_z[i:i+2],
                color='black', linewidth=2)
    plt.show()
    plt.pause(0.001)
    input("Press Enter to continue")
    plt.close()
    elemCharacsFile.close()


def tkPlotGeo(geo, elementScale, title):
    """Plot geometry in a tkinter window"""
    # Open file with characteristics of elements :
    # name, color, covalent radius (pm)
    try:
        elemCharacsFile = open("elementPlotCharac.data", 'r')
    except FileNotFoundError:
        print("File elementPlotCharac.data not found")
        sys.exit(1)
    elementCharacs = dict()
    elemCharacsLines = elemCharacsFile.readlines()
    for n, l in enumerate(elemCharacsLines):
        elementCharacs[n + 1] = l.split()
    xs = dict()
    ys = dict()
    zs = dict()
    # Coordinates stored in dict depending on the elements for plotting color
    # purpose
    for g in geo.values():
        if not g[0] in xs:
            xs[g[0]] = list()
        xs[g[0]].append(g[1][0])
        if not g[0] in ys:
            ys[g[0]] = list()
        ys[g[0]].append(g[1][1])
        if not g[0] in zs:
            zs[g[0]] = list()
        zs[g[0]].append(g[1][2])
    bounds_x, bounds_y, bounds_z = spotBounds(xs, ys, zs)
    plt.ion()
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d', facecolor="orange")
    ax.set_xlabel('x (angstrom)')
    ax.set_ylabel('y (angstrom)')
    ax.set_zlabel('z (angstrom)')
    for t in xs:
        ax.scatter(xs[t], ys[t], zs[t], c=elementCharacs[t][1],
                   s=int(elementCharacs[t][2])*float(elementScale), depthshade=False)
    for i in range(0, len(bounds_x), 2):
        ax.plot(bounds_x[i:i+2], bounds_y[i:i+2], bounds_z[i:i+2],
                color='black', linewidth=2)
    plt.show()


def spotBounds(xs, ys, zs):
    """Check if two atoms are closer than the sum of their covalent
    radius and return lists of coordinates of bounded atoms to plot"""
    # Open file with characteristics of elements :
    # name, color, covalent radius (pm)
    try:
        elemCharacsFile = open("elementPlotCharac.data", 'r')
    except FileNotFoundError:
        print("File elementPlotCharac.data not found")
        sys.exit(1)
    elementCharacs = dict()
    elemCharacsLines = elemCharacsFile.readlines()
    for n, l in enumerate(elemCharacsLines):
        elementCharacs[n + 1] = l.split()
    bounds_x = list()
    bounds_y = list()
    bounds_z = list()
    for k1 in xs.keys():
        for k2 in xs.keys():
            if int(k2) > int(k1):
                continue
            # Conversion picometer --> angstrom
            sumCovRad = (float(elementCharacs[k1][2]) +
                         float(elementCharacs[k1][2]))*0.01
            for i in range(len(xs[k1])):
                for j in range(len(xs[k2])):
                    if i != j:
                        dist = ((xs[k1][i]-xs[k2][j])**2 +
                                (ys[k1][i]-ys[k2][j])**2 +
                                (zs[k1][i]-zs[k2][j])**2)**0.5
                        if dist < sumCovRad + 0.1*sumCovRad:
                            bounds_x.append(xs[k1][i])
                            bounds_x.append(xs[k2][j])
                            bounds_y.append(ys[k1][i])
                            bounds_y.append(ys[k2][j])
                            bounds_z.append(zs[k1][i])
                            bounds_z.append(zs[k2][j])
    return bounds_x, bounds_y, bounds_z
