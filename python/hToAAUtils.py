import os
import json
import sys
import logging
from itertools import product, combinations_with_replacement

from DevTools.Utilities.utilities import ZMASS, getCMSSWVersion
from copy import deepcopy
import ROOT

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

version = getCMSSWVersion()

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
        'WZTo3LNu_TuneCUETP8M1_13TeV-powheg-pythia8',
    ],
    'ZZ': [
        'ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8',
        'ZZTo4L_13TeV-amcatnloFXFX-pythia8',
    ],
    'HToAAH125A5'  : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-5_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH125A7'  : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-7_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH125A9'  : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-9_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH125A11' : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-11_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH125A13' : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-13_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH125A15' : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-15_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH125A17' : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-17_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH125A19' : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-19_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH125A21' : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-21_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH300A5'  : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-300_M-5_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH300A7'  : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-300_M-7_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH300A9'  : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-300_M-9_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH300A11' : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-300_M-11_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH300A13' : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-300_M-13_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH300A15' : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-300_M-15_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH300A17' : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-300_M-17_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH300A19' : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-300_M-19_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH300A21' : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-300_M-21_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH750A5'  : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-750_M-5_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH750A7'  : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-750_M-7_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH750A9'  : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-750_M-9_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH750A11' : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-750_M-11_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH750A13' : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-750_M-13_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH750A15' : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-750_M-15_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH750A17' : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-750_M-17_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH750A19' : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-750_M-19_TuneCUETP8M1_13TeV_madgraph_pythia8'],
    'HToAAH750A21' : ['SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-750_M-21_TuneCUETP8M1_13TeV_madgraph_pythia8'],
}

def getSampleMap():
    return sigMap
