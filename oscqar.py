import argparse
# import readline

import fileClass as fc
import plotFuncs as pf
import tkWindowClasses as tkw

# readline.parse_and_bind("tab: complete")
# readline.parse_and_bind('set editing-mode vi')
# readline.set_completer_delims(' \t\n=')

parser = argparse.ArgumentParser()
parser.add_argument("fileName", type=str, nargs='?',
                    help="The name of the file you want to read,\
                    no name will open the visual mode")
parser.add_argument("-q", "--quick", action="store_true", default=False,
                    help="Enable quick mode for the chosen action")
parser.add_argument("-e", "--energy", action="store_true", default=False,
                    help="Get the final energy and energy convergence")
parser.add_argument("-g", "--geometry", action="store_true", default=False,
                    help="Get the geometry of the system")
parser.add_argument("-s", "--spectrum", action="store_true", default=False,
                    help="Get the frequencies and intensities\
                    and plot spectrum")
parser.add_argument("-v", "--visual", action="store_true", default=False,
                    help="Open the visual interface")
parser.add_argument("-t", "--time", action="store_true", default=False,
                    help="Record CPU time")
parser.add_argument("-pe", "--plotElements", action="store_true",
                    default=False, help="Plot element appearances")
args = parser.parse_args()

if not args.fileName:
    # Open visual interface without a file
    mw = tkw.mainWindow()
    mw.mainloop()
else:

    if args.visual:
        # Open visual interface with a file
        mw = tkw.mainWindow()
        mw.openFile(args.fileName)
        mw.mainloop()
    else:
        outputFile = fc.File(args.fileName)
        outputFile.infoCalcs()

        if args.energy:
            if args.quick:
                energy = outputFile.getEnergyQuick()
                print(energy)
            else:
                energies = outputFile.getEnergy()
                for i, ct in outputFile.calcTypes.items():
                    print('{} : {} a.u'.format(i, energies[i][-1]))
                    if 'Geometry optimization' in ct:
                        pf.plotEnergy(energies[i])

        if args.geometry:
            outputFile.getGeo()
            if args.quick:
                pf.plotGeo(outputFile.geos[1])
            else:
                calcNumb = input('Which calculations ?\n')
                isInt = False
                isGood = False
                while not isInt and not isGood:
                    try:
                        calcNumb = int(calcNumb)
                        isInt = True
                    except:
                        calcNumb = int(input('Wrong type of answer, ' +
                                             'please give an integer:\n'))
                        continue
                    if calcNumb not in outputFile.calcTypes.keys():
                        isInt = False
                        print('Please chose between :')
                        for k in outputFile.calcTypes.keys():
                            print(k)
                        calcNumb = input('Which one : ')
                    else:
                        isGood = True
                pf.plotGeo(outputFile.geos[calcNumb])

        if args.spectrum:
            freqs = dict()
            ints = dict()
            outputFile.getSpectrum()
            if outputFile.specType == 'harmonic':
                fqs, its = outputFile.buildHarmSpecLists()
                freqs[outputFile.shortName] = fqs
                ints[outputFile.shortName] = its
            elif outputFile.specType == 'anharmonic':
                fqs, its = outputFile.buildAnharmSpecLists()
                freqs[outputFile.shortName + ' anharmonic'] = fqs
                ints[outputFile.shortName + ' anharmonic'] = its
            pf.plotSpectrum(freqs, ints, 18, 'Infrared spectrum')

        if args.time:
            outputFile.recordTime()

        if args.plotElements:
            pf.plotElements()
