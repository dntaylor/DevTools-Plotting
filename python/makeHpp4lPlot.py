'''
Functions to produce a single plot for the Hpp4l analysis.
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

cats = getCategories('Hpp4l')
catLabels = getCategoryLabels('Hpp4l')
subCatChannels = getSubCategories('Hpp4l')
subCatLabels = getSubCategoryLabels('Hpp4l')
chans = getChannels('Hpp4l')
chanLabels = getChannelLabels('Hpp4l')
genRecoMap = getGenRecoChannelMap('Hpp4l')
sigMap = getSigMap('Hpp4l')
sigMapDD = getSigMap('Hpp4l',datadriven=True)

allmasses = [200,300,400,500,600,700,800,900,1000,1100,1200,1300,1400,1500]
masses = [200,400,600,800,1000]

samples = ['TTV','VVV','ZZ']
allsamples = ['TT','TTV','Z','VVV','ZZ','WZ']
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
    'WJetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'           : '(numGenJets==0 || numGenJets>4)',
    'W1JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          : 'numGenJets==1',
    'W2JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          : 'numGenJets==2',
    'W3JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          : 'numGenJets==3',
    'W4JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          : 'numGenJets==4',
}

leps = ['hpp1','hpp2','hmm1','hmm2']

##########################
### build the plotters ###
##########################

def getPlotter(blind=True,datadriven=False,control=False):
     plotter = Plotter('Hpp4l')
     plotter.setSelectionMap(sampleCuts)
     
     if datadriven: plotter.addHistogramToStack('datadriven',datadrivenSamples)

     mcSamples = samples if datadriven else allsamples
     signalMap = sigMapDD if datadriven else sigMap
     for s in mcSamples:
         plotter.addHistogramToStack(s,signalMap[s])
     
     if not control:
         for signal in signals:
             plotter.addHistogram(signal,signalMap[signal],signal=True)
     
     if not blind: plotter.addHistogram('data',signalMap['data'])
     return plotter


##########################
### Plotting functions ###
##########################
def makePlot(savename,variable,binning,selection='1',blind=True,**kwargs):
    '''
    Make a plot using MC background estimation.
    '''
    cat = kwargs.pop('category','')
    plotter = getPlotter(blind=blind)
    fullSelection = ' && '.join([selection]+['{0}_passMedium'.format(lep) for lep in leps])
    if cat in cats:
        channelCut = '(' + ' || '.join(['channel=="{0}"'.format(c) for subcat in subCatChannels[cat] for chan in subCatChannels[cat][subcat] for c in chans[chan]]) + ')'
        fullSelection = '{0} && {1}'.format(fullSelection,channelCut)
    mcscale = '*'.join(['genWeight','pileupWeight','triggerEfficiency'] + ['{0}_mediumScale'.format(lep) for lep in leps])
    plotter.plot(variable,savename,selection=fullSelection,binning=binning,mcscalefactor=mcscale,**kwargs)

def makeLowMassPlot(savename,variable,binning,selection='1',**kwargs):
    '''
    Make a plot using MC background estimation for low mass control.
    '''
    cat = kwargs.pop('category','')
    plotter = getPlotter(blind=False,control=True)
    fullSelection = ' && '.join([selection,'(hpp_mass<100 || hmm_mass<100)']+['{0}_passMedium'.format(lep) for lep in leps])
    if cat in cats:
        channelCut = '(' + ' || '.join(['channel=="{0}"'.format(c) for subcat in subCatChannels[cat] for chan in subCatChannels[cat][subcat] for c in chans[chan]]) + ')'
        fullSelection = '{0} && {1}'.format(fullSelection,channelCut)
    mcscale = '*'.join(['genWeight','pileupWeight','triggerEfficiency'] + ['{0}_mediumScale'.format(lep) for lep in leps])
    plotter.plot(variable,savename,selection=fullSelection,binning=binning,mcscalefactor=mcscale,**kwargs)
