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

plotter = Plotter('MuMuMuFakeRate')

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
        #'ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8',
        'ZZTo4L_13TeV-amcatnloFXFX-pythia8',
    ],
    'data' : [
        'DoubleMuon',
    ],
}

samples = ['W','TT','WW','WZ','ZZ','Z']

sigMap['BG'] = []
for s in ['WZ','ZZ']:
    sigMap['BG'] += sigMap[s]

sels = ['default','iso0.15','iso0.25','iso0.40']
sels += ['defaulttrig','iso0.15trig','iso0.25trig','iso0.40trig']
etaBins = [0,1.0,1.5,2.4]
for eb in range(len(etaBins)-1):
    sels += ['default/etaBin{0}'.format(eb), 'iso0.15/etaBin{0}'.format(eb), 'iso0.25/etaBin{0}'.format(eb), 'iso0.40/etaBin{0}'.format(eb),]
    sels += ['defaulttrig/etaBin{0}'.format(eb), 'iso0.15trig/etaBin{0}'.format(eb), 'iso0.25trig/etaBin{0}'.format(eb), 'iso0.40trig/etaBin{0}'.format(eb),]


########################
### plot definitions ###
########################
plots = {
    # z
    'zMass'                 : {'xaxis': 'm^{#mu#mu} (GeV)', 'yaxis': 'Events / 0.5 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.5, range(120,240,1)), 'logy': False, 'overflow': True},
    'z1Pt'                  : {'xaxis': 'm^{#mu#mu} #mu_{1} p_{T} (GeV)', 'yaxis': 'Events / 5 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,150,5), 'logy': False, 'overflow': True},
    'z2Pt'                  : {'xaxis': 'm^{#mu#mu} #mu_{2} p_{T} (GeV)', 'yaxis': 'Events / 5 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,150,5), 'logy': False, 'overflow': True},
    # t
    'mPt'                   : {'xaxis': '#mu p_{T} (GeV)', 'yaxis': 'Events / 5 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,150,5), 'logy': True, 'overflow': True},
    # event
    #'numVertices'           : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    #'met'                   : {'xaxis': 'E_{T}^{miss} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': range(0,320,20), 'numcol': 2, 'logy': False, 'overflow': True},
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


# ratios of tight/loose as func of pt/eta
plotter.clearHistograms()
plotter.addHistogram('MC',sigMap['BG'])
plotter.addHistogram('Z',sigMap['Z'])
plotter.addHistogram('data',sigMap['data'],style={'linecolor':ROOT.kBlack,'name':'Data'})
plotter.addHistogram('data_uncorrected',sigMap['data'],style={'linecolor':ROOT.kRed,'name':'Uncorrected'})

ptbins = [3,5,10,15,20,25,30,50,100]
etabins = [-2.4,-1.5,-1.0,0.,1.0,1.5,2.4]

cust = {
    'mPt'     : {'rebin': ptbins, 'overflow': False, 'logy': False},
    #'mEta'    : {'rebin': etabins},
}

numDenoms = [('iso0.15','default'),('iso0.25','default'),('iso0.40','default'),('iso0.15','iso0.40'),]
numDenoms += [('iso0.15trig','defaulttrig'),('iso0.25trig','defaulttrig'),('iso0.40trig','defaulttrig'),('iso0.15trig','iso0.40trig'),]

for plot in cust:
    for num,denom in numDenoms:
        kwargs = deepcopy(plots[plot])
        kwargs.update(cust[plot])
        kwargs['yaxis'] = 'Ratio'
        numname = '{0}/{1}'.format(num,plot)
        denomname = '{0}/{1}'.format(denom,plot)
        savename = 'ratio/{0}_{1}/{2}'.format(num,denom,plot)
        subtractMap = {
            'data': ['MC'],
        }
        customOrder = ['data_uncorrected','Z','data']
        plotter.plotRatio(numname,denomname,savename,ymax=1.,customOrder=customOrder,subtractMap=subtractMap,**kwargs)
        for eb in range(3):
            kwargs = deepcopy(plots[plot])
            kwargs.update(cust[plot])
            kwargs['yaxis'] = 'Ratio'
            numname = '{0}/etaBin{1}/{2}'.format(num,eb,plot)
            denomname = '{0}/etaBin{1}/{2}'.format(denom,eb,plot)
            savename = 'ratio/{0}_{1}/{2}_etaBin{3}'.format(num,denom,plot,eb)
            subtractMap = {
                'data': ['MC'],
            }
            customOrder = ['data_uncorrected','Z','data']
            plotter.plotRatio(numname,denomname,savename,ymax=1.,customOrder=customOrder,subtractMap=subtractMap,**kwargs)
