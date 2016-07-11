import os
import json
import sys
import logging
from itertools import product, combinations_with_replacement

from DevTools.Plotter.Plotter import Plotter
from DevTools.Utilities.utilities import ZMASS
from DevTools.Plotter.higgsUtilities import *
from copy import deepcopy
import ROOT

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

blind = True
plotCount = True
plotMC = True
plotDatadriven = True
plotFakeRegions = True

zzPlotter = Plotter('ZZ')

#########################
### Define categories ###
#########################

sigMap = getSigMap('Hpp4l')
sigMapDD = getSigMap('Hpp4l',datadriven=True)

chans = ['eeee','eemm','mmmm']
chanLabels = ['eeee','ee#mu#mu','#mu#mu#mu#mu']

samples = ['TTV','VVV','ZZ']
allsamples = ['TT','TTV','Z','WZ','VVV','ZZ']

allSamplesDict = {'BG':[]}
for s in allsamples:
    allSamplesDict['BG'] += sigMap[s]

datadrivenSamples = []
for s in samples + ['data']:
    datadrivenSamples += sigMapDD[s]


########################
### Helper functions ###
########################
def getDataDrivenPlot(*plots):
    histMap = {}
    regions = ['3P1F','2P2F','1P3F','0P4F']
    #regions = ['3P1F','2P2F']
    for s in samples + ['data','datadriven']: histMap[s] = []
    for plot in plots:
        plotdirs = plot.split('/')
        for s in samples + ['data']: histMap[s] += ['/'.join(['4P0F']+plotdirs)]
        histMap['datadriven'] += ['/'.join([reg]+plotdirs) for reg in regions]
    return histMap

def plotCounts(plotter,baseDir='default',saveDir='',datadriven=False,postfix=''):
    # per channel counts
    countVars = ['/'.join([x for x in [baseDir,'count'] if x])] + ['/'.join([x for x in [baseDir,chan,'count'] if x]) for chan in sorted(chans)]
    if datadriven:
        for i in range(len(countVars)):
            countVars[i] = getDataDrivenPlot(countVars[i])
    countLabels = ['Total'] + chanLabels
    savename = '/'.join([x for x in [saveDir,'individualChannels'] if x])
    if postfix: savename += '_{0}'.format(postfix)
    plotter.plotCounts(countVars,countLabels,savename,numcol=3,logy=0,legendpos=34)

def plotWithChannels(plotter,plot,baseDir='',saveDir='',datadriven=False,postfix='',**kwargs):
    plotname = '/'.join([x for x in [baseDir,plot] if x])
    plotvars = getDataDrivenPlot(plotname) if datadriven else plotname
    savename = '/'.join([x for x in [saveDir,plot] if x])
    if postfix: savename += '_{0}'.format(postfix)
    plotter.plot(plotvars,savename,**kwargs)
    for chan in chans:
        plotnames = ['/'.join([x for x in [baseDir,chan,plot] if x])]
        plotvars = getDataDrivenPlot(*plotnames) if datadriven else plotnames
        savename = '/'.join([x for x in [saveDir,chan,plot] if x])
        if postfix: savename += '_{0}'.format(postfix)
        plotter.plot(plotvars,savename,**kwargs)


########################
### plot definitions ###
########################
plots = {
    # z1
    'z1Mass'               : {'xaxis': 'm_{l^{+}l^{-}} (GeV)', 'yaxis': 'Events / 10 GeV', 'numcol': 3, 'lumipos': 11, 'legendpos':34, 'rebin': 1, 'rangex': [0,200]},
    'z1Pt'                 : {'xaxis': 'p_{T}^{l^{+}l^{-}} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': 2, 'rangex': [0,300]},
    'z1DeltaR'             : {'xaxis': '#DeltaR(l^{+}l^{-})', 'yaxis': 'Events', 'rebin': 5},
    'z1LeadingLeptonPt'    : {'xaxis': 'p_{T}^{Z lead} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': 2, 'rangex': [0,300]},
    'z1LeadingLeptonEta'   : {'xaxis': '#eta^{Z lead}', 'yaxis': 'Events', 'rebin': 5},
    'z1SubLeadingLeptonPt' : {'xaxis': 'p_{T}^{Z sublead} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': 2, 'rangex': [0,300]},
    'z1SubLeadingLeptonEta': {'xaxis': '#eta^{Z sublead}', 'yaxis': 'Events', 'rebin': 5},
    # z2
    'z2Mass'               : {'xaxis': 'm_{l^{+}l^{-}} (GeV)', 'yaxis': 'Events / 10 GeV', 'numcol': 3, 'lumipos': 11, 'legendpos':34, 'rebin': 1, 'rangex': [0,200]},
    'z2Pt'                 : {'xaxis': 'p_{T}^{l^{+}l^{-}} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': 2, 'rangex': [0,300]},
    'z2DeltaR'             : {'xaxis': '#DeltaR(l^{+}l^{-})', 'yaxis': 'Events', 'rebin': 5},
    'z2LeadingLeptonPt'    : {'xaxis': 'p_{T}^{Z lead} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': 2, 'rangex': [0,300]},
    'z2LeadingLeptonEta'   : {'xaxis': '#eta^{Z lead}', 'yaxis': 'Events', 'rebin': 5},
    'z2SubLeadingLeptonPt' : {'xaxis': 'p_{T}^{Z sublead} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': 2, 'rangex': [0,300]},
    'z2SubLeadingLeptonEta': {'xaxis': '#eta^{Z sublead}', 'yaxis': 'Events', 'rebin': 5},
    # event
    'numVertices'           : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    'met'                   : {'xaxis': 'E_{T}^{miss} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': 2},
    'metPhi'                : {'xaxis': '#phi(E_{T}^{miss})', 'yaxis': 'Events', 'rebin': 5},
    'mass'                  : {'xaxis': 'm_{4l} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': 2, 'rangex': [0,1000]},
    'st'                    : {'xaxis': '#Sigma p_{T}^{l} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': 2, 'rangex': [0,1000]},
    'nJets'                 : {'xaxis': 'Number of jets (p_{T} > 30 GeV)', 'yaxis': 'Events'},
}



############################
### MC based BG estimate ###
############################
if plotMC:
    for s in allsamples:
        zzPlotter.addHistogramToStack(s,sigMap[s])
    
    zzPlotter.addHistogram('data',sigMap['data'])
    
    if plotCount: plotCounts(zzPlotter,baseDir='default',saveDir='mc')
    if plotCount: plotCounts(zzPlotter,baseDir='zWindow',saveDir='mc-zWindow')
    
    for plot in plots:
        kwargs = deepcopy(plots[plot])
        plotWithChannels(zzPlotter,plot,baseDir='default',saveDir='mc',**kwargs)
        plotWithChannels(zzPlotter,plot,baseDir='zWindow',saveDir='mc-zWindow',**kwargs)
    
##############################
### datadriven backgrounds ###
##############################
if plotDatadriven:
    zzPlotter.clearHistograms()
    
    zzPlotter.addHistogramToStack('datadriven',datadrivenSamples)
    
    for s in samples:
        zzPlotter.addHistogramToStack(s,sigMapDD[s])
    
    zzPlotter.addHistogram('data',sigMapDD['data'])
    
    if plotCount: plotCounts(zzPlotter,baseDir='',saveDir='datadriven',datadriven=True)
    if plotCount: plotCounts(zzPlotter,baseDir='zWindow',saveDir='datadriven-zWindow',datadriven=True)
    
    for plot in plots:
        kwargs = deepcopy(plots[plot])
        plotWithChannels(zzPlotter,plot,baseDir='',saveDir='datadriven',datadriven=True,**kwargs)
        plotWithChannels(zzPlotter,plot,baseDir='zWindow',saveDir='datadriven-zWindow',datadriven=True,**kwargs)
    

####################
### Fake Regions ###
####################
if plotFakeRegions:
    zzPlotter.clearHistograms()
    
    for s in allsamples:
        zzPlotter.addHistogramToStack(s,sigMap[s])

    zzPlotter.addHistogram('data',sigMap['data'])
    
    for fr in ['3P1F','2P2F','1P3F','0P4F']:
        if plotCount: plotCounts(zzPlotter,baseDir='{0}_regular'.format(fr),saveDir='mc/{0}'.format(fr))
        #if plotCount: plotCounts(zzPlotter,baseDir='{0}_regular/zWindow'.format(fr),saveDir='mc-zWindow/{0}'.format(fr))
        
        for plot in plots:
            kwargs = deepcopy(plots[plot])
            plotWithChannels(zzPlotter,plot,baseDir='{0}_regular'.format(fr),saveDir='mc/{0}'.format(fr),**kwargs)
            #plotWithChannels(zzPlotter,plot,baseDir='{0}_regular/zWindow'.format(fr),saveDir='mc-zWindow/{0}'.format(fr),**kwargs)

