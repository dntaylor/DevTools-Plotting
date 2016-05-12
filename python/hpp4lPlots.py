import os
import json
import sys
import logging
from itertools import product, combinations_with_replacement

from DevTools.Plotter.Plotter import Plotter
from DevTools.Plotter.higgsUtilities import getChannels, getChannelLabels, getCategories, getCategoryLabels, getSubCategories, getSubCategoryLabels
from copy import deepcopy
import ROOT

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

blind = True
doCat = True
plotMC = True
plotDatadriven = True
plotSignal = False
plotNormalization = False
plotCount = True

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

sigMap = {
    'WZ'  : [
             'WZTo3LNu_TuneCUETP8M1_13TeV-powheg-pythia8',
             'WZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8',
             'WZTo1L3Nu_13TeV_amcatnloFXFX_madspin_pythia8',
             'WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8',
            ],
    'ZZ'  : [
             'ZZTo4L_13TeV_powheg_pythia8',
             'GluGluToContinToZZTo2e2mu_13TeV_MCFM701_pythia8',
             'GluGluToContinToZZTo2mu2tau_13TeV_MCFM701_pythia8',
             'GluGluToContinToZZTo4e_13TeV_MCFM701_pythia8',
             'GluGluToContinToZZTo4mu_13TeV_MCFM701_pythia8',
             'GluGluToContinToZZTo4tau_13TeV_MCFM701_pythia8',
            ],
    'ZZall' : [
             'ZZTo4L_13TeV_powheg_pythia8',
             'GluGluToContinToZZTo2e2mu_13TeV_MCFM701_pythia8',
             'GluGluToContinToZZTo2mu2tau_13TeV_MCFM701_pythia8',
             'GluGluToContinToZZTo4e_13TeV_MCFM701_pythia8',
             'GluGluToContinToZZTo4mu_13TeV_MCFM701_pythia8',
             'GluGluToContinToZZTo4tau_13TeV_MCFM701_pythia8',
             'ZZTo2L2Nu_13TeV_powheg_pythia8',
             'ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8',
            ],
    'VVV' : [
             'WZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
             'WWG_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
            ],
    'VH'  : [
             'ZH_HToBB_ZToLL_M125_13TeV_amcatnloFXFX_madspin_pythia8',
             'ZH_HToGG_ZToAll_M125_13TeV_powheg_pythia8',
             'ZH_HToZG_ZToAll_M-125_13TeV_powheg_pythia8',
             'ZH_HToZZ_4LFilter_M125_13TeV_powheg2-minlo-HZJ_JHUgenV6_pythia8',
            ],
    'VHall' : [
             'WH_HToBB_WToLNu_M125_13TeV_amcatnloFXFX_madspin_pythia8',
             'ZH_HToBB_ZToLL_M125_13TeV_amcatnloFXFX_madspin_pythia8',
             'ZH_HToBB_ZToNuNu_M125_13TeV_amcatnloFXFX_madspin_pythia8',
             'ZH_HToBB_ZToQQ_M125_13TeV_powheg_pythia8',
             'ZH_HToGG_ZToAll_M125_13TeV_powheg_pythia8',
             'ZH_HToZG_ZToAll_M-125_13TeV_powheg_pythia8',
             'ZH_HToZZ_4LFilter_M125_13TeV_powheg2-minlo-HZJ_JHUgenV6_pythia8',
            ],
    'TTV' : [
             'ttZJets_13TeV_madgraphMLM',
             'ttH_M125_13TeV_powheg_pythia8',
            ],
    'TTVall' : [
             'ttWJets_13TeV_madgraphMLM',
             'ttZJets_13TeV_madgraphMLM',
             'ttH_M125_13TeV_powheg_pythia8',
             'tZq_ll_4f_13TeV-amcatnlo-pythia8_TuneCUETP8M1',
             'tZq_nunu_4f_13TeV-amcatnlo-pythia8_TuneCUETP8M1',
            ],
    'WW'  : [
             'WWTo2L2Nu_13TeV-powheg',
             'WWToLNuQQ_13TeV-powheg',
            ],
    'W'   : [
             'WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
            ],
    'Z'   : [
             'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
             'DY1JetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
             'DY2JetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
             'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
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
    'T'   : [
             'ST_s-channel_4f_leptonDecays_13TeV-amcatnlo-pythia8_TuneCUETP8M1',
             #'ST_t-channel_4f_leptonDecays_13TeV-amcatnlo-pythia8_TuneCUETP8M1',
             'ST_t-channel_antitop_4f_leptonDecays_13TeV-powheg-pythia8_TuneCUETP8M1',
             'ST_t-channel_top_4f_leptonDecays_13TeV-powheg-pythia8_TuneCUETP8M1',
             'ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1',
             'ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1',
            ],
    'QCD' : [
             'QCD_Pt_15to30_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_30to50_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_50to80_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_80to120_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_120to170_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_170to300_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_300to470_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_470to600_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_600to800_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_800to1000_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_1000to1400_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_1400to1800_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_1800to2400_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_2400to3200_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_3200toInf_TuneCUETP8M1_13TeV_pythia8',
            ],
    'data': [
             'DoubleMuon',
             'DoubleEG',
             'MuonEG',
             'SingleMuon',
             'SingleElectron',
             'Tau',
            ],
    'HppHmm200GeV' : ['HPlusPlusHMinusMinusHTo4L_M-200_13TeV-pythia8'],
    'HppHmm300GeV' : ['HPlusPlusHMinusMinusHTo4L_M-300_13TeV-pythia8'],
    'HppHmm400GeV' : ['HPlusPlusHMinusMinusHTo4L_M-400_13TeV-pythia8'],
    'HppHmm500GeV' : ['HPlusPlusHMinusMinusHTo4L_M-500_13TeV-pythia8'],
    'HppHmm600GeV' : ['HPlusPlusHMinusMinusHTo4L_M-600_13TeV-pythia8'],
    'HppHmm700GeV' : ['HPlusPlusHMinusMinusHTo4L_M-700_13TeV-pythia8'],
    'HppHmm800GeV' : ['HPlusPlusHMinusMinusHTo4L_M-800_13TeV-pythia8'],
    'HppHmm900GeV' : ['HPlusPlusHMinusMinusHTo4L_M-900_13TeV-pythia8'],
    'HppHmm1000GeV': ['HPlusPlusHMinusMinusHTo4L_M-1000_13TeV-pythia8'],
}


samples = ['TTV','VH','VVV','ZZ']
allsamples = ['W','T','TT','TTVall','Z','WW','VHall','WZ','VVV','ZZall']
signals = ['HppHmm500GeV']

datadrivenSamples = []
for s in samples + ['data']:
    datadrivenSamples += sigMap[s]

def getDataDrivenPlot(*plots):
    histMap = {}
    #regions = ['3P1F','2P2F','1P3F','0P4F']
    regions = ['3P1F']
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
    plotter.plotCounts(countVars,countLabels,savename,numcol=3,logy=1,legendpos=34,yscale=10)
    
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
    plotter.plotCounts(countVars,countLabels,savename,numcol=3,logy=1,legendpos=34,yscale=10)
    
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
    plotter.plotCounts(countVars,countLabels,savename,numcol=3,logy=1,legendpos=34,yscale=10,ymin=0.001)

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
    'hppPt'                 : {'xaxis': 'p_{T}^{l^{+}l^{+}} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': 2},
    'hppDeltaR'             : {'xaxis': '#DeltaR(l^{+}l^{+})', 'yaxis': 'Events', 'rebin': 2},
    'hppLeadingLeptonPt'    : {'xaxis': 'p_{T}^{#Phi_{lead}^{++}} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': 2},
    'hppSubLeadingLeptonPt' : {'xaxis': 'p_{T}^{#Phi_{sublead}^{++}} (GeV)', 'yaxis': 'Events / 20 GeV', 'rebin': 2},
    # hmm
    'hmmMass'               : {'xaxis': 'm_{l^{-}l^{-}} (GeV)', 'yaxis': 'Events / 50 GeV', 'numcol': 3, 'lumipos': 11, 'legendpos':34, 'rebin': 5, 'logy': True},
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
    'hppPt'                : {'rangex': [0,300]},
    'hppLeadingLeptonPt'   : {'rangex': [0,300]},
    'hppSubLeadingLeptonPt': {'rangex': [0,300]},
    # hmm
    'hmmMass'              : {'rangex': [0,300], 'logy': False},
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
    'hppPt'                 : {'yaxis': 'Unit normalized', 'rebin': 20, 'numcol': 2},
    'hppDeltaR'             : {'yaxis': 'Unit normalized', 'rebin': 10},
    'hppLeadingLeptonPt'    : {'yaxis': 'Unit normalized', 'rebin': 5},
    'hppSubLeadingLeptonPt' : {'yaxis': 'Unit normalized', 'rebin': 5},
    # hmm
    'hmmMass'               : {'yaxis': 'Unit normalized', 'logy':0, 'rebin': 1},
    'hmmPt'                 : {'yaxis': 'Unit normalized', 'rebin': 20, 'numcol': 2},
    'hmmDeltaR'             : {'yaxis': 'Unit normalized', 'rebin': 10},
    'hmmLeadingLeptonPt'    : {'yaxis': 'Unit normalized', 'rebin': 5},
    'hmmSubLeadingLeptonPt' : {'yaxis': 'Unit normalized', 'rebin': 5},
    # z
    'zMass'                 : {'yaxis': 'Unit normalized', 'rebin': 20, 'numcol': 2},
    'mllMinusMZ'            : {'yaxis': 'Unit normalized', 'rebin': 1},
    # event
    'met'                   : {'yaxis': 'Unit normalized', 'rebin': 1},
    'numVertices'           : {'yaxis': 'Unit normalized'},
    'mass'                  : {'yaxis': 'Unit normalized', 'rebin': 10},
    'st'                    : {'yaxis': 'Unit normalized', 'rebin': 10},
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

########################
### normalized plots ###
########################
if plotNormalization:
    hpp4lPlotter.clearHistograms()
    
    allSamplesDict = {'BG':[]}
    
    for s in allsamples:
        allSamplesDict['BG'] += sigMap[s]
    
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

##############################
### all signal on one plot ###
##############################
if plotSignal:
    hpp4lPlotter.clearHistograms()
    
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
    
    #masses = [200,300,400,500,600,700,800,900,1000]
    masses = [200,400,600,800,1000]
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
    
    genDecayMap = {
        'ee' : ['ee'],
        'em' : ['em'],
        'et' : ['ee','em','et'],
        'mm' : ['mm'],
        'mt' : ['em','mm','mt'],
        'tt' : ['ee','em','et','mm','mt','tt'],
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
        if 'hpp' in plot: # plot just the channels of the type
            for higgsChan in ['ee','em','et','mm','mt','tt']:
                # reco
                plotnames = ['default/{0}/{1}'.format(chan,plot) for chan in chans if chan[:2]==higgsChan] + ['default/{0}/{1}'.format(chan,plot.replace('hpp','hmm')) for chan in chans if chan[2:]==higgsChan]
                savename = 'signal/{0}/{1}'.format(higgsChan,plot)
                genkwargs = deepcopy(kwargs)
                if higgsChan in genRebin and 'rebin' in genkwargs and plot in ['hppMass','hmmMass']: genkwargs['rebin'] = genkwargs['rebin'] * genRebin[higgsChan]
                hpp4lPlotter.plotNormalized(plotnames,savename,**genkwargs)
                # and the gen truth
                plotnames = []
                for gen in chans:
                    for reco in chans:
                        if reco[:2] in genDecayMap[gen[:2]] and reco[2:] in genDecayMap[gen[2:]] and gen[:2]==higgsChan:
                            plotnames += ['default/{0}/gen_{1}/{2}'.format(reco,gen,plot)] 
                        #if reco[:2] in genDecayMap[gen[:2]] and reco[2:] in genDecayMap[gen[2:]] and gen[2:]==higgsChan:
                        #    plotnames += ['default/{0}/gen_{1}/{2}'.format(reco,gen,plot.replace('hpp','hmm'))] 
                if plotnames:
                    savename = 'signal/{0}/{1}_genMatched'.format(higgsChan,plot)
                    #hpp4lPlotter.plotNormalized(plotnames,savename,**genkwargs)
