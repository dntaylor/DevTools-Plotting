'''
Functions to produce a single plot for the Hpp3l analysis.
'''
import os
import json
import sys
import logging
from itertools import product, combinations_with_replacement

from DevTools.Plotter.Plotter import Plotter
from DevTools.Plotter.Counter import Counter
from DevTools.Utilities.utilities import ZMASS
from DevTools.Plotter.higgsUtilities import *
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
modes = ['ee100','em100','et100','mm100','mt100','tt100','BP1','BP2','BP3','BP4']


samples = ['TTV','VVV','ZZ','WZ']
allsamples = ['W','T','TT','TTV','Z','WW','VVV','ZZ','WZ']
signals = ['HppHm500GeV']
allSignals4l = ['HppHmm{0}GeV'.format(mass) for mass in masses]
allSignals3l = ['HppHm{0}GeV'.format(mass) for mass in masses]

allSamplesDict = {'BG':[]}
for s in allsamples:
    allSamplesDict['BG'] += sigMap[s]

datadrivenSamples = []
for s in samples + ['data']:
    datadrivenSamples += sigMapDD[s]

scales = {}
for mode in modes:
    scales[mode] = getScales(mode)

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

leps = ['hpp1','hpp2','hm1']

##########################
### build the plotters ###
##########################

def getPlotter(blind=True,datadriven=False,control=False):
     plotter = Plotter('Hpp3l')
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
### Build the counters ###
##########################

def getCounter(blind=True,datadriven=False,mass=0,mode=''):
     counter = Counter('Hpp3l')

     mcSamples = samples if datadriven else allsamples
     signalMap = sigMapDD if datadriven else sigMap
     for s in mcSamples:
         sCuts = {}
         for ss in signalMap[s]:
             if ss in sampleCuts: sCuts[ss] = sampleCuts[ss]
         counter.addProcess(s,signalMap[s],sampleCuts=sCuts)
     
     allSignals = allSignals3l
     if mass: allSignals = ['HppHm{0}GeV'.format(mass)]
     cutScaleMap = {}
     if mode in scales:
         scaleMap = {}
         scale = scales[mode]
         for gen in genRecoMap:
             if len(gen)!=3: continue
             thisScale = scale.scale_Hpp3l(gen[:2],gen[2:])
             if not thisScale: continue
             if thisScale not in scaleMap:
                 scaleMap[thisScale] = []
             scaleMap[thisScale] += [gen]
         for s,chans in scaleMap.iteritems():
             cut = '(' + ' || '.join(['genChannel=="{0}"'.format(chan) for chan in chans]) + ')'
             cutScaleMap[cut] = s
     for signal in allSignals:
         scalesForSignal = {}
         for process in signalMap[signal]:
             if cutScaleMap: scalesForSignal[process] = cutScaleMap
         counter.addProcess(signal,signalMap[signal],signal=True,scale=scalesForSignal)
     
     if not blind: counter.addProcess('data',signalMap['data'])
     return counter



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
    fullSelection = ' && '.join([selection,'hpp_mass<100']+['{0}_passMedium'.format(lep) for lep in leps])
    if cat in cats:
        channelCut = '(' + ' || '.join(['channel=="{0}"'.format(c) for subcat in subCatChannels[cat] for chan in subCatChannels[cat][subcat] for c in chans[chan]]) + ')'
        fullSelection = '{0} && {1}'.format(fullSelection,channelCut)
    mcscale = '*'.join(['genWeight','pileupWeight','triggerEfficiency'] + ['{0}_mediumScale'.format(lep) for lep in leps])
    plotter.plot(variable,savename,selection=fullSelection,binning=binning,mcscalefactor=mcscale,**kwargs)

##########################
### Counting functions ###
##########################
def getCounts(*selections,**kwargs):
    mode = kwargs.pop('mode','')
    mass = kwargs.pop('mass',500)

    counter = getCounter(mode=mode,mass=mass,blind=False)

    result = []
    for selection in selections:
        fullSelection = ' && '.join([selection]+['{0}_passMedium'.format(lep) for lep in leps])
        mcscale = '*'.join(['genWeight','pileupWeight','triggerEfficiency'] + ['{0}_mediumScale'.format(lep) for lep in leps])

        result += [counter.getCounts('none',selection=fullSelection,mcscalefactor=mcscale)]

    return result

