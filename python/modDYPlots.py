import os
import sys
import logging

from DevTools.Plotter.Plotter import Plotter
from copy import deepcopy

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

dyPlotter = Plotter('ModDY',
    intLumi = 34867, # z skim lumi
)

sigMap = {
    'Z'   : [
             'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
             'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
            ],
    'TT'  : [
             'TTJets_TuneCUETP8M2T4_13TeV-amcatnloFXFX-pythia8',
             #'TTJets_DiLept_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             #'TTJets_SingleLeptFromT_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             #'TTJets_SingleLeptFromTbar_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
            ],
    'W'    : [
        'WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
    ],
    'WW' : [
        'WWTo2L2Nu_13TeV-powheg',
    ],
    'WZ' : [
        'WZTo3LNu_TuneCUETP8M1_13TeV-powheg-pythia8',
        'WZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8',
        'WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8',
        'WZTo1L3Nu_13TeV_amcatnloFXFX_madspin_pythia8',
    ],
    'ZZ' : [
        'ZZTo4L_13TeV_powheg_pythia8',
        'ZZTo2L2Q_13TeV_powheg_pythia8',
        'ZZTo2L2Nu_13TeV_powheg_pythia8',
        'GluGluToContinToZZTo2e2mu_13TeV_MCFM701_pythia8',
        'GluGluToContinToZZTo2e2tau_13TeV_MCFM701_pythia8',
        'GluGluToContinToZZTo2mu2tau_13TeV_MCFM701_pythia8',
        'GluGluToContinToZZTo4e_13TeV_MCFM701_pythia8',
        'GluGluToContinToZZTo4mu_13TeV_MCFM701_pythia8',
        'GluGluToContinToZZTo4tau_13TeV_MCFM701_pythia8',
    ],
    'data': [
             'SingleMuon',
            ],
}

samples = ['W','TT','WW','WZ','ZZ','Z']

for s in samples:
    dyPlotter.addHistogramToStack(s,sigMap[s])

dyPlotter.addHistogram('data',sigMap['data'])


# plot definitions
plots = {
    # z cand
    'zMass'                 : {'xaxis': 'm_{l^{+}l^{-}} (GeV)', 'yaxis': 'Events / 2 GeV', 'rebin': range(61,121,2), 'logy':1, 'ymin':1000, 'ymax': 1e9, 'legendpos': 34, 'numcol': 3,},
    'zPt'                   : {'xaxis': 'p_{T}^{l^{+}l^{-}} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': range(0,155,5), },
    'zLeadingLeptonPt'      : {'xaxis': 'p_{T}^{Z_{lead}} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': range(25,150,5),},
    'zSubLeadingLeptonPt'   : {'xaxis': 'p_{T}^{Z_{sublead}} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': range(20,150,5),},
    'zLeadingLeptonEta'     : {'xaxis': '#eta^{Z_{lead}} (GeV)', 'yaxis': 'Events', 'rebin':10, 'legendpos': 34, 'numcol': 3, 'yscale':1.4, },
    'zSubLeadingLeptonEta'  : {'xaxis': '#eta^{Z_{sublead}} (GeV)', 'yaxis': 'Events', 'rebin':10, 'legendpos': 34, 'numcol': 3, 'yscale':1.4, }, 
    # event
    'met'                   : {'xaxis': 'E_{T}^{miss} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': range(0,200,5),},
    'metPhi'                : {'xaxis': '#phi_{E_{T}^{miss}}', 'yaxis': 'Events', 'rebin': 10, 'numcol': 3, 'legendpos': 34, 'yscale': 1.4, },
}

# signal region
for plot in plots:
    plotname = 'default/{0}'.format(plot)
    dyPlotter.plot(plotname,plotname,ratiomin=0.9,ratiomax=1.1,**plots[plot])

