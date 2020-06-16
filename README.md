# Open Software for Quantum Chemistry Advanced Reading

*OSCQAR is a python software that read, process and represent data from quantum chemistry software output files.*

## Usage

*oscqar.py [option] filename

**-q**, **--quick** : enable quick mode for the various options
**-e**, **--energy** : retrieve and show the last energy for each calculation in the file, if geometry optimization plot the energies. Quick mode : retrieve and show the last energy in the file
**-s**, **--spectrum** : retrieve spectrum (only harmonic ones for now) and plot them after asking FWHM. Quick mode : retrieve and plot with a default FWHM.
**-g, --geometry** : retrieve geometries of each calculation and plot in 3D the last one for the calculation asked

Compatible softwares : Gaussian16

## What's next

- [ ] Read and plot anharmonic spectra 
- [ ] Make MOLCAS compatible
- [ ] Improve UI

