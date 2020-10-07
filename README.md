# Open Software for Quantum Chemistry Advanced Reading

*OSCQAR is a python software that read, process and represent data from quantum chemistry software output files.*

## Usage

*oscqar.py [option] filename*

**-q**, **--quick** : enable quick mode for the various options

**-e**, **--energy** : retrieve and show the last energy for each calculation in the file, if geometry optimization plot the energies. Quick mode : retrieve and show the last energy in the file

**-g, --geometry** : retrieve geometries of each calculation and plot in 3D the last one for the calculation asked

**-s**, **--spectrum** : retrieve spectrum (only harmonic ones for now) and plot them after asking FWHM. Quick mode : retrieve and plot with a default FWHM.

**-ms**, **--multispectra** : Get the frequencies and intensities and plot spectra from several files

Compatible softwares : Gaussian16

## Philosophy

The idea behind OSQCAR is to build a very simple, straightforward and easy to understand package to interpret output files from Quantum Chemistry softwares. In particular, it is conceived so it can be easily adapted to unique needs.

## What's next

- [x] Read and plot anharmonic spectra 

- [x] Read and plot multiple spectra on the same figure

- [ ] Write files to replot at will

- [ ] Make MOLCAS compatible

- [ ] Improve UI
