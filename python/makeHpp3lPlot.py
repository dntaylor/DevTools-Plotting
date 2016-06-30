'''
Functions to produce a single plot for the Hpp3l analysis.
'''
import os
import json
import sys
import logging
from itertools import product, combinations_with_replacement

from DevTools.Plotter.Plotter import Plotter
from DevTools.Utilities.utilities import ZMASS
from DevTools.Plotter.higgsUtilities import getChannels, getChannelLabels, getCategories, getCategoryLabels, getSubCategories, getSubCategoryLabels, getGenRecoChannelMap, getSigMap
from copy import deepcopy
import ROOT

blind = True

#########################
### Define categories ###
#########################

cats = getCategories('Hpp3l')
catLabels = getCategoryLabels('Hpp3l')
subCatChannels = getSubCategories('Hpp3l')
subCatLabels = getSubCategoryLabels('Hpp3l')
chans = getChannels('Hpp3l')
chanLabels = getChannelLabels('Hpp3l')
genRecoMap = getGenRecoChannelMap('Hpp3l')
sigMap = getSigMap('Hpp3l')
sigMapDD = getSigMap('Hpp3l',datadriven=True)

allmasses = [200,300,400,500,600,700,800,900,1000,1100,1200,1300,1400,1500]
masses = [200,400,600,800,1000]

samples = ['TTV','VVV','ZZ','WZ']
allsamples = ['W','T','TT','TTV','Z','WW','VVV','ZZ','WZ']
signals = ['HppHmm500GeV']

allSamplesDict = {'BG':[]}
for s in allsamples:
    allSamplesDict['BG'] += sigMap[s]

datadrivenSamples = []
for s in samples + ['data']:
    datadrivenSamples += sigMapDD[s]

sigColors = {
    200 : ROOT.TColor.GetColor('#000000'),
    300 : ROOT.TColor.GetColor('#330000'),
    400 : ROOT.TColor.GetColor('#660000'),
    500 : ROOT.TColor.GetColor('#800000'),
    600 : ROOT.TColor.GetColor('#990000'),
    700 : ROOT.TColor.GetColor('#B20000'),
    800 : ROOT.TColor.GetColor('#CC0000'),
    900 : ROOT.TColor.GetColor('#FF0000'),
    1000: ROOT.TColor.GetColor('#FF3333'),
    1100: ROOT.TColor.GetColor('#FF6666'),
    1200: ROOT.TColor.GetColor('#FF8080'),
    1300: ROOT.TColor.GetColor('#FF9999'),
    1400: ROOT.TColor.GetColor('#FFB2B2'),
    1500: ROOT.TColor.GetColor('#FFCCCC'),
}

# special selections for samples
# DY-10 0, 1, 2 bins (0 includes 3+)
# DY-50 0, 1, 2, 3, 4 bins (0 includes 5+)
sampleCuts = {
    #'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8' : '(numGenJets==0 || numGenJets>2)',
    #'DY1JetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8': 'numGenJets==1',
    #'DY2JetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8': 'numGenJets==2',
    'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'      : '(numGenJets==0 || numGenJets>4)',
    'DY1JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : 'numGenJets==1',
    'DY2JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : 'numGenJets==2',
    'DY3JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : 'numGenJets==3',
    'DY4JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : 'numGenJets==4',
    #'WJetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'           : '(numGenJets==0 || numGenJets>4)',
    #'W1JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          : 'numGenJets==1',
    #'W2JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          : 'numGenJets==2',
    #'W3JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          : 'numGenJets==3',
    #'W4JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          : 'numGenJets==4',
}

leps = ['hpp1','hpp2','hm1']

##########################
### build the plotters ###
##########################

# mc background
hpp3lPlotter = Plotter('Hpp3l')

hpp3lPlotter.setSelectionMap(sampleCuts)

for s in allsamples:
    hpp3lPlotter.addHistogramToStack(s,sigMap[s])

for signal in signals:
    hpp3lPlotter.addHistogram(signal,sigMap[signal],signal=True)

if not blind: hpp3lPlotter.addHistogram('data',sigMap['data'])

# datadriven background
hpp3lDDPlotter = Plotter('Hpp3l')

hpp3lDDPlotter.setSelectionMap(sampleCuts)

hpp3lDDPlotter.addHistogramToStack('datadriven',datadrivenSamples)

for s in samples:
    hpp3lDDPlotter.addHistogramToStack(s,sigMapDD[s])

for signal in signals:
    hpp3lDDPlotter.addHistogram(signal,sigMapDD[signal],signal=True)

if not blind: hpp3lDDPlotter.addHistogram('data',sigMapDD['data'])

##########################
### Plotting functions ###
##########################
def makePlot(savename,variable,binning,selection='1',**kwargs):
    '''
    Make a plot using MC background estimation.
    '''
    fullSelection = ' && '.join([selection]+['{0}_passMedium'.format(lep) for lep in leps])
    mcscale = '*'.join(['genWeight','pileupWeight','triggerEfficiency'] + ['{0}_mediumScale'.format(lep) for lep in leps])
    hpp3lPlotter.plot(variable,savename,selection=fullSelection,binning=binning,mcscalefactor=mcscale,**kwargs)
