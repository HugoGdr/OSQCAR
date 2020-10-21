import sys
import matplotlib.pyplot as plt


class File:
    """Outputfile of a quantum chemistry soft read by the script."""

    def __init__(self, outputFileName):
        """File constructor, determines the software"""
        self.name = outputFileName
        self.shortName = outputFileName.split('/')[-1]
        try:
            self.fileOpened = open(self.name, 'r')
        except FileNotFoundError:
            print("File {0} not found".format(self.name))
            sys.exit(1)
        self.software = "Unknown"
        self.method = "Unknown"
        self.basis = "Unknown"
        self.calcTypes = dict()
        self.numberCalculations = 0
        self.numberAtoms = 0
        self.limitLines = dict()
        self.fileLines = self.fileOpened.readlines()
        if not self.fileLines:
            print("Empty file !")
            sys.exit(1)
        if "Gaussian" in self.fileLines[0]:
            self.software = "Gaussian"
        else:
            print("Unknown software")
            sys.exit(1)
        print("File {0} opened\nSoftware = {1}".format(self.name, self.software))

    def infoCalcs(self, verbose=True):
        """Check if the calculation ended normally, the method, basis and type of all calculations in the file"""
        if self.software == "Gaussian":
            startLines = list()
            if verbose:
                if self.fileLines[-1].startswith(" Normal termination"):
                    print("Calculation ended normally")
                else:
                    print("Warning, calculation didn't end properly")
            for i, line in enumerate(self.fileLines):
                if line.startswith(" Entering Link 1"):
                    startLines.append(i)
                elif line.startswith(" NAtoms="):
                    self.numberAtoms = int(line.split()[1])
            self.numberCalculations = len(startLines)
            startLines.append(len(self.fileLines) - 1)
            for i in range(0, len(startLines) - 1):
                self.limitLines[i + 1] = (startLines[i], startLines[i + 1])
            n = 0
            for i, l in self.limitLines.items():
                for line in self.fileLines[l[0]:l[1]]:
                    if line.startswith(" #P"):
                        self.calcTypes[i] = list()
                        line = line.split()
                        if "/" in line[1]:
                            self.method = line[1].split("/")[0]
                            self.basis = line[1].split("/")[1]
                        else:
                            self.method = line[1]
                            self.basis = "None"
                        for keyword in line[2:]:
                            if "opt" in keyword:
                                self.calcTypes[i].append("Geometry optimization")
                            if "freq" in keyword:
                                if "anharm" in keyword:

                                    self.calcTypes[i].append("Anharmonic frequency calculation")
                                else:
                                    self.calcTypes[i].append("Frequency calculation")
                        break
        if verbose:
            print("""Number atoms = {0}\nMethod = {1}\nBasis set = {2} """.format(self.numberAtoms, self.method,
                                                                                  self.basis))
            print(str(self.numberCalculations) + " calculations :")
            for key in self.calcTypes:
                print(key, end=": ")
                for elt in self.calcTypes[key]:
                    print(elt, end=" ")
                print()

    def getEnergyQuick(self):
        """Get the last energy in the file and return it"""
        energy = 'Unknown'
        if self.software == "Gaussian":
            for line in self.fileLines[::-1]:
                if 'SCF Done' in line:
                    energy = float(line.split()[4])
                    break
        return energy

    def getEnergy(self):
        """Get all the energies in the file"""
        if self.software == "Gaussian":
            energies = dict()
            for i, l in self.limitLines.items():
                energies[i] = list()
                for n, line in enumerate(self.fileLines[l[0]:l[1]]):
                    if 'SCF Done' in line:
                        energies[i].append(float(line.split()[4]))
        else:
            print("Can't retrieve energy for this software")
            sys.exit(1)

        return energies

    def getGeo(self):
        self.geos = dict()
        for i, l in self.limitLines.items():
            self.geos[i] = list()
            for n, line in enumerate(self.fileLines[l[0]:l[1]]):
                n += l[0]
                if 'Standard orientation' in line:
                    geo = dict()
                    for geoLine in self.fileLines[n + 5:n + 5 + self.numberAtoms]:
                        geo[geoLine.split()[0]] = list()
                        geo[geoLine.split()[0]].append(int(geoLine.split()[1]))
                        geo[geoLine.split()[0]].append(geoLine.split()[3:6])
                    self.geos[i].append(geo)

    def plotGeo(self, calcNumb):
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
        for g in self.geos[calcNumb][-1].values():
            if not g[0] in xs:
                xs[g[0]] = list()
            xs[g[0]].append(float(g[1][0]))
            if not g[0] in ys:
                ys[g[0]] = list()
            ys[g[0]].append(float(g[1][1]))
            if not g[0] in zs:
                zs[g[0]] = list()
            zs[g[0]].append(float(g[1][2]))
        plt.ion()
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d', facecolor="orange")
        for t in xs:
            ax.scatter(xs[t], ys[t], zs[t], c=elementCharacs[t][1], s=int(elementCharacs[t][2]), depthshade=False)
        plt.show()
        plt.pause(0.001)
        input("Press Enter to continue")
        plt.close()
        elemCharacsFile.close()

    def getSpectrum(self):
        """Get the frequencies and intensities"""
        if self.software == "Gaussian":
            # Check if harmonic or anharmonic
            self.specType = "None"
            for key, calcType in self.calcTypes.items():
                if 'Frequency calculation' in calcType:
                    self.specType = "harmonic"
                    specKey = key
                    break
                elif "Anharmonic frequency calculation" in calcType:
                    self.specType = "anharmonic"
                    specKey = key
                    break
            if self.specType == "None":
                print("No frequency calculation in this file")
                sys.exit(1)
        else:
            print("Can't retrieve spectrum for this software")
            sys.exit(1)

        # Take harmonic spectrum in all cases
        self.nModes = 3 * self.numberAtoms - 6
        nFreqLines = self.nModes // 3
        if self.nModes % 3 != 0:
            nFreqLines += 1
        freqLines = list()
        for i, line in enumerate(self.fileLines[self.limitLines[specKey][0]:self.limitLines[specKey][1]]):
            if 'Frequencies' in line:
                freqLines.append(self.limitLines[specKey][0] + i)
                if len(freqLines) == nFreqLines:
                    break
        self.harmSpectrum = dict()
        for n in freqLines:
            for i in range(0, 3):
                self.harmSpectrum[int(self.fileLines[n - 2].split()[i])] = list()
                self.harmSpectrum[int(self.fileLines[n - 2].split()[i])].append(
                    self.fileLines[n - 1].split()[i])  # 0 : sym
                self.harmSpectrum[int(self.fileLines[n - 2].split()[i])].append(
                    float(self.fileLines[n].split()[2 + i]))  # 1 : freq
                self.harmSpectrum[int(self.fileLines[n - 2].split()[i])].append(
                    float(self.fileLines[n + 1].split()[3 + i]))  # 2 : Red. mass
                self.harmSpectrum[int(self.fileLines[n - 2].split()[i])].append(
                    float(self.fileLines[n + 2].split()[3 + i]))  # 3 : Frc const.
                self.harmSpectrum[int(self.fileLines[n - 2].split()[i])].append(
                    float(self.fileLines[n + 3].split()[3 + i]))  # 4 : IR int.
                for j in range(0, nFreqLines + 1):
                    self.harmSpectrum[int(self.fileLines[n - 2].split()[i])].append(
                        self.fileLines[n + 5 + j].split()[2 + 3 * i:5 + 3 * i])  # 5 : Displ. vect.
                if self.nModes % 3 != 0:
                    for j in range(0, self.nModes % 3):
                        self.harmSpectrum[int(self.fileLines[n - 2].split()[i])].append(
                            self.fileLines[n + 5 + j].split()[2 + 3 * i:5 + 3 * i])  # 5 : Displ. vect.

        # Take anharmonic spectrum if needed
        if self.specType == 'anharmonic':
            anFreqLines = list()
            self.anharmFunds = dict()  # anharmsFunds[mode] = [Harm Freq, Anharm Freq, Harm Int, Anharm Int]
            self.anharmOvs = dict()  # anharmsOvs[mode] = [Harm Freq, Anharm Freq, Anharm Int]
            self.anharmCBs = dict()  # anharmCBs[mode][mode] = [Harm Freq, Anharm Freq, Anharm Int]
            for i, line in enumerate(self.fileLines[self.limitLines[specKey][0]:self.limitLines[specKey][1]]):
                if "Anharmonic Infrared Spectroscopy" in line:
                    specAnLine = i + self.limitLines[specKey][0]
                    break
            for i, line in enumerate(self.fileLines[specAnLine:self.limitLines[specKey][1]]):
                if "Fundamental Bands" in line:
                    anFreqLines.append(i + specAnLine)
                    i += self.nModes + 3
                elif "Overtones" in line:
                    anFreqLines.append(i + specAnLine)
                    i += self.nModes + 3
                elif "Combination Bands" in line:
                    anFreqLines.append(i + specAnLine)
                    break
            for k, l in enumerate(anFreqLines):
                if k == 0:
                    # Fundamentals
                    for line in self.fileLines[l + 3:]:
                        if not line.strip():
                            break
                        mode = int(line.split()[0].split('(')[0])
                        self.anharmFunds[mode] = list()
                        self.anharmFunds[mode].append(float(line.split()[1]))  # Harm Freq
                        self.anharmFunds[mode].append(float(line.split()[2]))  # Anharm Freq
                        self.anharmFunds[mode].append(float(line.split()[3]))  # Harm Int
                        self.anharmFunds[mode].append(float(line.split()[4]))  # Anharm Int
                if k == 1:
                    # Overtones
                    for line in self.fileLines[l + 3:]:
                        if not line.strip():
                            break
                        mode = int(line.split()[0].split('(')[0])
                        self.anharmOvs[mode] = list()
                        self.anharmOvs[mode].append(float(line.split()[1]))  # Harm Freq
                        self.anharmOvs[mode].append(float(line.split()[2]))  # Anharm Freq
                        self.anharmOvs[mode].append(float(line.split()[3]))  # Anharm Int
                if k == 2:
                    # Combination bands
                    for line in self.fileLines[l + 3:]:
                        if not line.strip():
                            break
                        mode = int(line.split()[0].split('(')[0])
                        mode2 = int(line.split()[1].split('(')[0])
                        if mode not in self.anharmCBs:
                            self.anharmCBs[mode] = dict()
                        if mode not in self.anharmCBs[mode]:
                            self.anharmCBs[mode][mode2] = list()
                        self.anharmCBs[mode][mode2].append(float(line.split()[2]))  # Harm Freq
                        self.anharmCBs[mode][mode2].append(float(line.split()[3]))  # Anharm Freq
                        self.anharmCBs[mode][mode2].append(float(line.split()[4]))  # Anharm Int

    def buildHarmSpecLists(self):
        freqs = list()
        ints = list()
        for n in range(1, self.nModes + 1):
            freqs.append(self.harmSpectrum[n][1])
            ints.append(self.harmSpectrum[n][4])
        return freqs, ints

    def buildAnharmSpecLists(self):
        freqs = list()
        ints = list()
        for n in range(1, self.nModes + 1):
            freqs.append(self.anharmFunds[n][1])
            ints.append(self.anharmFunds[n][3])
            freqs.append(self.anharmOvs[n][1])
            ints.append(self.anharmOvs[n][2])
        for n in self.anharmCBs:
            for m in self.anharmCBs[n]:
                freqs.append(self.anharmCBs[n][m][1])
                ints.append(self.anharmCBs[n][m][2])
        return freqs, ints
