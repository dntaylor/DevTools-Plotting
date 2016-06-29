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

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

blind = True
doCat = True
plotMC = False
plotDatadriven = False
plotFakeRegions = False
plotSignal = False
plotROC = False
plotNormalization = False
plotSOverB = False
plotCount = False
plotAllMasses = True

hpp4lPlotter = Plotter('Hpp4l')

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

allmasses = [200,300,400,500,600,700,800,900,1000,1100,1200,1300,1400,1500]
masses = [200,400,600,800,1000]

samples = ['TTV','VH','VVV','ZZ']
allsamples = ['W','T','TT','TTVall','Z','WW','VHall','WZ','VVV','ZZall']
signals = ['HppHmm500GeV']

allSamplesDict = {'BG':[]}
for s in allsamples:
    allSamplesDict['BG'] += sigMap[s]

datadrivenSamples = []
for s in samples + ['data']:
    datadrivenSamples += sigMap[s]

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


########################
### Helper functions ###
########################
def getDataDrivenPlot(*plots):
    histMap = {}
    regions = ['3P1F','2P2F','1P3F','0P4F']
    #regions = ['3P1F','2P2F']
    for s in samples + signals + ['data','datadriven']: histMap[s] = []
    for plot in plots:
        plotdirs = plot.split('/')
        for s in samples + signals + ['data']: histMap[s] += ['/'.join(['4P0F']+plotdirs)]
        histMap['datadriven'] += ['/'.join([reg]+plotdirs) for reg in regions]
    return histMap

def plotCounts(plotter,baseDir='default',saveDir='',datadriven=False,postfix=''):
    # per channel counts
    countVars = ['/'.join([x for x in [baseDir,'count'] if x])] + ['/'.join([x for x in [baseDir,chan,'count'] if x]) for chan in chans]
    if datadriven:
        for i in range(len(countVars)):
            countVars[i] = getDataDrivenPlot(countVars[i])
    countLabels = ['Total'] + chanLabels
    savename = '/'.join([x for x in [saveDir,'individualChannels'] if x])
    if postfix: savename += '_{0}'.format(postfix)
    plotter.plotCounts(countVars,countLabels,savename,numcol=3,logy=1,legendpos=34,yscale=100,ymin=0.001,labelsOption='v')
    
    # per category counts
    countVars = [['/'.join([x for x in [baseDir,'count'] if x])]]
    for cat in cats:
        tempCountVars = []
        for subcat in subCatChannels[cat]:
            tempCountVars += ['/'.join([x for x in [baseDir,chan,'count'] if x]) for chan in subCatChannels[cat][subcat]]
        countVars += [tempCountVars]
    if datadriven:
        for i in range(len(countVars)):
            countVars[i] = getDataDrivenPlot(*countVars[i])
    countLabels = ['Total'] + catLabels
    savename = '/'.join([x for x in [saveDir,'individualCategories'] if x])
    if postfix: savename += '_{0}'.format(postfix)
    plotter.plotCounts(countVars,countLabels,savename,numcol=3,logy=1,legendpos=34,yscale=100,ymin=0.001)
    
    # per subcategory counts
    countVars = [['/'.join([x for x in [baseDir,'count'] if x])]]
    for cat in cats:
        for subCat in sorted(subCatChannels[cat]):
            countVars += [['/'.join([x for x in [baseDir,chan,'count'] if x]) for chan in subCatChannels[cat][subCat]]]
    if datadriven:
        for i in range(len(countVars)):
            countVars[i] = getDataDrivenPlot(*countVars[i])
    countLabels = ['Total'] + subCatLabels
    savename = '/'.join([x for x in [saveDir,'individualSubCategories'] if x])
    if postfix: savename += '_{0}'.format(postfix)
    plotter.plotCounts(countVars,countLabels,savename,numcol=3,logy=1,legendpos=34,yscale=100,ymin=0.001)

def plotWithCategories(plotter,plot,baseDir='',saveDir='',datadriven=False,postfix='',**kwargs):
    plotname = '/'.join([x for x in [baseDir,plot] if x])
    plotvars = getDataDrivenPlot(plotname) if datadriven else plotname
    savename = '/'.join([x for x in [saveDir,plot] if x])
    if postfix: savename += '_{0}'.format(postfix)
    plotter.plot(plotvars,savename,**kwargs)
    for cat in cats:
        plotnames = []
        for subcat in subCatChannels[cat]:
            plotnames += ['/'.join([x for x in [baseDir,chan,plot] if x]) for chan in subCatChannels[cat][subcat]]
        plotvars = getDataDrivenPlot(*plotnames) if datadriven else plotnames
        savename = '/'.join([x for x in [saveDir,cat,plot] if x])
        if postfix: savename += '_{0}'.format(postfix)
        if doCat: plotter.plot(plotvars,savename,**kwargs)


########################
### plot definitions ###
########################
plots = {
    # hpp
    'hppMass'               : {'xaxis': 'm_{l^{+}l^{+}} (GeV)', 'yaxis': 'Events / 50 GeV', 'numcol': 3, 'lumipos': 11, 'legendpos':34, 'rebin': 5, 'logy': True},
    'hppMt'                 : {'xaxis': 'm_{T}^{l^{+}l^{+}} (GeV)', 'yaxis': 'Events / 50 GeV', 'numcol': 3, 'lumipos': 11, 'legendpos':34, 'rebin': 5, 'logy': True},
    'hppPt'                 : {'xaxis': 'p_{T}^{l^{+}l^{+}} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': 2},
    'hppDeltaR'             : {'xaxis': '#DeltaR(l^{+}l^{+})', 'yaxis': 'Events', 'rebin': 2},
    'hppLeadingLeptonPt'    : {'xaxis': 'p_{T}^{#Phi_{lead}^{++}} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': 2},
    'hppSubLeadingLeptonPt' : {'xaxis': 'p_{T}^{#Phi_{sublead}^{++}} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': 2},
    # hmm
    'hmmMass'               : {'xaxis': 'm_{l^{-}l^{-}} (GeV)', 'yaxis': 'Events / 50 GeV', 'numcol': 3, 'lumipos': 11, 'legendpos':34, 'rebin': 5, 'logy': True},
    'hmmMt'                 : {'xaxis': 'm_{T}^{l^{-}l^{-}} (GeV)', 'yaxis': 'Events / 50 GeV', 'numcol': 3, 'lumipos': 11, 'legendpos':34, 'rebin': 5, 'logy': True},
    'hmmPt'                 : {'xaxis': 'p_{T}^{l^{-}l^{-}} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': 2},
    'hmmDeltaR'             : {'xaxis': '#DeltaR(l^{-}l^{-})', 'yaxis': 'Events', 'rebin': 2},
    'hmmLeadingLeptonPt'    : {'xaxis': 'p_{T}^{#Phi_{lead}^{--}} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': 2},
    'hmmSubLeadingLeptonPt' : {'xaxis': 'p_{T}^{#Phi_{sublead}^{--}} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': 2},
    # z cand
    'zMass'                 : {'xaxis': 'm_{l^{+}l^{-}} (GeV)', 'yaxis': 'Events / 10 GeV', 'rebin': 1},
    'mllMinusMZ'            : {'xaxis': '|m_{l^{+}l^{-}}-m_{Z}| (GeV)', 'yaxis': 'Events / 10 GeV', 'rebin': 1},
    # event
    'numVertices'           : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events'},
    'met'                   : {'xaxis': 'E_{T}^{miss} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': 2},
    'mass'                  : {'xaxis': 'm_{4l} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': 2},
    'st'                    : {'xaxis': '#Sigma p_{T}^{l} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': 2},
}

blind_cust = {
    'hppMass': {'blinder': [100,1200]},
    'hmmMass': {'blinder': [100,1200]},
}

lowmass_cust = {
    # hpp
    'hppMass'              : {'rangex': [0,300], 'logy': False},
    'hppMt'                : {'rangex': [0,300], 'logy': False},
    'hppPt'                : {'rangex': [0,300]},
    'hppLeadingLeptonPt'   : {'rangex': [0,300]},
    'hppSubLeadingLeptonPt': {'rangex': [0,300]},
    # hmm
    'hmmMass'              : {'rangex': [0,300], 'logy': False},
    'hmmMt'                : {'rangex': [0,300], 'logy': False},
    'hmmPt'                : {'rangex': [0,300]},
    'hmmLeadingLeptonPt'   : {'rangex': [0,300]},
    'hmmSubLeadingLeptonPt': {'rangex': [0,300]},
    # z
    'zMass'                : {'rangex': [60,120]},
    'mllMinusMZ'           : {'rangex': [0,60]},
    # event
    'met'                  : {'rangex': [0,200]},
    'mass'                 : {'rangex': [0,600], 'rebin':25, 'xaxis': 'Events / 25 GeV'},
    'st'                   : {'rangex': [0,400], 'rebin':25, 'xaxis': 'Events / 25 GeV'},
}

norm_cust = {
    # hpp
    'hppMass'               : {'yaxis': 'Unit normalized', 'logy':0, 'rebin': 1},
    'hppMt'                 : {'yaxis': 'Unit normalized', 'logy':0, 'rebin': 1},
    'hppPt'                 : {'yaxis': 'Unit normalized', 'rebin': 1, 'numcol': 2},
    'hppDeltaR'             : {'yaxis': 'Unit normalized', 'rebin': 1},
    'hppLeadingLeptonPt'    : {'yaxis': 'Unit normalized', 'rebin': 1},
    'hppSubLeadingLeptonPt' : {'yaxis': 'Unit normalized', 'rebin': 1},
    # hmm
    'hmmMass'               : {'yaxis': 'Unit normalized', 'logy':0, 'rebin': 1},
    'hmmMt'                 : {'yaxis': 'Unit normalized', 'logy':0, 'rebin': 1},
    'hmmPt'                 : {'yaxis': 'Unit normalized', 'rebin': 1, 'numcol': 2},
    'hmmDeltaR'             : {'yaxis': 'Unit normalized', 'rebin': 1},
    'hmmLeadingLeptonPt'    : {'yaxis': 'Unit normalized', 'rebin': 1},
    'hmmSubLeadingLeptonPt' : {'yaxis': 'Unit normalized', 'rebin': 1},
    # z
    'zMass'                 : {'yaxis': 'Unit normalized', 'rebin': 1, 'numcol': 2},
    'mllMinusMZ'            : {'yaxis': 'Unit normalized', 'rebin': 1},
    # event
    'met'                   : {'yaxis': 'Unit normalized', 'rebin': 1},
    'numVertices'           : {'yaxis': 'Unit normalized'},
    'mass'                  : {'yaxis': 'Unit normalized', 'rebin': 1},
    'st'                    : {'yaxis': 'Unit normalized', 'rebin': 1},
}

eff_cust = {
    # hpp
    'hppMass'               : {'yaxis': 'Efficiency', 'logy':0, 'rebin': 1},
    'hppMt'                 : {'yaxis': 'Efficiency', 'logy':0, 'rebin': 1},
    'hppPt'                 : {'yaxis': 'Efficiency', 'rebin': 1, 'numcol': 2},
    'hppDeltaR'             : {'yaxis': 'Efficiency', 'rebin': 1, 'invert': True},
    'hppLeadingLeptonPt'    : {'yaxis': 'Efficiency', 'rebin': 1},
    'hppSubLeadingLeptonPt' : {'yaxis': 'Efficiency', 'rebin': 1},
    'st'                    : {'yaxis': 'Efficiency', 'rebin': 1},
    'mllMinusMZ'            : {'yaxis': 'Efficiency', 'rebin': 1},
    'met'                   : {'yaxis': 'Efficiency', 'rebin': 1},
}

sOverB_cust = {
    # hpp
    'hppMass'               : {'yaxis': 'Signal over background', 'logy': 0, 'rebin': 1},
    'hppMt'                 : {'yaxis': 'Signal over background', 'logy': 0, 'rebin': 1},
    'hppPt'                 : {'yaxis': 'Signal over background', 'logy': 0, 'rebin': 1, 'numcol': 2},
    'hppDeltaR'             : {'yaxis': 'Signal over background', 'logy': 0, 'rebin': 1, 'invert': True},
    'hppLeadingLeptonPt'    : {'yaxis': 'Signal over background', 'logy': 0, 'rebin': 1},
    'hppSubLeadingLeptonPt' : {'yaxis': 'Signal over background', 'logy': 0, 'rebin': 1},
    'st'                    : {'yaxis': 'Signal over background', 'logy': 0, 'rebin': 1},
    'mllMinusMZ'            : {'yaxis': 'Signal over background', 'logy': 0, 'rebin': 1},
    'met'                   : {'yaxis': 'Signal over background', 'logy': 0, 'rebin': 1},
}

roc_cust = {
    # hpp
    'hppMass'               : {'yaxis': 'Background Rejection', 'xaxis': 'Signal Efficiency', 'legendpos':34, 'numcol': 3, 'ymax': 1.3, 'rebin': 1,'logy':0},
    'hppMt'                 : {'yaxis': 'Background Rejection', 'xaxis': 'Signal Efficiency', 'legendpos':34, 'numcol': 3, 'ymax': 1.3, 'rebin': 1,'logy':0},
    'hppPt'                 : {'yaxis': 'Background Rejection', 'xaxis': 'Signal Efficiency', 'legendpos':34, 'numcol': 3, 'ymax': 1.3, 'rebin': 1},
    'hppDeltaR'             : {'yaxis': 'Background Rejection', 'xaxis': 'Signal Efficiency', 'legendpos':34, 'numcol': 3, 'ymax': 1.3, 'rebin': 1, 'invert': True},
    'hppLeadingLeptonPt'    : {'yaxis': 'Background Rejection', 'xaxis': 'Signal Efficiency', 'legendpos':34, 'numcol': 3, 'ymax': 1.3, 'rebin': 1},
    'hppSubLeadingLeptonPt' : {'yaxis': 'Background Rejection', 'xaxis': 'Signal Efficiency', 'legendpos':34, 'numcol': 3, 'ymax': 1.3, 'rebin': 1},
    'st'                    : {'yaxis': 'Background Rejection', 'xaxis': 'Signal Efficiency', 'legendpos':34, 'numcol': 3, 'ymax': 1.3, 'rebin': 1},
    'mllMinusMZ'            : {'yaxis': 'Background Rejection', 'xaxis': 'Signal Efficiency', 'legendpos':34, 'numcol': 3, 'ymax': 1.3, 'rebin': 1},
    'met'                   : {'yaxis': 'Background Rejection', 'xaxis': 'Signal Efficiency', 'legendpos':34, 'numcol': 3, 'ymax': 1.3, 'rebin': 1},
}

envelope_cust = {
    # hpp
    'hppMass'               : {'yaxis': 'm_{l^{#pm}l^{#pm}} (GeV)',     'xaxis': 'm_{#Phi^{#pm#pm}} (GeV)', 'legendpos':13, 'numcol': 1},
    'st'                    : {'yaxis': '#Sigma p_{T}^{l} (GeV)',       'xaxis': 'm_{#Phi^{#pm#pm}} (GeV)', 'legendpos':13, 'numcol': 1},
    'hppDeltaR'             : {'yaxis': '#DeltaR(l^{+}l^{+})',          'xaxis': 'm_{#Phi^{#pm#pm}} (GeV)', 'legendpos':13, 'numcol': 1},
    'met'                   : {'yaxis': 'E_{T}^{miss} (GeV)',           'xaxis': 'm_{#Phi^{#pm#pm}} (GeV)', 'legendpos':13, 'numcol': 1},
    'mllMinusZ'             : {'yaxis': '|m_{l^{+}l^{-}}-m_{Z}| (GeV)', 'xaxis': 'm_{#Phi^{#pm#pm}} (GeV)', 'legendpos':13, 'numcol': 1},
}



############################
### MC based BG estimate ###
############################
if plotMC:
    for s in allsamples:
        hpp4lPlotter.addHistogramToStack(s.replace('all',''),sigMap[s])
    
    for signal in signals:
        hpp4lPlotter.addHistogram(signal,sigMap[signal],signal=True)
    
    if not blind: hpp4lPlotter.addHistogram('data',sigMap['data'])
    
    if plotCount: plotCounts(hpp4lPlotter,baseDir='default')
    
    for plot in plots:
        kwargs = deepcopy(plots[plot])
        plotWithCategories(hpp4lPlotter,plot,baseDir='default',**kwargs)
    
    # partially blinded plots
    if blind:
        hpp4lPlotter.addHistogram('data',sigMap['data'])
        
        for plot in blind_cust:
            kwargs = deepcopy(plots[plot])
            kwargs.update(blind_cust[plot])
            plotWithCategories(hpp4lPlotter,plot,baseDir='default',postfix='blinder',**kwargs)

## multiple st cuts on same plot:
#hpp4lPlotter.clearHistograms()
#
#allSamplesDict = {'BG':[]}
#
#for s in allsamples:
#    allSamplesDict['BG'] += sigMap[s]
#
#hpp4lPlotter.addHistogram('st100',allSamplesDict['BG'],style={'linecolor':ROOT.kRed,'name':'BG (s_{T}>100 GeV)'})
#hpp4lPlotter.addHistogram('st200',allSamplesDict['BG'],style={'linecolor':ROOT.kBlue,'name':'BG (s_{T}>200 GeV)'})
#hpp4lPlotter.addHistogram('st300',allSamplesDict['BG'],style={'linecolor':ROOT.kGreen,'name':'BG (s_{T}>300 GeV)'})
#
#for plot in plots:
#    plotvars = {}
#    for st in [100,200,300]:
#        plotvars['st{0}'.format(st)] = 'st{0}/{1}'.format(st,plot)
#    savename = 'stCuts/{0}'.format(plot)
#    #hpp4lPlotter.plotNormalized(plotvars,savename,**plots[plot])
#    hpp4lPlotter.plot(plotvars,savename,**plots[plot])
#    for cat in cats:
#        plotvars = {}
#        for st in [100,200,300]:
#            plotvars['st{0}'.format(st)] = []
#            for subcat in subCatChannels[cat]:
#                plotvars['st{0}'.format(st)] += ['st{0}/{1}/{2}'.format(st,chan,plot) for chan in subCatChannels[cat][subcat]]
#        savename = 'stCuts/{0}/{1}'.format(cat,plot)
#        #if doCat: hpp4lPlotter.plotNormalized(plotnames,savename,**plots[plot])
#        if doCat: hpp4lPlotter.plot(plotnames,savename,**plots[plot])

## multiple zmass cuts on same plot:
#hpp4lPlotter.clearHistograms()
#
#allSamplesDict = {'BG':[]}
#
#for s in allsamples:
#    allSamplesDict['BG'] += sigMap[s]
#
#hpp4lPlotter.addHistogram('default',allSamplesDict['BG'],style={'linecolor':ROOT.kRed,'name':'Preselection'})
#hpp4lPlotter.addHistogram('zveto',allSamplesDict['BG'],style={'linecolor':ROOT.kBlue,'name':'Z veto'})
#
#norm_cust = {
#    # hpp
#    'hppMass'               : {'yaxis': 'Unit normalized', 'logy':1, 'rebin': 100},
#    # hmm
#    'hmmMass'               : {'yaxis': 'Unit normalized', 'logy':1, 'rebin': 100},
#}
#for plot in norm_cust:
#    kwargs = deepcopy(plots[plot])
#    kwargs.update(norm_cust[plot])
#    plotvars = {}
#    for mode in ['default','zveto']:
#        plotvars[mode] = '{0}/{1}'.format(mode,plot)
#    savename = 'zVeto/{0}'.format(plot)
#    hpp4lPlotter.plotNormalized(plotvars,savename,**kwargs)
#    #hpp4lPlotter.plot(plotvars,savename,**kwargs)
#    for cat in cats:
#        plotvars = {}
#        for mode in ['default','zveto']:
#            plotvars[mode] = []
#            for subcat in subCatChannels[cat]:
#                plotvars[mode] += ['{0}/{1}/{2}'.format(mode,chan,plot) for chan in subCatChannels[cat][subcat]]
#        savename = 'zVeto/{0}/{1}'.format(cat,plot)
#        if doCat: hpp4lPlotter.plotNormalized(plotnames,savename,**kwargs)
#        #if doCat: hpp4lPlotter.plot(plotnames,savename,**kwargs)

##############################
### datadriven backgrounds ###
##############################
if plotDatadriven:
    hpp4lPlotter.clearHistograms()
    
    hpp4lPlotter.addHistogramToStack('datadriven',datadrivenSamples)
    
    for s in samples:
        hpp4lPlotter.addHistogramToStack(s,sigMap[s])
    
    for signal in signals:
        hpp4lPlotter.addHistogram(signal,sigMap[signal],signal=True)

    if not blind: hpp4lPlotter.addHistogram('data',sigMap['data'])
    
    if plotCount: plotCounts(hpp4lPlotter,baseDir='',saveDir='datadriven',datadriven=True)
    
    for plot in plots:
        kwargs = deepcopy(plots[plot])
        plotWithCategories(hpp4lPlotter,plot,baseDir='',saveDir='datadriven',datadriven=True,**kwargs)
    
    # partially blinded plots
    if blind:
        hpp4lPlotter.addHistogram('data',sigMap['data'])
    
        for plot in blind_cust:
            kwargs = deepcopy(plots[plot])
            kwargs.update(blind_cust[plot])
            plotWithCategories(hpp4lPlotter,plot,baseDir='',saveDir='datadriven',postfix='blinder',datadriven=True,**kwargs)

####################
### Fake Regions ###
####################
if plotFakeRegions:
    hpp4lPlotter.clearHistograms()
    
    for s in allsamples:
        hpp4lPlotter.addHistogramToStack(s.replace('all',''),sigMap[s])
    for signal in signals:
        hpp4lPlotter.addHistogram(signal,sigMap[signal],signal=True)

    hpp4lPlotter.addHistogram('data',sigMap['data'])
    
    for fr in ['3P1F','2P2F','1P3F','0P4F']:
        if plotCount: plotCounts(hpp4lPlotter,baseDir='{0}_regular'.format(fr),saveDir=fr)
        
        for plot in plots:
            kwargs = deepcopy(plots[plot])
            plotWithCategories(hpp4lPlotter,plot,baseDir='{0}_regular'.format(fr),saveDir=fr,**kwargs)

########################
### low mass control ###
########################
if plotMC:
    hpp4lPlotter.clearHistograms()
    
    for s in allsamples:
        hpp4lPlotter.addHistogramToStack(s.replace('all',''),sigMap[s])
    hpp4lPlotter.addHistogram('data',sigMap['data'])
    
    if plotCount: plotCounts(hpp4lPlotter,baseDir='lowmass',saveDir='lowmass')
    
    for plot in plots:
        kwargs = deepcopy(plots[plot])
        if plot in lowmass_cust: kwargs.update(lowmass_cust[plot])
        plotWithCategories(hpp4lPlotter,plot,baseDir='lowmass',saveDir='lowmass',**kwargs)

######################################
### lowmass datadriven backgrounds ###
######################################
if plotDatadriven:
    hpp4lPlotter.clearHistograms()
    
    hpp4lPlotter.addHistogramToStack('datadriven',datadrivenSamples)
    
    for s in samples:
        hpp4lPlotter.addHistogramToStack(s,sigMap[s])
    
    hpp4lPlotter.addHistogram('data',sigMap['data'])
    
    if plotCount: plotCounts(hpp4lPlotter,baseDir='lowmass',saveDir='lowmass/datadriven',datadriven=True)
    
    for plot in plots:
        kwargs = deepcopy(plots[plot])
        if plot in lowmass_cust: kwargs.update(lowmass_cust[plot])
        plotWithCategories(hpp4lPlotter,plot,baseDir='lowmass',saveDir='lowmass/datadriven',datadriven=True,**kwargs)

############################
### Fake Regions lowmass ###
############################
if plotFakeRegions:
    hpp4lPlotter.clearHistograms()
    
    for s in allsamples:
        hpp4lPlotter.addHistogramToStack(s.replace('all',''),sigMap[s])

    hpp4lPlotter.addHistogram('data',sigMap['data'])
    
    for fr in ['3P1F','2P2F','1P3F','0P4F']:
        if plotCount: plotCounts(hpp4lPlotter,baseDir='{0}_regular/lowmass'.format(fr),saveDir='lowmass/{0}'.format(fr))
        
        for plot in plots:
            kwargs = deepcopy(plots[plot])
            plotWithCategories(hpp4lPlotter,plot,baseDir='{0}_regular/lowmass'.format(fr),saveDir='lowmass/{0}'.format(fr),**kwargs)

########################
### normalized plots ###
########################
if plotNormalization:
    hpp4lPlotter.clearHistograms()
    
    hpp4lPlotter.addHistogram('BG',allSamplesDict['BG'])
    for signal in signals:
        hpp4lPlotter.addHistogram(signal,sigMap[signal],signal=True)
    
    for plot in plots:
        plotname = 'default/{0}'.format(plot)
        savename = 'normalized/{0}'.format(plot)
        kwargs = deepcopy(plots[plot])
        if plot in norm_cust: kwargs.update(norm_cust[plot])
        hpp4lPlotter.plotNormalized(plotname,savename,**kwargs)
        for cat in cats:
            plotnames = []
            for subcat in subCatChannels[cat]:
                plotnames += ['default/{0}/{1}'.format(chan,plot) for chan in subCatChannels[cat][subcat]]
            savename = 'normalized/{0}/{1}'.format(cat,plot)
            if doCat: hpp4lPlotter.plotNormalized(plotnames,savename,**kwargs)

if plotSOverB:
    hpp4lPlotter.clearHistograms()
    
    hpp4lPlotter.addHistogram('BG',allSamplesDict['BG'])
    sigOrder = []
    bgOrder = []
    for mass in masses:
        name = 'HppHmm{0}GeV'.format(mass)
        sigOrder += [name]
        bgOrder += ['BG']
        hpp4lPlotter.addHistogram(name,sigMap[name],signal=True,style={'linecolor': sigColors[mass]})

    for plot in sOverB_cust:
        plotname = 'default/{0}'.format(plot)
        savename = 'sOverB/{0}'.format(plot)
        kwargs = deepcopy(plots[plot])
        if plot in sOverB_cust: kwargs.update(sOverB_cust[plot])
        hpp4lPlotter.plotSOverB(plotname,sigOrder,bgOrder,savename,**kwargs)
        for cat in cats:
            plotnames = []
            for subcat in subCatChannels[cat]:
                plotnames += ['default/{0}/{1}'.format(chan,plot) for chan in subCatChannels[cat][subcat]]
            savename = 'sOverB/{0}/{1}'.format(cat,plot)
            if doCat: hpp4lPlotter.plotSOverB(plotnames,sigOrder,bgOrder,savename,**kwargs)


##############################
### all signal on one plot ###
##############################
if plotAllMasses:
    hpp4lPlotter.clearHistograms()

    xvals = {}
    for mass in allmasses:
        hpp4lPlotter.addHistogram('HppHmm{0}GeV'.format(mass),sigMap['HppHmm{0}GeV'.format(mass)],signal=True,style={'linecolor': sigColors[mass]})
        xvals[mass] = 'HppHmm{0}GeV'.format(mass)

    fitvalues = {
        'hppMass': {0.:[0.,0.9],1:[0.,0.4],2:[0.,0.3]},
    }

    varMap = {
        'hppMass'  : 'hpp_mass',
        'hppDeltaR': 'hpp_deltaR',
        'mllMinusZ': 'fabs(z_mass-{0})'.format(ZMASS),
        'met'      : 'met_pt',
        'st'       : 'hpp1_pt+hpp2_pt+hmm1_pt+hmm2_pt',
    }

    varBinning = {
        'hppMass'  : [1600,0,1600],
        'hppDeltaR': [300,0,6],
        'mllMinusZ': [1000,0,1000],
        'met'      : [1000,0,1000],
        'st'       : [3000,0,3000],
    }

    envelopePoints = [0.05,0.1,0.5,0.9,0.95]
    envelopeStyles = [3,2,1,1,2]
    envelopeColors = [4,4,1,2,2]
    envelopeLabels = ['p = 0.05','p = 0.1', 'p = 0.5', 'p = 0.9', 'p = 0.95']
    for plot in envelope_cust:
        savename = 'signal/envelopes/{0}'.format(plot)
        kwargs = deepcopy(envelope_cust[plot])
        selection = ' && '.join(['{0}_passMedium'.format(lep) for lep in ['hpp1','hpp2','hmm1','hmm2']])
        scalefactor = 'hpp1_mediumScale*hpp2_mediumScale*hmm1_mediumScale*hmm2_mediumScale*genWeight*pileupWeight*triggerEfficiency'
        hpp4lPlotter.plotEnvelope(varMap[plot],savename,xvals,envelopePoints,envelopeLabels=envelopeLabels,envelopeStyles=envelopeStyles,envelopeColors=envelopeColors,selection=selection,mcscalefactor=scalefactor,binning=varBinning[plot],**kwargs)

        for nTau in range(3):
            genChans = []
            recoChans = []
            for gen in genRecoMap:
                if gen[:2].count('t')!=nTau or gen[2:].count('t')!=nTau: continue
                genChans += [gen]
                for r in genRecoMap[gen]:
                    recoChans += chans[r]
            recoCut = '(' + ' || '.join(['channel=="{0}"'.format(r) for r in recoChans]) + ')'
            genCut = '(' + ' || '.join(['genChannel=="{0}"'.format(g) for g in genChans]) + ')'
            fullCut = ' && '.join([recoCut,genCut,selection])
            savename = 'signal/envelopes/{0}_{1}Taus'.format(plot,nTau)
            
            fitFunctions = [['pol1',200,1500]+fitvalues[plot][nTau]] if plot in fitvalues else []
            hpp4lPlotter.plotEnvelope(varMap[plot],savename,xvals,envelopePoints,envelopeLabels=envelopeLabels,envelopeStyles=envelopeStyles,envelopeColors=envelopeColors,fitFunctions=fitFunctions,selection=fullCut,mcscalefactor=scalefactor,binning=varBinning[plot],**kwargs)



if plotSignal:
    hpp4lPlotter.clearHistograms()
    
    for mass in masses:
        hpp4lPlotter.addHistogram('HppHmm{0}GeV'.format(mass),sigMap['HppHmm{0}GeV'.format(mass)],signal=True,style={'linecolor': sigColors[mass]})
    
    catRebin = {
        'I'  : 1,
        'II' : 5,
        'III': 10,
        'IV' : 10,
        'V'  : 20,
        'VI' : 50,
    }
    
    genRebin = {
        'ee' : 1,
        'em' : 1,
        'et' : 5,
        'mm' : 1,
        'mt' : 5,
        'tt' : 10,
    }
    
    for plot in norm_cust:
        plotname = 'default/{0}'.format(plot)
        savename = 'signal/{0}'.format(plot)
        kwargs = deepcopy(plots[plot])
        if plot in norm_cust: kwargs.update(norm_cust[plot])
        hpp4lPlotter.plotNormalized(plotname,savename,**kwargs)
        for cat in cats:
            plotnames = []
            for subcat in subCatChannels[cat]:
                plotnames += ['default/{0}/{1}'.format(chan,plot) for chan in subCatChannels[cat][subcat]]
            savename = 'signal/{0}/{1}'.format(cat,plot)
            catkwargs = deepcopy(kwargs)
            if cat in catRebin and 'rebin' in catkwargs and plot in ['hppMass','hmmMass']: catkwargs['rebin'] = catkwargs['rebin'] * catRebin[cat]
            if doCat: hpp4lPlotter.plotNormalized(plotnames,savename,**catkwargs)
    for plot in eff_cust:
        kwargs = deepcopy(plots[plot])
        if plot in norm_cust: kwargs.update(norm_cust[plot])
        for higgsChan in ['ee','em','et','mm','mt','tt']:
            # reco
            plotnames = ['default/{0}/{1}'.format(chan,plot) for chan in chans if chan[:2]==higgsChan]
            if 'hpp' in plot: plotnames += ['default/{0}/{1}'.format(chan,plot.replace('hpp','hmm')) for chan in chans if chan[2:]==higgsChan]
            savename = 'signal/{0}/{1}'.format(higgsChan,plot)
            genkwargs = deepcopy(kwargs)
            effkwargs = deepcopy(plots[plot])
            if plot in eff_cust: effkwargs.update(eff_cust[plot])
            #if higgsChan in genRebin and 'rebin' in genkwargs and plot in ['hppMass','hmmMass']: genkwargs['rebin'] = genkwargs['rebin'] * genRebin[higgsChan]
            hpp4lPlotter.plotNormalized(plotnames,savename,**genkwargs)
            # and the gen truth
            plotnames = []
            for gen in genRecoMap:
                for reco in genRecoMap[gen]:
                    if gen[:2]==higgsChan:
                        plotnames += ['default/{0}/gen_{1}/{2}'.format(reco,gen,plot)] 
                    if gen[2:]==higgsChan and 'hpp' in plot:
                        plotnames += ['default/{0}/gen_{1}/{2}'.format(reco,gen,plot.replace('hpp','hmm'))] 
            if plotnames:
                savename = 'signal/{0}/{1}_genMatched'.format(higgsChan,plot)
                hpp4lPlotter.plotNormalized(plotnames,savename,**genkwargs)
                savename = 'signal/{0}/{1}_genMatched_efficiency'.format(higgsChan,plot)
                hpp4lPlotter.plotEfficiency(plotnames,savename,**effkwargs)

# ROCs
if plotROC:
    hpp4lPlotter.clearHistograms()
    
    hpp4lPlotter.addHistogram('BG',allSamplesDict['BG'])
    sigOrder = []
    bgOrder = []
    workingPoints = {
        'mllMinusMZ' : {},
        'hppMass'    : {},
        'hppMt'      : {},
        'st'         : {},
    }
    for mass in masses:
        name = 'HppHmm{0}GeV'.format(mass)
        sigOrder += [name]
        bgOrder += ['BG']
        hpp4lPlotter.addHistogram(name,sigMap[name],signal=True,style={'linecolor': sigColors[mass]})
        workingPoints['mllMinusMZ'][name] = {'Z Veto 5 GeV': 5, 'Z Veto 5 GeV': 10, 'Z Veto 5 GeV': 50}
        workingPoints['hppMass'][name]    = {'0.2*m_{#Phi}': 0.2*mass, '0.3*m_{#Phi}': 0.3*mass, '0.4*m_{#Phi}': 0.4*mass, '0.5*m_{#Phi}': 0.5*mass, '0.9*m_{#Phi}': 0.9*mass,}
        workingPoints['hppMt'][name]      = {'0.2*m_{#Phi}': 0.2*mass, '0.3*m_{#Phi}': 0.3*mass, '0.4*m_{#Phi}': 0.4*mass, '0.5*m_{#Phi}': 0.5*mass, '0.9*m_{#Phi}': 0.9*mass,}
        workingPoints['st'][name]         = {'0.2*m_{#Phi}': 0.2*mass, '0.4*m_{#Phi}': 0.4*mass, '0.6*m_{#Phi}': 0.6*mass, '0.8*m_{#Phi}': 0.8*mass, '1.0*m_{#Phi}': 1.0*mass,}


    for plot in roc_cust:
        kwargs = deepcopy(plots[plot])
        kwargs.update(roc_cust[plot])
        for higgsChan in ['ee','em','et','mm','mt','tt']:
            plotnames = []
            bgnames = []
            for gen in genRecoMap:
                for reco in genRecoMap[gen]:
                    if gen[:2]==higgsChan:
                        plotnames += ['default/{0}/gen_{1}/{2}'.format(reco,gen,plot)] 
                        bgnames += ['default/{0}/{1}'.format(reco,plot)] 
                    if gen[2:]==higgsChan and 'hpp' in plot:
                        plotnames += ['default/{0}/gen_{1}/{2}'.format(reco,gen,plot.replace('hpp','hmm'))] 
            if plotnames:
                savename = 'signal/{0}/{1}_genMatched_roc'.format(higgsChan,plot)
                wp = workingPoints[plot] if plot in workingPoints else {}
                hpp4lPlotter.plotROC(plotnames,bgnames,savename,sigOrder=sigOrder,bgOrder=bgOrder,workingPoints=wp,**kwargs)
