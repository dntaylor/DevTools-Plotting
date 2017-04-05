
import os
import sys
import logging

from DevTools.Plotter.Plotter import Plotter
from copy import deepcopy
from DevTools.Plotter.wzUtilities import sigMap

import ROOT

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

wzPlotter = Plotter('WZ',new=True)

doCounts = True
doDatadriven = True
doMC = True
doNMinusOne = True
doControls = True
doVBS = True

plotStyles = {
    # Z
    'zMass'               : {'xaxis': 'm_{l^{+}l^{-}}', 'yaxis': 'Events / 1 GeV', 'rebin':range(60,121,1)},
    'zPt'                 : {'xaxis': 'p_{T}^{Z}', 'yaxis': 'Events / 5 GeV', 'rebin':range(0,205,5), 'overflow': True,},
    'zLeadingLeptonPt'    : {'xaxis': 'p_{T}^{Z lead}', 'yaxis': 'Events / 5 GeV', 'rebin':range(0,205,5), 'overflow': True,},
    'zSubLeadingLeptonPt' : {'xaxis': 'p_{T}^{Z sublead}', 'yaxis': 'Events / 5 GeV', 'rebin':range(0,205,5), 'overflow': True,},
    # W
    'wMass'               : {'xaxis': 'm_{T}^{W}', 'yaxis': 'Events / 5 GeV', 'rebin':range(0,205,5), 'overflow': True,},
    'wPt'                 : {'xaxis': 'p_{T}^{W}', 'yaxis': 'Events / 5 GeV', 'rebin':range(0,205,5), 'overflow': True,},
    'wLeptonPt'           : {'xaxis': 'p_{T}^{W lepton}', 'yaxis': 'Events / 5 GeV', 'rebin':range(0,205,5), 'overflow': True,},
    # event
    'met'                 : {'xaxis': 'E_{T}^{miss}', 'yaxis': 'Events / 5 GeV', 'rebin':range(0,205,5), 'overflow': True,},
    'mass'                : {'xaxis': 'm_{3l}', 'yaxis': 'Events / 10 GeV', 'rebin':range(0,510,10), 'overflow': True,},
    'nJets'               : {'xaxis': 'Number of Jets (p_{T} > 30 GeV)', 'yaxis': 'Events', 'rebin': [-0.5,0.5,1.5,2.5,3.5,4.5], 'overflow': True, 'binlabels': ['0','1','2','3','4','#geq5']},
    'nBjets'              : {'xaxis': 'Number of b-tagged Jets (p_{T} > 30 GeV)', 'yaxis': 'Events', 'rebin': [-0.5,0.5,1.5,2.5,3.5,4.5], 'overflow': True, 'binlabels': ['0','1','2','3','4','#geq5']},
    # vbf
    'leadJetPt'           : {'xaxis': 'Lead Jet p_{T}', 'yaxis': 'Events / 20 GeV', 'rebin': range(0,420,20), 'overflow': True,},
    'dijetMass'           : {'xaxis': 'm_{jj}', 'yaxis': 'Events / 100 GeV', 'rebin': range(0,2100,100), 'overflow': True,},
    'dijetDEta'           : {'xaxis': '\Delta\eta(jj)', 'yaxis': 'Events','rebin': range(0,11,1), 'overflow': True,},
}

chans = ['eee','eem','mme','mmm']
chanLabels = ['eee','ee#mu','#mu#mu e','#mu#mu#mu']

def getDataDrivenPlot(plot):
    histMap = {}
    plotdirs = plot.split('/')
    for s in samples + ['data']: histMap[s] = '/'.join(['PPP']+plotdirs)
    regions = ['PPF','PFP','FPP','PFF','FPF','FFP','FFF']
    histMap['datadriven'] = ['/'.join([reg]+plotdirs) for reg in regions]
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
    plotter.plotCounts(countVars,countLabels,savename,numcol=3,logy=0,legendpos=34,labelsOption='v')

# n-1 cuts
nMinusOneCuts = ['zptCut','wptCut','bvetoCut','metCut','zmassCut','3lmassCut','wmllCut']
vbsNMinusOneCuts = ['twoJets','jetPt','jetDEta','mjj']

# controls
controls = ['dy','tt']


samples = ['TTV','ZG','VVV','ZZ','WZ']
allsamples = ['W','TT','Z','WW','TTV','VVV','ZZall','WZall']

def addUncertainties(plotter,datadriven=False):
    if datadriven:
        plotter.addUncertainty('datadriven',nonprompt=0.3)

#################
### MC driven ###
#################
for s in allsamples:
    name = s.replace('all','')
    wzPlotter.addHistogramToStack(name,sigMap[s])

wzPlotter.addHistogram('data',sigMap['data'])

addUncertainties(wzPlotter)

if doCounts and doMC:
    plotCounts(wzPlotter,saveDir='mc',baseDir='default')
    if doVBS: plotCounts(wzPlotter,saveDir='vbs',baseDir='vbs')
    for cut in nMinusOneCuts:
        if doNMinusOne: plotCounts(wzPlotter,baseDir='default/{0}'.format(cut),saveDir='nMinusOne/{0}'.format(cut))
    for cut in vbsNMinusOneCuts:
        if doNMinusOne and doVBS: plotCounts(wzPlotter,baseDir='vbs/{0}'.format(cut),saveDir='vbsNMinusOne/{0}'.format(cut))
    for control in controls:
        if doControls: plotCounts(wzPlotter,saveDir=control,baseDir=control)

if doMC:
    for plot in plotStyles:
        plotname = 'default/{0}'.format(plot)
        savename = 'mc/{0}'.format(plot)
        wzPlotter.plot(plotname,savename,**plotStyles[plot])
        plotname = 'vbs/{0}'.format(plot)
        savename = 'vbs/{0}'.format(plot)
        if doVBS: wzPlotter.plot(plotname,savename,**plotStyles[plot])
        for cut in nMinusOneCuts:
            plotname = 'default/{0}/{1}'.format(cut,plot)
            savename = 'nMinusOne/{0}/{1}'.format(cut,plot)
            if doNMinusOne: wzPlotter.plot(plotname,savename,**plotStyles[plot])
        for cut in vbsNMinusOneCuts:
            plotname = 'vbs/{0}/{1}'.format(cut,plot)
            savename = 'vbsNMinusOne/{0}/{1}'.format(cut,plot)
            if doNMinusOne and doVBS: wzPlotter.plot(plotname,savename,**plotStyles[plot])
        for control in controls:
            plotname = '{0}/{1}'.format(control,plot)
            savename = '{0}/{1}'.format(control,plot)
            if doControls: wzPlotter.plot(plotname,savename,**plotStyles[plot])

##################
### Datadriven ###
##################
wzPlotter.clearHistograms()
datadrivenSamples = []
for s in samples + ['data']:
    datadrivenSamples += sigMap[s]
wzPlotter.addHistogramToStack('datadriven',datadrivenSamples)

for s in samples:
    wzPlotter.addHistogramToStack(s,sigMap[s])

wzPlotter.addHistogram('data',sigMap['data'])

addUncertainties(wzPlotter,datadriven=True)

if doCounts and doDatadriven:
    plotCounts(wzPlotter,baseDir='default',saveDir='datadriven',datadriven=True)
    if doVBS: plotCounts(wzPlotter,baseDir='vbs',saveDir='vbs-datadriven',datadriven=True)
    for cut in nMinusOneCuts:
        if doNMinusOne: plotCounts(wzPlotter,baseDir='default/{0}'.fromat(cut),saveDir='nMinusOne-datadriven/{0}'.format(cut),datadriven=True)
    for cut in vbsNMinusOneCuts:
        if doNMinusOne and doVBS: plotCounts(wzPlotter,baseDir='vbs/{0}'.format(cut),saveDir='vbsNMinusOne-datadriven/{0}'.format(cut),datadriven=True)
    for control in controls:
        if doControls: plotCounts(wzPlotter,baseDir=control,saveDir='{0}-datadriven'.format(control),datadriven=True)

if doDatadriven:
    for plot in plotStyles:
        plotvars = getDataDrivenPlot('default/{0}'.format(plot))
        savename = 'datadriven/{0}'.format(plot)
        wzPlotter.plot(plotvars,savename,**plotStyles[plot])
        plotvars = getDataDrivenPlot('vbs/{0}'.format(plot))
        savename = 'vbs-datadriven/{0}'.format(plot)
        if doVBS: wzPlotter.plot(plotvars,savename,**plotStyles[plot])
        for cut in nMinusOneCuts:
            plotvars = getDataDrivenPlot('default/{0}/{1}'.format(cut,plot))
            savename = 'nMinusOne-datadriven/{0}/{1}'.format(cut,plot)
            if doNMinusOne: wzPlotter.plot(plotvars,savename,**plotStyles[plot])
        for cut in vbsNMinusOneCuts:
            plotvars = getDataDrivenPlot('vbs/{0}/{1}'.format(cut,plot))
            savename = 'vbsNMinusOne-datadriven/{0}/{1}'.format(cut,plot)
            if doNMinusOne and doVBS: wzPlotter.plot(plotvars,savename,**plotStyles[plot])
        for control in controls:
            plotvars = getDataDrivenPlot('{0}/{1}'.format(control,plot))
            savename = '{0}-datadriven/{1}'.format(control,plot)
            if doControls: wzPlotter.plot(plotvars,savename,**plotStyles[plot])

wzPlotter.clearHistograms()

