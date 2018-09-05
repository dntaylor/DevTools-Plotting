import os
import sys
import logging

from DevTools.Plotter.HistMaker import HistMaker
from DevTools.Plotter.Plotter import Plotter
from copy import deepcopy

import ROOT

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

fakeratePlotter = Plotter(
    'MuMuTauFakeRate',
)

fakerateMaker = HistMaker(
    'MuMuTauFakeRate',
    outputFileName = 'root/MuMuTauFakeRate/fakerates.root',
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

etaBins = [0.,1.479,2.3]
#ptBins = [10,15,20,25,30,50,100]
ptBins = [10,20,50,100]

numDenoms = []
numDenoms_base = [
    ('nearMuonVLoose','nearMuon'),
    ('nearMuonLoose','nearMuon'),
    ('nearMuonMedium','nearMuon'),
    ('nearMuonTight','nearMuon'),
    ('cutbased/nearMuonLoose','nearMuon'),
    ('cutbased/nearMuonMedium','nearMuon'),
    ('cutbased/nearMuonTight','nearMuon'),
]
for n, d in numDenoms_base:
    numDenoms += [(n,d)]
    numDenoms += [('noBVeto/{}'.format(n), 'noBVeto/{}'.format(d))]
for newloose in [-0.8,-0.5]:
    numDenoms += [('nearMuonMedium','nearMuonWithMVA{:0.1f}'.format(newloose))]

name = '{0}/etaBin{1}/tPt'
dmname = '{0}/dm{1}/etaBin{2}/tPt'

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
        if '/' in denom:
            savename = '{0}_{1}'.format(num,denom.split('/')[-1])
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
    if '/' in denom:
        savedir = '{0}_{1}'.format(num,denom.split('/')[-1])
    savename = 'fakeratePtEta'
    fakerateMaker.make2D(savename,values,errors,ptBins,etaBins,savedir=savedir,xaxis=xaxis,yaxis=yaxis)
    savename = 'fakeratePtEta_fromMC'
    fakerateMaker.make2D(savename,values_mc,errors_mc,ptBins,etaBins,savedir=savedir,xaxis=xaxis,yaxis=yaxis)

    for dm in [0,1,10]:
        values = {}
        errors = {}
        values_mc = {}
        errors_mc = {}
        # get the values
        for e in range(len(etaBins)-1):
            # get the histogram
            numname = dmname.format(num,dm,e)
            denomname = dmname.format(denom,dm,e)
            savename = '{0}_{1}_{2}'.format(num,denom,dm)
            if '/' in denom:
                savename = '{0}_{1}_{2}'.format(num,denom.split('/')[-1],dm)
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
        if '/' in denom:
            savedir = '{0}_{1}'.format(num,denom.split('/')[-1])
        savename = 'fakeratePtEta_DM{}'.format(dm)
        fakerateMaker.make2D(savename,values,errors,ptBins,etaBins,savedir=savedir,xaxis=xaxis,yaxis=yaxis)
        savename = 'fakeratePtEta_DM{}_fromMC'.format(dm)
        fakerateMaker.make2D(savename,values_mc,errors_mc,ptBins,etaBins,savedir=savedir,xaxis=xaxis,yaxis=yaxis)


