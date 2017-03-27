
import os
import sys
import logging

from DevTools.Plotter.Plotter import Plotter
from copy import deepcopy

import ROOT

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

wzPlotter = Plotter('WZ')

doCounts = True
doDatadriven = True
doMC = True
doNMinusOne = True
doControls = True
doVBS = True

sigMap = {
    'WZ'  : [
             'WZTo3LNu_TuneCUETP8M1_13TeV-powheg-pythia8',
             #'WZTo3LNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
            ],
    'WZall'  : [
             'WZTo3LNu_TuneCUETP8M1_13TeV-powheg-pythia8',
             #'WZTo3LNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
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
    'ZZall'  : [
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
             'WWW_4F_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
             'WWZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
             'WZG_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
             'WZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
             'ZZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
            ],
    'TTV' : [
             #'ttWJets_13TeV_madgraphMLM',
             'ttZJets_13TeV_madgraphMLM',
             'tZq_ll_4f_13TeV-amcatnlo-pythia8',
             'TTWJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8',
            ],
    'WW'  : [
             'WWTo2L2Nu_13TeV-powheg',
             'WWToLNuQQ_13TeV-powheg',
            ],
    'W'   : [
             'WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
            ],
    'Z'   : [
             'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
             'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
            ],
    'ZG'  : [
             'ZGTo2LG_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
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
             'QCD_Pt_5to10_TuneCUETP8M1_13TeV_pythia8',
             'QCD_Pt_10to15_TuneCUETP8M1_13TeV_pythia8',
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
            ],
}


plotStyles = {
    # Z
    'zMass'               : {'xaxis': 'm_{l^{+}l^{-}}', 'yaxis': 'Events / 1 GeV', 'rangex':[60,120]},
    #'mllMinusMZ'          : {'xaxis': '|m_{l^{+}l^{-}}-m_{Z}|', 'yaxis': 'Events / 1 GeV', 'rangex':[0,60]},
    'zPt'                 : {'xaxis': 'p_{T}^{Z}', 'yaxis': 'Events / 10 GeV', 'rebin':10, 'rangex':[0,200]},
    'zLeadingLeptonPt'    : {'xaxis': 'p_{T}^{Z lead}', 'yaxis': 'Events / 10 GeV', 'rebin':10, 'rangex':[0,200]},
    'zSubLeadingLeptonPt' : {'xaxis': 'p_{T}^{Z sublead}', 'yaxis': 'Events / 10 GeV', 'rebin':10, 'rangex':[0,200]},
    # W
    'wMass'               : {'xaxis': 'm_{T}^{W}', 'yaxis': 'Events / 10 GeV', 'rebin':10, 'rangex':[0,200]},
    'wPt'                 : {'xaxis': 'p_{T}^{W}', 'yaxis': 'Events / 10 GeV', 'rebin':10, 'rangex':[0,200]},
    'wLeptonPt'           : {'xaxis': 'p_{T}^{W lepton}', 'yaxis': 'Events / 10 GeV', 'rebin':10, 'rangex':[0,200]},
    # event
    'met'                 : {'xaxis': 'E_{T}^{miss}', 'yaxis': 'Events / 10 GeV', 'rebin':10, 'rangex':[0,200]},
    'mass'                : {'xaxis': 'm_{3l}', 'yaxis': 'Events / 20 GeV', 'rebin':20, 'rangex':[0,500]},
    'nJets'               : {'xaxis': 'Number of Jets (p_{T} > 30 GeV)', 'yaxis': 'Events', 'rangex':[0,8]},
    'nBjets'              : {'xaxis': 'Number of b-tagged Jets (p_{T} > 30 GeV)', 'yaxis': 'Events', 'rangex':[0,8]},
    # vbf
    'leadJetPt'           : {'xaxis': 'Lead Jet p_{T}', 'yaxis': 'Events / 20 GeV', 'rebin': 20, 'rangex': [20,400]},
    'dijetMass'           : {'xaxis': 'm_{jj}', 'yaxis': 'Events / 100 GeV', 'rebin': 100, 'rangex': [0,2000]},
    'dijetDEta'           : {'xaxis': '\Delta\eta(jj)', 'yaxis': 'Events', 'rebin': 10, 'rangex': [0,10]},
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

#################
### MC driven ###
#################
for s in allsamples:
    name = s.replace('all','')
    wzPlotter.addHistogramToStack(name,sigMap[s])

wzPlotter.addHistogram('data',sigMap['data'])

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


if doCounts and doDatadriven:
    plotCounts(wzPlotter,baseDir='',saveDir='datadriven',datadriven=True)
    if doVBS: plotCounts(wzPlotter,baseDir='vbs',saveDir='vbs-datadriven',datadriven=True)
    for cut in nMinusOneCuts:
        if doNMinusOne: plotCounts(wzPlotter,baseDir=cut,saveDir='nMinusOne-datadriven/{0}'.format(cut),datadriven=True)
    for cut in vbsNMinusOneCuts:
        if doNMinusOne and doVBS: plotCounts(wzPlotter,baseDir='vbs/{0}'.format(cut),saveDir='vbsNMinusOne-datadriven/{0}'.format(cut),datadriven=True)
    for control in controls:
        if doControls: plotCounts(wzPlotter,baseDir=control,saveDir='{0}-datadriven'.format(control),datadriven=True)

if doDatadriven:
    for plot in plotStyles:
        plotvars = getDataDrivenPlot(plot)
        savename = 'datadriven/{0}'.format(plot)
        wzPlotter.plot(plotvars,savename,**plotStyles[plot])
        plotvars = getDataDrivenPlot('vbs/{0}'.format(plot))
        savename = 'vbs-datadriven/{0}'.format(plot)
        if doVBS: wzPlotter.plot(plotvars,savename,**plotStyles[plot])
        for cut in nMinusOneCuts:
            plotvars = getDataDrivenPlot('{0}/{1}'.format(cut,plot))
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

