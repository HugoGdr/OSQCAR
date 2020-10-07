#!/usr/local/bin/python3.8

import sys
import argparse
import matplotlib.pyplot as plt
import readline

from fileClass import *
from plotFuncs import *

readline.parse_and_bind("tab: complete")
readline.parse_and_bind('set editing-mode vi')
readline.set_completer_delims(' \t\n=')

parser = argparse.ArgumentParser()
parser.add_argument("fileName", type=str, help="The name of the file you want to read")
parser.add_argument("-q", "--quick", action="store_true", default=False, help="Execute the program as quickly as possible")
parser.add_argument("-e", "--energy", action="store_true", default=False, help="Get the total energy of the system")
parser.add_argument("-g", "--geometry", action="store_true", default=False, help="Get the geometry of the system")
parser.add_argument("-s", "--spectrum", action="store_true", default=False, help="Get the frequencies and intensities and plot spectrum")
parser.add_argument("-ms", "--multispectra", action="store_true", default=False, help="Get the frequencies and intensities and plot spectra from several files")
args = parser.parse_args()

if args.multispectra:
    freqs = dict()
    ints = dict()
    fName = args.fileName
    fwhm = input('What FWHM?\n')
    while True:
        try:
            fwhm = float(fwhm)
            break
        except:
            fwhm = input('Please give a floating number:\n')
    while 1:
        outputFile = File(fName)
        outputFile.infoCalcs()
        outputFile.getSpectrum()
        if outputFile.specType == 'harmonic':
            fqs,its = outputFile.buildHarmSpecLists()
        elif outputFile.specType == 'anharmonic':
            fqs,its = outputFile.buildAnharmSpecLists()
        else:
                print("No specType specified")
                sys.exit(1)
        freqs[fName.split('/')[-1]] = fqs
        ints[fName.split('/')[-1]] = its
        plotSpectrum(freqs,ints,fwhm,'Infrared spectrum')
        newFile = input('If you want to add another file type its name, else type stop \n')
        if newFile.lower() == 'stop':
            break
        else:
            fName = newFile

else:

    outputFile = File(args.fileName)
    outputFile.infoCalcs()

    if args.energy:
        if args.quick:
            energy = outputFile.getEnergyQuick()
            print(energy)
        else:
            energies = outputFile.getEnergy()
            for i,ct in outputFile.calcTypes.items():
                print(i,energies[i][-1])
                if 'Geometry optimization' in ct:
                    plt.ion()
                    plt.xlabel('Iteration')
                    plt.ylabel(r'Energy (a.u.)')
                    plt.plot(energies[i])
            plt.show()
            plt.pause(0.001)
            input("Press Enter to continue")
            plt.close()
    
    if args.geometry:
        outputFile.getGeo()
        if args.quick:
            outputFile.plotGeo(1)
        else:
            calcNumb = input('Which calculations ?\n')
            isInt = False
            isGood = False
            while not isInt and not isGood:
                try:
                    calcNumb = int(calcNumb)
                    isInt = True
                except:
                    calcNumb = input('Wrong type of answer, please give an integer:\n')
                    continue
                if int(calcNumb) not in outputFile.calcTypes.keys():
                    isInt = False
                    print('Please chose between :')
                    for k in outputFile.calcTypes.keys():
                        print(k)
                    calcNumb = input('Which one : ')
                else:
                    isGood = True
            outputFile.plotGeo(calcNumb)
                    
    if args.spectrum:
        freqs = dict()
        ints = dict()
        outputFile.getSpectrum()
        if args.quick:
            outputFile.plotHarmSpectrum(18,1)
        else:
            fwhm = input('What FWHM?\n')
            while True:
                try:
                    fwhm = float(fwhm)
                    break
                except:
                    fwhm = input('Please give a floating number:\n')
            fqs = list()
            its = list()
            if outputFile.software == "Gaussian":
                for key,calcType in outputFile.calcTypes.items():
                    if 'Frequency calculation' in calcType:
                        fqs,its = outputFile.buildHarmSpecLists()
                        freqs[args.fileName.split('/')[-1]] = fqs
                        ints[args.fileName.split('/')[-1]] = its
                        break
                    elif "Anharmonic frequency calculation" in calcType:
                        fqs,its = outputFile.buildHarmSpecLists()
                        freqs[args.fileName.split('/')[-1]+' harm'] = fqs
                        ints[args.fileName.split('/')[-1]+' harm'] = its
                        fqs,its = outputFile.buildAnharmSpecLists()
                        freqs[args.fileName.split('/')[-1]+' anharm'] = fqs
                        ints[args.fileName.split('/')[-1]+' anharm'] = its
                        break
            plotSpectrum(freqs,ints,fwhm,'Infrared spectrum')
                
        

