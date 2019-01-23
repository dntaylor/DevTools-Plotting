import os
import json
import sys
import logging
from itertools import product, combinations_with_replacement

from DevTools.Plotter.Plotter import Plotter
from DevTools.Utilities.utilities import ZMASS, getCMSSWVersion
from copy import deepcopy
import ROOT

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

version = getCMSSWVersion()

blind = False

plotter = Plotter('MonoHZZ',new=True)

#########################
### Define categories ###
#########################

sigMap = {
    'Z'   : [
             #'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             #'DY1JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             #'DY2JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             #'DY3JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             #'DY4JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             #'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             #'DY1JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             #'DY2JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             #'DY3JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             #'DY4JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
             'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
            ],
    'TT'  : [
             'TTJets_DiLept_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'TTJets_SingleLeptFromT_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'TTJets_SingleLeptFromTbar_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
            ],
    'WZ' : [
             #'WZTo3LNu_TuneCUETP8M1_13TeV-powheg-pythia8',
             'WZTo3LNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8', # more stats but neg weights
             'WZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8',
             'WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8',
            ],
    'ZZ' : [
             'ZZTo4L_13TeV_powheg_pythia8',
             'ZZTo2L2Nu_13TeV_powheg_pythia8',
             'ZZTo2L2Q_13TeV_powheg_pythia8',
             'GluGluToContinToZZTo2e2mu_13TeV_MCFM701_pythia8',
             'GluGluToContinToZZTo2mu2tau_13TeV_MCFM701_pythia8',
             'GluGluToContinToZZTo2e2tau_13TeV_MCFM701_pythia8',
             'GluGluToContinToZZTo4e_13TeV_MCFM701_pythia8',
             'GluGluToContinToZZTo4mu_13TeV_MCFM701_pythia8',
             'GluGluToContinToZZTo4tau_13TeV_MCFM701_pythia8',
             #'ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8',
            ],
    'TTV' : [
             #'ttWJets_13TeV_madgraphMLM',
             'TTWJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8',
             'ttZJets_13TeV_madgraphMLM-pythia8',
             'tZq_ll_4f_13TeV-amcatnlo-pythia8',
            ],
    'VVV' : [
             'WWW_4F_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
             'WWZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
             'WZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
             'ZZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
            ],
    'data' : [
        'DoubleMuon',
        'DoubleEG',
        'MuonEG',
        'SingleMuon',
        'SingleElectron',
    ],
}

samples = ['TT','TTV','Z','WZ','VVV','ZZ']



########################
### plot definitions ###
########################
plots = {
    # h
    'hMass'                 : {'xaxis': 'm_{4l} (GeV)', 'yaxis': 'Events / 5 GeV', 'numcol': 3, 'lumipos': 11, 'legendpos':34, 'rebin': range(80,605,5)},
    # z cand
    'z1Mass'                : {'xaxis': 'm_{l^{+}l^{-}} (GeV)', 'yaxis': 'Events / 2 GeV', 'rebin': range(40,122,2), 'numcol': 2, 'legendpos':34},
    'z2Mass'                : {'xaxis': 'm_{l^{+}l^{-}} (GeV)', 'yaxis': 'Events / 2 GeV', 'rebin': range(12,122,2), 'numcol': 2, 'legendpos':34},
    # event
    #'numVertices'           : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    'met'                   : {'xaxis': 'E_{T}^{miss} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': range(0,300,5), 'numcol': 2, 'logy': True, 'overflow': True,},
}


############################
### MC based BG estimate ###
############################
for s in samples:
    plotter.addHistogramToStack(s,sigMap[s])

if not blind: plotter.addHistogram('data',sigMap['data'])

for plot in plots:
    kwargs = deepcopy(plots[plot])
    plotname = '{0}/{1}'.format('default',plot)
    savename = '{0}/mc/{1}'.format('default',plot)
    plotter.plot(plotname,savename,**kwargs)
    
