import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot(lm.wave, lm.flux, label='Blue arm')
ax.scatter(lm.wave[idcsLinePeak], lm.flux[idcsLinePeak], label='linePeaks', facecolors='tab:green')
ax.plot(wave_blue, flux_blue, label='Blue arm')
ax.legend()
ax.update({'xlabel':'Wavelength', 'ylabel':'Flux', 'title':'Gaussian fitting'})
plt.show()