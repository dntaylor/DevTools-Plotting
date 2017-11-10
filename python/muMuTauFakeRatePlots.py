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

plotter = Plotter('MuMuTauFakeRate')

#########################
### Define categories ###
#########################

sigMap = {
    'Z' : [
        'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
        'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
    ],
    'QCD' : [
        'QCD_Pt-15to20_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8',
        'QCD_Pt-20to30_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8',
        'QCD_Pt-30to50_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8',
        'QCD_Pt-50to80_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8',
        'QCD_Pt-80to120_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8',
        'QCD_Pt-120to170_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8',
        'QCD_Pt-170to300_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8',
        'QCD_Pt-300to470_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8',
        'QCD_Pt-470to600_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8',
        'QCD_Pt-600to800_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8',
        'QCD_Pt-800to1000_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8',
        'QCD_Pt-1000toInf_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8',
    ],
    'W' : [
        'WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
    ],
    'TT': [
        'TTJets_DiLept_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
    ],
    'WW': [
        'VVTo2L2Nu_13TeV_amcatnloFXFX_madspin_pythia8',
    ],
    'WZ': [
        #'WZTo3LNu_TuneCUETP8M1_13TeV-powheg-pythia8',
        'WZTo3LNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
    ],
    'ZZ': [
        'ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8',
        'ZZTo4L_13TeV-amcatnloFXFX-pythia8',
    ],
    'data' : [
        'DoubleMuon',
    ],
}

samples = ['QCD','W','TT','WW','WZ','ZZ','Z']

sigMap['BG'] = []
for s in samples:
    sigMap['BG'] += sigMap[s]

sels = ['default','vloose',]
etaBins = [0,1.479,2.3]
for eb in range(len(etaBins)-1):
    sels += ['default/etaBin{0}'.format(eb), 'vloose/etaBin{0}'.format(eb)]

########################
### plot definitions ###
########################
plots = {
    # z
    'zMass'                 : {'xaxis': 'm^{#mu#mu} (GeV)', 'yaxis': 'Events / 0.5 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.5, range(120,240,1)), 'logy': False, 'overflow': True},
    'z1Pt'                  : {'xaxis': 'm^{#mu#mu} #mu_{1} p_{T} (GeV)', 'yaxis': 'Events / 5 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,150,5), 'logy': False, 'overflow': True},
    'z2Pt'                  : {'xaxis': 'm^{#mu#mu} #mu_{2} p_{T} (GeV)', 'yaxis': 'Events / 5 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,150,5), 'logy': False, 'overflow': True},
    # t
    'tPt'                   : {'xaxis': '#tau p_{T} (GeV)', 'yaxis': 'Events / 5 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,150,5), 'logy': False, 'overflow': True},
    # event
    'numVertices'           : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    'met'                   : {'xaxis': 'E_{T}^{miss} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': range(0,320,20), 'numcol': 2, 'logy': False, 'overflow': True},
}

############################
### MC based BG estimate ###
############################
for s in samples:
    plotter.addHistogramToStack(s,sigMap[s])

if not blind: plotter.addHistogram('data',sigMap['data'])


for plot in plots:
    for sel in sels:
        kwargs = deepcopy(plots[plot])
        plotname = '{0}/{1}'.format(sel,plot)
        savename = '{0}/mc/{1}'.format(sel,plot)
        plotter.plot(plotname,savename,**kwargs)

