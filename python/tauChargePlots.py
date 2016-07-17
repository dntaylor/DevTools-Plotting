import os
import sys
import logging

from DevTools.Plotter.Plotter import Plotter
from copy import deepcopy

import ROOT

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

chargePlotter = Plotter('TauCharge')

chans = ['tt']

labelMap = {
    'e': 'e',
    'm': '#mu',
    't': '#tau',
}
chanLabels = ['#tau_{#mu}#tau_{h}']

sigMap = {
    'WW'  : [
             'WWTo2L2Nu_13TeV-powheg',
             #'WWToLNuQQ_13TeV-powheg',
            ],
    'W'   : [
             #'WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
             'WJetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'W1JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'W2JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'W3JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'W4JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
            ],
    'Z'   : [
             #'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
             #'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
             'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'DY1JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'DY2JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'DY3JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'DY4JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
            ],
    'TT'  : [
             'TTJets_DiLept_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'TTJets_SingleLeptFromT_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'TTJets_SingleLeptFromTbar_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
            ],
    'data': [
             'SingleMuon',
            ],
}

samples = ['W','WW','TT','Z']
#samples = ['TT','Z']

for s in samples:
    chargePlotter.addHistogramToStack(s,sigMap[s])

chargePlotter.addHistogram('data',sigMap['data'])

# plot definitions
plots = {
    # z cand
    'zMass'                 : {'xaxis': 'm_{#tau_{#mu}#tau_{h}} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': 50, 'rangex': [35,85]},
    'zTauMuPt'              : {'xaxis': 'p_{T}^{#tau_{#mu}} (GeV)',     'yaxis': 'Events / 5 GeV', 'rebin': 50, 'rangex': [0,150]},
    'zTauMuEta'             : {'xaxis': '|#eta^{#tau_{#mu}}|',          'yaxis': 'Events',         'rebin': 25, 'rangex': [-2.5,2.5]},
    'zTauHadPt'             : {'xaxis': 'p_{T}^{#tau_{h}} (GeV)',       'yaxis': 'Events / 5 GeV', 'rebin': 50, 'rangex': [0,150]},
    'zTauHadEta'            : {'xaxis': '|#eta^{#tau_{h}}|',            'yaxis': 'Events',         'rebin': 25, 'rangex': [-2.5,2.5]},
    # met
    'met'                   : {'xaxis': 'E_{T}^{miss} (GeV)',           'yaxis': 'Events / 20 GeV','rebin': 20, 'rangex': [0,300]},
    'tauMuMt'               : {'xaxis': 'm_{T}^{#mu} (GeV)',            'yaxis': 'Events / 5 GeV', 'rebin': 50, 'rangex': [0,200]},
}

# signal region
for plot in plots:
    for sign in ['SS','OS','SS/mtCut','OS/mtCut']:
        for chan in chans:
            plotname = '{0}/{1}/{2}'.format(sign,chan,plot)
            savename = '{0}/{1}/{2}'.format(sign,chan,plot)
            chargePlotter.plot(plotname,savename,**plots[plot])

# ratios of SS/OS as func of pt/eta
chargePlotter.clearHistograms()

allSamplesDict = {'MC':[]}

for s in samples:
    allSamplesDict['MC'] += sigMap[s]

chargePlotter.addHistogram('MC',allSamplesDict['MC'],style={'linecolor': ROOT.kRed})
chargePlotter.addHistogram('data',sigMap['data'],style={'linecolor':ROOT.kBlack})

ptbins = [10,20,40,60,200]
etabins = [-2.3,-1.479,-0.8,0.,0.8,1.479,2.3]

ratio_cust = {
    'zTauMuPt'   : {'yaxis': 'N_{SS}/N_{OS}', 'rebin': ptbins},
    'zTauMuEta'  : {'yaxis': 'N_{SS}/N_{OS}', 'rebin': etabins},
    'zTauHadPt'  : {'yaxis': 'N_{SS}/N_{OS}', 'rebin': ptbins},
    'zTauHadEta' : {'yaxis': 'N_{SS}/N_{OS}', 'rebin': etabins},
}

for plot in ['Pt','Eta']:
    for lepton in ['zTauMu','zTauHad']:
        kwargs = deepcopy(plots[lepton+plot])
        if lepton+plot in ratio_cust: kwargs.update(ratio_cust[lepton+plot])
        for chan in chans:
            numname = 'SS/mtCut/{0}/{1}{2}'.format(chan,lepton,plot)
            denomname = 'OS/mtCut/{0}/{1}{2}'.format(chan,lepton,plot)
            savename = 'ratio/{0}/{1}{2}'.format(chan,lepton,plot)
            chargePlotter.plotRatio(numname,denomname,savename,ymax=1.,**kwargs)


