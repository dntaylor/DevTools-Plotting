import os
import sys
import logging

from DevTools.Plotter.HistMaker import HistMaker
from DevTools.Plotter.Plotter import Plotter
from copy import deepcopy

import ROOT

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

fakeratePlotter = Plotter(
    'WTauFakeRate',
)

fakerateMaker = HistMaker(
    'WTauFakeRate',
    outputFileName = 'root/WTauFakeRate/fakerates.root',
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
             #'DY1JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             #'DY2JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             #'DY3JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
             #'DY4JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
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
             'ST_s-channel_4f_leptonDecays_13TeV-amcatnlo-pythia8_TuneCUETP8M1',
             'ST_t-channel_antitop_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1',
             #'ST_t-channel_antitop_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV-powhegV2-madspin',
             'ST_t-channel_top_4f_inclusiveDecays_13TeV-powhegV2-madspin-pythia8_TuneCUETP8M1',
             #'ST_t-channel_top_4f_inclusiveDecays_TuneCUETP8M2T4_13TeV-powhegV2-madspin',
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
             #'DoubleMuon',
             #'DoubleEG',
             #'MuonEG',
             'SingleMuon',
             #'SingleElectron',
             #'Tau',
            ],
}

samples = ['T','TT','Z','WW']

allSamplesDict = {'MC':[]}

for s in samples:
    allSamplesDict['MC'] += sigMap[s]

fakeratePlotter.addHistogram('MC',allSamplesDict['MC'])
fakeratePlotter.addHistogram('W',sigMap['W'])
fakeratePlotter.addHistogram('data',sigMap['data'],style={'linecolor':ROOT.kBlack,'name':'Corrected'})
fakeratePlotter.addHistogram('data_uncorrected',sigMap['data'],style={'linecolor':ROOT.kRed,'name':'Uncorrected'})

etaBins = [0.,1.479,2.3]
ptBins = [0,20,25,30,40,50,60,100]

numDenom = [('medium','loose'),('tight','loose'),('tight','medium'),('medium','newloose'),('tight','newloose'),]

numdms = {
    0: [0,5],
    1: [1,6],
    10: [10],
}

for num,denom in numDenom:
    xaxis = 'p_{T}^{#tau}'
    yaxis = '|#eta^{#tau}|'
    values = {}
    errors = {}
    values_mc = {}
    errors_mc = {}
    values_dm = {}
    errors_dm = {}
    values_dm_mc = {}
    errors_dm_mc = {}
    for ndm in numdms:
        values_dm[ndm] = {}
        errors_dm[ndm] = {}
        values_dm_mc[ndm] = {}
        errors_dm_mc[ndm] = {}
    # get the values
    for e in range(len(etaBins)-1):
        # get the histogram
        numname = '{0}/all/etaBin{1}/tPt'.format(num,e)
        denomname = '{0}/all/etaBin{1}/tPt'.format(denom,e)
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
        customOrder = ['W']
        hists_mc = fakeratePlotter.plotRatio(numname,denomname,savename,customOrder=customOrder,rebin=ptBins,getHists=True)
        for p in range(len(ptBins)-1):
            pt = float(ptBins[p]+ptBins[p+1])/2.
            eta = float(etaBins[e]+etaBins[e+1])/2.
            key = (pt,eta)
            values_mc[key] = hists_mc['W'].GetBinContent(p+1)
            errors_mc[key] = hists_mc['W'].GetBinError(p+1)

        # now decay modes
        for ndm in numdms:
            numname = '{0}/all/etaBin{1}/dm{2}/tPt'.format(num,e,ndm)
            denomname = ['{0}/all/etaBin{1}/dm{2}/tPt'.format(denom,e,ddm) for ddm in numdms[ndm]]
            savename = '{0}_{1}_{2}_{3}'.format(num,denom,ndm,e)
            subtractMap = {
                'data': ['MC'],
            }
            customOrder = ['data']
            hists = fakeratePlotter.plotRatio(numname,denomname,savename,customOrder=customOrder,subtractMap=subtractMap,rebin=ptBins,getHists=True)
            for p in range(len(ptBins)-1):
                pt = float(ptBins[p]+ptBins[p+1])/2.
                eta = float(etaBins[e]+etaBins[e+1])/2.
                key = (pt,eta)
                values_dm[ndm][key] = hists['data'].GetBinContent(p+1)
                errors_dm[ndm][key] = hists['data'].GetBinError(p+1)
            customOrder = ['W']
            hists_mc = fakeratePlotter.plotRatio(numname,denomname,savename,customOrder=customOrder,rebin=ptBins,getHists=True)
            for p in range(len(ptBins)-1):
                pt = float(ptBins[p]+ptBins[p+1])/2.
                eta = float(etaBins[e]+etaBins[e+1])/2.
                key = (pt,eta)
                values_dm_mc[ndm][key] = hists_mc['W'].GetBinContent(p+1)
                errors_dm_mc[ndm][key] = hists_mc['W'].GetBinError(p+1)
    # save the values
    print values
    savedir = '{0}_{1}'.format(num,denom)
    savename = 'fakeratePtEta'
    fakerateMaker.make2D(savename,values,errors,ptBins,etaBins,savedir=savedir,xaxis=xaxis,yaxis=yaxis)
    savename = 'fakeratePtEta_fromMC'
    fakerateMaker.make2D(savename,values_mc,errors_mc,ptBins,etaBins,savedir=savedir,xaxis=xaxis,yaxis=yaxis)
    for ndm in numdms:
        print values_dm[ndm]
        savename = 'fakeratePtEtaDM{0}'.format(ndm)
        fakerateMaker.make2D(savename,values_dm[ndm],errors_dm[ndm],ptBins,etaBins,savedir=savedir,xaxis=xaxis,yaxis=yaxis)
        savename = 'fakeratePtEtaDM{0}_fromMC'.format(ndm)
        fakerateMaker.make2D(savename,values_dm_mc[ndm],errors_dm_mc[ndm],ptBins,etaBins,savedir=savedir,xaxis=xaxis,yaxis=yaxis)

