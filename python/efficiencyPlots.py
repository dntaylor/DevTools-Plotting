
import os
import sys
import logging

from DevTools.Plotter.EfficiencyPlotter import EfficiencyPlotter
from copy import deepcopy

import ROOT

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

effPlotter = EfficiencyPlotter()

efficiencies = {
    # muon
    'HppMediumID'             : {'filename': 'fits_muon/HppMediumID_scalefactor.root',              'etabins': [0., 0.2, 0.3, 0.9, 1.2, 1.6, 2.1, 2.4], 'ptbins': [10, 20, 30, 40, 50, 200], 'ymin': 0.8, 'ymax': 1.1,},
    'HppMediumIsoFromMediumID': {'filename': 'fits_muon/HppMediumIsoFromMediumID_scalefactor.root', 'etabins': [0., 0.2, 0.3, 0.9, 1.2, 1.6, 2.1, 2.4], 'ptbins': [10, 20, 30, 40, 50, 200], 'ymin': 0.5, 'ymax': 1.1,},
    # electron
    'CutBasedIDMedium'        : {'filename': 'fits_electron/CutBasedIDMedium_scalefactor.root',     'etabins': [0., 0.8, 1.479, 2.0, 2.5],              'ptbins': [10, 20, 30, 40, 50, 200], 'ymin': 0.0, 'ymax': 1.1,},
    'CutBasedIDTight'         : {'filename': 'fits_electron/CutBasedIDTight_scalefactor.root',      'etabins': [0., 0.8, 1.479, 2.0, 2.5],              'ptbins': [10, 20, 30, 40, 50, 200], 'ymin': 0.0, 'ymax': 1.1,},
}

for eff in efficiencies:
    effPlotter = EfficiencyPlotter()
    effPlotter.addFile(eff,efficiencies[eff]['filename'])
    effPlotter.setBinning(etabins=efficiencies[eff]['etabins'],ptbins=efficiencies[eff]['ptbins'])
    effPlotter.addHist('data','eff_data')
    effPlotter.plot('efficiencies/'+eff,xaxis='p_{T} (GeV)',yaxis='Efficiency',xrange=[10,200],numcol=2,legendpos=21,ymin=efficiencies[eff]['ymin'],ymax=efficiencies[eff]['ymax'])
