import os
import json
import sys
import logging
from itertools import product, combinations_with_replacement

from DevTools.Plotter.Counter import Counter
from DevTools.Plotter.higgsUtilities import getChannels, getChannelLabels, getCategories, getCategoryLabels, getSubCategories, getSubCategoryLabels, getGenRecoChannelMap
from copy import deepcopy
import ROOT

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

blind = True

hpp4lCounter = Counter('Hpp4l')

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

sampleCuts = {
    'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8' : '(numGenJets==0 || numGenJets>2)',
    'DY1JetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8': 'numGenJets==1',
    'DY2JetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8': 'numGenJets==2',
    'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8'     : '(numGenJets==0 || numGenJets>4)',
    'DY1JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : 'numGenJets==1',
    'DY2JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : 'numGenJets==2',
    'DY3JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : 'numGenJets==3',
    'DY4JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : 'numGenJets==4',
}

samples = ['TTV','VH','VVV','ZZ']
allsamples = ['W','T','TT','TTVall','Z','WW','VHall','WZ','VVV','ZZall']
signals = ['HppHmm500GeV']

datadrivenSamples = []
for s in samples + ['data']:
    datadrivenSamples += sigMap[s]

genSelection = {
    'ee100': 'genChannel=="eeee"',
    'em100': 'genChannel=="emem"',
    'et100': 'genChannel=="etet"',
    'mm100': 'genChannel=="mmmm"',
    'mt100': 'genChannel=="mtmt"',
    'tt100': 'genChannel=="tttt"',
}

genChanMap = {
    'ee100': 'eeee',
    'em100': 'emem',
    'et100': 'etet',
    'mm100': 'mmmm',
    'mt100': 'mtmt',
    'tt100': 'tttt',
}


for bp in ['ee100','em100','et100','mm100','mt100','tt100']:
    hpp4lCounter.clear()

    for s in allsamples:
        processSampleCuts = {}
        for sample in sigMap[s]:
            if sample in sampleCuts:
                processSampleCuts[sample] = sampleCuts[sample]
        hpp4lCounter.addProcess(s.replace('all',''),sigMap[s],sampleCuts=processSampleCuts)
    
    for signal in signals:
        scales = {}
        for s in sigMap[signal]:
            scales[s] = '({0} ? 36. : 0.)'.format(genSelection[bp])
        hpp4lCounter.addProcess(signal,sigMap[signal],signal=True,scale=scales)
    
    if not blind: hpp4lCounter.addProcess('data',sigMap['data'])
    
    baseSelection = 'hpp1_passMedium==1 && hpp2_passMedium==1 && hmm1_passMedium==1 && hmm2_passMedium==1'
    recoSelection = '(' + ' || '.join(['channel=="{0}"'.format(reco) for chan in genRecoMap[genChanMap[bp]] for reco in chans[chan]]) + ')'
    baseSelection += ' && {0}'.format(recoSelection)
    mcscalefactor = 'hpp1_mediumScale*hpp2_mediumScale*hmm1_mediumScale*hmm2_mediumScale*genWeight*pileupWeight*triggerEfficiency'
    
    hpp4lCounter.printHeader(bp)
    hpp4lCounter.printDivider()
    hpp4lCounter.printCounts('All','none',selection=baseSelection,mcscalefactor=mcscalefactor,doError=True)
    #for cat in sorted(subCatChannels):
    #    for subcat in sorted(subCatChannels[cat]):
    #        recoCut = '(' + ' || '.join(['channel=="{0}"'.format(c) for chan in subCatChannels[cat][subcat] for c in chans[chan]]) + ')'
    #        fullCut = '{0} && {1}'.format(baseSelection,recoCut)
    #        hpp4lCounter.printCounts(' - {0}-{1}'.format(cat,subcat),'none',selection=fullCut,mcscalefactor=mcscalefactor,doError=True)
    for chan in sorted(chans):
        if chan not in genRecoMap[genChanMap[bp]]: continue
        recoCut = '(' + ' || '.join(['channel=="{0}"'.format(c) for c in chans[chan]]) + ')'
        fullCut = '{0} && {1}'.format(baseSelection,recoCut)
        hpp4lCounter.printCounts(' - {0}'.format(chan),'none',selection=fullCut,mcscalefactor=mcscalefactor,doError=True)
