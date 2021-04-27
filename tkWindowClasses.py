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

        buttonFrame = tk.Frame(self, borderwidth=2)
        quitButton = tk.Button(buttonFrame, text="Quit", command=self.quit)
        showButton = tk.Button(buttonFrame, text="Show",
                               command=lambda: self.new_window(outputFile,
                                                               calcList))

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

        self.grid_columnconfigure(0, weight=1)

    def new_window(self, outputFile, calcList):
        """Open a new window for plotting spectra or energy convergence"""
        clc = calcList.curselection()
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
            _class(self.new, outputFile)

    def close_window(self):
        """Close main window"""
        self.master.destroy()


class specWindow(tk.Toplevel):
    """Window for plotting spectra, fwhm, normalisation, title can be changed,
    New files can be opened and several spectra can be plotted together"""

    def __init__(self, master, outputFile):
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
        titleDef = 'Infrared spectrum'
        self.master = master
        self.master.title('Infrared spectrum')
        menubar = tk.Menu(self.master)
        fileMenu = tk.Menu(menubar, tearoff=0)
        fileMenu.add_command(label="Open", command=lambda: self.openSpecFile(
            freqs, ints, specList))
        menubar.add_cascade(label="File", menu=fileMenu)
        ftCadre = tk.Frame(self.master, borderwidth=2)
        figTitle = tk.StringVar()
        figTitle.set(titleDef)
        fTtxt = tk.Label(ftCadre, text='Figure title: ')
        fTEntry = tk.Entry(ftCadre, textvariable=figTitle, width=30)
        prmCadre = tk.Frame(self.master, borderwidth=2)
        fwhmV = tk.IntVar()
        fwhmV.set(fwhmDefVal)
        fwhmL = tk.Label(prmCadre, text='FWHM: ')
        fwhmBox = tk.Spinbox(prmCadre, from_=0, to=100,
                             increment=1, textvariable=fwhmV, width=5)
        normV = tk.BooleanVar()
        normB = tk.Checkbutton(prmCadre, text="Normalized", variable=normV,
                               onvalue=True, offvalue=False)
        normB.select()

        listCadre = tk.Frame(self.master, borderwidth=2)
        listTxt = tk.Label(listCadre, text='Choose the spectra to draw: ')
        ln = list()
        for k in freqs.keys():
            ln.append(len(k))
        lnmax = sorted(ln)[-1]
        specList = tk.Listbox(listCadre, selectmode="multiple", width=lnmax)

        for ch in freqs.keys():
            specList.insert('end', ch)

        btnCadre = tk.Frame(self.master, borderwidth=2)
        drawBtn = tk.Button(btnCadre, text="Draw",
                            command=lambda: self.drawSpec(figTitle,
                                                          specList,
                                                          fwhmV,
                                                          normV,
                                                          freqs,
                                                          ints))
        closeBtn = tk.Button(btnCadre, text="Close", command=self.close_window)

        self.master.config(menu=menubar)
        ftCadre.pack(side='top', padx=10, pady=10)
        btnCadre.pack(side='bottom', fill='x', padx=5)
        prmCadre.pack(side='left', padx=10, pady=10)
        listCadre.pack(side='right', padx=10, pady=10)
        fTtxt.pack(side='left')
        fTEntry.pack(side='right')
        normB.grid(row=0, column=0, columnspan=2, pady=5)
        fwhmL.grid(row=1, column=0, pady=5)
        fwhmBox.grid(row=1, column=1, pady=5)
        listTxt.pack(side='top')
        specList.pack(side='bottom')
        drawBtn.pack(side='left')
        closeBtn.pack(side='right')

    def close_window(self):
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
    def __init__(self, master, outputFile):
        outputFile.getGeo()
        outputFile.plotGeo(1)


class energyWindow(tk.Toplevel):
    """Window for plotting energy convergence"""

    def __init__(self, master, outputFile):
        """Create energy window"""
        energies = outputFile.getEnergy()
        titleDef = 'Energy convergence'
        self.master = master
        self.master.title('Energy convergence')
        menubar = tk.Menu(self.master)
        fileMenu = tk.Menu(menubar, tearoff=0)
        fileMenu.add_command(label="Open", command=lambda: self.openEnergyFile(
            energies))
        menubar.add_cascade(label="File", menu=fileMenu)
        ftCadre = tk.Frame(self.master, borderwidth=2)
        figTitle = tk.StringVar()
        figTitle.set(titleDef)
        fTtxt = tk.Label(ftCadre, text='Figure title: ')
        fTEntry = tk.Entry(ftCadre, textvariable=figTitle, width=30)
        btnCadre = tk.Frame(self.master, borderwidth=2)
        drawBtn = tk.Button(btnCadre, text="Draw",
                            command=lambda: self.drawEnergy(energies,
                                                            figTitle))
        closeBtn = tk.Button(btnCadre, text="Close", command=self.close_window)

        self.master.config(menu=menubar)
        ftCadre.pack(side='top', padx=10, pady=10)
        btnCadre.pack(side='bottom', fill='x', padx=5)
        fTtxt.pack(side='left')
        fTEntry.pack(side='right')
        drawBtn.pack(side='left')
        closeBtn.pack(side='right')

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

    def close_window(self):
        """Close energy window"""
        self.master.destroy()
