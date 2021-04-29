import tkinter as tk
import tkinter.filedialog as tkfd
from tkinter import messagebox as mb

import fileClass as fc
import plotFuncs as pf


class mainWindow(tk.Tk):
    """Main window of OSCQAR software, show software, method, basis set,
    calculations can be opened without any file"""

    def __init__(self):
        """Create main window without any file"""
        tk.Tk.__init__(self)
        self.title('OSCQAR')
        self.nameFrame = tk.Frame(self, bd=2)
        nameLabel = tk.Label(self.nameFrame, text='')
        self.infoFrame = tk.Frame(self, bd=2, pady=5)
        softLabel = tk.Label(self.infoFrame,
                             text='Software:             ')
        methodLabel = tk.Label(self.infoFrame,
                               text='Method:             ')
        basisLabel = tk.Label(self.infoFrame,
                              text='Basis set:           ')
        self.calcFrame = tk.Frame(self, bd=2, pady=5)
        calcLabel = tk.Label(self.calcFrame, text='Calculations:')
        calcList = tk.Listbox(self.calcFrame, width=20)

        buttonFrame = tk.Frame(self, borderwidth=2)
        quitButton = tk.Button(buttonFrame, text="Quit", command=self.quit)

        mainMenuBar = tk.Menu(self)
        mainFileMenu = tk.Menu(mainMenuBar, tearoff=0)
        mainFileMenu.add_command(label='Open', command=lambda: self.openFile())
        mainMenuBar.add_cascade(label='File', menu=mainFileMenu)

        self.config(menu=mainMenuBar)

        self.nameFrame.grid(column=0, row=0, columnspan=2)
        nameLabel.pack()
        self.infoFrame.grid(column=0, row=1)
        softLabel.pack()
        methodLabel.pack()
        basisLabel.pack()
        self.calcFrame.grid(column=1, row=1)
        calcLabel.pack()
        calcList.pack()
        buttonFrame.grid(column=0, row=3, columnspan=2, sticky='we')
        quitButton.pack(side='right', padx=5)

        self.grid_columnconfigure(0, weight=1)

    def openFile(self, filepath='noFile'):
        """Open a file in main window, either with file name in argument
        or via a graphic interface"""
        if filepath == 'noFile':
            filepath = tkfd.askopenfilename(title="Open a new file",
                                            filetypes=[('Gaussian files',
                                                        '.out'),
                                                       ('all files', '.*')])
        outputFile = fc.File(filepath)
        outputFile.infoCalcs(False)

        self.nameFrame.grid_forget()
        self.nameFrame.destroy()
        self.infoFrame.grid_forget()
        self.infoFrame.destroy()
        self.calcFrame.grid_forget()
        self.calcFrame.destroy()

        self.nameFrame = tk.Frame(self, bd=2)
        nameLabel = tk.Label(self.nameFrame, text=outputFile.shortName)
        self.infoFrame = tk.Frame(self, bd=2, pady=5)
        softLabel = tk.Label(self.infoFrame,
                             text='Software: ' + outputFile.software)
        methodLabel = tk.Label(self.infoFrame,
                               text='Method: ' + outputFile.method[1])
        basisLabel = tk.Label(self.infoFrame,
                              text='Basis set: ' + outputFile.basis[1])
        self.calcFrame = tk.Frame(self, bd=2, pady=5)
        calcLabel = tk.Label(self.calcFrame, text='Calculations:')
        cln = list()
        for k in outputFile.calcTypes:
            for v in outputFile.calcTypes[k]:
                cln.append(len(str(v)))
        clnmax = sorted(cln)[-1]
        calcList = tk.Listbox(self.calcFrame, width=clnmax)

        for k in outputFile.calcTypes:
            for c in outputFile.calcTypes[k]:
                calcList.insert('end', c)
        calcList.select_set(0)

        buttonFrame = tk.Frame(self, borderwidth=2)
        quitButton = tk.Button(buttonFrame, text="Quit", command=self.quit)
        showButton = tk.Button(buttonFrame, text="Show",
                               command=lambda: self.new_window(outputFile,
                                                               calcList))
        geoButton = tk.Button(buttonFrame, text="Geometry",
                              command=lambda: self.new_window(outputFile,
                                                              calcList, True))

        self.nameFrame.grid(column=0, row=0, columnspan=2)
        nameLabel.pack()
        self.infoFrame.grid(column=0, row=1)
        softLabel.pack()
        methodLabel.pack()
        basisLabel.pack()
        self.calcFrame.grid(column=1, row=1)
        calcLabel.pack()
        calcList.pack()
        buttonFrame.grid(column=0, row=3, columnspan=2, sticky='we')
        quitButton.pack(side='right', padx=5)
        showButton.pack(side='left', padx=5)
        geoButton.pack(side='left', padx=5)

        self.grid_columnconfigure(0, weight=1)

    def new_window(self, outputFile, calcList, openGeoWindow=False):
        """Open a new window for plotting spectra or energy convergence"""
        clc = calcList.curselection()
        if len(clc) == 0:
            clc = (0,)
        if openGeoWindow:
            _class = geoWindow
        else:
            if outputFile.calcTypes[clc[0]+1][0] \
                    == 'Anharmonic frequency calculation'\
                    or outputFile.calcTypes[clc[0]+1][0] \
                    == 'Frequency calculation':
                _class = specWindow
            elif outputFile.calcTypes[clc[0]+1][0] == 'Geometry optimization':
                _class = energyWindow
            else:
                _class = 'Unknown'

        if _class == 'NotSupported':
            mb.showwarning(
                'Warning', 'Nothing to show for this type of calculation')
        elif _class == 'Unknown':
            mb.showwarning(
                'Warning',
                'There was a problem in the selection of the calculation')
        else:
            self.new = tk.Toplevel(self)
            _class(self.new, outputFile, clc[0]+1)

    def close_window(self):
        """Close main window"""
        self.master.destroy()


class specWindow(tk.Toplevel):
    """Window for plotting spectra, fwhm, normalisation, title can be changed,
    New files can be opened and several spectra can be plotted together"""

    def __init__(self, master, outputFile, n):
        """Create spectra window"""
        freqs = dict()
        ints = dict()
        outputFile.getSpectrum()
        if outputFile.specType == 'harmonic':
            fqs, its = outputFile.buildHarmSpecLists()
            freqs[outputFile.shortName] = fqs
            ints[outputFile.shortName] = its
        elif outputFile.specType == 'anharmonic':
            hfqs, hits = outputFile.buildHarmSpecLists()
            freqs[outputFile.shortName+' harmonic'] = hfqs
            ints[outputFile.shortName+' harmonic'] = hits
            afqs, aits = outputFile.buildAnharmSpecLists()
            freqs[outputFile.shortName+' anharmonic'] = afqs
            ints[outputFile.shortName+' anharmonic'] = aits
        fwhmDefVal = 10
        specTitleDef = 'Infrared spectrum'
        self.master = master
        self.master.title('Infrared spectrum')
        specMenubar = tk.Menu(self.master)
        specFileMenu = tk.Menu(specMenubar, tearoff=0)
        specFileMenu.add_command(label="Open",
                                 command=lambda: self.openSpecFile(freqs,
                                                                   ints,
                                                                   specList))
        specMenubar.add_cascade(label="File", menu=specFileMenu)
        specFTCadre = tk.Frame(self.master, borderwidth=2)
        specFigTitle = tk.StringVar()
        specFigTitle.set(specTitleDef)
        specFTTxt = tk.Label(specFTCadre, text='Figure title: ')
        specFTEntry = tk.Entry(specFTCadre, textvariable=specFigTitle,
                               width=30)
        specPRMCadre = tk.Frame(self.master, borderwidth=2)
        fwhmV = tk.IntVar()
        fwhmV.set(fwhmDefVal)
        fwhmL = tk.Label(specPRMCadre, text='FWHM: ')
        fwhmBox = tk.Spinbox(specPRMCadre, from_=0, to=100,
                             increment=1, textvariable=fwhmV, width=5)
        normV = tk.BooleanVar()
        normB = tk.Checkbutton(specPRMCadre, text="Normalized", variable=normV,
                               onvalue=True, offvalue=False)
        normB.select()

        specListCadre = tk.Frame(self.master, borderwidth=2)
        specListTxt = tk.Label(specListCadre,
                               text='Choose the spectra to draw: ')
        ln = list()
        for k in freqs.keys():
            ln.append(len(k))
        lnmax = sorted(ln)[-1]
        specList = tk.Listbox(specListCadre, selectmode="multiple",
                              width=lnmax)

        for ch in freqs.keys():
            specList.insert('end', ch)

        specBTNCadre = tk.Frame(self.master, borderwidth=2)
        specDrawBTN = tk.Button(specBTNCadre, text="Draw",
                                command=lambda: self.drawSpec(specFigTitle,
                                                              specList,
                                                              fwhmV,
                                                              normV,
                                                              freqs,
                                                              ints))
        specCloseBTN = tk.Button(specBTNCadre, text="Close",
                                 command=self.close_SpecWindow)

        self.master.config(menu=specMenubar)
        specFTCadre.pack(side='top', padx=10, pady=10)
        specBTNCadre.pack(side='bottom', fill='x', padx=5)
        specPRMCadre.pack(side='left', padx=10, pady=10)
        specListCadre.pack(side='right', padx=10, pady=10)
        specFTTxt.pack(side='left')
        specFTEntry.pack(side='right')
        normB.grid(row=0, column=0, columnspan=2, pady=5)
        fwhmL.grid(row=1, column=0, pady=5)
        fwhmBox.grid(row=1, column=1, pady=5)
        specListTxt.pack(side='top')
        specList.pack(side='bottom')
        specDrawBTN.pack(side='left')
        specCloseBTN.pack(side='right')

    def close_SpecWindow(self):
        """Close spectra window"""
        self.master.destroy()

    def drawSpec(self, figTitle, specList, fwhmV, normV, freqs, ints):
        """Draw the spectra with matplotlib"""
        freqsDrawned = dict()
        intsDrawned = dict()
        ft = figTitle.get()
        sl = specList.curselection()
        if len(sl) == 0:
            sl = (0,)
        fwhm = fwhmV.get()
        norm = normV.get()
        for s in sl:
            key = list(freqs.keys())[s]
            freqsDrawned[key] = freqs[key]
            intsDrawned[key] = ints[key]
        pf.tkPlotSpectrum(freqsDrawned, intsDrawned, fwhm, ft, 1, norm)

    def openSpecFile(self, freqs, ints, specList):
        """Open a new file"""
        filepath = tkfd.askopenfilename(title="Open a new file",
                                        filetypes=[('Gaussian files', '.out'),
                                                   ('all files', '.*')])
        newOutputFile = fc.File(filepath)
        newOutputFile.infoCalcs(False)
        newOutputFile.getSpectrum()
        if newOutputFile.specType == 'harmonic':
            fqs, its = newOutputFile.buildHarmSpecLists()
            freqs[filepath.split('/')[-1]] = fqs
            ints[filepath.split('/')[-1]] = its
            specList.insert('end', filepath.split('/')[-1])
        elif newOutputFile.specType == 'anharmonic':
            hfqs, hits = newOutputFile.buildHarmSpecLists()
            specList.insert('end', filepath.split('/')[-1]+' harmonic')
            freqs[filepath.split('/')[-1]+' harmonic'] = hfqs
            ints[filepath.split('/')[-1]+' harmonic'] = hits
            afqs, aits = newOutputFile.buildAnharmSpecLists()
            specList.insert('end', filepath.split('/')[-1]+' anharmonic')
            freqs[filepath.split('/')[-1]+' anharmonic'] = afqs
            ints[filepath.split('/')[-1]+' anharmonic'] = aits


class geoWindow(tk.Toplevel):
    """Window for plotting geometry"""

    def __init__(self, master, outputFile, n):
        """Create geometry window"""
        outputFile.getGeo()
        energies = outputFile.getEnergy()
        geoTitleDef = 'Geometry'
        eltScaleDefVal = 1.0
        self.master = master
        self.master.title(geoTitleDef)
        geoMenubar = tk.Menu(self.master)
        geoFileMenu = tk.Menu(geoMenubar, tearoff=0)
        geoFileMenu.add_command(label="Open", command=lambda:
                                self.openGeoFile())
        geoMenubar.add_cascade(label="File", menu=geoFileMenu)
        geoFTCadre = tk.Frame(self.master, borderwidth=2)
        geoFigTitle = tk.StringVar()
        geoFigTitle.set(geoTitleDef)
        geoFTtxt = tk.Label(geoFTCadre, text='Figure title: ')
        geoFTEntry = tk.Entry(geoFTCadre, textvariable=geoFigTitle, width=15)
        geoPRMCadre = tk.Frame(self.master, borderwidth=2)
        eltScaleV = tk.DoubleVar()
        eltScaleV.set(eltScaleDefVal)
        eltScaleL = tk.Label(geoPRMCadre, text='Elements scale: ')
        eltScaleBox = tk.Spinbox(geoPRMCadre, from_=0, to=10,
                                 increment=0.1, textvariable=eltScaleV,
                                 width=5)
        geoBTNCadre = tk.Frame(self.master, borderwidth=2)
        geoDrawBtn = tk.Button(geoBTNCadre, text="Draw",
                               command=lambda: self.drawGeo(outputFile.geos,
                                                            geoFigTitle,
                                                            geoList,
                                                            eltScaleV, n))
        geoCloseBtn = tk.Button(geoBTNCadre, text="Close",
                                command=self.close_GeoWindow)
        geoListCadre = tk.Frame(self.master, borderwidth=2)
        geoListTxt = tk.Label(geoListCadre,
                              text='Choose the geometry to draw: ')

        geoList = tk.Listbox(geoListCadre, selectmode="browse",
                             width=25)

        for i in range(len(outputFile.geos[n]), 0, -1):
            geoList.insert('end', '{} : {} a.u'.format(i, energies[n][i-1]))

        geoList.select_set(0)

        self.master.config(menu=geoMenubar)
        geoPRMCadre.pack(side='left', padx=10, pady=10)
        geoFTCadre.pack(side='top', padx=10, pady=10)
        geoBTNCadre.pack(side='bottom', fill='x', padx=5)
        geoListCadre.pack(side='right', padx=10, pady=10)
        geoFTtxt.pack(side='left')
        geoFTEntry.pack(side='right')
        geoListTxt.pack(side='top')
        geoList.pack(side='bottom')
        eltScaleL.grid(row=1, column=0, pady=5)
        eltScaleBox.grid(row=1, column=1, pady=5)
        geoDrawBtn.pack(side='left')
        geoCloseBtn.pack(side='right')

    def drawGeo(self, geos, figTitle, geoList, eltScaleV, n):
        ft = figTitle.get()
        gl = geoList.curselection()
        if len(gl) == 0:
            gl = (0,)
        gl2 = int(geoList.get(gl)[0].split()[0]) - 1
        geo = geos[n][gl2]
        elementScale = eltScaleV.get()
        pf.tkPlotGeo(geo, elementScale, ft)

    def close_GeoWindow(self):
        """Close geo window"""
        self.master.destroy()


class energyWindow(tk.Toplevel):
    """Window for plotting energy convergence"""

    def __init__(self, master, outputFile, n):
        """Create energy window"""
        energies = outputFile.getEnergy()
        energyTitleDef = 'Energy convergence'
        self.master = master
        self.master.title('Energy convergence')
        energyMenubar = tk.Menu(self.master)
        energyFileMenu = tk.Menu(energyMenubar, tearoff=0)
        energyFileMenu.add_command(label="Open",
                                   command=lambda: self.openEnergyFile(
                                       energies))
        energyMenubar.add_cascade(label="File", menu=energyFileMenu)
        energyFTCadre = tk.Frame(self.master, borderwidth=2)
        energyFigTitle = tk.StringVar()
        energyFigTitle.set(energyTitleDef)
        energyFTtxt = tk.Label(energyFTCadre, text='Figure title: ')
        energyFTEntry = tk.Entry(energyFTCadre, textvariable=energyFigTitle,
                                 width=30)
        energyBTNCadre = tk.Frame(self.master, borderwidth=2)
        energyDrawBtn = tk.Button(energyBTNCadre, text="Draw",
                                  command=lambda:
                                      self.drawEnergy(energies,
                                                      energyFigTitle))
        energyCloseBtn = tk.Button(energyBTNCadre, text="Close",
                                   command=self.close_EnergyWindow)

        self.master.config(menu=energyMenubar)
        energyFTCadre.pack(side='top', padx=10, pady=10)
        energyBTNCadre.pack(side='bottom', fill='x', padx=5)
        energyFTtxt.pack(side='left')
        energyFTEntry.pack(side='right')
        energyDrawBtn.pack(side='left')
        energyCloseBtn.pack(side='right')

    def drawEnergy(self, energies, figTitle):
        """Draw energy convergence with matplotlib (work in progress)"""
        ft = figTitle.get()
        pf.tkPlotEnergy(energies[1], ft)

    def openEnergyFile(self, energies):
        """Open a new energy file (doesn't work right now !)"""
        filepath = tkfd.askopenfilename(title="Open a new file",
                                        filetypes=[('Gaussian files', '.out'),
                                                   ('all files', '.*')])
        newOutputFile = fc.File(filepath)
        newOutputFile.infoCalcs(False)
        newEnergies = newOutputFile.getEnergy()

    def close_EnergyWindow(self):
        """Close energy window"""
        self.master.destroy()
