import os
import json
import sys
import logging
from itertools import product, combinations_with_replacement

from DevTools.Plotter.HistMaker import HistMaker
from DevTools.Plotter.Plotter import Plotter
from DevTools.Utilities.utilities import ZMASS, getCMSSWVersion
from copy import deepcopy
import ROOT

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

version = getCMSSWVersion()

plotter = Plotter('MonoHZZFakeRate',new=True)
maker = HistMaker('MonoHZZFakeRate',outputFileName = 'root/MonoHZZFakeRate/fakerates.root')

#########################
### Define categories ###
#########################

sigMap = {
    'Z'   : [
            'DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8',
            'DYJetsToLL_M-10to50_TuneCP5_13TeV-amcatnloFXFX-pythia8',
            ],
    'TT'  : [
            #'TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8',
            #'TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8',
            #'TT_DiLept_TuneCP5_13TeV-amcatnlo-pythia8',
            'TTJets_TuneCP5_13TeV-amcatnloFXFX-pythia8',
            ],
    'WW' : [
            'WWTo2L2Nu_NNPDF31_TuneCP5_13TeV-powheg-pythia8',
            ],
    'WZ' : [
            'WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8',
            #'WZTo3LNu_13TeV-powheg-pythia8',
            'WZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8',
            ],
    'ZZ' : [
            'ZZTo4L_13TeV_powheg_pythia8',
            'ZZTo2L2Nu_13TeV_powheg_pythia8',
            #'ZZTo2L2Q_13TeV_powheg_pythia8',
            'ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8',
            'GluGluToContinToZZTo2e2mu_13TeV_MCFM701_pythia8',
            'GluGluToContinToZZTo2mu2tau_13TeV_MCFM701_pythia8',
            'GluGluToContinToZZTo2e2tau_13TeV_MCFM701_pythia8',
            'GluGluToContinToZZTo4e_13TeV_MCFM701_pythia8',
            'GluGluToContinToZZTo4mu_13TeV_MCFM701_pythia8',
            'GluGluToContinToZZTo4tau_13TeV_MCFM701_pythia8',
            ],
    'TTV' : [
            'ttWJets_TuneCP5_13TeV_madgraphMLM_pythia8',
            'ttZJets_TuneCP5_13TeV_madgraphMLM_pythia8',
            ],
    'VVV' : [
            'WWW_4F_TuneCP5_13TeV-amcatnlo-pythia8',
            'WWZ_4F_TuneCP5_13TeV-amcatnlo-pythia8',
            'WZG_TuneCP5_13TeV-amcatnlo-pythia8',
            'WZZ_TuneCP5_13TeV-amcatnlo-pythia8',
            'ZZZ_TuneCP5_13TeV-amcatnlo-pythia8',
            ],
    'HZZ' : [
            'GluGluHToZZTo4L_M125_13TeV_powheg2_JHUGenV7011_pythia8',
            'VBF_HToZZTo4L_M125_13TeV_powheg2_JHUGenV7011_pythia8',
            'WminusH_HToZZTo4L_M125_13TeV_powheg2-minlo-HWJ_JHUGenV7011_pythia8',
            'WplusH_HToZZTo4L_M125_13TeV_powheg2-minlo-HWJ_JHUGenV7011_pythia8',
            'ttH_HToZZ_4LFilter_M125_13TeV_powheg2_JHUGenV7011_pythia8',
            'ZH_HToZZ_4LFilter_M125_13TeV_powheg2-minlo-HZJ_JHUGenV7011_pythia8',
            ],
    'data' : [
            'DoubleMuon',
            'DoubleEG',
            'MuonEG',
            'SingleMuon',
            'SingleElectron',
            ],
}

sigMap['BG'] = []
for s in ['WZ','ZZ','VVV','TTV']:
    sigMap['BG'] += sigMap[s]

samples = ['TT','TTV','WZ','VVV','ZZ','Z']

selections = ['default','tight']

channels = ['e','m']
channelMap = {'e': ['eee','mme'], 'm': ['eem','mmmm']}


plotter.addHistogram('MC',sigMap['BG'])
plotter.addHistogram('Z',sigMap['Z'])
plotter.addHistogram('data',sigMap['data'],style={'linecolor':ROOT.kBlack,'name':'Data'})
plotter.addHistogram('data_uncorrected',sigMap['data'],style={'linecolor':ROOT.kRed,'name':'Uncorrected'})

denom = 'default'
num = 'tight'
plot = 'lPt'

ptBins = [5,7,10,15,20,30,50,100]
etaBins = {
    'e' : [0,1.479,2.5],
    'm' : [0,0.8,1.2,2.4],
}

xaxis = 'p_{T}'
yaxis = '|#eta|'
values = {}
errors = {}
values_mc = {}
errors_mc = {}
for chan in channels:
    for e in range(len(etaBins[chan])-1):
        numname = ['{}/etaBin{}/{}/{}'.format(num,e,c,plot) for c in channelMap[chan]]
        denomname = ['{}/etaBin{}/{}/{}'.format(denom,e,c,plot) for c in channelMap[chan]]
        savename = 'fake_{}'.format(chan)
        subtractMap = {'data': ['MC']}
        customOrder = ['data']
        hists = plotter.plotRatio(numname,denomname,savename,customOrder=customOrder,subtractMap=subtractMap,rebin=ptBins,getHists=True)
        for p in range(len(ptBins)-1):
            pt = float(ptBins[p]+ptBins[p+1])/2.
            eta = float(etaBins[chan][e]+etaBins[chan][e+1])/2.
            key = (pt,eta)
            values[key] = hists['data'].GetBinContent(p+1)
            errors[key] = hists['data'].GetBinError(p+1)
        customOrder = ['Z']
        hists_mc = plotter.plotRatio(numname,denomname,savename,customOrder=customOrder,rebin=ptBins,getHists=True)
        for p in range(len(ptBins)-1):
            pt = float(ptBins[p]+ptBins[p+1])/2.
            eta = float(etaBins[chan][e]+etaBins[chan][e+1])/2.
            key = (pt,eta)
            values_mc[key] = hists_mc['Z'].GetBinContent(p+1)
            errors_mc[key] = hists_mc['Z'].GetBinError(p+1)
    savedir = chan
    savename = 'fakeratePtEta'
    maker.make2D(savename,values,errors,ptBins,etaBins[chan],savedir=savedir,xaxis=xaxis,yaxis=yaxis)
    savename = 'fakeratePtEta_fromMC'
    maker.make2D(savename,values_mc,errors_mc,ptBins,etaBins[chan],savedir=savedir,xaxis=xaxis,yaxis=yaxis)
    print chan
    print values
    print errors
    print values_mc
    print errors_mc
