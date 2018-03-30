import os
import sys
import logging

from DevTools.Plotter.HistMaker import HistMaker
from DevTools.Plotter.Plotter import Plotter
from copy import deepcopy

import ROOT

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

fakeratePlotter = Plotter(
    'MuMuMuFakeRate',
)

fakerateMaker = HistMaker(
    'MuMuMuFakeRate',
    outputFileName = 'root/MuMuMuFakeRate/fakerates.root',
)

sigMap = {
    'Z' : [
        'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
        'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
    ],
    'QCD' : [
        'QCD_Pt-15to20_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8',
        'QCD_Pt-20to30_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8',
        'QCD_Pt-30to50_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8',
        'QCD_Pt-50to80_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8',
        'QCD_Pt-80to120_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8',
        'QCD_Pt-120to170_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8',
        'QCD_Pt-170to300_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8',
        'QCD_Pt-300to470_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8',
        'QCD_Pt-470to600_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8',
        'QCD_Pt-600to800_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8',
        'QCD_Pt-800to1000_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8',
        'QCD_Pt-1000toInf_MuEnrichedPt5_TuneCUETP8M1_13TeV_pythia8',
    ],
    'W' : [
        'WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
    ],
    'TT': [
        'TTJets_DiLept_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
    ],
    'WW': [
        'VVTo2L2Nu_13TeV_amcatnloFXFX_madspin_pythia8',
    ],
    'WZ': [
        #'WZTo3LNu_TuneCUETP8M1_13TeV-powheg-pythia8',
        'WZTo3LNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
    ],
    'ZZ': [
        'ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8',
        'ZZTo4L_13TeV-amcatnloFXFX-pythia8',
    ],
    'data' : [
        'DoubleMuon',
    ],
}

samples = ['W','TT','Z','WW','WZ','ZZ']
subsamples = ['WZ','ZZ']

allSamplesDict = {'MC':[]}

for s in subsamples:
    allSamplesDict['MC'] += sigMap[s]

fakeratePlotter.addHistogram('MC',allSamplesDict['MC'])
fakeratePlotter.addHistogram('Z',sigMap['Z'])
fakeratePlotter.addHistogram('data',sigMap['data'],style={'linecolor':ROOT.kBlack,'name':'Corrected'})
fakeratePlotter.addHistogram('data_uncorrected',sigMap['data'],style={'linecolor':ROOT.kRed,'name':'Uncorrected'})

etaBins = [0.,1.0,1.5,2.4]
ptBins = [3,5,10,15,20,25,30,50,100]

numDenoms = [('iso0.15','default'),('iso0.40','default'),('iso0.25','default'),('iso0.15','iso0.40'),]
numDenoms += [('iso0.15trig','defaulttrig'),('iso0.40trig','defaulttrig'),('iso0.25trig','defaulttrig'),('iso0.15trig','iso0.40trig'),]
numDenoms += [('mediumiso0.15','mediumdefault'),('mediumiso0.40','mediumdefault'),('mediumiso0.25','mediumdefault'),('mediumiso0.15','mediumiso0.40'),]
numDenoms += [('mediumiso0.15trig','mediumdefaulttrig'),('mediumiso0.40trig','mediumdefaulttrig'),('mediumiso0.25trig','mediumdefaulttrig'),('mediumiso0.15trig','mediumiso0.40trig'),]

name = '{0}/etaBin{1}/mPt'

for num,denom in numDenoms:
    xaxis = 'p_{T}^{#tau}'
    yaxis = '|#eta^{#tau}|'
    values = {}
    errors = {}
    values_mc = {}
    errors_mc = {}
    # get the values
    for e in range(len(etaBins)-1):
        # get the histogram
        numname = name.format(num,e)
        denomname = name.format(denom,e)
        savename = '{0}_{1}'.format(num,denom)
        subtractMap = {
            'data': ['MC'],
        }
        customOrder = ['data']
        hists = fakeratePlotter.plotRatio(numname,denomname,savename,customOrder=customOrder,subtractMap=subtractMap,rebin=ptBins,getHists=True)
        for p in range(len(ptBins)-1):
            pt = float(ptBins[p]+ptBins[p+1])/2.
            eta = float(etaBins[e]+etaBins[e+1])/2.
            key = (pt,eta)
            values[key] = hists['data'].GetBinContent(p+1)
            errors[key] = hists['data'].GetBinError(p+1)
        customOrder = ['Z']
        hists_mc = fakeratePlotter.plotRatio(numname,denomname,savename,customOrder=customOrder,rebin=ptBins,getHists=True)
        for p in range(len(ptBins)-1):
            pt = float(ptBins[p]+ptBins[p+1])/2.
            eta = float(etaBins[e]+etaBins[e+1])/2.
            key = (pt,eta)
            values_mc[key] = hists_mc['Z'].GetBinContent(p+1)
            errors_mc[key] = hists_mc['Z'].GetBinError(p+1)

    # save the values
    print values
    savedir = '{0}_{1}'.format(num,denom)
    savename = 'fakeratePtEta'
    fakerateMaker.make2D(savename,values,errors,ptBins,etaBins,savedir=savedir,xaxis=xaxis,yaxis=yaxis)
    savename = 'fakeratePtEta_fromMC'
    fakerateMaker.make2D(savename,values_mc,errors_mc,ptBins,etaBins,savedir=savedir,xaxis=xaxis,yaxis=yaxis)

