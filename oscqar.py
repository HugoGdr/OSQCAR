#!/usr/local/bin/python3.8

import sys
import argparse
import matplotlib.pyplot as plt
import tkinter as tk

from fileClass import *
from tools import *

parser = argparse.ArgumentParser()
parser.add_argument("fileName", type=str, help="The name of the file you want to read")
parser.add_argument("-q", "--quick", action="store_true", default=False, help="Execute the program as quickly as possible")
parser.add_argument("-e", "--energy", action="store_true", default=False, help="Get the total energy of the system")
parser.add_argument("-g", "--geometry", action="store_true", default=False, help="Get the geometry of the system")
parser.add_argument("-s", "--spectrum", action="store_true", default=False, help="Get the frequencies and intensities")
args = parser.parse_args()

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
    outputFile.getSpectrum()
    if args.quick:
        outputFile.plotSpectrum(18,1)
    else:
        fwhm = input('What FWHM?\n')
        while True:
            try:
                fwhm = float(fwhm)
                break
            except:
                fwhm = input('Please give a floating number:\n')
        outputFile.plotSpectrum(fwhm,1)
                
        

