import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib import collections as mc
from matplotlib.pyplot import cm
import numpy as np
import sys
import pickle

def distance(geo,atom1,atom2):
    dist = pow(pow(geo[atom1][1][0]-geo[atom2][1][0],2) + #x
               pow(geo[atom1][1][1]-geo[atom2][1][1],2) + #y
               pow(geo[atom1][1][2]-geo[atom2][1][2],2), #z
               0.5)
    return dist

def jacobi(geo,a1,a2,a3):
    """Return jacobi coordinates for a 3 atoms system, rs is distance between
    atoms a1 and a2, Rl is distance from center of mass of a1 and a2 to a3,
    theta is angle between rs and Rl"""    
    convAng = 1/np.pi*180
    m1 = geo[a1][0]
    m2 = geo[a2][0]
    m3 = geo[a3][0]
    x1 = geo[a1][1][0]
    y1 = geo[a1][1][1]
    z1 = geo[a1][1][2]
    x2 = geo[a2][1][0]
    y2 = geo[a2][1][1]
    z2 = geo[a2][1][2]
    x3 = geo[a3][1][0]
    y3 = geo[a3][1][1]
    z3 = geo[a3][1][2]
    M = m1 + m2
    rs = pow(pow(x1-x2,2) + pow(y1-y2,2) + pow(z1-z2,2), 0.5)
    xcom = x1*m1/M + x2*m2/M
    ycom = y1*m1/M + y2*m2/M
    zcom = z1*m1/M + z2*m2/M
    Rl = pow(pow(xcom-x3,2) + pow(ycom-y3,2) + pow(zcom-z3,2), 0.5)
    r13 = pow(pow(x1-x3,2) + pow(y1-y3,2) + pow(z1-z3,2), 0.5)
    r1com = pow(pow(xcom-x1,2) + pow(ycom-y1,2) + pow(zcom-z1,2), 0.5)
    if Rl == 0.0 or r13 == 0.0:
        theta = 0.0
    else:
        theta = np.arccos((pow(Rl,2)+pow(r1com,2)-pow(r13,2))/(2*Rl*r1com))\
                *convAng
    return Rl,rs,theta
                
def writeOrbFile(orbitals,outputFileName):
    orbFile = open(outputFileName, 'w')
    for calc in orbitals:
        if orbitals[calc] != 'None':
            for mo in orbitals[calc]:
                orbFile.write('Orbital {}\n'.format(mo))
                for ao in orbitals[calc][mo][2]:
                    orbFile.write('{}: {}\n'.format(ao,
                                                    orbitals[calc][mo][2][ao]))
    print('File {} written'.format(outputFileName))
    orbFile.close()
    

def evolOrbitals(orbitals,geos,calcTypes):
    rightCalcTypes = ['RHF-SCF','UHF-SCF','MULTI']
    lstyles = ['solid','dashed', 'dotted', 'dashdot']
    uCalcTypes = list()
    for i in calcTypes:
        if calcTypes[i][0] in rightCalcTypes:
            if calcTypes[i][0] not in uCalcTypes:
                uCalcTypes.append(calcTypes[i][0])
    n = 1
    for ct in uCalcTypes:
        dists = list()
        if ct == 'UHF-SCF':
            mos_a = dict()
            mos_b = dict()
        else:
            mos = dict()
        for i in orbitals.keys():
            if calcTypes[i][0] == ct:
                if orbitals[i] != "None":
                    for key in orbitals[i].keys():
                        if ct == 'UHF-SCF':
                            if key not in mos_a:
                                mos_a[key] = list()
                                if len(orbitals[i][key]) > 3:
                                    mos_b[key] = list()
                        else:
                            if key not in mos:
                                mos[key] = list()
                    for geo in geos[i]:
                        #distance between H1 and C
                        Rl,rs,theta = jacobi(geo,'1','2','3')
                        #dist = Rl
                        dist = rs
                        #dist = theta
                        dists.append(dist)
                    if ct == 'UHF-SCF':
                        for key in orbitals[i].keys():
                            mos_a[key].append(orbitals[i][key][0])
                            if len(orbitals[i][key]) > 3:
                                mos_b[key].append(orbitals[i][key][3])
                    else:
                        for key in orbitals[i].keys():
                            mos[key].append(orbitals[i][key][0])
        if ct == 'UHF-SCF':
            plt.figure(n)
            plt.title("{} alpha".format(ct))
            for key in mos_a.keys():
                ls = lstyles[int(key.split(".")[-1])-1]
                plt.plot(dists, mos_a[key],linestyle=ls)
            plt.legend(mos_a.keys(),loc='upper right')
            plt.xlabel(r'R$_{l}$ (angstrom)')
            plt.ylabel('Energy (u.a)')
            n += 1
            plt.figure(n)
            plt.title("{} beta".format(ct))
            for key in mos_b.keys():
                ls = lstyles[int(key.split(".")[-1])-1]
                plt.plot(dists, mos_b[key],linestyle=ls)
            plt.legend(mos_b.keys(),loc='upper right')
            #plt.xlabel(r'R$_{l}$ (angstrom)')
            plt.xlabel(r'r$_{s}$ (angstrom)')
            #plt.xlabel(r'theta (degree)')
            plt.ylabel('Energy (u.a)')
        else:
            plt.figure(n)
            plt.title(ct)
            for key in mos.keys():
                ls = lstyles[int(key.split(".")[-1])-1]
                plt.plot(dists, mos[key],linestyle=ls)
            plt.legend(mos.keys(),loc='upper right')
            #plt.xlabel(r'R$_{l}$ (angstrom)')
            plt.xlabel(r'r$_{s}$ (angstrom)')
            #plt.xlabel(r'theta (degree)')
            plt.ylabel('Energy (u.a)')
        n += 1
    plt.show()
    plt.close()

def evolOrbitalsOcc(orbitals,geos,calcTypes):
    rightCalcTypes = ['RHF-SCF','UHF-SCF','MULTI']
    lstyles = ['solid','dashed', 'dotted', 'dashdot']
    uCalcTypes = list()
    intMOs = dict()
    for i in calcTypes:
        if calcTypes[i][0] in rightCalcTypes:
            if calcTypes[i][0] not in uCalcTypes:
                uCalcTypes.append(calcTypes[i][0])
    n = 1
    for ct in uCalcTypes:
        if ct not in intMOs:
            intMOs[ct] = list()
        dists = list()
        if ct == 'UHF-SCF':
            mos_a = dict()
            mos_b = dict()
        else:
            mos = dict()
        for i in orbitals.keys():
            if calcTypes[i][0] == ct:
                if orbitals[i] != "None":
                    for key in orbitals[i].keys():
                        if ct == 'UHF-SCF':
                            if key not in mos_a:
                                mos_a[key] = list()
                                if len(orbitals[i][key]) > 3:
                                    mos_b[key] = list()
                        else:
                            if key not in mos:
                                mos[key] = list()
                    for geo in geos[i]:
                        #distance between H1 and C
                        Rl,rs,theta = jacobi(geo,'1','2','3')
                        dists.append(Rl)
                    if ct == 'UHF-SCF':
                        for key in orbitals[i].keys():
                            mos_a[key].append(orbitals[i][key][1])
                            if orbitals[i][key][1] != 0 and \
                               key not in intMOs[ct]:
                                intMOs[ct].append(key)
                            if len(orbitals[i][key]) > 3:
                                mos_b[key].append(orbitals[i][key][4])
                                if orbitals[i][key][4] != 0 and \
                                   key not in intMOs[ct]:
                                    intMOs[ct].append(key)
                    else:
                        for key in orbitals[i].keys():
                            mos[key].append(orbitals[i][key][1])
                            if orbitals[i][key][1] != 0 and \
                               key not in intMOs[ct]:
                                intMOs[ct].append(key)
        if ct == 'RHF-SCF':
            columns = 2
            nMOs = len(intMOs[ct])
            r, rm = divmod(nMOs, columns)
            if rm != 0:
                r += 1
            rows = r
            fig, axs = plt.subplots(rows, columns)
            for j,key in enumerate(intMOs[ct]):
                r,c = divmod(j,columns)
                axs[r,c].set_title(key)
                axs[r,c].plot(dists,mos[key])
            fig.suptitle("Occ for {}".format(ct))
            n += 1
        elif ct == 'UHF-SCF':
            columns = 4
            nMOs = 2*len(intMOs[ct])
            r, rm = divmod(nMOs, columns)
            if rm != 0:
                r += 1
            rows = r
            fig, axs = plt.subplots(rows, columns)
            for j,key in enumerate(intMOs[ct]):
                r,c = divmod(j,columns)
                axs[r,c].set_title("{} alpha".format(key))
                axs[r,c].plot(dists,mos_a[key])
            for k,key in enumerate(intMOs[ct]):
                r,c = divmod((j+k+1),columns)
                axs[r,c].set_title("{} beta".format(key))
                axs[r,c].plot(dists,mos_b[key])
            fig.suptitle("Occ for {}".format(ct))
            n += 1
        else:
            plt.figure(n)
            plt.title(ct)
            for key in mos.keys():
                ls = lstyles[int(key.split(".")[-1])-1]
                plt.plot(dists, mos[key],linestyle=ls)
            plt.legend(mos.keys(),loc='upper right')
            plt.xlabel(r'R$_{l}$ (angstrom)')
            plt.ylabel('AO coefficient')
            n += 1
    plt.show()
    plt.close()

def evolOrbitalsCompo(orbitals,geos,calcTypes,symNumb,nMOs=0,normalized=True):
    def inversion(coeffs,orbs,prevOrbs,coeffThr,isInv):
        sortedCoeffs = coeffs.copy()
        sortedCoeffs.sort()
        posCoeff = sortedCoeffs[-1]
        negCoeff = sortedCoeffs[0]
        if abs(posCoeff) >= abs(negCoeff):
            biggestCoeff = posCoeff
        else:
            biggestCoeff = negCoeff
        index = coeffs.index(biggestCoeff)
        ao_BC = list(orbs.keys())[index]
        prev_BC = prevOrbs[ao_BC] 
        if abs(prev_BC) > coeffThr and \
           abs(biggestCoeff) > coeffThr and \
           biggestCoeff*prev_BC < 0.0: 
            isInv = not isInv
        return isInv

    rightCalcTypes = ['RHF-SCF','UHF-SCF','MULTI']
    atomStyle = ['solid', 'dashed', 'dotted']
    coeffThr = 0.5
    dists = dict()
    mosCompo = dict()
    aos = dict()
    isFirst = dict()
    isInv = dict()
    prev_i = dict()
    for i in orbitals:
        ct = calcTypes[i][0]
        if ct not in isFirst:
            isFirst[ct] = True
        if ct in rightCalcTypes:
            if not ct in aos:
                aos[ct] = dict()
            if not ct in mosCompo:
                mosCompo[ct] = dict()
            if not ct in dists:
                dists[ct] = list()
            for mo in orbitals[i]:
                if mo not in isInv:
                    isInv[mo] = False
                sym = int(mo.split('.')[1])
                for ao in orbitals[i][mo][2]:
                    if not sym in aos[ct]:
                        aos[ct][sym] = list()
                    if ao not in aos[ct][sym]:
                        aos[ct][sym].append(ao)
            for geo in geos[i]:
                #distance between H1 and C
                Rl,rs,theta = jacobi(geo,'1','2','3')
                dists[ct].append(Rl)
            for sym in range(1,symNumb+1):
                if sym not in mosCompo[ct]:
                    mosCompo[ct][sym] = dict()
                for mo in orbitals[i]:
                    if int(mo.split('.')[1]) == sym:
                        if mo not in mosCompo[ct][sym]:
                            mosCompo[ct][sym][mo] = dict()
                        coeffs = list()
                        if normalized:
                            normFactor = 0
                        else:
                            normFactor = 1
                        for ao in aos[ct][sym]:
                            if ao not in mosCompo[ct][sym][mo]:
                                mosCompo[ct][sym][mo][ao] = list()
                            if ao in orbitals[i][mo][2]:
                                coeff = orbitals[i][mo][2][ao]
                                coeffs.append(coeff)
                                if normalized:
                                    normFactor += coeff*coeff
                            else:
                                coeffs.append(0.0)
                        if isFirst[ct]:
                            if normalized:
                                normFactor = pow(normFactor,0.5)
                            for j,ao in enumerate(aos[ct][sym]):
                                mosCompo[ct][sym][mo][ao].append(coeffs[j]/
                                                             normFactor)
                        else:
                            isInv[mo] = inversion(coeffs,orbitals[i][mo][2],
                                orbitals[prev_i[ct]][mo][2],coeffThr,isInv[mo])
                            if normalized:
                                normFactor = pow(normFactor,0.5)
                            for j,ao in enumerate(aos[ct][sym]):
                                if isInv[mo]:
                                    mosCompo[ct][sym][mo][ao].append(
                                        -coeffs[j]/normFactor)
                                else:
                                    mosCompo[ct][sym][mo][ao].append(
                                        coeffs[j]/normFactor)
            if isFirst[ct]:
                isFirst[ct] = False
            prev_i[ct] = i
            
    for ct in mosCompo:
        columns = 5
        rows = list()

        aosCensus = dict()
        for sym in mosCompo[ct]:
            aosCensus[sym] = dict()
            for mo in mosCompo[ct][sym]:
                for ao in mosCompo[ct][sym][mo]:
                    atom = ao.split()[0]
                    if not atom in aosCensus[sym]:
                        aosCensus[sym][atom] = list()
                    if not ao in aosCensus[sym][atom]:
                        aosCensus[sym][atom].append(ao)
                        
        maxAOs = list()
        for sym in aosCensus:
            nAOs = list()
            for atom in aosCensus[sym]:
                nAOs.append(len(aosCensus[sym][atom]))
            nAOs.sort()
            maxAOs.append(nAOs[-1])
                    
        #for i,d in enumerate(dists):
        #    print("{}: {}".format(i+1,d))
        
        for i,sym in enumerate(range(1,symNumb+1)):
            nMOs = len(mosCompo[ct][sym])
            r, rm = divmod(nMOs, columns)
            if rm != 0:
                r += 1
            rows.append(r)
        for i,sym in enumerate(range(1,symNumb+1)):
            colors = cm.nipy_spectral(np.linspace(0, 1, maxAOs[i]))
            fig, axs = plt.subplots(rows[i], columns)
            for j,mo in enumerate(mosCompo[ct][sym]):
                r,c = divmod(j,columns)
                axs[r,c].set_title(mo)
                l = 0
                for ao in mosCompo[ct][sym][mo]:
                    if l == 0:
                        atom = ao.split()[0]
                    if ao.split()[0] != atom:
                        l = 0
                        atom = ao.split()[0]
                    if len(mosCompo[ct][sym][mo][ao]) != len(dists[ct]):
                        diff = len(dists[ct]) - len(mosCompo[ct][sym][mo][ao])
                        for k in range(diff):
                            mosCompo[ct][sym][mo][ao].insert(0,0.0)
                    ls = atomStyle[int(ao.split()[0])-1]
                    lc = colors[l]
                    axs[r,c].plot(dists[ct], mosCompo[ct][sym][mo][ao],
                                  linestyle=ls,color=lc)
                    l += 1
                #axs[r,c].text(1,1,'hop',fontsize=6)
            fig.legend(aos[ct][sym],loc='upper right',fontsize=8)
            fig.suptitle("{} MOs for IR {}".format(ct,sym))
        plt.show()
        plt.close()

def evolOrbitalsCompoProj(orbitals,geos,calcTypes,symNumb,nMOs=0):
    def normalize(orbital):
        normOrbital = dict()
        sumCoeff = 0.0
        for bf in orbital:
            sumCoeff += pow(orbital[bf],2)
        sumCoeff = pow(sumCoeff,0.5)
        for bf in orbital:
            normOrbital[bf] = orbital[bf]/sumCoeff
        return normOrbital
        
    def aoProj(orbital,aosFileNames):
        aoBasis = dict()
        projOrbital = dict()
        for fn in aosFileNames:
            try:
                aosFile = open(fn, 'r')
            except FileNotFoundError:
                print("File {0} not found".format(aosFileName))
                sys.exit(1)
            for line in aosFile:
                line = line.rstrip('\n')
                if line.startswith('Orbital'):
                    orb = '{} {}'.format(fn.split('_')[0],line.split()[1])
                    aoBasis[orb] = dict()
                else:
                    aoBasis[orb][line.split(':')[0]]=float(line.split(':')[1])
            
        normMO = normalize(orbital[2])
        for mo in aoBasis:
            scalarprod = 0.0
            norm = 0.0
            normAO = normalize(aoBasis[mo]) 
            for bf in orbital[2]:
                for bf2 in aoBasis[mo]:
                    if bf==bf2:
                        norm += pow(normAO[bf2],2)
                        prod = abs(normMO[bf] * normAO[bf2])
                        scalarprod += prod
            if norm != 0.0:
                norm = pow(norm,0.5) 
                projOrbital[mo] = scalarprod/norm
            else:
                projOrbital[mo] = scalarprod
        return projOrbital

    rightCalcTypes = ['RHF-SCF','UHF-SCF','MULTI']
    aoFiles = ['h2_hf_vtz.orb','c_hf_vtz.orb']
    atomStyle = ['solid', 'dashed', 'dotted']
    coeffThr = 0.5
    dists = dict()
    mosCompo = dict()
    isFirst = True
    isInv = dict()
    for i in orbitals:
        ct = calcTypes[i][0]
        if ct in rightCalcTypes:
            if not ct in mosCompo:
                mosCompo[ct] = dict()
            if not ct in dists:
                dists[ct] = list()
            for mo in orbitals[i]:
                if mo not in isInv:
                    isInv[mo] = False
                sym = int(mo.split('.')[1])
            for geo in geos[i]:
                #distance between H1 and C
                Rl,rs,theta = jacobi(geo,'1','2','3')
                dists[ct].append(Rl)
            for sym in range(1,symNumb+1):
                if sym not in mosCompo[ct]:
                    mosCompo[ct][sym] = dict()
                for mo in orbitals[i]:
                    if int(mo.split('.')[1]) == sym:
                        if mo not in mosCompo[ct][sym]:
                            mosCompo[ct][sym][mo] = dict()
                        projection = aoProj(orbitals[i][mo],aoFiles)
                        for ao in projection:
                            if ao not in mosCompo[ct][sym][mo]:
                                mosCompo[ct][sym][mo][ao] = list()
                            mosCompo[ct][sym][mo][ao].append(projection[ao])
            
    for ct in mosCompo:
        columns = 5
        rows = list()

        aosCensus = dict()
        for sym in mosCompo[ct]:
            aosCensus[sym] = dict()
            for mo in mosCompo[ct][sym]:
                for ao in mosCompo[ct][sym][mo]:
                    atom = ao.split()[0]
                    if not atom in aosCensus[sym]:
                        aosCensus[sym][atom] = list()
                    if not ao in aosCensus[sym][atom]:
                        aosCensus[sym][atom].append(ao)
                        
        maxAOs = list()
        for sym in aosCensus:
            nAOs = list()
            for atom in aosCensus[sym]:
                nAOs.append(len(aosCensus[sym][atom]))
            nAOs.sort()
            maxAOs.append(nAOs[-1])
                    
        #for i,d in enumerate(dists):
        #    print("{}: {}".format(i+1,d))
        
        for i,sym in enumerate(range(1,symNumb+1)):
            nMOs = len(mosCompo[ct][sym])
            r, rm = divmod(nMOs, columns)
            if rm != 0:
                r += 1
            rows.append(r)
        for i,sym in enumerate(range(1,symNumb+1)):
            colors = cm.nipy_spectral(np.linspace(0, 1, maxAOs[i]))
            fig, axs = plt.subplots(rows[i], columns)
            for j,mo in enumerate(mosCompo[ct][sym]):
                r,c = divmod(j,columns)
                axs[r,c].set_title(mo)
                l = 0
                for ao in mosCompo[ct][sym][mo]:
                    if l == 0:
                        atom = ao.split()[0]
                    if ao.split()[0] != atom:
                        l = 0
                        atom = ao.split()[0]
                    if len(mosCompo[ct][sym][mo][ao]) != len(dists[ct]):
                        diff = len(dists[ct]) - len(mosCompo[ct][sym][mo][ao])
                        for k in range(diff):
                            mosCompo[ct][sym][mo][ao].insert(0,0.0)
                    #ls = atomStyle[int(ao.split()[0])-1]
                    lc = colors[l]
                    axs[r,c].plot(dists[ct], mosCompo[ct][sym][mo][ao],
                                  color=lc)
                                  #linestyle=ls,color=lc)
                    l += 1
                #axs[r,c].text(1,1,'hop',fontsize=6)
            fig.legend(list(mosCompo[ct][sym][mo].keys()),
                       loc='upper right',fontsize=8)
            fig.suptitle("MOs for IR {}".format(sym))
        plt.show()
        plt.close()
   
def pes(energiess,geoss,calcTypess,grouping='sameMethod',saveData=False):
    plt.rcParams["figure.autolayout"] = True
    dim = 2
    showCuts = True
    convNRJ = 27.211399
    relativeNRJs = True
    allRelatives = False #Are all asymptotes put to 0 or just lowest one
    rightCalcTypes = ['RHF-SCF','UHF-SCF', 'MULTI', 'CI']
    lstyles = ['solid','dashed', 'dotted', 'dashdot']
    #levelsShowed = "all"
    levelsShowed = ['1.1','1.2','2.1','2.2']
    #levelsShowed = ['1.1','1.2']
    #levelsShowed = ['1.1']
    lineLabels = dict()
    plotGroups = dict()
    datas = dict()
    #grouping = 'all' 
    #grouping = 'sameMethod'
    #grouping = 'sameFile'
    if grouping == 'all':
        plotGroups['all'] = list()
    for m,f in enumerate(energiess):
        if grouping == 'sameFile':
            plotGroups[f] = list()
        uCalcTypes = list()
        #Make a list of calcTypes
        for i in calcTypess[f]:
            if calcTypess[f][i][0] not in uCalcTypes and \
               calcTypess[f][i][0] in rightCalcTypes:
                uCalcTypes.append(calcTypess[f][i][0])
                if grouping == 'sameMethod' and calcTypess[f][i][0] \
                                                not in plotGroups:
                    plotGroups[calcTypess[f][i][0]] = list()
                plotName = '{} {}'.format(f,calcTypess[f][i][0])
                if grouping == 'all':
                    plotGroups['all'].append(plotName)
                elif grouping == 'sameMethod':
                    plotGroups[calcTypess[f][i][0]].append(plotName)
                elif grouping == 'sameFile':
                    plotGroups[f].append(plotName)
            

        for n,ct in enumerate(uCalcTypes):
            coords = list()
            nrjss = dict()
            for i in energiess[f]:
                if calcTypess[f][i][0] == ct:
                    for geo in geoss[f][i]:
                        #Choose coordinate for x axis
                        Rl,rs,theta = jacobi(geo,'1','2','3')
                        coord = (Rl,rs,theta)
                        if coord not in coords:
                            coords.append(coord)
                            for lvl in energiess[f][i]:
                                if not lvl in nrjss:
                                    nrjss[lvl] = list()
                                nrjss[lvl].append(
                                    energiess[f][i][lvl]*convNRJ)
            plotName = '{} {}'.format(f,ct)
            datas[plotName] = [coords,nrjss]
    
    refNRJs = dict()
    if dim == 1:
        print('Well depths:')
    for pn in datas:
        for lvl in datas[pn][1]:
            if levelsShowed == "all" or lvl in levelsShowed:
                sortedNRJs = datas[pn][1][lvl].copy()
                sortedNRJs.sort()
                minNRJ = sortedNRJs[0]
                if dim == 1:
                    wellDepth = datas[pn][1][lvl][-1] - minNRJ
                    print('{} {}: {}eV'.format(pn,lvl,wellDepth))
                if lvl == '1.1':
                    refNRJs[pn] = datas[pn][1][lvl][-1]

    if not allRelatives:
        lowestRef = dict()
        for pn in refNRJs:
            if not pn.split()[1] in lowestRef:
                lowestRef[pn.split()[1]] = refNRJs[pn]
            else:
                if refNRJs[pn] >= lowestRef[pn.split()[1]]:
                    refNRJs[pn] = lowestRef[pn.split()[1]]
                else:
                    lowestRef[pn.split()[1]] = refNRJs[pn]
    if relativeNRJs:
        for pn in datas:
            for lvl in datas[pn][1]:
                for n,nrj in enumerate(datas[pn][1][lvl]):
                    datas[pn][1][lvl][n] = nrj - refNRJs[pn]
                    

    if saveData:
        dataSaved = list()
        dataSaved.append(datas)
        dataSaved.append(plotGroups)
        dataFileName = 'energy.data'
        dataFile = open(dataFileName, 'wb') 
        pickle.dump(dataSaved, dataFile)
        dataFile.close()
    
    xs = list()
    ys = list()
    if showCuts:
        cuts = dict()
    for i,c in enumerate(coords):
        #print("{}: {}".format(i+1,c))
        xs.append(c[0])
        if dim > 1:
            ys.append(c[1])
            if showCuts:
                fixC = c[1]
                varC = c[0]
                if fixC not in cuts:
                    cuts[fixC] = list()
                    cuts[fixC].append([])
                    cuts[fixC].append({})
                cuts[fixC][0].append(varC)
                for group in plotGroups:
                    for p in plotGroups[group]:
                        if p not in cuts[fixC][1]:
                            cuts[fixC][1][p] = dict()
                        for l,lvl in enumerate(datas[p][1]):
                            if levelsShowed == "all" or lvl in levelsShowed:
                                if lvl not in cuts[fixC][1][p]:
                                    cuts[fixC][1][p][lvl] = list()
                                cuts[fixC][1][p][lvl].append(
                                    datas[p][1][lvl][i])
    if showCuts:
        rows = 6
        columns = 6
        nCuts = len(cuts)
        nf,rf = divmod(nCuts,rows*columns)
        if rf != 0:
            nf += 1

    if dim == 1:
        for m,group in enumerate(plotGroups):
            plt.figure(m)
            plt.title(group)
            lineLabels = list()
            for p in plotGroups[group]:
                fn = p.split()[0]
                met = p.split()[1]
                for l,lvl in enumerate(datas[p][1]):
                    if levelsShowed == "all" or lvl in levelsShowed:
                        ls = lstyles[int(lvl.split('.')[1])-1]
                        plt.plot(xs,datas[p][1][lvl],linestyle=ls)
                        if grouping == 'all':
                            lineLabels.append("{} {}".format(p,lvl))
                        elif grouping == 'sameMethod':
                            lineLabels.append("{} {}".format(fn,lvl))
                        elif grouping == 'sameFile':
                            lineLabels.append("{} {}".format(met,lvl))
            plt.legend(lineLabels)
            plt.xlabel(r'R$_{l}$ (angstrom)')
            #plt.xlabel(r'r$_{s}$ (angstrom)')
            #plt.xlabel(r'Theta (degree)')
            plt.ylabel('Energy (eV)')
        plt.show()
        plt.close()
    elif dim == 2:
        f = 0
        for group in plotGroups:
            for p in plotGroups[group]:
                f += 1
                fig3d = plt.figure(f)
                ax = fig3d.add_subplot(projection='3d')
                plt.title(p)
                for l,lvl in enumerate(datas[p][1]):
                    if levelsShowed == "all" or lvl in levelsShowed:
                        ax.scatter(xs,ys,datas[p][1][lvl])
                plt.xlabel(r'R$_{l}$ (angstrom)')
                plt.ylabel(r'r$_{s}$ (angstrom)')
                if showCuts:
                    c = 0
                    for fc in range(0,nf):
                        f += 1
                        print(p,fc,f)
                        figC, axsC = plt.subplots(rows, columns)
                        figC.text(0.5,0.02,r'R$_{l}$ (angstrom)')
                        figC.suptitle("{} {}".format(group,fc))
                        for row in range(0,rows):
                            for col in range(0,columns):
                                try:
                                    cut = list(cuts.keys())[c]
                                except:
                                    continue
                                lineLabels = list()
                                for l,lvl in enumerate(datas[p][1]):
                                    if levelsShowed == "all"\
                                       or lvl in levelsShowed:
                                        axsC[row,col].set_title('{}'
                                                                .format(cut))
                                        ls = lstyles[int(lvl.split('.')[1])-1]
                                        axsC[row,col].plot(cuts[cut][0],
                                            cuts[cut][1][p][lvl],linestyle=ls)
                                        lineLabels.append("{}".format(lvl))
                                plt.legend(lineLabels)
                                c += 1
                        figC.legend(lineLabels,loc='upper right',fontsize=8)
        plt.show()
        plt.close()

def evolEnergyDiff(energiess,geoss,calcTypess,grouping='sameMethod',
                   saveData=False):
    rightCalcTypes = ['MULTI', 'CI']
    levelsDiff = ['1.1','1.2']
    lineLabels = dict()
    plotGroups = dict()
    datas = dict()
    #grouping = 'every' 
    #grouping = 'sameMethod'
    #grouping = 'sameFile'
    if grouping == 'every':
        plotGroups['all'] = list()
    for m,f in enumerate(energiess):
        if grouping == 'sameFile':
            plotGroups[f] = list()
        uCalcTypes = list()
        #Make a list of calcTypes
        for i in calcTypess[f]:
            if calcTypess[f][i][0] not in uCalcTypes and \
               calcTypess[f][i][0] in rightCalcTypes:
                uCalcTypes.append(calcTypess[f][i][0])
                if grouping == 'sameMethod' and calcTypess[f][i][0] \
                                                not in plotGroups:
                    plotGroups[calcTypess[f][i][0]] = list()
                plotName = '{} {}'.format(f,calcTypess[f][i][0])
                if grouping == 'every':
                    plotGroups['all'].append(plotName)
                elif grouping == 'sameMethod':
                    plotGroups[calcTypess[f][i][0]].append(plotName)
                elif grouping == 'sameFile':
                    plotGroups[f].append(plotName)
            

        for n,ct in enumerate(uCalcTypes):
            dists = list()
            nrjss = dict()
            diffNRJ = list()
            for i in energiess[f]:
                if calcTypess[f][i][0] == ct:
                    for geo in geoss[f][i]:
                        Rl,rs,theta = jacobi(geo,'1','2','3')
                        dist = Rl
                        #dist = rs
                        #dist = theta
                        if dist not in dists:
                            dists.append(dist)
                        for lvl in energiess[f][i]:
                            if not lvl in nrjss:
                                nrjss[lvl] = list()
                            nrjss[lvl].append(
                                energiess[f][i][lvl])
            for d in range(0,len(dists)):
                diffNRJ.append(nrjss[levelsDiff[1]][d]-nrjss[levelsDiff[0]][d])
            plotName = '{} {}'.format(f,ct)
            datas[plotName] = [dists,diffNRJ]

    if saveData:
        dataSaved = list()
        dataSaved.append(datas)
        dataSaved.append(plotGroups)
        dataFileName = 'energy.data'
        dataFile = open(dataFileName, 'wb') 
        pickle.dump(dataSaved, dataFile)
        dataFile.close()

    for m,group in enumerate(plotGroups):
        plt.figure(m)
        plt.title(group)
        lineLabels = list()
        for p in plotGroups[group]:
            fn = p.split()[0]
            met = p.split()[1]
            plt.plot(datas[p][0],datas[p][1])
            if grouping == 'every':
                lineLabels.append("{} {}".format(p,levelsDiff))
            elif grouping == 'sameMethod':
                lineLabels.append("{} {}".format(fn,levelsDiff))
            elif grouping == 'sameFile':
                lineLabels.append("{} {}".format(met,levelsDiff))
        plt.legend(lineLabels)
        plt.xlabel(r'R$_{l}$ (angstrom)')
        #plt.xlabel(r'r$_{s}$ (angstrom)')
        #plt.xlabel(r'Theta (degree)')
        plt.ylabel('Energy (a.u)')
            
    plt.show()
    plt.close()

def evolWF(wfss,geoss):
    lstyles = ['solid','dashed', 'dotted', 'dashdot']

    for m,f in enumerate(wfss):
        dists = list()
        wfs = dict()
        lineLabels = list()
        for n,i in enumerate(wfss[f]):
            for geo in geoss[f][i]:
                #distance between H1 and C
                Rl,rs,theta = jacobi(geo,'1','2','3')
                dist = Rl
                dists.append(dist)
                for sym in wfss[f][i]:
                    for l,wf in enumerate(wfss[f][i][sym]):
                        lvl = '{}.{}'.format(l+1,sym)
                        if n == 0:
                            wfs[lvl] = list()
                        wfs[lvl].append(wf)
        plt.figure(f)
        for lvl in wfs:
            ls = lstyles[int(lvl.split('.')[1])-1]
            plt.plot(dists,wfs[lvl],linestyle=ls)
            lineLabels.append("{}".format(lvl))
        plt.legend(lineLabels)
        plt.xlabel(r'R$_{l}$ (angstrom)')
        #plt.xlabel(r'r$_{s}$ (angstrom)')
        #plt.xlabel(r'Theta (degree)')
        plt.ylabel('Weight factor')
        plt.show()
        plt.close()

def evolPartialCharges(pcss,geoss,saveData=False):
    for m,f in enumerate(pcss):
        dists = list()
        pcs = dict()
        lineLabels = list()
        if saveData:
            dataSaved = list()
        for n,i in enumerate(pcss[f]):
            for geo in geoss[f][i]:
                #distance between H1 and C
                Rl,rs,theta = jacobi(geo,'1','2','3')
                dist = Rl
                #dist = rs
                #dist = theta
                dists.append(dist)
                for atom in pcss[f][i]:
                    if n == 0:
                        pcs[atom] = list()
                    pcs[atom].append(pcss[f][i][atom])
        if saveData:
            datas = list()
            datas.append(dists)
            datas.append(pcs)
            dataSaved.append(datas)
            dataFileName = 'partCharges.data'
            dataFile = open(dataFileName, 'wb') 
            pickle.dump(dataSaved, dataFile)
            dataFile.close()

        plt.figure(f)
        for atom in pcs:
            plt.plot(dists,pcs[atom],linestyle='solid')
            lineLabels.append("{}".format(atom))
        plt.legend(lineLabels)
        plt.xlabel(r'R$_{l}$ (angstrom)')
        #plt.xlabel(r'r$_{s}$ (angstrom)')
        #plt.xlabel(r'Theta (degree)')
        plt.ylabel('Partial charges (e)')
        plt.show()
        plt.close()
