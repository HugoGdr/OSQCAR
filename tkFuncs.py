import tkinter as tk
import tkinter.filedialog as tkfd
import matplotlib.pyplot as plt
import plotFuncs as pf
import fileClass as fc

def openFile(freqs,ints,specList):
    filepath = tkfd.askopenfilename(title="Open a new file",filetypes=[('Gaussian files','.out'),('all files','.*')]) 
    newOutputFile = fc.File(filepath)
    newOutputFile.infoCalcs()
    newOutputFile.getSpectrum()
    newFreqs = dict()
    newInts = dict()
    if newOutputFile.specType == 'harmonic':
        fqs,its = newOutputFile.buildHarmSpecLists()
        freqs[filepath.split('/')[-1]] = fqs
        ints[filepath.split('/')[-1]] = its
        specList.insert('end',filepath.split('/')[-1])
    elif newOutputFile.specType == 'anharmonic':
        hfqs,hits = newOutputFile.buildHarmSpecLists()
        specList.insert('end',filepath.split('/')[-1]+' harmonic')
        freqs[filepath.split('/')[-1]+' harmonic'] = hfqs
        ints[filepath.split('/')[-1]+' harmonic'] = hits
        afqs,aits = newOutputFile.buildAnharmSpecLists()
        specList.insert('end',filepath.split('/')[-1]+' anharmonic')
        freqs[filepath.split('/')[-1]+' anharmonic'] = afqs
        ints[filepath.split('/')[-1]+' anharmonic'] = aits
    

def drawSpec(figTitle,specList,fwhmV,normV,freqs,ints):
    freqsDrawned = dict()
    intsDrawned = dict()
    ft=figTitle.get()
    sl=specList.curselection()
    if len(sl) == 0:
        sl=(0,)
    fwhm = fwhmV.get()
    norm = normV.get()
    for s in sl:
        key = list(freqs.keys())[s]
        freqsDrawned[key] = freqs[key]
        intsDrawned[key] = ints[key]
    pf.tkPlotSpectrum(freqsDrawned,intsDrawned,fwhm,ft,1,norm)

def specWindow(freqs,ints):
    fwhmDefVal = 10
    titleDef = 'Infrared spectrum'
    fen = tk.Tk()
    fen.title("Infrared spectrum")
    menubar = tk.Menu(fen)
    fileMenu = tk.Menu(menubar, tearoff=0)
    fileMenu.add_command(label="Open",command=lambda: openFile(freqs,ints,specList))
    menubar.add_cascade(label="File",menu=fileMenu)
    ftCadre = tk.Frame(fen,borderwidth=2)
    figTitle = tk.StringVar()
    figTitle.set(titleDef)
    fTtxt = tk.Label(ftCadre, text = 'Figure title: ')
    fTEntry = tk.Entry(ftCadre, textvariable=figTitle, width=30)
    prmCadre = tk.Frame(fen,borderwidth=2)
    fwhmV = tk.IntVar()
    fwhmV.set(fwhmDefVal)
    fwhmL = tk.Label(prmCadre, text='FWHM: ')
    fwhmBox = tk.Spinbox(prmCadre, from_=0,to=100,increment=1,textvariable=fwhmV,width=5)
    normV = tk.BooleanVar()
    normB = tk.Checkbutton(prmCadre, text="Normalized", variable = normV, onvalue=True, offvalue=False)
    normB.select()

    listCadre = tk.Frame(fen,borderwidth=2)
    listTxt = tk.Label(listCadre, text = 'Choose the spectra to draw: ')
    ln = list()
    for k in freqs.keys():
        ln.append(len(k))
    lnmax = sorted(ln)[-1]
    specList = tk.Listbox(listCadre,selectmode="multiple",width=lnmax)
            
    for ch in freqs.keys():
        specList.insert('end', ch)

    btnCadre = tk.Frame(fen,borderwidth=2)
    drawBtn = tk.Button(btnCadre, text="Draw", command=lambda: drawSpec(figTitle,specList,fwhmV,normV,freqs,ints))
    quitBtn = tk.Button(btnCadre, text="Quit", command=fen.quit)

    fen.config(menu=menubar)
    ftCadre.pack(side='top',padx=10,pady=10)
    btnCadre.pack(side='bottom',fill='x',padx = 5)
    prmCadre.pack(side='left',padx=10,pady=10)
    listCadre.pack(side='right',padx=10,pady=10)
    fTtxt.pack(side='left')
    fTEntry.pack(side='right')
    normB.grid(row=0,column=0,columnspan=2,pady=5)
    fwhmL.grid(row=1,column=0,pady=5)
    fwhmBox.grid(row=1,column=1,pady=5)
    listTxt.pack(side='top')
    specList.pack(side='bottom')
    drawBtn.pack(side='left')
    quitBtn.pack(side='right')

    fen.mainloop()

