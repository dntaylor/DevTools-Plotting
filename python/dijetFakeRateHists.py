import os
import sys
import logging

from DevTools.Plotter.HistMaker import HistMaker
from DevTools.Plotter.Plotter import Plotter
from copy import deepcopy

import ROOT

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

dijetFakeRatePlotter = Plotter(
    'DijetFakeRate',
)

dijetFakeRateMaker = HistMaker(
    'DijetFakeRate',
    outputFileName = 'root/DijetFakeRate/fakerates.root',
)

sigMap = {
    'WW'  : [
             'WWTo2L2Nu_13TeV-powheg',
             'WWToLNuQQ_13TeV-powheg',
            ],
    'W'   : [
             'WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
             #'WJetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             #'W1JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             #'W2JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             #'W3JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             #'W4JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
            ],
    'Z'   : [
             'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
             'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
             #'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             #'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             #'DY1JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             #'DY2JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             #'DY3JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             #'DY4JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
            ],
    'TT'  : [
             'TTJets_DiLept_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'TTJets_SingleLeptFromT_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             'TTJets_SingleLeptFromTbar_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
            ],
    'T'   : [
             #'ST_s-channel_4f_leptonDecays_13TeV-amcatnlo-pythia8_TuneCUETP8M1',
             #'ST_t-channel_4f_leptonDecays_13TeV-amcatnlo-pythia8_TuneCUETP8M1',
             'ST_t-channel_antitop_4f_leptonDecays_13TeV-powheg-pythia8_TuneCUETP8M1',
             'ST_t-channel_top_4f_leptonDecays_13TeV-powheg-pythia8_TuneCUETP8M1',
             'ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1',
             'ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1',
            ],
    'data': [
             'DoubleMuon',
             'DoubleEG',
            ],
}

samples = ['TT','Z','W','T','WW']

allSamplesDict = {'MC':[]}

for s in samples:
    allSamplesDict['MC'] += sigMap[s]

dijetFakeRatePlotter.addHistogram('MC',allSamplesDict['MC'])
dijetFakeRatePlotter.addHistogram('data',sigMap['data'],style={'linecolor':ROOT.kBlack,'name':'EWK Corrected'})
dijetFakeRatePlotter.addHistogram('data_uncorrected',sigMap['data'],style={'linecolor':ROOT.kRed,'name':'Uncorrected'})



channels = ['e','m']

dirName = {
    'e': 'electron',
    'm': 'muon',
    't': 'tau'
}

labelMap = {
    'e': 'e',
    'm': '#mu',
    't': '#tau',
}

etaBins = {
    'e': [0.,1.479,2.5],
    'm': [0.,1.2,2.4],
}
ptBins = {
    'e': [0,10,15,20,25,30,100],
    'm': [0,10,15,20,25,30,100],
}

jetPtBins = [20,25,30,35,40,45,50]

for num,denom in [('medium','loose'),('tight','loose'),('tight','medium')]:
    for chan in channels:
        xBinning = ptBins[chan]
        xaxis = 'p_{{T}}^{{{0}}}'.format(labelMap[chan])
        yBinning = etaBins[chan]
        yaxis = '|#eta^{{{0}}}|'.format(labelMap[chan])
        values = {}
        errors = {}
        # get the values
        for e in range(len(yBinning)-1):
            # get the histogram
            numname = '{0}/{1}/etaBin{2}/pt'.format(num,chan,e)
            denomname = '{0}/{1}/etaBin{2}/pt'.format(denom,chan,e)
            savename = 'filler'
            subtractMap = {
                'data': ['MC'],
            }
            customOrder = ['data']
            hists = dijetFakeRatePlotter.plotRatio(numname,denomname,savename,customOrder=customOrder,subtractMap=subtractMap,rebin=xBinning,getHists=True)
            # get the pt bins
            for p in range(len(xBinning)-1):
                pt = float(xBinning[p]+xBinning[p+1])/2.
                eta = float(yBinning[e]+yBinning[e+1])/2.
                key = (pt,eta)
                values[key] = hists['data'].GetBinContent(p+1)
                errors[key] = hists['data'].GetBinError(p+1)
        # save the values
        savename = 'fakeratePtEta'
        savedir = '{0}/{1}_{2}'.format(chan,num,denom)
        dijetFakeRateMaker.make2D(savename,values,errors,xBinning,yBinning,savedir=savedir,xaxis=xaxis,yaxis=yaxis)
        # jet Pt change
        #for jetPt in jetPtBins:
        #    values = {}
        #    errors = {}
        #    # get the values
        #    for e in range(len(yBinning)-1):
        #        # get the histogram
        #        numname = '{0}/{1}/jetPt{2}/etaBin{3}/pt'.format(num,chan,jetPt,e)
        #        denomname = '{0}/{1}/jetPt{2}/etaBin{3}/pt'.format(denom,chan,jetPt,e)
        #        savename = 'filler{0}'.format(jetPt)
        #        subtractMap = {
        #            'data': ['MC'],
        #        }
        #        customOrder = ['data']
        #        hists = dijetFakeRatePlotter.plotRatio(numname,denomname,savename,customOrder=customOrder,subtractMap=subtractMap,rebin=xBinning,getHists=True)
        #        # get the pt bins
        #        for p in range(len(xBinning)-1):
        #            pt = float(xBinning[p]+xBinning[p+1])/2.
        #            eta = float(yBinning[e]+yBinning[e+1])/2.
        #            key = (pt,eta)
        #            values[key] = hists['data'].GetBinContent(p+1)
        #            errors[key] = hists['data'].GetBinError(p+1)
        #    # save the values
        #    savename = 'fakeratePtEta_jetPt{0}'.format(jetPt)
        #    savedir = '{0}/{1}_{2}'.format(chan,num,denom)
        #    dijetFakeRateMaker.make2D(savename,values,errors,xBinning,yBinning,savedir=savedir,xaxis=xaxis,yaxis=yaxis)
