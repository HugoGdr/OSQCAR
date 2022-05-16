#!/usr/bin/python3
import argparse
import sys
# import readline

import fileClass as fc
import plotFuncs as pf
import tkWindowClasses as tkw
import ch2PESMolpro as ch2 #Functions specific to my needs

# readline.parse_and_bind("tab: complete")
# readline.parse_and_bind('set editing-mode vi')
# readline.set_completer_delims(' \t\n=')

parser = argparse.ArgumentParser()
parser.add_argument("fileNames", type=str, nargs='*',
                    help="The name of the file you want to read,\
                    no name will open the visual mode")
parser.add_argument("-q", "--quick", action="store_true", default=False,
                    help="Enable quick mode for the chosen action")
parser.add_argument("-e", "--energy", action="store_true", default=False,
                    help="Get the final energy and energy convergence")
parser.add_argument("-g", "--geometry", action="store_true", default=False,
                    help="Get the geometry of the system")
parser.add_argument("-ag", "--animGeo", action="store_true", default=False,
                    help="Plot an animation of the evolution of the system"
                         "geometry")
parser.add_argument("-s", "--spectrum", action="store_true", default=False,
                    help="Get the frequencies and intensities\
                    and plot spectrum")
parser.add_argument("-o", "--orbitals", action="store_true", default=False,
                    help="Get the orbitals energies and print them")
parser.add_argument("-v", "--visual", action="store_true", default=False,
                    help="Open the visual interface")
parser.add_argument("-t", "--time", action="store_true", default=False,
                    help="Record CPU time")
parser.add_argument("-pe", "--plotElements", action="store_true",
                    default=False, help="Plot element appearances")
parser.add_argument("-pc", "--partCharges", action="store_true", default=False,
                    help="Get the partial charges")

# Functionalities specific to CH2+ PES Molpro calculations
parser.add_argument("-pes", "--potNRJSurf", action="store_true", default=False,
                    help="Get the energies and plot them in function\
                          of atomic distance")
parser.add_argument("-ded", "--drawEnergyDiff", action="store_true", \
                    default=False, help="Get the energies and plot the \
                    difference between two levels in function of atomic \
                    distance")
parser.add_argument("-dwf", "--drawWeightFactors", action="store_true", \
                    default=False, help="Get the weight factors and plot them \
                    'in function of atomic distance")
parser.add_argument("-do", "--drawOrbitals", action="store_true", 
                    default=False, help="Get the orbitals energies and plot "
                    "them in function of one coordinate")
parser.add_argument("-doo", "--drawOrbitalsOcc", action="store_true", 
                    default=False, help="Get the orbitals occupations and plot"
                    " them in function of one coordinate")
parser.add_argument("-doc", "--drawOrbitalsCompo", action="store_true", 
                    default=False, help="Get the orbitals composition and plot"
                    " them in function of one coordinate")
parser.add_argument("-docp", "--drawOrbitalsCompoProj", action="store_true", 
                    default=False, help="Get the orbitals composition and plot"
                    " their projection on aos in function of one coordinate")
parser.add_argument("-wo", "--writeOrbitals", action="store_true", 
                    default=False, help="Get the orbitals composition and "
                    " write a file with them")
args = parser.parse_args()

if args.plotElements:
    pf.plotElements()

if not args.fileNames:
    #print('File name missing')
    #sys.exit(1)
    # Open visual interface without a file
    mw = tkw.mainWindow()
    mw.mainloop()
else:
    if args.visual:
#        print('Visual interface not available')
#        sys.exit(1)
        # Open visual interface with a file
        mw = tkw.mainWindow()
        mw.openFile(args.fileName)
        mw.mainloop()
    else:
        outputFiles = list()
        for fileName in args.fileNames:
            outputFile = fc.File(fileName)
            outputFile.infoCalcs()
            outputFiles.append(outputFile)
            

        if args.energy:
            if args.quick:
                for outputFile in outputFiles:
                    energy = outputFile.getEnergyQuick()
                    print(energy)
            else:
                for outputFile in outputFiles:
                    outputFile.getEnergy()
                    for i, ct in outputFile.calcTypes.items():
                        if isinstance(outputFile.energy[i], float):
                            print('{}: {} a.u'.format(i, outputFile.energy[i]))
                        else:
                            print('{}: {}'.format(i, outputFile.energy[i]))
                        if 'Geometry optimization' in ct or 'OPT' in ct:
                            if not "energiess" in locals():
                                energiess = dict()
                            if not outputFile.name in energiess:
                                energiess[outputFile.name] = dict()
                            energiess[outputFile.name][i] = energies[i]
                if "energiess" in locals():
                    pf.plotEnergy(energiess)

        if args.geometry:
            for outputFile in outputFiles:
                outputFile.getGeo()
                if args.quick or len(outputFile.calcTypes.keys()) == 1:
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

        if args.animGeo:
            for outputFile in outputFiles:
                outputFile.getGeo()
                if outputFile.software == 'Molpro':
                    goodGeos=dict()
                    for calc in outputFile.geos:
                        if 'SEWARD' in outputFile.calcTypes[calc]:
                            goodGeos[calc]=outputFile.geos[calc]
                    pf.animateGeo(goodGeos,outputFile.numberAtoms)
                else:
                    pf.animateGeo(outputFile.geos,outputFile.numberAtoms)
            

        if args.spectrum:
            for outputFile in outputFiles:
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

        if args.orbitals:
            #orbitalss = dict()
            #for outputFile in outputFiles:
            #    outputFile.getOrbitals()
            #    orbitalss[outputFile.name] = outputFile.orbitals
            #    for i, ct in outputFile.calcTypes.items():
            #        print('{} : {}'.format(i, outputFile.orbitals[i]))
            #    pf.plotOrbitalsCompo(outputFile.orbitals,outputFile.calcTypes)
            #    
            #pf.plotOrbitals(orbitalss)
            i = 3
            mo = '1.2'
            outputFile.getOrbitals()
            ch2.plotOrbitalsCompoBar(outputFile.orbitals[i][mo])

        if args.partCharges:
            pcss = dict()
            geoss = dict()
            for outputFile in outputFiles:
                outputFile.getGeo()
                geoss[outputFile.name] = outputFile.geos
                outputFile.getPartialCharges()
                pcss[outputFile.name] = outputFile.pop
            ch2.evolPartialCharges(pcss,geoss,True)

        if args.time:
            outputFile.recordTime()

# Functionalities specific to CH2+ PES Molpro calculations
        if args.drawOrbitals:
            for outputFile in outputFiles:
                outputFile.getOrbitals()
                outputFile.getGeo()
                ch2.evolOrbitals(outputFile.orbitals,outputFile.geos,
                                     outputFile.calcTypes)

        if args.drawOrbitalsOcc:
            for outputFile in outputFiles:
                outputFile.getOrbitals()
                outputFile.getGeo()
                ch2.evolOrbitalsOcc(outputFile.orbitals,outputFile.geos,
                                     outputFile.calcTypes)

        if args.drawOrbitalsCompo:
            for outputFile in outputFiles:
                outputFile.getOrbitals()
                outputFile.getGeo()
                ch2.evolOrbitalsCompo(outputFile.orbitals,outputFile.geos,
                                     outputFile.calcTypes,outputFile.symNumb,
                                     normalized=True)

        if args.drawOrbitalsCompoProj:
            for outputFile in outputFiles:
                outputFile.getOrbitals()
                outputFile.getGeo()
                ch2.evolOrbitalsCompoProj(outputFile.orbitals,outputFile.geos,
                    outputFile.calcTypes,outputFile.symNumb)

        if args.writeOrbitals:
            for outputFile in outputFiles:
                orbFileName = outputFile.name.split('.')[0] + '.orb'
                outputFile.getOrbitals()
                ch2.writeOrbFile(outputFile.orbitals,orbFileName)

        if args.potNRJSurf:
            energiess = dict()
            geoss = dict()
            calcTypess = dict()
            for outputFile in outputFiles:
                outputFile.getEnergy()
                energiess[outputFile.name] = outputFile.energies
                outputFile.getGeo()
                geoss[outputFile.name] = outputFile.geos
                calcTypess[outputFile.name] = outputFile.calcTypes
            ch2.pes(energiess,geoss,calcTypess,grouping='sameMethod',
                    saveData=False)

        if args.drawEnergyDiff:
            energiess = dict()
            geoss = dict()
            calcTypess = dict()
            for outputFile in outputFiles:
                outputFile.getEnergy()
                energiess[outputFile.name] = outputFile.energies
                outputFile.getGeo()
                geoss[outputFile.name] = outputFile.geos
                calcTypess[outputFile.name] = outputFile.calcTypes
            ch2.evolEnergyDiff(energiess,geoss,calcTypess,'sameMethod')

        if args.drawWeightFactors:
            wfss = dict()
            geoss = dict()
            for outputFile in outputFiles:
                outputFile.getEnergy()
                wfss[outputFile.name] = outputFile.weightFactors
                outputFile.getGeo()
                geoss[outputFile.name] = outputFile.geos
            ch2.evolWF(wfss,geoss)


