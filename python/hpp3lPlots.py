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

blind = False
plotCount = True
doCat = True
plotMC = True
plotDatadriven = True
plotFakeRegions = True
plotSignal = False
plotROC = False
plotNormalization = False
plotSOverB = False
plotSignificance = False
plotAllMasses = False
plotSig500 = False

hpp3lPlotter = Plotter('Hpp3l',new=True)

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
signals = ['HppHm500GeV']

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


########################
### Helper functions ###
########################
def getDataDrivenPlot(*plots):
    histMap = {}
    regions = ['2P1F','1P2F','0P3F']
    #regions = ['2P1F','1P2F']
    #regions = ['2P1F']
    for s in samples + signals + ['data','datadriven']: histMap[s] = []
    for plot in plots:
        plotdirs = plot.split('/')
        for s in samples + signals + ['data']: histMap[s] += ['/'.join(['3P0F']+plotdirs)]
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
    plotter.plotCounts(countVars,countLabels,savename,numcol=3,logy=1,legendpos=34,yscale=5000,ymin=1,labelsOption='v')

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
    plotter.plotCounts(countVars,countLabels,savename,numcol=3,logy=1,legendpos=34,yscale=5000,ymin=1)

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
    plotter.plotCounts(countVars,countLabels,savename,numcol=3,logy=1,legendpos=34,yscale=5000,ymin=1)

# variable binning
variable_binning = {
    'hppMass': {
        'I'  : [x*20 for x in range(10)]+[200+x*20 for x in range(15)]+[500+x*50 for x in range(10)]+[1000+x*100 for x in range(4)]+[1650],
        'II' : [0,20,40,60,80,100,140,180,220,260,300,350,400,500,600,1650],
        'III': [x*10 for x in range(20)]+[200+x*20 for x in range(15)]+[500+x*100 for x in range(5)]+[1000,1650],
        'IV' : [0,20,40,60,80,100,140,180,220,260,300,400,600,1650],
        'V'  : [0,20,40,60,80,100,150,200,300,400,1650],
        'VI' : [0,20,40,60,80,100,140,180,220,260,300,350,400,600,1650],
    },
    'st': {
        'I'  : [60+x*10 for x in range(14)]+[200+x*20 for x in range(15)]+[500+x*100 for x in range(5)]+[1000,1200,1400,2000],
        'II' : [70,80,90,100,120,140,160,180,200,250,300,350,400,500,600,800,2000],
        'III': [70+x*10 for x in range(13)]+[200+x*20 for x in range(15)]+[500+x*100 for x in range(5)]+[1000,1200,1400,2000],
        'IV' : [60,70,80,90,100,120,140,160,180,200,250,300,350,400,500,600,2000],
        'V'  : [60,70,80,90,100,120,140,160,180,200,250,300,350,400,500,600,2000],
        'VI' : [100,125,150,200,300,2000],
    },
    #'hppLeadingLeptonPt': {
    #    'I'  : [30+x*20 for x in range(10)]+[250+x*50 for x in range(5)]+[500],
    #    'II' : [30,50,70,100,150,200,300,500,1000],
    #    'III': [30+x*10 for x in range(17)]+[200+x*20 for x in range(15)]+[500],
    #    'IV' : [30,40,60,80,100,140,180,220,260,300,400,500],
    #    'V'  : [30,40,60,80,100,150,200,300,400,500],
    #    'VI' : [30,60,80,100,140,180,220,260,300,350,400,500],
    #},
}

ymin = {
    'hppMass': {
        'I'  : 0.001,
        'II' : 0.0001,
        'III': 0.001,
        'IV' : 0.0001,
        'V'  : 0.00001,
        'VI' : 0.00001,
    },
    'st': {
        'I'  : 0.0001,
        'II' : 0.0001,
        'III': 0.0001,
        'IV' : 0.0001,
        'V'  : 0.0001,
        'VI' : 0.00001,
    },
}

def plotWithCategories(plotter,plot,baseDir='default',saveDir='',datadriven=False,postfix='',perCatBins=False,**kwargs):
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
        if perCatBins and plot in variable_binning:
            kwargs['rebin'] = variable_binning[plot][cat]
            kwargs['yaxis'] = 'Events / 1 GeV'
            kwargs['scalewidth'] = True
        if perCatBins and plot in ymin and kwargs.get('logy',False): kwargs['ymin'] = ymin[plot][cat]
        if doCat: plotter.plot(plotvars,savename,**kwargs)

def plotChannels(plotter,plot,baseDir='default',saveDir='',datadriven=False,postfix='',**kwargs):
    for chan in chans:
        plotname = '/'.join([x for x in [baseDir,chan,plot] if x])
        plotvars = getDataDrivenPlot(plotname) if datadriven else plotname
        savename = '/'.join([x for x in [saveDir,'channels',chan,plot] if x])
        if postfix: savename += '_{0}'.format(postfix)
        plotter.plot(plotvars,savename,**kwargs)

########################
### plot definitions ###
########################
plots = {
    # hpp
    'hppMass'               : {'xaxis': 'm_{l^{#pm}l^{#pm}} (GeV)', 'yaxis': 'Events / 25 GeV', 'numcol': 3, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,625,25), 'logy': True, 'overflow': True,},
    #'hppMt'                 : {'xaxis': 'm_{T}^{l^{#pm}l^{#pm}} (GeV)', 'yaxis': 'Events / 50 GeV', 'numcol': 3, 'lumipos': 11, 'legendpos':34, 'rebin': 5, 'logy': True},
    'hppPt'                 : {'xaxis': 'p_{T}^{l^{#pm}l^{#pm}} (GeV)', 'yaxis': 'Events / 10 GeV', 'rebin': range(0,410,10), 'numcol': 3, 'legendpos':34, 'overflow': True},
    'hppDeltaR'             : {'xaxis': '#DeltaR(l^{#pm}l^{#pm})', 'yaxis': 'Events', 'rebin': 25, 'numcol': 3, 'legendpos':34, 'yscale': 1.8,},
    'hppLeadingLeptonPt'    : {'xaxis': 'p_{T}^{#Phi_{lead}^{#pm#pm}} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': range(10,205,5), 'numcol': 2, 'overflow': True},
    'hppLeadingLeptonEta'   : {'xaxis': '#eta^{#Phi_{lead}^{#pm#pm}}', 'yaxis': 'Events', 'numcol': 3, 'legendpos':34, 'rebin': 20, 'yscale': 1.8,},
    'hppSubLeadingLeptonPt' : {'xaxis': 'p_{T}^{#Phi_{sublead}^{#pm#pm}} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': range(10,205,5), 'numcol': 2, 'overflow': True},
    'hppSubLeadingLeptonEta': {'xaxis': '#eta^{#Phi_{sublead}^{#pm#pm}}', 'yaxis': 'Events', 'numcol': 3, 'legendpos':34, 'rebin': 20, 'yscale': 1.8,},
    # hm
    'hmMass'                : {'xaxis': 'm_{T}(l^{#mp},E_{T}^{miss}) (GeV)', 'yaxis': 'Events / 10 GeV', 'numcol': 3, 'lumipos': 11, 'legendpos':34, 'rebin': range(0,610,10), 'logy': True, 'overflow': True},
    'hmLeptonPt'            : {'xaxis': 'p_{T}^{#Phi_{lepton}^{#mp}} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': range(10,205,5), 'numcol': 2, 'overflow': True},
    'hmLeptonEta'           : {'xaxis': '#eta^{#Phi_{lepton}^{#mp}}', 'yaxis': 'Events', 'numcol': 3, 'legendpos':34, 'rebin': 20, 'yscale': 1.8,},
    # z cand
    'zMass'                 : {'xaxis': 'm_{l^{+}l^{-}} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': range(11,241,5), 'numcol': 2, 'legendpos':34, 'yscale': 50, 'logy': True, 'overflow': True,},
    'zPt'                   : {'xaxis': 'p_{T}^{l^{+}l^{-}} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': range(0,320,20), 'numcol': 2, 'overflow': True},
    #'mllMinusMZ'            : {'xaxis': '|m_{l^{+}l^{-}}-m_{Z}| (GeV)', 'yaxis': 'Events / 2 GeV', 'rebin': 2, 'rangex': [0,80]},
    # event
    'numVertices'           : {'xaxis': 'Reconstructed Vertices', 'yaxis': 'Events', 'numcol': 3, 'legendpos':34, 'yscale': 1.8,},
    'met'                   : {'xaxis': 'E_{T}^{miss} (GeV)', 'yaxis': 'Events / 5 GeV', 'rebin': range(0,305,5), 'numcol': 2, 'overflow': True},
    #'metPhi'                : {'xaxis': '#phi(E_{T}^{miss})', 'yaxis': 'Events', 'rebin': 20},
    'mass'                  : {'xaxis': 'm_{3l} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': range(0,1020,20), 'numcol': 2, 'overflow': True},
    'st'                    : {'xaxis': '#Sigma p_{T}^{l} (GeV)', 'yaxis': 'Events / 25 GeV', 'rebin': range(25,525,25), 'numcol': 2, 'logy': True, 'numcol': 2, 'legendpos': 34, 'overflow': True},
    'nJets'                 : {'xaxis': 'Number of jets (p_{T} > 30 GeV)', 'yaxis': 'Events', 'numcol': 2, 'rebin': [-0.5,0.5,1.5,2.5,3.5,4.5], 'overflow': True, 'binlabels': ['0','1','2','3','4','#geq5']},
    #'pileupWeight'          : {'xaxis': 'Pileup Weight', 'yaxis': 'Events'},
}

blind_cust = {
    'hppMass': {'blinder': [100,1650], 'rangex': [0,1650],},
}

lowmass_cust = {
    # hpp
    'hppMass'              : {'rangex': [0,300], 'logy': False},
    #'hppMt'                : {'rangex': [0,300], 'logy': False},
    'hppPt'                : {'rangex': [0,300]},
    'hppLeadingLeptonPt'   : {'rangex': [0,100]},
    'hppSubLeadingLeptonPt': {'rangex': [0,300]},
    # hm
    'hmMass'               : {'rangex': [0,400], 'logy': False},
    'hmLeptonPt'           : {'rangex': [0,300]},
    # z
    'zMass'                : {'rangex': [60,120]},
    'zPt'                  : {'rangex': [0,300]},
    'mllMinusMZ'           : {'rangex': [0,60]},
    # event
    'met'                  : {'rangex': [0,200]},
    'mass'                 : {'rangex': [0,600]},
    'st'                   : {'rangex': [0,400], 'logy': False},
}

norm_cust = {
    # hpp
    'hppMass'               : {'yaxis': 'Unit normalized', 'logy':0, 'rebin': 1},
    #'hppMt'                 : {'yaxis': 'Unit normalized', 'logy':0, 'rebin': 1},
    'hppPt'                 : {'yaxis': 'Unit normalized', 'rebin': 1, 'numcol': 2},
    'hppDeltaR'             : {'yaxis': 'Unit normalized', 'rebin': 1},
    'hppLeadingLeptonPt'    : {'yaxis': 'Unit normalized', 'rebin': 1},
    'hppSubLeadingLeptonPt' : {'yaxis': 'Unit normalized', 'rebin': 1},
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
    #'hppMt'                 : {'yaxis': 'Efficiency', 'logy':0, 'rebin': 1},
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
    #'hppMt'                 : {'yaxis': 'Signal over background', 'logy': 0, 'rebin': 1},
    'hppPt'                 : {'yaxis': 'Signal over background', 'logy': 0, 'rebin': 1, 'numcol': 2},
    'hppDeltaR'             : {'yaxis': 'Signal over background', 'logy': 0, 'rebin': 1},
    'hppLeadingLeptonPt'    : {'yaxis': 'Signal over background', 'logy': 0, 'rebin': 1},
    'hppSubLeadingLeptonPt' : {'yaxis': 'Signal over background', 'logy': 0, 'rebin': 1},
    'st'                    : {'yaxis': 'Signal over background', 'logy': 0, 'rebin': 1},
    'mllMinusMZ'            : {'yaxis': 'Signal over background', 'logy': 0, 'rebin': 1},
    'met'                   : {'yaxis': 'Signal over background', 'logy': 0, 'rebin': 1},
}

significance_cust = {
    # hpp
    'hppMass'               : {'yaxis': 'Signal over background', 'logy': 0, 'rebin': 1},
    #'hppMt'                 : {'yaxis': 'Signal over background', 'logy': 0, 'rebin': 1},
    'hppPt'                 : {'yaxis': 'Signal over background', 'logy': 0, 'rebin': 1},
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
    #'hppMt'                 : {'yaxis': 'Background Rejection', 'xaxis': 'Signal Efficiency', 'legendpos':34, 'numcol': 3, 'ymax': 1.3, 'rebin': 1,'logy':0},
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
        hpp3lPlotter.addHistogramToStack(s,sigMap[s])

    for signal in signals:
        hpp3lPlotter.addHistogram(signal,sigMap[signal],signal=True)

    if not blind: hpp3lPlotter.addHistogram('data',sigMap['data'])

    if plotCount: plotCounts(hpp3lPlotter,saveDir='mc',baseDir='default')

    for plot in plots:
        kwargs = deepcopy(plots[plot])
        plotWithCategories(hpp3lPlotter,plot,saveDir='mc',baseDir='default',perCatBins=True,**kwargs)
        if plot=='hppMass': plotChannels(hpp3lPlotter,plot,saveDir='mc',baseDir='default',**kwargs)

    # selection assuming mass 500
    if plotSig500:
        if plotCount: plotCounts(hpp3lPlotter,saveDir='sig500',baseDir='nMinusOne/massWindow/500/hpp2')

        for plot in plots:
            kwargs = deepcopy(plots[plot])
            plotWithCategories(hpp3lPlotter,plot,saveDir='sig500',baseDir='nMinusOne/massWindow/500/hpp2',perCatBins=True,**kwargs)
            if plot=='hppMass': plotChannels(hpp3lPlotter,plot,saveDir='sig500',baseDir='nMinusOne/massWindow/500/hpp2',**kwargs)

    # partially blinded plots
    if blind:
        hpp3lPlotter.addHistogram('data',sigMap['data'])

        for plot in blind_cust:
            kwargs = deepcopy(plots[plot])
            kwargs.update(blind_cust[plot])
            plotWithCategories(hpp3lPlotter,plot,saveDir='mc',baseDir='default',postfix='blinder',perCatBins=True,**kwargs)


##############################
### datadriven backgrounds ###
##############################
if plotDatadriven:
    hpp3lPlotter.clearHistograms()

    hpp3lPlotter.addHistogramToStack('datadriven',datadrivenSamples)

    for s in samples:
        hpp3lPlotter.addHistogramToStack(s,sigMapDD[s])

    for signal in signals:
        hpp3lPlotter.addHistogram(signal,sigMapDD[signal],signal=True)

    if not blind: hpp3lPlotter.addHistogram('data',sigMapDD['data'])

    if plotCount: plotCounts(hpp3lPlotter,baseDir='default',saveDir='datadriven',datadriven=True)

    for plot in plots:
        kwargs = deepcopy(plots[plot])
        plotWithCategories(hpp3lPlotter,plot,baseDir='default',saveDir='datadriven',datadriven=True,perCatBins=True,**kwargs)
        if plot=='hppMass': plotChannels(hpp3lPlotter,plot,saveDir='datadriven',baseDir='',datadriven=True,**kwargs)

    # selection assuming mass 500
    if plotSig500:
        if plotCount: plotCounts(hpp3lPlotter,baseDir='nMinusOne/massWindow/500/hpp2',saveDir='sig500-datadriven',datadriven=True)

        for plot in plots:
            kwargs = deepcopy(plots[plot])
            plotWithCategories(hpp3lPlotter,plot,baseDir='nMinusOne/massWindow/500/hpp2',saveDir='sig500-datadriven',datadriven=True,perCatBins=True,**kwargs)
            if plot=='hppMass': plotChannels(hpp3lPlotter,plot,saveDir='sig500-datadriven',baseDir='nMinusOne/massWindow/500/hpp2',datadriven=True,**kwargs)

    # partially blinded plots
    if blind:
        hpp3lPlotter.addHistogram('data',sigMapDD['data'])

        for plot in blind_cust:
            kwargs = deepcopy(plots[plot])
            kwargs.update(blind_cust[plot])
            plotWithCategories(hpp3lPlotter,plot,baseDir='',saveDir='datadriven',postfix='blinder',datadriven=True,perCatBins=True,**kwargs)


########################
### low mass control ###
########################
if plotMC:
    hpp3lPlotter.clearHistograms()

    for s in allsamples:
        hpp3lPlotter.addHistogramToStack(s,sigMap[s])
    hpp3lPlotter.addHistogram('data',sigMap['data'])

    if plotCount: plotCounts(hpp3lPlotter,baseDir='lowmass',saveDir='lowmass')

    for plot in plots:
        kwargs = deepcopy(plots[plot])
        if plot in lowmass_cust: kwargs.update(lowmass_cust[plot])
        plotWithCategories(hpp3lPlotter,plot,baseDir='lowmass',saveDir='lowmass',**kwargs)
        if plot=='hppMass': plotChannels(hpp3lPlotter,plot,saveDir='lowmass',baseDir='lowmass',**kwargs)

######################################
### lowmass datadriven backgrounds ###
######################################
if plotDatadriven:
    hpp3lPlotter.clearHistograms()

    hpp3lPlotter.addHistogramToStack('datadriven',datadrivenSamples)

    for s in samples:
        hpp3lPlotter.addHistogramToStack(s,sigMapDD[s])

    hpp3lPlotter.addHistogram('data',sigMapDD['data'])

    if plotCount: plotCounts(hpp3lPlotter,baseDir='lowmass',saveDir='lowmass-datadriven',datadriven=True)

    for plot in plots:
        kwargs = deepcopy(plots[plot])
        if plot in lowmass_cust: kwargs.update(lowmass_cust[plot])
        plotWithCategories(hpp3lPlotter,plot,baseDir='lowmass',saveDir='lowmass-datadriven',datadriven=True,**kwargs)
        if plot=='hppMass': plotChannels(hpp3lPlotter,plot,saveDir='lowmass-datadriven',baseDir='lowmass',datadriven=True,**kwargs)

####################
### Fake Regions ###
####################
if plotFakeRegions:
    hpp3lPlotter.clearHistograms()

    for s in allsamples:
        hpp3lPlotter.addHistogramToStack(s,sigMap[s])
    for signal in signals:
        hpp3lPlotter.addHistogram(signal,sigMap[signal],signal=True)

    hpp3lPlotter.addHistogram('data',sigMap['data'])

    for fr in ['2P1F','1P2F','0P3F']:
        if plotCount: plotCounts(hpp3lPlotter,baseDir='{0}_regular'.format(fr),saveDir='mc/{0}'.format(fr))

        for plot in plots:
            kwargs = deepcopy(plots[plot])
            plotWithCategories(hpp3lPlotter,plot,baseDir='{0}_regular'.format(fr),saveDir='mc/{0}'.format(fr),**kwargs)
            #if plot=='hppMass': plotChannels(hpp3lPlotter,plot,baseDir='{0}_regular'.format(fr),saveDir='mc/{0}'.format(fr),**kwargs)
            plotChannels(hpp3lPlotter,plot,baseDir='{0}_regular'.format(fr),saveDir='mc/{0}'.format(fr),**kwargs)

############################
### Fake Regions lowmass ###
############################
if plotFakeRegions:
    hpp3lPlotter.clearHistograms()

    for s in allsamples:
        hpp3lPlotter.addHistogramToStack(s,sigMap[s])

    hpp3lPlotter.addHistogram('data',sigMap['data'])

    for fr in ['2P1F','1P2F','0P3F']:
        if plotCount: plotCounts(hpp3lPlotter,baseDir='{0}_regular/lowmass'.format(fr),saveDir='lowmass/{0}'.format(fr))

        for plot in plots:
            kwargs = deepcopy(plots[plot])
            plotWithCategories(hpp3lPlotter,plot,baseDir='{0}_regular/lowmass'.format(fr),saveDir='lowmass/{0}'.format(fr),**kwargs)
            if plot=='hppMass': plotChannels(hpp3lPlotter,plot,baseDir='{0}_regular/lowmass'.format(fr),saveDir='lowmass/{0}'.format(fr),**kwargs)


########################
### normalized plots ###
########################
if plotNormalization:
    hpp3lPlotter.clearHistograms()

    hpp3lPlotter.addHistogram('BG',allSamplesDict['BG'])
    for signal in signals:
        hpp3lPlotter.addHistogram(signal,sigMap[signal],signal=True)

    for plot in plots:
        plotname = 'default/{0}'.format(plot)
        savename = 'normalized/{0}'.format(plot)
        kwargs = deepcopy(plots[plot])
        if plot in norm_cust: kwargs.update(norm_cust[plot])
        hpp3lPlotter.plotNormalized(plotname,savename,**kwargs)
        for cat in cats:
            plotnames = []
            for subcat in subCatChannels[cat]:
                plotnames += ['default/{0}/{1}'.format(chan,plot) for chan in subCatChannels[cat][subcat]]
            savename = 'normalized/{0}/{1}'.format(cat,plot)
            if doCat: hpp3lPlotter.plotNormalized(plotnames,savename,**kwargs)

####################################
### Signal over background plots ###
####################################
if plotSOverB:
    hpp3lPlotter.clearHistograms()

    hpp3lPlotter.addHistogram('BG',allSamplesDict['BG'])
    sigOrder = []
    bgOrder = []
    for mass in masses:
        name = 'HppHm{0}GeV'.format(mass)
        sigOrder += [name]
        bgOrder += ['BG']
        hpp3lPlotter.addHistogram(name,sigMap[name],signal=True,style={'linecolor': sigColors[mass]})

    for plot in sOverB_cust:
        plotname = 'default/{0}'.format(plot)
        savename = 'sOverB/{0}'.format(plot)
        kwargs = deepcopy(plots[plot])
        if plot in sOverB_cust: kwargs.update(sOverB_cust[plot])
        hpp3lPlotter.plotSOverB(plotname,sigOrder,bgOrder,savename,**kwargs)
        for cat in cats:
            plotnames = []
            for subcat in subCatChannels[cat]:
                plotnames += ['default/{0}/{1}'.format(chan,plot) for chan in subCatChannels[cat][subcat]]
            savename = 'sOverB/{0}/{1}'.format(cat,plot)
            if doCat: hpp3lPlotter.plotSOverB(plotnames,sigOrder,bgOrder,savename,**kwargs)

##########################
### Significance plots ###
##########################
if plotSignificance:
    hpp3lPlotter.clearHistograms()

    hpp3lPlotter.addHistogram('BG',allSamplesDict['BG'])
    sigOrder = []
    bgOrder = []
    for mass in masses:
        name = 'HppHm{0}GeV'.format(mass)
        sigOrder += [name]
        bgOrder += ['BG']
        hpp3lPlotter.addHistogram(name,sigMap[name],signal=True,style={'linecolor': sigColors[mass]})

    for plot in significance_cust:
        plotname = 'default/{0}'.format(plot)
        savename = 'significance/{0}'.format(plot)
        kwargs = deepcopy(plots[plot])
        if plot in significance_cust: kwargs.update(significance_cust[plot])
        hpp3lPlotter.plotSignificance(plotname,sigOrder,bgOrder,savename,**kwargs)
        for cat in cats:
            plotnames = []
            for subcat in subCatChannels[cat]:
                plotnames += ['default/{0}/{1}'.format(chan,plot) for chan in subCatChannels[cat][subcat]]
            savename = 'significance/{0}/{1}'.format(cat,plot)
            if doCat: hpp3lPlotter.plotSignificance(plotnames,sigOrder,bgOrder,savename,**kwargs)

##############################
### all signal on one plot ###
##############################
if plotAllMasses:
    hpp3lPlotter.clearHistograms()

    xvals = {}
    for mass in allmasses:
        hpp3lPlotter.addHistogram('HppHm{0}GeV'.format(mass),sigMap['HppHm{0}GeV'.format(mass)],signal=True,style={'linecolor': sigColors[mass]})
        xvals[mass] = 'HppHm{0}GeV'.format(mass)

    fitvalues = {
        'hppMass': {0.:[0.,0.9],1:[0.,0.4],2:[0.,0.3]},
    }

    varMap = {
        'hppMass'  : 'hpp_mass',
        'hppDeltaR': 'hpp_deltaR',
        'mllMinusZ': 'fabs(z_mass-{0})'.format(ZMASS),
        'met'      : 'met_pt',
        'st'       : 'hpp1_pt+hpp2_pt+hm1_pt',
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
        selection = ' && '.join(['{0}_passMedium'.format(lep) for lep in ['hpp1','hpp2','hm1']])
        scalefactor = 'hpp1_mediumScale*hpp2_mediumScale*hm1_mediumScale*genWeight*pileupWeight*triggerEfficiency'
        hpp3lPlotter.plotEnvelope(varMap[plot],savename,xvals,envelopePoints,envelopeLabels=envelopeLabels,envelopeStyles=envelopeStyles,envelopeColors=envelopeColors,selection=selection,mcscalefactor=scalefactor,binning=varBinning[plot],**kwargs)

        for nTau in range(3):
            genChans = []
            recoChans = []
            for gen in genRecoMap:
                if len(gen)==4: continue 
                if gen[:2].count('t')!=nTau: continue
                genChans += [gen]
                for r in genRecoMap[gen]:
                    recoChans += chans[r]
            recoCut = '(' + ' || '.join(['channel=="{0}"'.format(r) for r in recoChans]) + ')'
            genCut = '(' + ' || '.join(['genChannel=="{0}"'.format(g) for g in genChans]) + ')'
            fullCut = ' && '.join([recoCut,genCut,selection])
            savename = 'signal/envelopes/{0}_{1}Taus'.format(plot,nTau)

            fitFunctions = [['pol1',200,1500]+fitvalues[plot][nTau]] if plot in fitvalues else []
            hpp3lPlotter.plotEnvelope(varMap[plot],savename,xvals,envelopePoints,envelopeLabels=envelopeLabels,envelopeStyles=envelopeStyles,envelopeColors=envelopeColors,fitFunctions=fitFunctions,selection=fullCut,mcscalefactor=scalefactor,binning=varBinning[plot],**kwargs)


if plotSignal:
    hpp3lPlotter.clearHistograms()

    for mass in masses:
        hpp3lPlotter.addHistogram('HppHm{0}GeV'.format(mass),sigMap['HppHm{0}GeV'.format(mass)],signal=True,style={'linecolor': sigColors[mass]})

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
        hpp3lPlotter.plotNormalized(plotname,savename,**kwargs)
        for cat in cats:
            plotnames = []
            for subcat in subCatChannels[cat]:
                plotnames += ['default/{0}/{1}'.format(chan,plot) for chan in subCatChannels[cat][subcat]]
            savename = 'signal/{0}/{1}'.format(cat,plot)
            catkwargs = deepcopy(kwargs)
            if cat in catRebin and 'rebin' in catkwargs and plot in ['hppMass']: catkwargs['rebin'] = catkwargs['rebin'] * catRebin[cat]
            if doCat: hpp3lPlotter.plotNormalized(plotnames,savename,**catkwargs)

    for plot in eff_cust:
        kwargs = deepcopy(plots[plot])
        if plot in norm_cust: kwargs.update(norm_cust[plot])
        for higgsChan in ['ee','em','et','mm','mt','tt']:
            # reco
            plotnames = ['default/{0}/{1}'.format(chan,plot) for chan in chans if chan[:2]==higgsChan]
            savename = 'signal/{0}/{1}'.format(higgsChan,plot)
            genkwargs = deepcopy(kwargs)
            effkwargs = deepcopy(plots[plot])
            if plot in eff_cust: effkwargs.update(eff_cust[plot])
            #if higgsChan in genRebin and 'rebin' in genkwargs and plot in ['hppMass','hmmMass']: genkwargs['rebin'] = genkwargs['rebin'] * genRebin[higgsChan]
            hpp3lPlotter.plotNormalized(plotnames,savename,**genkwargs)
            # and the gen truth
            plotnames = []
            for gen in genRecoMap:
                if len(gen)==4: continue
                for reco in genRecoMap[gen]:
                    if gen[:2]==higgsChan:
                        plotnames += ['default/{0}/gen_{1}/{2}'.format(reco,gen,plot)]
            if plotnames:
                savename = 'signal/{0}/{1}_genMatched'.format(higgsChan,plot)
                hpp3lPlotter.plotNormalized(plotnames,savename,**genkwargs)
                savename = 'signal/{0}/{1}_genMatched_efficiency'.format(higgsChan,plot)
                hpp3lPlotter.plotEfficiency(plotnames,savename,**effkwargs)

# ROCs
if plotROC:
    hpp3lPlotter.clearHistograms()

    hpp3lPlotter.addHistogram('BG',allSamplesDict['BG'])
    sigOrder = []
    bgOrder = []
    workingPoints = {
        'mllMinusMZ' : {},
        'hppMass'    : {},
        'hppMt'      : {},
        'st'         : {},
    }
    for mass in masses:
        name = 'HppHm{0}GeV'.format(mass)
        sigOrder += [name]
        bgOrder += ['BG']
        hpp3lPlotter.addHistogram(name,sigMap[name],signal=True,style={'linecolor': sigColors[mass]})
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
                if len(gen)==4: continue
                for reco in genRecoMap[gen]:
                    if gen[:2]==higgsChan:
                        plotnames += ['default/{0}/gen_{1}/{2}'.format(reco,gen,plot)]
                        bgnames += ['default/{0}/{1}'.format(reco,plot)]
            if plotnames:
                savename = 'signal/{0}/{1}_genMatched_roc'.format(higgsChan,plot)
                wp = workingPoints[plot] if plot in workingPoints else {}
                hpp3lPlotter.plotROC(plotnames,bgnames,savename,sigOrder=sigOrder,bgOrder=bgOrder,workingPoints=wp,**kwargs)
                    
                                                                                                          
