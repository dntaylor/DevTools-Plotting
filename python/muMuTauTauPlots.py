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

blind = True

plotter = Plotter('MuMuTauTau')

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
        'WZTo3LNu_TuneCUETP8M1_13TeV-powheg-pythia8',
    ],
    'ZZ': [
        'ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8',
        'ZZTo4L_13TeV-amcatnloFXFX-pythia8',
    ],
    'HToAAH125A5'  : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-5_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH125A7'  : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-7_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH125A9'  : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-9_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH125A11' : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-11_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH125A13' : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-13_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH125A15' : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-15_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH125A17' : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-17_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH125A19' : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-19_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH125A21' : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-21_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH300A5'  : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-300_M-5_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH300A7'  : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-300_M-7_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH300A9'  : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-300_M-9_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH300A11' : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-300_M-11_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH300A13' : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-300_M-13_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH300A15' : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-300_M-15_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH300A17' : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-300_M-17_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH300A19' : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-300_M-19_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH300A21' : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-300_M-21_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH750A5'  : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-750_M-5_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH750A7'  : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-750_M-7_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH750A9'  : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-750_M-9_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH750A11' : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-750_M-11_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH750A13' : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-750_M-13_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH750A15' : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-750_M-15_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH750A17' : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-750_M-17_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH750A19' : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-750_M-19_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH750A21' : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-750_M-21_TuneCUETP8M1_13TeV_madgraph_pythia8'],
}

samples = ['QCD','W','Z','TT','WW','WZ','ZZ']
signals = ['HToAAH125A15']


########################
### plot definitions ###
########################
plots = {
    # h
    'hMass'                 : {'xaxis': 'm^{#mu#mu#tau_{#mu}#tau_{h}} (GeV)', 'yaxis': 'Events / 10 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,650,10), 'logy': True, 'overflow': True},
    'hMt'                   : {'xaxis': 'm_{T}^{#mu#mu#tau_{#mu}#tau_{h}} (GeV)', 'yaxis': 'Events / 10 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,650,10), 'logy': True, 'overflow': True},
    'hDeltaMass'            : {'xaxis': 'm^{#mu#mu}-m^{#tau_{#mu}#tau_{h}} (GeV)', 'yaxis': 'Events / 10 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(-250,250,50), 'logy': True, 'overflow': True},
    'hDeltaMt'              : {'xaxis': 'm^{#mu#mu}-m_{T}^{#tau_{#mu}#tau_{h}} (GeV)', 'yaxis': 'Events / 10 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(-250,250,50), 'logy': True, 'overflow': True},
    # amm
    'ammMass'               : {'xaxis': 'm^{#mu#mu} (GeV)', 'yaxis': 'Events / 0.5 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.5, range(0,60,1)), 'logy': True, 'overflow': True},
    'ammDeltaR'             : {'xaxis': '#Delta R(#mu#mu) (GeV)', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.05, range(0,30,1)), 'logy': True, 'overflow': True},
    'am1Pt'                 : {'xaxis': 'a_{1}^{#mu#mu} #mu_{1} p_{T} (GeV)', 'yaxis': 'Events / 5 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,150,5), 'logy': True, 'overflow': True},
    'am2Pt'                 : {'xaxis': 'a_{1}^{#mu#mu} #mu_{2} p_{T} (GeV)', 'yaxis': 'Events / 5 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,150,5), 'logy': True, 'overflow': True},
    # att
    'attMass'               : {'xaxis': 'm^{#tau_{#mu}#tau_{h}} (GeV)', 'yaxis': 'Events / 1 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,60,1), 'logy': True, 'overflow': True},
    'attMt'                 : {'xaxis': 'm_{T}^{#tau_{#mu}#tau_{h}} (GeV)', 'yaxis': 'Events / 1 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,60,1), 'logy': True, 'overflow': True},
    'attDeltaR'             : {'xaxis': '#Delta R(#tau_{#mu}#tau_{h}) (GeV)', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.05, range(0,90,1)), 'logy': True, 'overflow': True},
    'atmPt'                 : {'xaxis': 'a_{1}^{#tau_{#mu}#tau_{h}} #tau_{#mu} p_{T} (GeV)', 'yaxis': 'Events / 5 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,150,5), 'logy': True, 'overflow': True},
    'athPt'                 : {'xaxis': 'a_{1}^{#tau_{#mu}#tau_{h}} #tau_{h} p_{T} (GeV)', 'yaxis': 'Events / 5 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,150,5), 'logy': True, 'overflow': True},
    # event
    'numVertices'           : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    'met'                   : {'xaxis': 'E_{T}^{miss} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': range(0,320,20), 'numcol': 2, 'logy': True, 'overflow': True},
}

############################
### MC based BG estimate ###
############################
for s in samples:
    plotter.addHistogramToStack(s,sigMap[s])

for signal in signals:
    plotter.addHistogram(signal,sigMap[signal],signal=True)

if not blind: plotter.addHistogram('data',sigMap['data'])


sels = ['default','regionA','regionB','regionC','regionD']

for plot in plots:
    for sel in sels:
        kwargs = deepcopy(plots[plot])
        plotname = '{0}/{1}'.format(sel,plot)
        savename = 'mc-{0}/{1}'.format(sel,plot)
        plotter.plot(plotname,savename,**kwargs)

