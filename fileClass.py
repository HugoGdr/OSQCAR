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
        self.cpuTimeSec = dict()
        self.cpuTimeTot = 0.0

        if not self.fileLines:
            print("Empty file !")
            sys.exit(1)
        if "Gaussian" in self.fileLines[0]:
            self.software = "Gaussian"
        elif any("PROGRAM SYSTEM MOLPRO" in l for l in self.fileLines[0:200]):
            self.software = "Molpro"
        #for l in self.fileLines[0:200]:
        #    if "PROGRAM SYSTEM MOLPRO" in l:
        #        self.software = "Molpro"
        #        break
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
                    if self.fileLines[l[1]]\
                            .startswith(" Normal termination"):
                        self.normalTermination[i] = True
                    else:
                        self.normalTermination[i] = False
                    self.cpuTime[i] = list()
                    self.cpuTime[i].append(float(self.fileLines[
                        l[1]-3].split()[3]))
                    self.cpuTime[i].append(float(self.fileLines[
                        l[1]-3].split()[5]))
                    self.cpuTime[i].append(float(self.fileLines[
                        l[1]-3].split()[7]))
                    self.cpuTime[i].append(float(self.fileLines[
                        l[1]-3].split()[9]))
                    self.cpuTimeSec[i] = self.cpuTime[i][0]*24*60*60\
                        + self.cpuTime[i][1]*60*60\
                        + self.cpuTime[i][2]*60\
                        + self.cpuTime[i][3]
                else:
                    if self.fileLines[l[1]-3]\
                            .startswith(" Normal termination"):
                        self.normalTermination[i] = True
                    else:
                        self.normalTermination[i] = False
                    self.cpuTime[i] = list()
                    self.cpuTime[i].append(float(self.fileLines[
                        l[1]-6].split()[3]))
                    self.cpuTime[i].append(float(self.fileLines[
                        l[1]-6].split()[5]))
                    self.cpuTime[i].append(float(self.fileLines[
                        l[1]-6].split()[7]))
                    self.cpuTime[i].append(float(self.fileLines[
                        l[1]-6].split()[9]))
                    self.cpuTimeSec[i] = self.cpuTime[i][0]*24*60*60\
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
                    print("{} calculation :\n"
                        .format(self.numberCalculations))
                else:
                    print("{} calculations :\n"
                        .format(self.numberCalculations))
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
	
        elif self.software == 'Molpro':
            startLines = list()
            self.orbPrint = 0.25
            self.pointGroup = "Unknown"
            symNumbs = {
                "C1"  : 1,
                "Cs"  : 2,
                "C2V" : 4
             }
            for i, line in enumerate(self.fileLines):
                if line.startswith(" PROGRAM *"):
                    startLines.append(i)
                elif line.startswith(" SETTING BASIS"):
                    basisSet=line.split()[3] 
                elif not self.numberAtoms and\
                    line.startswith(" ATOMIC COORDINATES"):
                    for j, l in enumerate(self.fileLines[i+4:]):
                        if l.isspace():
                            self.numberAtoms = int(j)
                            break
                elif self.orbPrint == 0.25 and line.startswith(" THRPRINT"):
                    self.orbPrint = float(line.split()[1].replace('D','e'))
                elif self.pointGroup == "Unknown" \
                        and line.startswith(" Point group"):
                    self.pointGroup = line.split()[2]
            if self.pointGroup in symNumbs:
                self.symNumb = symNumbs[self.pointGroup]
            else:
                print("Point group {} not in point group dict, please add it "
                      "in fileClass.py file".format(self.pointGroup))
                sys.exit(1)
                    
            self.numberCalculations = len(startLines)
            startLines.append(len(self.fileLines) - 1)
            if self.fileLines[-1].startswith(" Molpro calculation terminated"):
                for i in range(1,len(startLines)):
                    self.normalTermination[i] = True
            else:
                for i in range(1,len(startLines)):
                    if i == len(startLines) - 1:
                        self.normalTermination[i] = False
                    else:
                        self.normalTermination[i] = True
            for i in range(0, len(startLines) - 1):
                self.limitLines[i + 1] = (startLines[i], startLines[i + 1])
            for i, l in self.limitLines.items():
                self.calcTypes[i] = list()
                self.calcTypes[i].append(str(self.fileLines[l[0]].split()[2]))
                self.basis[i]=basisSet	
                for j in self.fileLines[l[1]:l[0]:-1]:
                    if j.startswith(' CPU TIMES  *'):
                        self.cpuTimeSec[i] = float(j.split()[4])
                        if i == len(self.limitLines):
                            self.cpuTotalTime = float(j.split()[3])
                        break
                    

            if verbose:
                print("Number atoms = {}\n".format(self.numberAtoms))
                if self.numberCalculations == 1:
                    print("{} calculation :\n"
                        .format(self.numberCalculations))
                else:
                    print("{} calculations :\n"
                        .format(self.numberCalculations))
                for key in self.calcTypes:
                    print(key, end=": ")
                    for elt in self.calcTypes[key]:
                        print(elt, end=" ")
                    print()
                    if self.normalTermination[key]:
                        print("Calculation ended normally")
                    else:
                        print("Warning calculation did not end normally")
                    print("Basis set = {} "
                        .format(self.basis[key]))
                    print("CPU Time : {} seconds"
                        .format(self.cpuTimeSec[key]))
                    print()
                print("Total CPU time = {} seconds"
                    .format(self.cpuTotalTime))
            print('Molpro part of software in developement')
        print("\n\n")
	

    def getEnergyQuick(self):
        """Get the last energy in the file and return it"""
        energy = 'Unknown'
        if self.software == "Gaussian":
            for line in self.fileLines[::-1]:
                if 'SCF Done' in line:
                    energy = float(line.split()[4])
                    break
        elif self.software == "Molpro":
            self.energies = dict()
            for i, line in enumerate(self.fileLines[::-1]):
                if '******************' in line:
                    energies_tmp=self.fileLines[-i-2].split()
                    break
            for i,e in enumerate(energies_tmp[::-1]):
                self.energies[i] = e
            energy = energies_tmp[0]
                    
        else:
            print("Can't retrieve energy for this software")
            sys.exit(1)
        return energy

    def getEnergy(self):
        """Get all the energies in each calculation"""
        if self.software == "Gaussian":
            self.energies = dict()
            for i, l in self.limitLines.items():
                self.energies[i] = list()
                for line in self.fileLines[l[0]:l[1]]:
                    if 'SCF Done' in line:
                        self.energies[i].append(float(line.split()[4]))
        elif self.software == "Molpro":
            energyConv = dict()
            self.energies = dict()
            self.energy = dict()
            self.weightFactors = dict()
            for i, l in self.limitLines.items():
                energyConv[i] = list()
                self.energies[i] = dict()
                if 'RHF-SCF' in self.calcTypes[i] or\
                   'UHF-SCF' in self.calcTypes[i]:
                    for j,line in enumerate(self.fileLines[l[0]:l[1]]):
                        if line.startswith(' ITERATION'):
                            for nrjLine in self.fileLines[l[0]+j+1:l[1]]:
                                if nrjLine.isspace():
                                    break
                                try:
                                    energyConv[i].append(
                                        float(nrjLine.split()[3]))
                                except:
                                    print('Issue with convergence in calculati'
                                          'on {}'.format(i))
                        elif (line.startswith(' !UHF STATE') or \
                             line.startswith(' !RHF STATE')) and \
                             'Energy' in line:
                            self.energies[i][line.split()[2]] = float(
                                line.split()[4])
                    energiesOrdered = list()
                    for nrj in self.energies[i].values():
                       energiesOrdered.append(nrj) 
                    energiesOrdered.sort()
                    self.energy[i] = energiesOrdered[0]
                elif 'MULTI' in self.calcTypes[i]: 
                    dynw = False
                    nwf = dict()
                    weights = list()
                    self.weightFactors[i] = dict()
                    for j,line in enumerate(self.fileLines[l[0]:l[1]]):
                        if dynw == False and \
                           line.startswith(' Dynamical weighting'):
                            dynw = True
                            dynfac = float(line.split()[4])
                        elif dynw == True and \
                           line.startswith(' Weight factors'):
                            for k,wfline in enumerate(self.fileLines[l[0]+j:
                                                                     l[1]]):
                                if k==0:
                                    sym = wfline.split()[5].strip(':')
                                    nwf[sym] = len(wfline.split()) - 6
                                else:
                                    if wfline.startswith(' Weight factors') or\
                                       wfline.isspace():
                                        break
                                    nwf[sym] += len(wfline.split())
                                
                        elif line.startswith(' ITER.'):
                            if dynw:
                                for k,nrjLine in enumerate(self.fileLines[
                                                           l[0]+j+2:l[1]]):
                                    if nrjLine.isspace():
                                        #Goes back to take last weights
                                        for weightline in self.fileLines[
                                                l[0]+j+2+k:l[0]+j+2:-1]:
                                            if weightline.startswith(
                                                    ' New weights'):
                                                wl = weightline.split()[2:]
                                                for w in wl[::-1]:
                                                    weights.insert(0,float(w))
                                                break
                                            wl = weightline.split()
                                            for w in wl[::-1]:
                                                weights.insert(0,float(w))
                                        break
                                    elif nrjLine.split()[0].isnumeric():
                                        energyConv[i].append(
                                            float(nrjLine.split()[4]))
                            else:
                                for nrjLine in self.fileLines[l[0]+j+2:l[1]]:
                                    if nrjLine.isspace():
                                        break
                                    energyConv[i].append(
                                        float(nrjLine.split()[4]))
                        elif line.startswith(' !MCSCF STATE') and \
                             'Energy' in line:
                            self.energies[i][line.split()[2]] = float(
                                line.split()[4])
                    start = 0
                    for sym in nwf:
                        self.weightFactors[i][sym] = list()
                        for j in range(0,nwf[sym]):
                            self.weightFactors[i][sym].append(weights[j+start])
                        start += j+1
                    energiesOrdered = list()
                    for nrj in self.energies[i].values():
                       energiesOrdered.append(nrj) 
                    energiesOrdered.sort()
                    self.energy[i] = energiesOrdered[0]
                elif 'CI' in self.calcTypes[i]: 
                    for j,line in enumerate(self.fileLines[l[0]:l[1]]):
                        if line.startswith('  ITER.'):
                            for nrjLine in self.fileLines[l[0]+j+1:l[1]]:
                                if nrjLine.isspace():
                                    break
                                if nrjLine.split()[1] == "1":
                                    energyConv[i].append(
                                        float(nrjLine.split()[5]))
                        elif line.startswith(' !MRCI STATE') and \
                             'Energy' in line:
                            self.energies[i][line.split()[2]] = float(
                                line.split()[4])
                    energiesOrdered = list()
                    for nrj in self.energies[i].values():
                       energiesOrdered.append(nrj) 
                    energiesOrdered.sort()
                    self.energy[i] = energiesOrdered[0]
                elif 'OPT' in self.calcTypes[i]:
                    for j,line in enumerate(self.fileLines[l[0]:l[1]]):
                        if line.startswith(' ITER.'):
                            for k,nrjLine in enumerate(self.fileLines
                                                            [l[0]+j+1:l[1]]):
                                if nrjLine.isspace():
                                    break
                                if k==0:
                                    energyConv[i].append(
                                        float(nrjLine.split()[1]))
                                    energyConv[i].append(
                                        float(nrjLine.split()[2]))
                                else:
                                    energyConv[i].append(
                                        float(nrjLine.split()[2])
                                        )
                            break
                else: 
                    self.energy[i] = 'None'
        else:
            print("Can't retrieve energy for this software")
            sys.exit(1)

    def getGeo(self):
        """Get all the geometries in each calculation"""
        self.geos = dict()
        if self.software == "Gaussian":
            for i, l in self.limitLines.items():
                self.geos[i] = list()
                for n, line in enumerate(self.fileLines[l[0]:l[1]]):
                    n += l[0]
                    if 'Standard orientation' in line:
                        geo = dict()
                        for geoLine in self.fileLines[
                                n + 5:n + 5 + self.numberAtoms]:
                            geo[geoLine.split()[0]] = list()
                            geo[geoLine.split()[0]].append(
                                int(geoLine.split()[1]))
                            strCoord = geoLine.split()[3:6]
                            floatCoord = list()
                            for sc in strCoord:
                                floatCoord.append(float(sc))
                            geo[geoLine.split()[0]].append(floatCoord)
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
                                strCoord = geoLine.split()[3:6]
                                floatCoord = list()
                                for sc in strCoord:
                                    floatCoord.append(float(sc))
                                geo[geoLine.split()[0]].append(floatCoord)
                            self.geos[i].append(geo)
                            break
            #If the 2 last geometries are the same delete the last one
            for k in self.geos.keys():
                if len(self.geos[k]) > 1:
                    if self.geos[k][-1] == self.geos[k][-2]:
                        del self.geos[k][-1]

        if self.software == "Molpro":
            elements = {
                "H"  : 1,
                "He" : 2,
                "Li" : 3,
                "Be" : 4,
                "B"  : 5,
                "C"  : 6,
                "N"  : 7,
                "O"  : 8,
                "F"  : 9,
                "Ne" : 10,
                "Na" : 11,
                "Mg" : 12,
                "Al" : 13,
                "Si" : 14,
                "P"  : 15,
                "S"  : 16,
                "Cl" : 17,
                "Ar" : 18,
                "K"  : 19,
                "Ca" : 20
             }

            convFactor = 0.529177249

            for i, l in self.limitLines.items():
                if 'SEWARD' in self.calcTypes[i]:
                    self.geos[i] = list()
                    for n, line in enumerate(self.fileLines[l[0]:l[1]]):
                        n += l[0]
                        if 'ATOMIC COORDINATES' in line:
                            geo = dict()
                            for geoLine in self.fileLines[
                                    n + 4:n + 4 + self.numberAtoms]:
                                geo[geoLine.split()[0]] = list()
                                if int(float(geoLine.split()[2])) != 0:
                                    geo[geoLine.split()[0]].append(
                                        int(float(geoLine.split()[2])))
                                else:
                                    #Remove number from the element names
                                    elem = ''.join([j for j 
                                        in geoLine.split()[1] 
                                        if not j.isdigit()]
                                        )
                                    geo[geoLine.split()[0]]\
                                        .append(elements[elem])
                                strCoord = geoLine.split()[3:6]
                                floatCoord = list()
                                for sc in strCoord:
                                    floatCoord.append(float(sc)*convFactor)
                                geo[geoLine.split()[0]].append(floatCoord)
                            self.geos[i].append(geo)
                            break
                elif 'OPT' in self.calcTypes[i]:
                    self.geos[i] = list()
                    for n, line in enumerate(self.fileLines[l[0]:l[1]]):
                        n += l[0]
                        if 'Current geometry' in line:
                            geo = dict()
                            for j, geoLine in enumerate(
                                self.fileLines[n + 4:n + 4 +
                                self.numberAtoms]):
                                geo[j] = list()
                                if isinstance(geoLine.split()[0], int):
                                    geo[j].append(geoLine.split[1])
                                else:
                                    #Remove number from the element names
                                    elem = ''.join([j for j 
                                        in geoLine.split()[0] 
                                        if not j.isdigit()]
                                        )
                                    geo[j].append(elements[elem])
                                strCoord = geoLine.split()[1:4]
                                floatCoord = list()
                                for sc in strCoord:
                                    floatCoord.append(float(sc))
                                geo[j].append(floatCoord)
                            self.geos[i].append(geo)
                            break
		#If no geometry for a calculation take the one from the previous one
                else:
                    self.geos[i] = self.geos[i-1]
                    

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

    def getOrbitals(self):
        """Get the orbitals energies"""

        def checkMOCoeff(coeff):
            """Check if there is no issue with the AOs coefficients"""
            problem = False
            try:
                coeffChecked=float(coeff)
            except:
                if '*' in coeff:
                    coeffChecked=0.0
                    problem = True
                #elif '-' in coeff[1:]:
                #    mps = [c+1 for c, char in enumerate(coeff[1:]) \
                #           if '-' in char]
                #    mps.append(len(coeff))
                #    for m,mp in enumerate(mps):
                #        if m==0:
                #            coeffChecked = float(coeff[:mp])
                #        else:
                #            coeffChecked = float(coeff[mps[m-1]:mp])
                else:
                    pps = [c+1 for c, char in enumerate(coeff) if '.' in char]
                    for p,pp in enumerate(pps):
                        if p==0:
                            coeffChecked = float(coeff[:pp+6])
                        else:
                            coeffChecked = float(coeff[pps[p-1]+6:pp+6])
            return coeffChecked, problem

        def reordering(orbitals,ct):
            orbEnergies = dict()
            orderedOrbs = dict()
            if 'UHF-SCF' in ct:
                orbitals_beta = orbitals
            for sym in syms:
                orbEnergies[sym] = list()
                for orb in orbitals:
                    if orb.split('.')[1] == sym:
                        orbEnergies[sym].append(
                            orbitals[orb][0])
                orbEnergies[sym].sort()
                for j,nrj in enumerate(orbEnergies[sym]):
                    for orb in orbitals:
                        if orb.split('.')[1] == sym and \
                           orbitals[orb][0] == nrj:
                            orderedOrbs["{}.{}".format(j+1,sym)]=\
                                orbitals[orb]
                            orbitals.pop(orb)
                            break
            if 'UHF-SCF' in ct:
                orbEnergies_beta = dict()
                #orderedOrbs_beta = dict()
                for sym in syms:
                    orbEnergies_beta[sym] = list()
                    for orb in orbitals_beta:
                        if orb.split('.')[1] == sym and \
                           len(orbitals_beta[orb]) > 3:
                            orbEnergies_beta[sym].append(orbitals_beta[orb][3])
                    orbEnergies_beta[sym].sort()
                    for j,nrj in enumerate(orbEnergies_beta[sym]):
                        for orb in orbitals_beta:
                            if len(orbitals_beta[orb]) > 3:
                                if orb.split('.')[1] == sym and \
                                   orbitals_beta[orb][3] == nrj:
                                    orderedOrbs["{}.{}".format(j+1,sym)]\
                                        .append(orbitals_beta[orb][3:])
                                    orbitals_beta.pop(orb)
                                    break
                #for mo in orderedOrbs_beta:
                #    if len(self.orbitals[i][mo]) > 3:
                #        self.orbitals[i][mo][3] = \
                #            orderedOrbs_beta[mo][0]
                #        self.orbitals[i][mo][4] = \
                #            orderedOrbs_beta[mo][1]
                #        self.orbitals[i][mo][5] = \
                #            orderedOrbs_beta[mo][2]
            return orderedOrbs

        if self.software == "Molpro":
            energyReorder = False
            self.orbitals = dict()
            syms = list()
            for i, l in self.limitLines.items():
                if 'RHF-SCF' in self.calcTypes[i]: 
                    self.orbitals[i] = dict()
                    #If thrprint is 0 MOs are shown in a different way
                    if self.orbPrint == 0.0:
                        numIdOrb = dict() #Count how many AOs of each type
                        aosZone = True
                        coeffsZone = False
                        s = 1 #Symmetry counter
                        aosLabels = dict()
                        for j,line in enumerate(self.fileLines[l[0]:l[1]]):
                            if line.startswith(' MOLECULAR ORBITALS'):
                                orbStartLineN = l[0]+j+5
                                break
                        else:
                            print("WARNING: No orbitals for 'RHF-SCF in this "
                                  "file, use \"print, orbitals\" in input file"
                                  " to show them")
                            self.orbitals[i] = "None"
                            continue
                        for o,orbitalsLine in enumerate(
                                    self.fileLines[orbStartLineN:l[1]]):
                            if orbitalsLine.startswith(" HOMO"):
                                break
                            if not aosZone:
                                #orbitals[calc][n°]: energy; occ
                                if orbitalsLine.isspace():
                                    if coeffsZone:
                                        orbCompo = dict()
                                        for k,coeff in enumerate(orbCoeffs):
                                            orbCoeffs[k], prob = \
                                                checkMOCoeff(coeff)
                                            if prob:
                                                print("Warning, coefficient "
                                                "unavailable for calculation: "
                                                "{}, MO: {}, AO: {}"
                                                .format(i,numb,
                                                aosLabels[s][k]))
                                        for k in range(len(orbCoeffs)):
                                            orbCompo[aosLabels[s][k]]=\
                                                float(orbCoeffs[k])
                                        self.orbitals[i][numb].append(orbCompo)
                                    continue
                                elif "." in orbitalsLine.split()[0]\
                                    and len(orbitalsLine.split()[0])<5:
                                    orbCoeffs = list()
                                    if not coeffsZone:
                                        coeffsZone = True
                                    sym = orbitalsLine.split()[0].split('.')[1]
                                    if sym not in syms:
                                        syms.append(sym)
                                    numb = orbitalsLine.split()[0]
                                    self.orbitals[i][numb]=list()
                                    self.orbitals[i][numb].append(
                                        float(orbitalsLine.split()[2]))
                                    if orbitalsLine.split()[1]=='+' or\
                                       orbitalsLine.split()[1]=='-':
                                        
                                        self.orbitals[i][numb]\
                                            .append(1.0)
                                    else:        
                                        self.orbitals[i][numb].append(
                                            float(orbitalsLine.split()[1]))
                                    orbCoeffs += orbitalsLine.split()[3:]
                                elif "." not in orbitalsLine.split()[0]:
                                    aosZone = True
                                    s += 1
                                    coeffsZone = False
                                else:
                                    orbCoeffs += orbitalsLine.split()
                            if aosZone:
                                if not s in aosLabels:
                                    aosLabels[s] = list()
                                for k in range(0,len(orbitalsLine.split()),2):
                                    label = "{} {}".format(
                                        orbitalsLine.split()[k],
                                        orbitalsLine.split()[k+1])
                                    if label in aosLabels[s]:
                                        if label not in numIdOrb:
                                            numIdOrb[label] = 2
                                            label = "{} {}".format(
                                                label, numIdOrb[label])
                                        else:
                                            numIdOrb[label] += 1
                                            label = "{} {}".format(
                                                label, numIdOrb[label])
                                    aosLabels[s].append(label)
                                if orbitalsLine.isspace():
                                    aosZone = False
                    else:
                        for j,line in enumerate(self.fileLines[l[0]:l[1]]):
                            if line.startswith(' ELECTRON ORBITALS'):
                                orbStartLineN = l[0]+j+4
                                break
                        else:
                            print("WARNING: No orbitals for 'RHF-SCF in this "
                                  "file, use \"print, orbitals\" in input file "
                                  "to show them")
                            self.orbitals[i] = "None"
                            continue
                        for orbitalsLine in self.fileLines[orbStartLineN:l[1]]:
                            if orbitalsLine.isspace():
                                break
                            #orbitals[calc][n°]: energy; occ
                            if "." in orbitalsLine.split()[0]:
                                sym = orbitalsLine.split()[0].\
                                                   split('.')[1]
                                if sym not in syms:
                                    syms.append(sym)
                                numb = orbitalsLine.split()[0]
                                self.orbitals[i][numb]=list()
                                self.orbitals[i][numb].append(
                                    float(orbitalsLine.split()[2]))
                                self.orbitals[i][numb].append(
                                    float(orbitalsLine.split()[1]))
                elif 'UHF-SCF' in self.calcTypes[i]: 
                    self.orbitals[i] = dict()
                    alphaAndBeta = 0
                    if self.orbPrint == 0.0:
                        numIdOrb = dict() #Count how many AOs of each type
                        aosZone = True
                        coeffsZone = False
                        spaceBefore = False
                        s = 1 #Symmetry counter
                        aosLabels = dict()
                        for j,line in enumerate(self.fileLines[l[0]:l[1]]):
                            if line.startswith(' ELECTRON ORBITALS'):
                                orbStartLineN = l[0]+j+5
                                break
                        else:
                            print("WARNING: No orbitals for 'UHF-SCF in this "
                                  "file, use \"print, orbitals\" in input file"
                                  " to show them")
                            self.orbitals[i] = "None"
                            continue
                        for o,orbitalsLine in enumerate(
                                self.fileLines[orbStartLineN:l[1]]):
                            if orbitalsLine.startswith(" HOMO"):
                                break
                            elif orbitalsLine.startswith(" ELECTRON ORB") or \
                                 orbitalsLine.startswith(" ============"):
                                aosZone = True
                                coeffsZone = False
                                spaceBefore = False
                                continue
                            if not aosZone:
                                #orbitals[calc][n°]: energy; occ
                                if orbitalsLine.isspace():
                                    if spaceBefore:
                                        continue
                                    else:
                                        spaceBefore = True
                                    if coeffsZone:
                                        orbCompo = dict()
                                        for k,coeff in enumerate(orbCoeffs):
                                            orbCoeffs[k], prob = \
                                                checkMOCoeff(coeff)
                                            if prob:
                                                print("Warning, coefficient "
                                                "unavailable for calculation: "
                                                "{}, MO: {}, AO: {}"
                                                .format(i,numb,
                                                aosLabels[s][k]))
                                        for k in range(len(orbCoeffs)):
                                            orbCompo[aosLabels[s][k]]=\
                                                float(orbCoeffs[k])
                                        self.orbitals[i][numb].append(orbCompo)
                                    continue
                                elif "." in orbitalsLine.split()[0]\
                                    and len(orbitalsLine.split()[0])<5:
                                    if spaceBefore:
                                        spaceBefore = False
                                    orbCoeffs = list()
                                    if not coeffsZone:
                                        coeffsZone = True
                                    sym = orbitalsLine.split()[0].split('.')[1]
                                    if sym not in syms:
                                        syms.append(sym)
                                    numb = orbitalsLine.split()[0]
                                    if not numb in self.orbitals[i]:
                                        self.orbitals[i][numb]=list()
                                    self.orbitals[i][numb].append(
                                        float(orbitalsLine.split()[2]))
                                    if orbitalsLine.split()[1]=='+' or\
                                       orbitalsLine.split()[1]=='-':
                                        
                                        self.orbitals[i][numb]\
                                            .append(1.0)
                                    else:        
                                        self.orbitals[i][numb].append(
                                            float(orbitalsLine.split()[1]))
                                    orbCoeffs += orbitalsLine.split()[3:]
                                elif "." not in orbitalsLine.split()[0]:
                                    if spaceBefore:
                                        spaceBefore = False
                                    aosZone = True
                                    s += 1
                                    coeffsZone = False
                                else:
                                    if spaceBefore:
                                        spaceBefore = False
                                    orbCoeffs += orbitalsLine.split()
                            if aosZone:
                                if not s in aosLabels:
                                    aosLabels[s] = list()
                                for k in range(0,len(orbitalsLine.split()),2):
                                    label = "{} {}".format(
                                        orbitalsLine.split()[k],
                                        orbitalsLine.split()[k+1])
                                    if label in aosLabels[s]:
                                        if label not in numIdOrb:
                                            numIdOrb[label] = 2
                                            label = "{} {}".format(
                                                label, numIdOrb[label])
                                        else:
                                            numIdOrb[label] += 1
                                            label = "{} {}".format(
                                                label, numIdOrb[label])
                                    aosLabels[s].append(label)
                                if orbitalsLine.isspace():
                                    if spaceBefore:
                                        continue
                                    else:
                                        spaceBefore = True
                                    aosZone = False
                    else:
                        for j,line in enumerate(self.fileLines[l[0]:l[1]]):
                            if line.startswith(' ELECTRON ORBITALS'):
                                alphaAndBeta += 1
                                for orbitalsLine in self.fileLines[l[0]+j+4:\
                                                                   l[1]]:
                                    if orbitalsLine.isspace():
                                        break
                                    #orbitals[calc][n°]: alpha energy; 
                                    #                    alpha occ;
                                    #                    beta energy; 
                                    #                    beta occ
                                    if "." in orbitalsLine.split()[0]:
                                        sym = orbitalsLine.split()[0]\
                                                          .split('.')[1]
                                        if sym not in syms:
                                            syms.append(sym)
                                        numb = orbitalsLine.split()[0]
                                        if alphaAndBeta == 1:
                                            orbitals[i][numb]=list()
                                        self.orbitals[i][numb].append(
                                            float(orbitalsLine.split()[2]))
                                        self.orbitals[i][numb].append(
                                            foat(orbitalsLine.split()[1]))
                                if alphaAndBeta == 2:
                                    break
                        else:
                            print("WARNING: No orbitals for 'UHF-SCF in this "
                                  "file, use \"print, orbitals\" in input file"
                                  " to show them")
                            self.orbitals[i] = "None"
                            continue
                elif 'MULTI' in self.calcTypes[i]: 
                    self.orbitals[i] = dict()
                    #If thrprint is 0 MOs are shown in a different way
                    if self.orbPrint == 0.0:
                        numIdOrb = dict() #Count how many AOs of each type
                        aosZone = True
                        coeffsZone = False
                        s = 1 #Symmetry counter
                        aosLabels = dict()
                        for j,line in enumerate(self.fileLines[l[0]:l[1]]):
                            if line.startswith(' NATURAL ORBITALS'):
                                orbStartLineN = l[0]+j+5
                                break
                        else:
                            print("WARNING: No natural orbitals for MULTI in "
                                  "this file, use\"natorb\" in input file to "
                                  "show them")
                            self.orbitals[i] = "None"
                            continue
                        for o,orbitalsLine in enumerate(
                                self.fileLines[orbStartLineN:l[1]]):
                            if orbitalsLine.startswith(" Total charg"):
                                break
                            if not aosZone:
                                #orbitals[calc][n°]: energy; occ
                                if orbitalsLine.isspace():
                                    if coeffsZone:
                                        orbCompo = dict()
                                        for k,coeff in enumerate(orbCoeffs):
                                            orbCoeffs[k], prob = \
                                                checkMOCoeff(coeff)
                                            if prob:
                                                print("Warning, coefficient "
                                                "unavailable for calculation: "
                                                "{}, MO: {}, AO: {}"
                                                .format(i,numb,
                                                aosLabels[s][k]))
                                        for k in range(len(orbCoeffs)):
                                            orbCompo[aosLabels[s][k]]=\
                                                float(orbCoeffs[k])
                                        self.orbitals[i][numb].append(orbCompo)
                                    continue
                                elif "." in orbitalsLine.split()[0]\
                                    and len(orbitalsLine.split()[0])<5:
                                    orbCoeffs = list()
                                    if not coeffsZone:
                                        coeffsZone = True
                                    sym = orbitalsLine.split()[0].split('.')[1]
                                    if sym not in syms:
                                        syms.append(sym)
                                    numb = orbitalsLine.split()[0]
                                    self.orbitals[i][numb]=list()
                                    self.orbitals[i][numb].append(
                                        float(orbitalsLine.split()[2]))
                                    self.orbitals[i][numb].append(
                                        float(orbitalsLine.split()[1]))
                                    orbCoeffs += orbitalsLine.split()[3:]
                                elif "." not in orbitalsLine.split()[0]:
                                    aosZone = True
                                    s += 1
                                    coeffsZone = False
                                else:
                                    orbCoeffs += orbitalsLine.split()
                            if aosZone:
                                if not s in aosLabels:
                                    aosLabels[s] = list()
                                for k in range(0,len(orbitalsLine.split()),2):
                                    label = "{} {}".format(
                                        orbitalsLine.split()[k],
                                        orbitalsLine.split()[k+1])
                                    if label in aosLabels[s]:
                                        if label not in numIdOrb:
                                            numIdOrb[label] = 2
                                            label = "{} {}".format(label, 
                                                numIdOrb[label])
                                        else:
                                            numIdOrb[label] += 1
                                            label = "{} {}".format(
                                                label, numIdOrb[label])
                                    aosLabels[s].append(label)
                                if orbitalsLine.isspace():
                                    aosZone = False
                    else:
                        for j,line in enumerate(self.fileLines[l[0]:l[1]]):
                            if line.startswith(' NATURAL ORBITALS'):
                                orbStartLineN = l[0]+j+4
                                break
                        else:
                            print("WARNING: No natural orbitals for MULTI in "
                                  "this file, use\"natorb\" in input file to "
                                  "show them")
                            self.orbitals[i] = "None"
                            continue
                        for o,orbitalsLine in enumerate(
                                self.fileLines[orbStartLineN:l[1]]):
                            if orbitalsLine.isspace():
                                self.orbitals[i][numb].append(orbCompo)
                                break
                            #orbitals[calc][n°]: energy; occ; coeffs
                            if "." in orbitalsLine.split()[0]:
                                #Dict to store the number of ao with
                                #same name
                                numIdOrb = dict()
                                sym = orbitalsLine.split()[0].split('.')[1]
                                if sym not in syms:
                                    syms.append(sym)
                                if o != 0: 
                                    self.orbitals[i][numb].append(orbCompo)
                                orbCompo = dict()
                                numb = orbitalsLine.split()[0]
                                self.orbitals[i][numb]=list()
                                self.orbitals[i][numb].append(
                                    float(orbitalsLine.split()[2]))
                                self.orbitals[i][numb].append(
                                    float(orbitalsLine.split()[1]))
                                for k in range(3,len(orbitalsLine.split()),3):
                                    label = "{} {}".format(
                                            orbitalsLine.split()[k],
                                            orbitalsLine.split()[k+1])
                                    if label in orbCompo:
                                        if label not in numIdOrb:
                                            numIdOrb[label] = 2
                                            label = "{} {}".format(
                                                label, numIdOrb[label])
                                        else:
                                            numIdOrb[label] += 1
                                            label = "{} {}".format(
                                                label, numIdOrb[label])
                                    orbCompo[label] = float(
                                        orbitalsLine.split()[k+2])
                            else:
                                for k in range(3,len(orbitalsLine
                                                .split()),3):
                                    label = "{} {}".format(
                                            orbitalsLine.split()[k],
                                            orbitalsLine.split()[k+1])
                                    if label in orbCompo:
                                        if label not in numIdOrb:
                                            numIdOrb[label] = 2
                                            label = "{} {}".format(
                                                label, numIdOrb[label])
                                        else:
                                            numIdOrb[label] += 1
                                            label = "{} {}".format(
                                                label, numIdOrb[label])
                                    orbCompo[label] = float(
                                        orbitalsLine.split()[k+2])
                else:
                    self.orbitals[i] = "None"
                
                #Reorder orbitals by energy because they are ordered by
                #occupation in MOLPRO output
                if energyReorder and self.orbitals[i] != "None":
                    self.orbitals[i] = reordering(self.orbitals[i],
                                                  self.calcTypes[i])

    def getPartialCharges(self):
        """Get the partial atomic charges"""
        self.pop = dict()
        if self.software == "Molpro":
            for i, l in self.limitLines.items():
                if 'POP' in self.calcTypes[i]: 
                    self.pop[i] = dict()
                    for j,line in enumerate(self.fileLines[l[0]:l[1]]):
                        if line.startswith(' Unique atom'):
                            popStartLineN = l[0] + j + 1
                            break
                    for popLine in self.fileLines[popStartLineN:l[1]]:
                        if popLine.isspace():
                            break
                        if popLine.split()[8] == '+':
                            self.pop[i][popLine.split()[1]] = \
                                float(popLine.split()[9])
                        elif popLine.split()[8] == '-':
                            self.pop[i][popLine.split()[1]] = \
                                -float(popLine.split()[9])
        

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
                        if float(splitLine[-1]) == self.cpuTimeSec[key]:
                            already = True
                            break
                if not already:
                    for ct in self.calcTypes[key]:
                        cpuTimeFile.write('{} '.format(ct))
                    cpuTimeFile.write('{} {} {} {}\n'.format(
                        self.method[key], self.basis[key], self.numberAtoms,
                        self.cpuTimeSec[key])
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
                                                         self.cpuTimeSec[key])
                                  )
            cpuTimeFile.close()
