import sys
import os.path


class File:
    """Outputfile of a quantum chemistry soft read by the script."""

    def __init__(self, outputFileName):
        """File constructor, determines the software"""
        self.name = outputFileName
        if '/' in self.name:
            self.shortName = outputFileName.split('/')[-1]
        elif '\\' in self.name:
            self.shortName = outputFileName.split('\\')[-1]
        else:
            self.shortName = self.name

        try:
            self.fileOpened = open(self.name, 'r')
        except FileNotFoundError:
            print("File {0} not found".format(self.name))
            sys.exit(1)

        self.fileLines = self.fileOpened.readlines()
        self.software = "Unknown"
        self.method = dict()
        self.basis = dict()
        self.normalTermination = dict()
        self.calcTypes = dict()
        self.numberCalculations = 0
        self.numberAtoms = 0
        self.limitLines = dict()
        self.cpuTime = dict()
        self.cpuTimeSum = dict()
        self.cpuTimeTot = 0.0

        if not self.fileLines:
            print("Empty file !")
            sys.exit(1)
        if "Gaussian" in self.fileLines[0]:
            self.software = "Gaussian"
        else:
            print("Unknown software")
            sys.exit(1)
        print("File {0} opened\nSoftware = {1}"
              .format(self.name, self.software))

    def infoCalcs(self, verbose=True):
        """Check if the calculation ended normally,
        the method, basis and type of all calculations in the file"""
        if self.software == "Gaussian":
            startLines = list()
            for i, line in enumerate(self.fileLines):
                if line.startswith(" Entering Link 1"):
                    startLines.append(i)
                elif line.startswith(" NAtoms="):
                    self.numberAtoms = int(line.split()[1])
            self.numberCalculations = len(startLines)
            startLines.append(len(self.fileLines) - 1)
            for i in range(0, len(startLines) - 1):
                self.limitLines[i + 1] = (startLines[i], startLines[i + 1])
            for i, l in self.limitLines.items():
                if i == len(self.limitLines):
                    if self.fileLines[self.limitLines[i][1]]\
                            .startswith(" Normal termination"):
                        self.normalTermination[i] = True
                    else:
                        self.normalTermination[i] = False
                    self.cpuTime[i] = list()
                    self.cpuTime[i].append(float(self.fileLines[
                        self.limitLines[i][1]-3].split()[3]))
                    self.cpuTime[i].append(float(self.fileLines[
                        self.limitLines[i][1]-3].split()[5]))
                    self.cpuTime[i].append(float(self.fileLines[
                        self.limitLines[i][1]-3].split()[7]))
                    self.cpuTime[i].append(float(self.fileLines[
                        self.limitLines[i][1]-3].split()[9]))
                    self.cpuTimeSum[i] = self.cpuTime[i][0]*24*60*60\
                        + self.cpuTime[i][1]*60*60\
                        + self.cpuTime[i][2]*60\
                        + self.cpuTime[i][3]
                else:
                    if self.fileLines[self.limitLines[i][1]-3]\
                            .startswith(" Normal termination"):
                        self.normalTermination[i] = True
                    else:
                        self.normalTermination[i] = False
                    self.cpuTime[i] = list()
                    self.cpuTime[i].append(float(self.fileLines[
                        self.limitLines[i][1]-6].split()[3]))
                    self.cpuTime[i].append(float(self.fileLines[
                        self.limitLines[i][1]-6].split()[5]))
                    self.cpuTime[i].append(float(self.fileLines[
                        self.limitLines[i][1]-6].split()[7]))
                    self.cpuTime[i].append(float(self.fileLines[
                        self.limitLines[i][1]-6].split()[9]))
                    self.cpuTimeSum[i] = self.cpuTime[i][0]*24*60*60\
                        + self.cpuTime[i][1]*60*60\
                        + self.cpuTime[i][2]*60\
                        + self.cpuTime[i][3]

                for line in self.fileLines[l[0]:l[1]]:
                    if line.startswith(" #P"):
                        self.calcTypes[i] = list()
                        line = line.split()
                        if "/" in line[1]:
                            self.method[i] = line[1].split("/")[0]
                            self.basis[i] = line[1].split("/")[1]
                        else:
                            self.method[i] = line[1]
                            self.basis[i] = "None"
                        for keyword in line[2:]:
                            if "opt" in keyword:
                                self.calcTypes[i].append(
                                    "Geometry optimization")
                            if "freq" in keyword:
                                if "anharm" in keyword:

                                    self.calcTypes[i].append(
                                        "Anharmonic frequency calculation")
                                else:
                                    self.calcTypes[i].append(
                                        "Frequency calculation")
                        break
        if verbose:
            print("Number atoms = {}\n".format(self.numberAtoms))
            if self.numberCalculations == 1:
                print("{} calculation :\n".format(self.numberCalculations))
            else:
                print("{} calculations :\n".format(self.numberCalculations))
            for key in self.calcTypes:
                print(key, end=": ")
                for elt in self.calcTypes[key]:
                    print(elt, end=" ")
                print()
                print("Method = {}\nBasis set = {} "
                      .format(self.method[key], self.basis[key]))
                if self.normalTermination[key]:
                    print("Calculation ended normally")
                else:
                    print("Warning, calculation didn't end properly\n")
                print("CPU Time : {} days, {} hours, {} minutes, {} seconds"
                      .format(self.cpuTime[key][0],
                              self.cpuTime[key][1],
                              self.cpuTime[key][2],
                              self.cpuTime[key][3]))
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
        """Get all the energies in each calculation"""
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

    # def plotEnergy(self)

    def getGeo(self):
        """Get all the geometries in each calculation"""
        self.geos = dict()
        for i, l in self.limitLines.items():
            self.geos[i] = list()
            for n, line in enumerate(self.fileLines[l[0]:l[1]]):
                n += l[0]
                if 'Standard orientation' in line:
                    geo = dict()
                    for geoLine in self.fileLines[
                            n + 5:n + 5 + self.numberAtoms]:
                        geo[geoLine.split()[0]] = list()
                        geo[geoLine.split()[0]].append(int(geoLine.split()[1]))
                        geo[geoLine.split()[0]].append(geoLine.split()[3:6])
                    self.geos[i].append(geo)
            # If no standard orientation, take the first input orientation
            if not self.geos[i]:
                for n, line in enumerate(self.fileLines[l[0]:l[1]]):
                    n += l[0]
                    if 'Input orientation' in line:
                        geo = dict()
                        for geoLine in self.fileLines[
                                n + 5:n + 5 + self.numberAtoms]:
                            geo[geoLine.split()[0]] = list()
                            geo[geoLine.split()[0]].append(
                                int(geoLine.split()[1]))
                            geo[geoLine.split()[0]].append(
                                geoLine.split()[3:6])
                        self.geos[i].append(geo)
                        break

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
        for i, line in enumerate(self.fileLines[
                self.limitLines[specKey][0]:self.limitLines[specKey][1]]):
            if 'Frequencies' in line:
                freqLines.append(self.limitLines[specKey][0] + i)
                if len(freqLines) == nFreqLines:
                    break
        self.harmSpectrum = dict()
        for n in freqLines:
            for i in range(0, 3):
                self.harmSpectrum[int(self.fileLines[n - 2].split()[i])]\
                    = list()
                # 0 : sym
                self.harmSpectrum[int(self.fileLines[n - 2].split()[i])]\
                    .append(self.fileLines[n - 1].split()[i])
                # 1 : freq
                self.harmSpectrum[int(self.fileLines[n - 2].split()[i])]\
                    .append(float(self.fileLines[n].split()[2 + i]))
                # 2 : Red. mass
                self.harmSpectrum[int(self.fileLines[n - 2].split()[i])]\
                    .append(float(self.fileLines[n + 1].split()[3 + i]))
                # 3 : Frc const.
                self.harmSpectrum[int(self.fileLines[n - 2].split()[i])]\
                    .append(float(self.fileLines[n + 2].split()[3 + i]))
                # 4 : IR int.
                self.harmSpectrum[int(self.fileLines[n - 2].split()[i])]\
                    .append(float(self.fileLines[n + 3].split()[3 + i]))
                # 5 : Displ. vect.
                for j in range(0, nFreqLines + 1):
                    self.harmSpectrum[int(self.fileLines[n - 2].split()[i])]\
                        .append(self.fileLines[n + 5 + j].split()
                                [2 + 3 * i:5 + 3 * i])
                if self.nModes % 3 != 0:
                    for j in range(0, self.nModes % 3):
                        self.harmSpectrum[
                            int(self.fileLines[n - 2].split()[i])].append(
                            self.fileLines[n + 5 + j].split()
                            [2 + 3 * i:5 + 3 * i])

        # Take anharmonic spectrum if needed
        if self.specType == 'anharmonic':
            anFreqLines = list()
            # Fundamentals : anharmsFunds[mode] =
            # [Harm Freq, Anharm Freq, Harm Int, Anharm Int]
            self.anharmFunds = dict()
            # Overtones : anharmsOvs[mode] =
            # [Harm Freq, Anharm Freq, Anharm Int]
            self.anharmOvs = dict()
            # Combination bands : anharmCBs[mode][mode] =
            # [Harm Freq, Anharm Freq, Anharm Int]
            self.anharmCBs = dict()
            for i, line in enumerate(self.fileLines[
                    self.limitLines[specKey][0]:self.limitLines[specKey][1]
                    ]):
                if "Anharmonic Infrared Spectroscopy" in line:
                    specAnLine = i + self.limitLines[specKey][0]
                    break
            for i, line in enumerate(self.fileLines[
                    specAnLine:self.limitLines[specKey][1]
                    ]):
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
                        # Harm Freq
                        self.anharmFunds[mode].append(float(line.split()[1]))
                        # Anharm Freq
                        self.anharmFunds[mode].append(float(line.split()[2]))
                        # Harm Int
                        self.anharmFunds[mode].append(float(line.split()[3]))
                        # Anharm Int
                        self.anharmFunds[mode].append(float(line.split()[4]))
                if k == 1:
                    # Overtones
                    for line in self.fileLines[l + 3:]:
                        if not line.strip():
                            break
                        mode = int(line.split()[0].split('(')[0])
                        self.anharmOvs[mode] = list()
                        # Harm Freq
                        self.anharmOvs[mode].append(float(line.split()[1]))
                        # Anharm Freq
                        self.anharmOvs[mode].append(float(line.split()[2]))
                        # Anharm Int
                        self.anharmOvs[mode].append(float(line.split()[3]))
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
                        # Harm Freq
                        self.anharmCBs[mode][mode2].append(
                            float(line.split()[2])
                            )
                        # Anharm Freq
                        self.anharmCBs[mode][mode2].append(
                            float(line.split()[3])
                            )
                        # Anharm Int
                        self.anharmCBs[mode][mode2].append(
                            float(line.split()[4])
                            )

    def buildHarmSpecLists(self):
        """Build harmonic frequencies and intensities list for plotting"""
        freqs = list()
        ints = list()
        for n in range(1, self.nModes + 1):
            freqs.append(self.harmSpectrum[n][1])
            ints.append(self.harmSpectrum[n][4])
        return freqs, ints

    def buildAnharmSpecLists(self):
        """Build anharmonic frequencies and intensities list for plotting"""
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

    def recordTime(self):
        """Record the CPU time and type of calculation,
        method, size of basis set, number of atoms and electrons in a file"""
        if os.path.isfile('cpuTime.data'):
            already = False
            cpuTimeFileOld = open('cpuTime.data', 'r')
            ctfoLines = cpuTimeFileOld.readlines()
            cpuTimeFile = open('cpuTime.data', 'a')
            for key in self.calcTypes:
                if ctfoLines:
                    for line in ctfoLines:
                        splitLine = line.split()
                        if float(splitLine[-1]) == self.cpuTimeSum[key]:
                            already = True
                            break
                if not already:
                    for ct in self.calcTypes[key]:
                        cpuTimeFile.write('{} '.format(ct))
                    cpuTimeFile.write('{} {} {} {}\n'.format(
                        self.method[key], self.basis[key], self.numberAtoms,
                        self.cpuTimeSum[key])
                        )
            cpuTimeFile.close()
            cpuTimeFileOld.close()
        else:
            cpuTimeFile = open('cpuTime.data', 'w')
            for key in self.calcTypes:
                for ct in self.calcTypes[key]:
                    cpuTimeFile.write('{} '.format(ct))
                cpuTimeFile.write('{} {} {} {}\n'.format(self.method[key],
                                                         self.basis[key],
                                                         self.numberAtoms,
                                                         self.cpuTimeSum[key])
                                  )
            cpuTimeFile.close()
