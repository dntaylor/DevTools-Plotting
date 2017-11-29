import os
import json
import sys
import logging
from itertools import product, combinations_with_replacement

from DevTools.Plotter.Plotter import Plotter
from DevTools.Utilities.utilities import ZMASS, getCMSSWVersion
from copy import deepcopy
import ROOT
ROOT.gROOT.SetBatch(ROOT.kTRUE)

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

version = getCMSSWVersion()

blind = True
doDetRegions = True
doSignals = True
doMC = True
do2D = True

plotter = Plotter('MuMuTauTau')

#########################
### Define categories ###
#########################

sigMap = {
    'Z' : [
        'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
        'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
    ],
    'JPsi' : [
        'JpsiToMuMu_JpsiPt8_TuneCUEP8M1_13TeV-pythia8',
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
        'TTJets_SingleLeptFromTbar_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
        'TTJets_SingleLeptFromT_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
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
    'data' : [
        'SingleMuon',
    ],
}

#samples = ['QCD','W','Z','TT','WW','WZ','ZZ']
samples = ['W','Z','TT','WW','WZ','ZZ']

sigMap['BG'] = []
for s in samples:
    sigMap['BG'] += sigMap[s]

signals = ['HToAAH125A15']

signame = 'HToAAH{h}A{a}'

hmasses = [125,300,750]
amasses = [5,7,9,11,13,15,17,19,21]
amasses = [5,9,13,17,21]

hColors = {
    125: ROOT.TColor.GetColor('#000000'),
    300: ROOT.TColor.GetColor('#B20000'),
    750: ROOT.TColor.GetColor('#FFCCCC'),
}

aColors = {
    5 : ROOT.TColor.GetColor('#000000'),
    7 : ROOT.TColor.GetColor('#330000'),
    9 : ROOT.TColor.GetColor('#660000'),
    11: ROOT.TColor.GetColor('#800000'),
    13: ROOT.TColor.GetColor('#B20000'),
    15: ROOT.TColor.GetColor('#FF0000'),
    17: ROOT.TColor.GetColor('#FF6666'),
    19: ROOT.TColor.GetColor('#FF9999'),
    21: ROOT.TColor.GetColor('#FFCCCC'),
}


sels = ['default','regionA','regionB','regionC','regionD']

if doDetRegions:
    for sel in ['default','regionA','regionB','regionC','regionD']:
        sels += ['{0}/{1}'.format(sel,det) for det in ['BB','BE','EE']]

#for sel in ['default','regionA','regionB','regionC','regionD']:
#    sels += ['{0}/{1}'.format(sel,'dr0p8')]

########################
### plot definitions ###
########################
plots = {
    # h
    'hMass'                 : {'xaxis': 'm^{#mu#mu#tau_{#mu}#tau_{h}} (GeV)', 'yaxis': 'Events / 10 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,650,10), 'logy': False, 'overflow': True},
    'hMt'                   : {'xaxis': 'm_{T}^{#mu#mu#tau_{#mu}#tau_{h}} (GeV)', 'yaxis': 'Events / 10 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,650,10), 'logy': False, 'overflow': True},
    'hDeltaMass'            : {'xaxis': 'm^{#mu#mu}-m^{#tau_{#mu}#tau_{h}} (GeV)', 'yaxis': 'Events / 10 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(-250,250,10), 'logy': True, 'overflow': True},
    'hDeltaMt'              : {'xaxis': 'm^{#mu#mu}-m_{T}^{#tau_{#mu}#tau_{h}} (GeV)', 'yaxis': 'Events / 10 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(-250,250,10), 'logy': True, 'overflow': True},
    # amm
    'ammMass'               : {'xaxis': 'm^{#mu#mu} (GeV)', 'yaxis': 'Events / 0.5 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.5, range(0,60,1)), 'logy': False, 'overflow': True},
    'ammDeltaR'             : {'xaxis': '#Delta R(#mu#mu) (GeV)', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.05, range(0,30,1)), 'logy': False, 'overflow': True},
    'am1Pt'                 : {'xaxis': 'a_{1}^{#mu#mu} #mu_{1} p_{T} (GeV)', 'yaxis': 'Events / 5 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,150,5), 'logy': False, 'overflow': True},
    'am2Pt'                 : {'xaxis': 'a_{1}^{#mu#mu} #mu_{2} p_{T} (GeV)', 'yaxis': 'Events / 5 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,150,5), 'logy': False, 'overflow': True},
    # att
    'attMass'               : {'xaxis': 'm^{#tau_{#mu}#tau_{h}} (GeV)', 'yaxis': 'Events / 1 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,60,1), 'logy': False, 'overflow': True},
    'attMt'                 : {'xaxis': 'm_{T}^{#tau_{#mu}#tau_{h}} (GeV)', 'yaxis': 'Events / 2 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,120,2), 'logy': False, 'overflow': True},
    'attDeltaR'             : {'xaxis': '#Delta R(#tau_{#mu}#tau_{h}) (GeV)', 'yaxis': 'Events', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.1, range(0,30,1)), 'logy': False, 'overflow': True},
    'atmPt'                 : {'xaxis': 'a_{1}^{#tau_{#mu}#tau_{h}} #tau_{#mu} p_{T} (GeV)', 'yaxis': 'Events / 5 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,150,5), 'logy': False, 'overflow': True},
    'athPt'                 : {'xaxis': 'a_{1}^{#tau_{#mu}#tau_{h}} #tau_{h} p_{T} (GeV)', 'yaxis': 'Events / 5 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,150,5), 'logy': False, 'overflow': True},
    # event
    'numVertices'           : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    'met'                   : {'xaxis': 'E_{T}^{miss} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': range(0,320,20), 'numcol': 2, 'logy': False, 'overflow': True},
}

plots2D = {
    'ammMass_vs_attMass'    : {'xaxis': 'm^{#mu#mu} (GeV)', 'yaxis': 'm^{#tau_{#mu}#tau_{h}} (GeV)',},
    'ammMass_vs_hMass'      : {'xaxis': 'm^{#mu#mu} (GeV)', 'yaxis': 'm^{#mu#mu#tau_{#mu}#tau_{h}} (GeV)', 'rangey': [0,250],},
    'attMass_vs_hMass'      : {'xaxis': 'm^{#tau_{#mu}#tau_{h}} (GeV)', 'yaxis': 'm^{#mu#mu#tau_{#mu}#tau_{h}} (GeV)', 'rangey': [0,250],},
}

special = {
    'jpsi': {
        'ammMass'               : {'xaxis': 'm^{#mu#mu} (GeV)', 'yaxis': 'Events / 10 MeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.01, range(290,400,1)), 'logy': False, 'overflow': False},
    },
    'upsilon': {
        'ammMass'               : {'xaxis': 'm^{#mu#mu} (GeV)', 'yaxis': 'Events / 50 MeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.01, range(850,1150,5)), 'logy': False, 'overflow': False},
    },
}

############################
### MC based BG estimate ###
############################
if doMC:
    for s in samples:
        plotter.addHistogramToStack(s,sigMap[s])
    
    for signal in signals:
        plotter.addHistogram(signal,sigMap[signal],signal=True)
    
    if not blind: plotter.addHistogram('data',sigMap['data'])
    
    for plot in plots:
        for sel in sels:
            kwargs = deepcopy(plots[plot])
            plotname = '{0}/{1}'.format(sel,plot)
            savename = '{0}/mc/{1}'.format(sel,plot)
            plotter.plot(plotname,savename,**kwargs)
    
    if blind: plotter.addHistogram('data',sigMap['data'])
    
    for s in special:
        for plot in special[s]:
            for sel in sels:
                kwargs = deepcopy(special[s][plot])
                plotname = '{0}/{1}'.format(sel,plot)
                savename = '{0}/mc/{1}_{2}'.format(sel,plot,s)
                plotter.plot(plotname,savename,**kwargs)

#########################
### Signals on 1 plot ###
#########################

if doSignals:
    for h in hmasses:
        plotter.clearHistograms()
    
        for a in amasses:
            name = signame.format(h=h,a=a)
            plotter.addHistogram(name,sigMap[name],signal=True,style={'linecolor': aColors[a]})
    
        for plot in plots:
            for sel in sels:
                kwargs = deepcopy(plots[plot])
                plotname = '{0}/{1}'.format(sel,plot)
                savename = '{0}/h{h}/{1}'.format(sel,plot,h=h)
                plotter.plot(plotname,savename,plotratio=False,**kwargs)
        
    
    for a in [5,19]:
        plotter.clearHistograms()
        
        for h in hmasses:
            name = signame.format(h=h,a=a)
            plotter.addHistogram(name,sigMap[name],signal=True,style={'linecolor': hColors[h]})
    
        for plot in plots:
            for sel in sels:
                kwargs = deepcopy(plots[plot])
                plotname = '{0}/{1}'.format(sel,plot)
                savename = '{0}/a{a}/{1}'.format(sel,plot,a=a)
                plotter.plot(plotname,savename,plotratio=False,**kwargs)
    
################
### 2D plots ###
################
if do2D:
    for sample in samples+signals:
        plotter.clearHistograms()
        plotter.addHistogram(sample,sigMap[sample])
        
        for plot in plots2D:
            for sel in sels:
                kwargs = deepcopy(plots2D[plot])
                if sample not in signals:
                    kwargs['rebinx'] = 10
                    kwargs['rebiny'] = 10
                plotname = '{0}/{1}'.format(sel,plot)
                savename = '{0}/2D/{1}/{2}'.format(sel,sample,plot)
                plotter.plot2D(plotname,savename,**kwargs)

