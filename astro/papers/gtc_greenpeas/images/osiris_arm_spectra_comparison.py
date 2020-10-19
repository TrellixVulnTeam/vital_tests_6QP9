import numpy as np
import pandas as pd
import src.specsiser as sr
from pathlib import Path
from astro.papers.gtc_greenpeas.common_methods import red_corr_HalphaHbeta_ratio
from src.specsiser.physical_model.line_tools import STANDARD_PLOT, STANDARD_AXES
from matplotlib import pyplot as plt, rcParams, gridspec

objList = ['gp030321', 'gp101157', 'gp121903']
conf_file_address = '../../../papers/gtc_greenpeas/gtc_greenpeas_data.ini'
obsData = sr.loadConfData(conf_file_address, objList=objList, group_variables=False)

dataFolder = Path(obsData['file_information']['data_folder'])
resultsFolder = Path(obsData['file_information']['results_folder'])
fileList = obsData['file_information']['files_list']
output_folder = Path(obsData['file_information']['images_folder'])

z_objs = obsData['sample_data']['z_array']
wmin_array = obsData['sample_data']['wmin_array']
wmax_array = obsData['sample_data']['wmax_array']
flux_norm = obsData['sample_data']['norm_flux']
noise_region = obsData['sample_data']['noiseRegion_array']
idx_band = int(obsData['file_information']['band_flux'])

colors_dict = dict(zip(['_BR', '_B', '_R'], ['tab:purple', 'tab:blue', 'tab:red']))
legend_dict = dict(zip(['_BR', '_B', '_R'], ['Combined arm', 'Blue arm', 'Red arm']))



counter = 0
for i, obj in enumerate(objList):

    z = z_objs[i]
    wmin, wmax = wmin_array[i], wmax_array[i]
    fit_conf = obsData[f'{obj}_line_fitting']

    # Plot Configuration
    defaultConf = STANDARD_PLOT.copy()
    rcParams.update(defaultConf)

    # Plot the spectra
    fig = plt.figure(figsize=(16, 9))
    spec = gridspec.GridSpec(ncols=2, nrows=1, width_ratios=[16, 9])

    for ext in ('_BR', '_B', '_R'):

        # Declare files location
        fits_file = dataFolder/f'{obj}{ext}.fits'
        objFolder = resultsFolder/f'{obj}'
        objMask = objFolder/f'{obj}{ext}_mask.txt'
        lineLog_file, lineGrid_file = objFolder/f'{obj}{ext}_linesLog.txt', objFolder/f'{obj}{ext}_lineGrid.png'
        pdfTableFile, txtTableFile = objFolder/f'{obj}{ext}_linesTable', objFolder/f'{obj}{ext}_linesTable.txt'

        # Load spectrum
        print(f'\n-- Treating {counter} :{obj}{ext}.fits')
        wave, flux_array, header = sr.import_fits_data(fits_file, instrument='OSIRIS')
        flux = flux_array[idx_band][0] if ext in ('_B', '_R') else flux_array

        # Load line measurer object
        maskDF = pd.read_csv(objMask, delim_whitespace=True, header=0, index_col=0)
        lm = sr.LineMesurer(wave, flux, redshift=z, normFlux=flux_norm, crop_waves=(wmin, wmax))


        ax0 = fig.add_subplot(spec[0])
        ax0.step(lm.wave, lm.flux, label=legend_dict[ext], color=colors_dict[ext])

        idx_inset = np.searchsorted(lm.wave, (6200, 6800))
        ax1 = fig.add_subplot(spec[1])
        ax1.step(lm.wave[idx_inset[0]:idx_inset[1]], lm.flux[idx_inset[0]:idx_inset[1]],
                label=legend_dict[ext], color=colors_dict[ext])

    ax0.set_yscale('log')
    ax0.update(STANDARD_AXES)
    ax0.set_title(f'Galaxy {obj}')
    ax0.legend()
    ax0.update(STANDARD_AXES)

    ax1.set_yscale('log')
    ax1.update(STANDARD_AXES)
    ax1.set_title(r'Galaxy {} $H\alpha$ region'.format(obj))
    ax1.legend()
    ax1.update(STANDARD_AXES)
    fig.tight_layout()

    plotAddress = output_folder/fileList[i].replace('.fits', '_armFluxComparison.png')
    plt.savefig(plotAddress, dpi=200, bbox_inches='tight')
    # plt.show()
