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
        'SingleMuon',
    ],
}

samples = ['W','TT','WW','WZ','ZZ','Z']

sigMap['BG'] = []
for s in ['WZ','ZZ']:
    sigMap['BG'] += sigMap[s]

sels = []
etaBins = [0,1.479,2.3]
base_sels = ['nearMuon','nearMuonMedium']
for sel in base_sels:
    sels += [sel]
    sels += ['noBVeto/{}'.format(sel)]
    for dm in [0,1,10]:
        sels += ['{}/dm{}'.format(sel,dm)]
        sels += ['noBVeto/{}/dm{}'.format(sel,dm)]
    for eb in range(len(etaBins)-1):
        sels += ['{}/etaBin{}'.format(sel,eb)]
        sels += ['noBVeto/{}/etaBin{}'.format(sel,eb)]
        for dm in [0,1,10]:
            sels += ['{}/dm{}/etaBin{}'.format(sel,dm,eb)]
            sels += ['noBVeto/{}/dm{}/etaBin{}'.format(sel,dm,eb)]

alt_sels = ['default','medium','notMedium']
alt_sels += ['noBVeto/default','noBVeto/medium','noBVeto/notMedium']
pt_sels = ['pt10to20','pt20']
sels2 = []
for sel in alt_sels:
    sels2 += [sel]
    for s in pt_sels:
        sels2 += ['{}/{}'.format(sel,s)]

########################
### plot definitions ###
########################
plots = {
    # z
    'zMass'                 : {'xaxis': 'm^{#mu#mu} (GeV)', 'yaxis': 'Events / 0.5 GeV', 'numcol': 3, 'lumipos': 11, 'legendpos':34, 'rebin': map(lambda x: x*0.5, range(162,202,1)), 'logy': False, 'overflow': True, 'yscale':1.6},
    'z1Pt'                  : {'xaxis': 'm^{#mu#mu} #mu_{1} p_{T} (GeV)', 'yaxis': 'Events / 5 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(25,150,5), 'logy': False, 'overflow': True},
    'z2Pt'                  : {'xaxis': 'm^{#mu#mu} #mu_{2} p_{T} (GeV)', 'yaxis': 'Events / 5 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(10,150,5), 'logy': False, 'overflow': True},
    # t
    'tPt'                   : {'xaxis': '#tau p_{T} (GeV)', 'yaxis': 'Events / 5 GeV', 'numcol': 2, 'lumipos': 11, 'legendpos':34, 'rebin': range(10,150,5), 'logy': False, 'overflow': True},
    'tDM'                   : {'xaxis': '#tau Decay Mode', 'yaxis': 'Events', 'numcol': 3, 'lumipos': 11, 'legendpos':34, 'logy': False, 'yscale': 1.5,},
    # event
    'count'                 : {'xaxis': '', 'yaxis': 'Events', 'numcol': 3, 'lumipos': 11, 'legendpos':34, 'logy': False, 'yscale': 1.5,'binlabels': ['']},
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

plotter.clearHistograms()
plotter.addHistogramToStack('W',sigMap['W'])
plotter.addHistogramToStack('TT',sigMap['TT'])
plotter.addHistogramToStack('VV',sigMap['WW']+sigMap['WZ']+sigMap['ZZ'])
plotter.addHistogramToStack('DYB',sigMap['Z'])
plotter.addHistogramToStack('DYJ',sigMap['Z'])
#plotter.addHistogramToStack('DYS',sigMap['Z'])

if not blind: plotter.addHistogram('data',sigMap['data'])

realmcs = ['W','TT','VV']
zllfakes = ['DYJ']
zlllight = ['DYB']
zlltau = ['DYS']

for plot in plots:
    for sel in sels2:
        kwargs = deepcopy(plots[plot])
        plotnames = {}
        for bg in realmcs+['data']:
            plotnames[bg] = '{0}/{1}'.format(sel,plot)
        for bg in zllfakes:
            plotnames[bg] = 'fakeTau/{0}/{1}'.format(sel,plot)
        for bg in zlllight:
            plotnames[bg] = 'leptonicTau/{0}/{1}'.format(sel,plot)
        for bg in zlltau:
            plotnames[bg] = 'hadronicTau/{0}/{1}'.format(sel,plot)
        savename = '{0}/mc/{1}'.format(sel,plot)
        plotter.plot(plotnames,savename,**kwargs)


# ratios of tight/loose as func of pt/eta
plotter.clearHistograms()
plotter.addHistogram('MC',sigMap['BG'])
plotter.addHistogram('Z',sigMap['Z'])
plotter.addHistogram('data',sigMap['data'],style={'linecolor':ROOT.kBlack,'name':'Data'})
plotter.addHistogram('data_uncorrected',sigMap['data'],style={'linecolor':ROOT.kRed,'name':'Uncorrected'})

ptbins = [10,20,30,50,100]
etabins = [-2.3,-1.479,0.,1.479,2.3]

cust = {
    'tPt'     : {'rebin': ptbins, 'overflow': False},
    #'tEta'    : {'rebin': etabins},
}

numDenoms = []
numDenoms_base = [
    #('nearMuonVLoose','nearMuon'),
    #('nearMuonLoose','nearMuon'),
    ('nearMuonMedium','nearMuon'),
    #('nearMuonTight','nearMuon'),
    #('cutbased/nearMuonLoose','nearMuon'),
    #('cutbased/nearMuonMedium','nearMuon'),
    #('cutbased/nearMuonTight','nearMuon'),
]
for n, d in numDenoms_base:
    numDenoms += [(n,d)]
    numDenoms += [('noBVeto/{}'.format(n), 'noBVeto/{}'.format(d))]
    for dm in [0,1,10]:
        numDenoms += [('{}/dm{}'.format(n,dm), '{}/dm{}'.format(d,dm))]
        numDenoms += [('noBVeto/{}/dm{}'.format(n,dm), 'noBVeto/{}/dm{}'.format(d,dm))]
for newloose in [-0.5]:
    numDenoms += [('nearMuonMedium','nearMuonWithMVA{:0.1f}'.format(newloose))]
    for dm in [0,1,10]:
        numDenoms += [('nearMuonMedium/dm{}'.format(dm),'nearMuonWithMVA{:0.1f}/dm{}'.format(newloose,dm))]

for plot in cust:
    for num,denom in numDenoms:
        kwargs = deepcopy(plots[plot])
        kwargs.update(cust[plot])
        kwargs['yaxis'] = 'Ratio'
        numname = '{0}/{1}'.format(num,plot)
        denomname = '{0}/{1}'.format(denom,plot)
        savename = 'ratio/{0}_{1}/{2}'.format(num,denom,plot)
        #if '/' in num:
        #    savename = 'ratio/{0}_{1}/{2}'.format(num,denom.split('/')[-1],plot)
        subtractMap = {
            'data': ['MC'],
        }
        customOrder = ['data_uncorrected','Z','data']
        plotter.plotRatio(numname,denomname,savename,ymax=1.,customOrder=customOrder,subtractMap=subtractMap,**kwargs)
        for eb in range(2):
            kwargs = deepcopy(plots[plot])
            kwargs.update(cust[plot])
            kwargs['yaxis'] = 'Ratio'
            numname = '{0}/etaBin{1}/{2}'.format(num,eb,plot)
            denomname = '{0}/etaBin{1}/{2}'.format(denom,eb,plot)
            savename = 'ratio/{0}_{1}/{2}_etaBin{3}'.format(num,denom,plot,eb)
            #if '/' in num:
            #    savename = 'ratio/{0}_{1}/{2}_etaBin{3}'.format(num,denom.split('/')[-1],plot,eb)
            subtractMap = {
                'data': ['MC'],
            }
            customOrder = ['data_uncorrected','Z','data']
            plotter.plotRatio(numname,denomname,savename,ymax=1.,customOrder=customOrder,subtractMap=subtractMap,**kwargs)
