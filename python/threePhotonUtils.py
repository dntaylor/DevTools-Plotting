import os
import sys

sampleMap = {
    'Z': [
        'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
        'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
    ],
    'W': [
        'WJetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
    ],
    'ZG': [
        'ZGTo2LG_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
        'WGToLNuG_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
    ],
    'TT': [
        'TTJets_DiLept_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
        'TTJets_SingleLeptFromT_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
        'TTJets_SingleLeptFromTbar_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
    ],
    'GG': [
        'DiPhotonJetsBox_M40_80-Sherpa',
        'DiPhotonJetsBox_MGG-80toInf_13TeV-Sherpa',
        #'DiPhotonJets_MGG-80toInf_13TeV_amcatnloFXFX_pythia8',
    ],
    'SHERPA': [
        'DiPhotonJetsBox_M40_80-Sherpa',
        'DiPhotonJetsBox_MGG-80toInf_13TeV-Sherpa',
    ],
    'AMCATNLO': [
        'DiPhotonJets_MGG-80toInf_13TeV_amcatnloFXFX_pythia8',
    ],
    'TTG': [
        'TTGG_0Jets_TuneCUETP8M1_13TeV_amcatnlo_madspin_pythia8',
        'TTGJets_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8',
        'TGJets_TuneCUETP8M1_13TeV_amcatnlo_madspin_pythia8',
    ],
    'VVG': [
        'WGG_5f_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
        'WWG_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
        'WZG_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
        'ZGGToLLGG_5f_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
        'ZGGToNuNuGG_5f_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
    ],
    'G': [
        'GJet_Pt-20to40_DoubleEMEnriched_MGG-80toInf_TuneCUETP8M1_13TeV_Pythia8',
        'GJet_Pt-20toInf_DoubleEMEnriched_MGG-40to80_TuneCUETP8M1_13TeV_Pythia8',
        'GJet_Pt-40toInf_DoubleEMEnriched_MGG-80toInf_TuneCUETP8M1_13TeV_Pythia8',
    ],
    'QCD': [
        'QCD_Pt-40toInf_DoubleEMEnriched_MGG-80toInf_TuneCUETP8M1_13TeV_Pythia8',
        'QCD_Pt-30toInf_DoubleEMEnriched_MGG-40to80_TuneCUETP8M1_13TeV_Pythia8',
        'QCD_Pt-30to40_DoubleEMEnriched_MGG-80toInf_TuneCUETP8M1_13TeV_Pythia8',
    ],
    'data': [
        'DoubleEG',
        #'SinglePhoton',
    ],
    'HToAG_250_1': [
        'HToAGmToGmGmGm_M-250_MA-1_TuneCUETP8M1_13TeV_pythia8',
    ],
    'HToAG_250_30': [
        'HToAGmToGmGmGm_M-250_MA-30_TuneCUETP8M1_13TeV_pythia8',
    ],
    'HToAG_250_150': [
        'HToAGmToGmGmGm_M-250_MA-150_TuneCUETP8M1_13TeV_pythia8',
    ],
}


def getSampleMap():
    return sampleMap
