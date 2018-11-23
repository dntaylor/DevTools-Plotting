import os
import sys

sampleMap = {
    'Z' : [
        'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
        'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
    ],
    'JPsi' : [
        'JpsiToMuMu_JpsiPt8_TuneCUEP8M1_13TeV-pythia8',
    ],
    'Upsilon' : [
        'UpsilonMuMu_UpsilonPt6_TuneCUEP8M1_13TeV-pythia8-evtgen',
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
        'TTJets_SingleLeptFromTbar_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
        'TTJets_SingleLeptFromT_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
    ],
    'WW': [
        'VVTo2L2Nu_13TeV_amcatnloFXFX_madspin_pythia8',
    ],
    'WZ': [
        'WZTo3LNu_TuneCUETP8M1_13TeV-powheg-pythia8',
    ],
    'ZZ': [
        'ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8',
        'ZZTo4L_13TeV-amcatnloFXFX-pythia8',
    ],
    'data' : [
        'SingleMuon',
    ],
}

amasses = ['3p6',4,5,6,7,8,9,10,11,13,15,17,19,21]
hmasses = [125,200,250,300,400,500,750,1000]

for h in hmasses:
    if h==125:
        ggName = 'SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-{a}_TuneCUETP8M1_13TeV_madgraph_pythia8'
        vbfName = 'SUSYVBFToHToAA_AToMuMu_AToTauTau_M-{a}_TuneCUETP8M1_13TeV_madgraph_pythia8'
    else:
        ggName = 'SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-{h}_M-{a}_TuneCUETP8M1_13TeV_madgraph_pythia8'
        vbfName = 'SUSYVBFToHToAA_AToMuMu_AToTauTau_M-{h}_M-{a}_TuneCUETP8M1_13TeV_madgraph_pythia8'
    sigName = 'HToAAH{h}A{a}'
    ggSigName = 'ggHToAAH{h}A{a}'
    vbfSigName = 'vbfHToAAH{h}A{a}'
    for a in amasses:
        sampleMap[sigName.format(h=h,a=a)] = [ggName.format(h=h,a=a), vbfName.format(h=h,a=a)]
        sampleMap[ggSigName.format(h=h,a=a)] = [ggName.format(h=h,a=a)]
        sampleMap[vbfSigName.format(h=h,a=a)] = [vbfName.format(h=h,a=a)]

def getSampleMap():
    return sampleMap
