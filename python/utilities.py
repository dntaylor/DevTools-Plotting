# common utilities for plotting
import os
import sys
import hashlib
import glob
import logging

from DevTools.Utilities.utilities import python_mkdir, ZMASS, getCMSSWVersion
from DevTools.Utilities.hdfsUtils import get_hdfs_root_files

CMSSW_BASE = os.environ['CMSSW_BASE']

def hashFile(*filenames,**kwargs):
    BUFFSIZE = kwargs.pop('BUFFSIZE',65536)
    hasher = hashlib.md5()
    for filename in filenames:
        with open(filename,'rb') as f:
            buff = f.read(BUFFSIZE)
            while len(buff)>0:
                hasher.update(buff)
                buff = f.read(BUFFSIZE)
    return hasher.hexdigest()

def hashString(*strings):
    hasher = hashlib.md5()
    for string in strings:
        hasher.update(string)
    return hasher.hexdigest()



def isData(sample):
    '''Test if sample is data'''
    dataSamples = ['DoubleMuon','DoubleEG','MuonEG','SingleMuon','SingleElectron','Tau']
    return sample in dataSamples

runMap = {
    'Run2016B': 5788.,
    'Run2016C': 2573.,
    'Run2016D': 4248.,
    'Run2016E': 4009.,
    'Run2016F': 3102.,
    'Run2016G': 7540.,
    'Run2016H': 8606.,
    'Run2017B': 4792.,
    'Run2017C': 9755.,
    'Run2017D': 4319.,
    'Run2017E': 9424.,
    'Run2017F':13500.,
}

runRange = {
    'Run2016B': [272760,275344],
    'Run2016C': [275656,276283],
    'Run2016D': [276315,276811],
    'Run2016E': [276831,277420],
    'Run2016F': [277932,278808],
    'Run2016G': [278820,280385],
    'Run2016H': [281613,284044],
    'Run2017B': [297046,299329],
    'Run2017C': [299368,300676],
    'Run2017D': [302030,303434],
    'Run2017E': [303824,304797],
    'Run2017F': [305040,306462],
}

def getLumi(version=getCMSSWVersion(),run=''):
    '''Get the integrated luminosity to scale monte carlo'''
    if run in runMap:
        return runMap[run]
    if version=='76X':
        #return 2263 # december jamboree golden json
        return 2318 # moriond golden json
    elif version=='80X':
        #return 12892.762 # ichep dataset golden json
        return 35867.060 # full 2016 for moriond
    elif version=='94X':
        return 41370
    else:
        return 0

def getRunRange(version=getCMSSWVersion(),run=''):
    if run in runRange:
        return runRange[run]
    return [0,999999]

latestNtuples = {}
latestNtuples['76X'] = {
    'Charge'         : '2016-04-23_ChargeAnalysis_v1-merge',
    'DY'             : '2016-05-02_DYAnalysis_v1-merge',
    'DijetFakeRate'  : '',
    'Electron'       : '2016-04-14_ElectronAnalysis_v1-merge',
    'Hpp3l'          : '2016-10-16_Hpp3lAnalysis_76X_v1-merge',
    'Hpp4l'          : '2016-10-16_Hpp4lAnalysis_76X_v1-merge',
    'Muon'           : '2016-04-14_MuonAnalysis_v1-merge',
    'SingleElectron' : '',
    'SingleMuon'     : '',
    'Tau'            : '2016-05-11_TauAnalysis_v1-merge',
    'TauCharge'      : '',
    'WTauFakeRate'   : '',
    'WFakeRate'      : '',
    'WZ'             : '2016-04-29_WZAnalysis_v1-merge',
}
latestNtuples['80X'] = {
# ICHEP 2016
#    'Charge'         : '2016-11-28_ChargeAnalysis_80X_v1-merge',
#    'DY'             : '2016-09-27_DYAnalysis_80X_v1-merge',
#    'DijetFakeRate'  : '2016-11-03_DijetFakeRateAnalysis_80X_v4-merge', # hpp ids
#    'Hpp3l'          : '2016-12-19_Hpp3lAnalysis_80X_v1-merge',
#    'Hpp4l'          : '2016-12-19_Hpp4lAnalysis_80X_v1-merge',
#    'Electron'       : '2016-06-25_ElectronAnalysis_80X_v1-merge',
#    'Muon'           : '2016-06-25_MuonAnalysis_80X_v1-merge',
#    'Tau'            : '2016-07-06_TauAnalysis_80X_v1-merge',
#    'TauCharge'      : '2016-07-24_TauChargeAnalysis_80X_v1-merge',
#    'WTauFakeRate'   : '2016-07-24_WTauFakeRateAnalysis_80X_v1-merge',
#    'WFakeRate'      : '2016-07-24_WFakeRateAnalysis_80X_v1-merge',
#    'ZFakeRate'      : '2016-07-24_ZFakeRateAnalysis_80X_v1-merge',
#    'WZ'             : '2016-11-27_WZAnalysis_80X_v1-merge',
#    'ZZ'             : '2016-08-08_ZZAnalysis_80X_v1-merge',
#    'ThreeLepton'    : '2017-01-05_ThreeLeptonAnalysis_80X_v1-merge',
# Moriond 2017
    'Tau'            : '2017-03-30_TauAnalysis_80X_Moriond_v1-merge',
    'Charge'         : '2018-08-22_ChargeAnalysis_80X_Moriond_v1-merge',
    'DY'             : '2018-01-09_DYAnalysis_80X_Moriond_v1-merge', # fix metFilter
    #'ModDY'          : '2018-10-03_ModDYAnalysis_80X_Moriond_v2-merge', # miniaod
    'ModDY'          : '2018-12-03_ModDYAnalysis_80X_ZSkim_v1-merge', # zskim
    'DijetFakeRate'  : '2018-01-09_DijetFakeRateAnalysis_80X_Moriond_v1-merge', # fix metFilter
    'ZFakeRate'      : '2017-03-21_ZFakeRateAnalysis_80X_Moriond_v1-merge',
    'WFakeRate'      : '2017-03-24_WFakeRateAnalysis_80X_Moriond_v1-merge',
    'WTauFakeRate'   : '2018-01-10_WTauFakeRateAnalysis_80X_Moriond_v2-merge', # new DMs, fix t dz, fix metFilter
    #'ZTauFakeRate'   : '2018-01-10_ZTauFakeRateAnalysis_80X_Moriond_v2-merge', # new DMs, fix t dz, fix metFilter
    'ZTauFakeRate'   : '2018-09-21_ZTauFakeRateAnalysis_80X_Moriond_v1-merge', # new DMs, fix t dz, fix metFilter add bveto
    'WZ'             : '2017-06-29_WZAnalysis_80X_Moriond_v1-merge',
    'Hpp3l'          : '2018-07-20_Hpp3lAnalysis_80X_Moriond_v1-merge', # new DMs, fix t dz, fix metFilter, add tau trig
    'Hpp4l'          : '2018-07-20_Hpp4lAnalysis_80X_Moriond_v1-merge', # new DMs, fix t dz, fix metFilter, add tau trig
# Photon
    'FourPhoton'     : '2017-06-20_FourPhotonAnalysis_80X_Photon_v2-merge',
    'ThreePhoton'    : '2017-09-15_ThreePhotonAnalysis_80X_Photon_v1-merge',
    'TwoPhoton'      : '2017-06-21_TwoPhotonAnalysis_80X_Photon_v1-merge',
    'EG'             : '2017-09-27_EGAnalysis_80X_Photon_v1-merge',
    'DYGG'           : '2017-06-22_DYGGAnalysis_80X_Photon_v1-merge',
    'MMG'            : '2017-08-03_MMGAnalysis_80X_Photon_v1-merge',
    'LLG'            : '2017-08-23_LLGAnalysis_80X_Photon_v1-merge',
    'SingleJet'      : '2017-07-18_SingleJetAnalysis_80X_QCD_v1-merge',
# MuMuTauTau
    'MuMu'           : '2018-08-22_MuMuAnalysis_80X_v1-merge',
    #'MuMuTauTau'     : '2018-10-10_MuMuTauTauAnalysis_80X_v1-merge',
    'MuMuTauTau'     : '2018-11-28_MuMuTauTauAnalysis_80X_v1-merge',
    'MuMuTauTauMod'  : '2018-12-03_MuMuTauTauModAnalysis_80X_trigOnly_v1-merge',
    'MuMuTauTauModMC': '2018-12-03_MuMuTauTauModAnalysis_80X_trigOnlyMC_v1-merge',
    'MuMuTauFakeRate': '2018-03-19_MuMuTauFakeRateAnalysis_80X_v2-merge',
    'MuMuMuFakeRate' : '2018-02-09_MuMuMuFakeRateAnalysis_80X_v1-merge',
}
latestNtuples['94X'] = {
    'MonoHZZ'        : '2019-01-23_MonoHZZAnalysis_94X_v2',
    'MonoHZZFakeRate': '2019-01-23_MonoHZZFakeRateAnalysis_94X_v2',
}

latestShifts = {}
latestShifts['80X'] = {}
latestShifts['80X']['Hpp3l'] = {
# ICHEP 2016
#    'ElectronEnUp'     : '2016-12-19_Hpp3lAnalysis_ElectronEnUp_80X_v1-merge',
#    'ElectronEnDown'   : '2016-12-19_Hpp3lAnalysis_ElectronEnDown_80X_v1-merge',
#    'MuonEnUp'         : '2016-12-19_Hpp3lAnalysis_MuonEnUp_80X_v1-merge',
#    'MuonEnDown'       : '2016-12-19_Hpp3lAnalysis_MuonEnDown_80X_v1-merge',
#    'TauEnUp'          : '2016-12-19_Hpp3lAnalysis_TauEnUp_80X_v1-merge',
#    'TauEnDown'        : '2016-12-19_Hpp3lAnalysis_TauEnDown_80X_v1-merge',
#    'JetEnUp'          : '2016-12-19_Hpp3lAnalysis_JetEnUp_80X_v1-merge',
#    'JetEnDown'        : '2016-12-19_Hpp3lAnalysis_JetEnDown_80X_v1-merge',
#    'JetResUp'         : '2016-12-19_Hpp3lAnalysis_JetResUp_80X_v1-merge',
#    'JetResDown'       : '2016-12-19_Hpp3lAnalysis_JetResDown_80X_v1-merge',
#    'UnclusteredEnUp'  : '2016-12-19_Hpp3lAnalysis_UnclusteredEnUp_80X_v1-merge',
#    'UnclusteredEnDown': '2016-12-19_Hpp3lAnalysis_UnclusteredEnDown_80X_v1-merge',
# Moriond 2017
    'ElectronEnUp'     : '2018-07-20_Hpp3lAnalysis_ElectronEnUp_80X_Moriond_v1-merge',
    'ElectronEnDown'   : '2018-07-20_Hpp3lAnalysis_ElectronEnDown_80X_Moriond_v1-merge',
    'MuonEnUp'         : '2018-07-20_Hpp3lAnalysis_MuonEnUp_80X_Moriond_v1-merge',
    'MuonEnDown'       : '2018-07-20_Hpp3lAnalysis_MuonEnDown_80X_Moriond_v1-merge',
    'TauEnUp'          : '2018-07-20_Hpp3lAnalysis_TauEnUp_80X_Moriond_v1-merge',
    'TauEnDown'        : '2018-07-20_Hpp3lAnalysis_TauEnDown_80X_Moriond_v1-merge',
    'JetEnUp'          : '2018-07-20_Hpp3lAnalysis_JetEnUp_80X_Moriond_v1-merge',
    'JetEnDown'        : '2018-07-20_Hpp3lAnalysis_JetEnDown_80X_Moriond_v1-merge',
    'JetResUp'         : '2018-07-20_Hpp3lAnalysis_JetResUp_80X_Moriond_v1-merge',
    'JetResDown'       : '2018-07-20_Hpp3lAnalysis_JetResDown_80X_Moriond_v1-merge',
    'UnclusteredEnUp'  : '2018-07-20_Hpp3lAnalysis_UnclusteredUp_80X_Moriond_v1-merge',
    'UnclusteredEnDown': '2018-07-20_Hpp3lAnalysis_UnclusteredDown_80X_Moriond_v1-merge',
}
latestShifts['80X']['Hpp4l'] = {
# ICHEP 2016
#    'ElectronEnUp'     : '2016-12-19_Hpp4lAnalysis_ElectronEnUp_80X_v1-merge',
#    'ElectronEnDown'   : '2016-12-19_Hpp4lAnalysis_ElectronEnDown_80X_v1-merge',
#    'MuonEnUp'         : '2016-12-19_Hpp4lAnalysis_MuonEnUp_80X_v1-merge',
#    'MuonEnDown'       : '2016-12-19_Hpp4lAnalysis_MuonEnDown_80X_v1-merge',
#    'TauEnUp'          : '2016-12-19_Hpp4lAnalysis_TauEnUp_80X_v1-merge',
#    'TauEnDown'        : '2016-12-19_Hpp4lAnalysis_TauEnDown_80X_v1-merge',
#    'JetEnUp'          : '2016-12-19_Hpp4lAnalysis_JetEnUp_80X_v1-merge',
#    'JetEnDown'        : '2016-12-19_Hpp4lAnalysis_JetEnDown_80X_v1-merge',
#    'JetResUp'         : '2016-12-19_Hpp4lAnalysis_JetResUp_80X_v1-merge',
#    'JetResDown'       : '2016-12-19_Hpp4lAnalysis_JetResDown_80X_v1-merge',
#    'UnclusteredEnUp'  : '2016-12-19_Hpp4lAnalysis_UnclusteredEnUp_80X_v1-merge',
#    'UnclusteredEnDown': '2016-12-19_Hpp4lAnalysis_UnclusteredEnDown_80X_v1-merge',
# Moriond 2017
    'ElectronEnUp'     : '2018-07-20_Hpp4lAnalysis_ElectronEnUp_80X_Moriond_v1-merge',
    'ElectronEnDown'   : '2018-07-20_Hpp4lAnalysis_ElectronEnDown_80X_Moriond_v1-merge',
    'MuonEnUp'         : '2018-07-20_Hpp4lAnalysis_MuonEnUp_80X_Moriond_v1-merge',
    'MuonEnDown'       : '2018-07-20_Hpp4lAnalysis_MuonEnDown_80X_Moriond_v1-merge',
    'TauEnUp'          : '2018-07-20_Hpp4lAnalysis_TauEnUp_80X_Moriond_v1-merge',
    'TauEnDown'        : '2018-07-20_Hpp4lAnalysis_TauEnDown_80X_Moriond_v1-merge',
    'JetEnUp'          : '2018-07-20_Hpp4lAnalysis_JetEnUp_80X_Moriond_v1-merge',
    'JetEnDown'        : '2018-07-20_Hpp4lAnalysis_JetEnDown_80X_Moriond_v1-merge',
    'JetResUp'         : '2018-07-20_Hpp4lAnalysis_JetResUp_80X_Moriond_v1-merge',
    'JetResDown'       : '2018-07-20_Hpp4lAnalysis_JetResDown_80X_Moriond_v1-merge',
    'UnclusteredEnUp'  : '2018-07-20_Hpp4lAnalysis_UnclusteredUp_80X_Moriond_v1-merge',
    'UnclusteredEnDown': '2018-07-20_Hpp4lAnalysis_UnclusteredDown_80X_Moriond_v1-merge',
}
latestShifts['80X']['MuMuTauTau'] = {
# Moriond 2017
    #'ElectronEnUp'     : '2018-09-04_MuMuTauTauAnalysis_ElectronEnUp_80X_v1-merge',
    #'ElectronEnDown'   : '2018-09-04_MuMuTauTauAnalysis_ElectronEnDown_80X_v1-merge',
    'MuonEnUp'         : '2018-11-28_MuMuTauTauAnalysis_MuonEnUp_80X_v1-merge',
    'MuonEnDown'       : '2018-11-28_MuMuTauTauAnalysis_MuonEnDown_80X_v1-merge',
    'TauEnUp'          : '2018-11-28_MuMuTauTauAnalysis_TauEnUp_80X_v1-merge',
    'TauEnDown'        : '2018-11-28_MuMuTauTauAnalysis_TauEnDown_80X_v1-merge',
    #'JetEnUp'          : '2018-09-04_MuMuTauTauAnalysis_JetEnUp_80X_v1-merge',
    #'JetEnDown'        : '2018-09-04_MuMuTauTauAnalysis_JetEnDown_80X_v1-merge',
    #'JetResUp'         : '2018-09-04_MuMuTauTauAnalysis_JetResUp_80X_v1-merge',
    #'JetResDown'       : '2018-09-04_MuMuTauTauAnalysis_JetResDown_80X_v1-merge',
    #'UnclusteredEnUp'  : '2018-09-04_MuMuTauTauAnalysis_UnclusteredEnUp_80X_v1-merge',
    #'UnclusteredEnDown': '2018-09-04_MuMuTauTauAnalysis_UnclusteredEnDown_80X_v1-merge',
}

def getNtupleDirectory(analysis,local=False,version=getCMSSWVersion(),shift=''):
    # first grab the local one
    if local:
        #ntupleDir = '{0}/src/ntuples/{0}'.format(CMSSW_BASE,analysis)
        ntupleDir = 'ntuples/{0}'.format(analysis)
        if os.path.exists(ntupleDir):
            return ntupleDir
    # if not read from hdfs
    baseDir = '/hdfs/store/user/dntaylor'
    if shift and analysis in latestShifts[version] and shift in latestShifts[version][analysis]:
        return os.path.join(baseDir,latestShifts[version][analysis][shift])
    if analysis in latestNtuples[version] and latestNtuples[version][analysis]:
        return os.path.join(baseDir,latestNtuples[version][analysis])

def getTestFiles(analysis,sample,n=1,version=None):
    if not version: version = getCMSSWVersion()

    sampleMap = {
        'wz'    : 'WZTo3LNu_TuneCUETP8M1_13TeV-powheg-pythia8',
        'zz'    : 'ZZTo4L_13TeV_powheg_pythia8',
        'data'  : 'DoubleMuon',
        'hpp'   : 'HPlusPlusHMinusMinusHTo4L_M-500_13TeV-pythia8' if version=='76X' else 'HPlusPlusHMinusMinusHTo4L_M-500_TuneCUETP8M1_13TeV_pythia8',
        'hpp4l' : 'HPlusPlusHMinusMinusHTo4L_M-500_13TeV-pythia8' if version=='76X' else 'HPlusPlusHMinusMinusHTo4L_M-500_TuneCUETP8M1_13TeV_pythia8',
        'hppr4l': 'HPlusPlusHMinusMinusHRTo4L_M-500_13TeV-pythia8' if version=='76X' else 'HPlusPlusHMinusMinusHRTo4L_M-500_TuneCUETP8M1_13TeV-pythia8',
        'hpp3l' : 'HPlusPlusHMinusHTo3L_M-500_TuneCUETP8M1_13TeV_calchep-pythia8' if version=='76X' else 'HPlusPlusHMinusHTo3L_M-500_13TeV-calchep-pythia8',
        'haa'   : 'SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-15_TuneCUETP8M1_13TeV_madgraph_pythia8',
        #'dy'    : 'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
        'dy'    : 'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
        'w'     : 'WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
        'qcd'   : 'QCD_Pt_300to470_TuneCUETP8M1_13TeV_pythia8',
        'SingleMuon'    : 'SingleMuon',
        'SingleElectron': 'SingleElectron',
        'DoubleMuon'    : 'DoubleMuon',
        'DoubleEG'      : 'DoubleEG',
        'MuonEG'        : 'MuonEG',
        'Tau'           : 'Tau',
    }

    if sample not in sampleMap: return []

    files = get_hdfs_root_files('{0}/{1}'.format(getNtupleDirectory(analysis,version=version),sampleMap[sample]))

    return files[:min(n,len(files))]

latestHistograms = {'80X':{}}

latestHistograms['80X']['MuMuTauTau'] = {
    'MuonEnUp'         : '2018-12-05_MuMuTauTauHistogramsNew_MuonEnUp_80X_Moriond_v1',
    'MuonEnDown'       : '2018-12-05_MuMuTauTauHistogramsNew_MuonEnDown_80X_Moriond_v1',
    'TauEnUp'          : '2018-12-05_MuMuTauTauHistogramsNew_TauEnUp_80X_Moriond_v1',
    'TauEnDown'        : '2018-12-05_MuMuTauTauHistogramsNew_TauEnDown_80X_Moriond_v1',
    'lepUp'            : '2018-12-05_MuMuTauTauHistogramsNew_lepUp_80X_Moriond_v1',
    'lepDown'          : '2018-12-05_MuMuTauTauHistogramsNew_lepDown_80X_Moriond_v1',
    'trigUp'           : '2018-12-05_MuMuTauTauHistogramsNew_trigUp_80X_Moriond_v1',
    'trigDown'         : '2018-12-05_MuMuTauTauHistogramsNew_trigDown_80X_Moriond_v1',
    'puUp'             : '2018-12-05_MuMuTauTauHistogramsNew_puUp_80X_Moriond_v1',
    'puDown'           : '2018-12-05_MuMuTauTauHistogramsNew_puDown_80X_Moriond_v1',
    'fakeUp'           : '2018-12-05_MuMuTauTauHistogramsNew_fakeUp_80X_Moriond_v1',
    'fakeDown'         : '2018-12-05_MuMuTauTauHistogramsNew_fakeDown_80X_Moriond_v1',
    'btagUp'           : '2018-12-05_MuMuTauTauHistogramsNew_btagUp_80X_Moriond_v1',
    'btagDown'         : '2018-12-05_MuMuTauTauHistogramsNew_btagDown_80X_Moriond_v1',
    'tauUp'            : '2018-12-05_MuMuTauTauHistogramsNew_tauUp_80X_Moriond_v1',
    'tauDown'          : '2018-12-05_MuMuTauTauHistogramsNew_tauDown_80X_Moriond_v1',
    'muR1.0muF1.0'     : '2018-12-05_MuMuTauTauHistogramsNew_muR1.0muF1.0_80X_Moriond_v1',
    'muR1.0muF2.0'     : '2018-12-05_MuMuTauTauHistogramsNew_muR1.0muF2.0_80X_Moriond_v1',
    'muR1.0muF0.5'     : '2018-12-05_MuMuTauTauHistogramsNew_muR1.0muF0.5_80X_Moriond_v1',
    'muR2.0muF1.0'     : '2018-12-05_MuMuTauTauHistogramsNew_muR2.0muF1.0_80X_Moriond_v1',
    'muR2.0muF2.0'     : '2018-12-05_MuMuTauTauHistogramsNew_muR2.0muF2.0_80X_Moriond_v1',
    'muR2.0muF0.5'     : '2018-12-05_MuMuTauTauHistogramsNew_muR2.0muF0.5_80X_Moriond_v1',
    'muR0.5muF1.0'     : '2018-12-05_MuMuTauTauHistogramsNew_muR0.5muF1.0_80X_Moriond_v1',
    'muR0.5muF2.0'     : '2018-12-05_MuMuTauTauHistogramsNew_muR0.5muF2.0_80X_Moriond_v1',
    'muR0.5muF0.5'     : '2018-12-05_MuMuTauTauHistogramsNew_muR0.5muF0.5_80X_Moriond_v1',
}

def getNewFlatHistograms(analysis,sample,version=getCMSSWVersion(),shift='',base='newflat'):
    return getFlatHistograms(analysis,sample,version,shift,base)

def getNewProjectionHistograms(analysis,sample,version=getCMSSWVersion(),shift='',base='newflat'):
    #return getProjectionHistograms(analysis,sample,version,shift,base)
    return 'dummy.root'
        
def getFlatHistograms(analysis,sample,version=getCMSSWVersion(),shift='',base='flat'):
    flat = '{}/{}/{}.root'.format(base,analysis,sample)
    if shift in latestHistograms.get(version,{}).get(analysis,{}):
        baseDir = '/hdfs/store/user/dntaylor'
        flatpath = os.path.join(baseDir,latestHistograms[version][analysis][shift],sample)
        for fname in glob.glob('{0}/*.root'.format(flatpath)):
            if 'projection' not in fname: flat = fname
    elif shift:
        logging.warning('Shift {} provided but not found'.format(shift))
        flat = 'dummy.root'
    return flat
        
def getProjectionHistograms(analysis,sample,version=getCMSSWVersion(),shift='',base='projections'):
    proj = '{}/{}/{}.root'.format(base,analysis,sample)
    if shift in latestHistograms.get(version,{}).get(analysis,{}):
        baseDir = '/hdfs/store/user/dntaylor'
        projpath = os.path.join(baseDir,latestHistograms[version][analysis][shift],sample)
        for fname in glob.glob('{0}/*.root'.format(projpath)):
            if 'projection' in fname: proj = fname
    elif shift:
        logging.warning('Shift {} provided but not found'.format(shift))
        proj = 'dummy.root'
    return proj
        
latestSkims = {}
latestSkims['80X'] = {}
latestSkims['80X']['Hpp3l'] = {
# ICHEP 2016
#    #''                 : '2016-12-21_Hpp3lSkims_80X_v1',
#    'ElectronEnUp'     : '2016-12-21_Hpp3lSkims_ElectronEnUp_80X_v1',
#    'ElectronEnDown'   : '2016-12-21_Hpp3lSkims_ElectronEnDown_80X_v1',
#    'MuonEnUp'         : '2016-12-21_Hpp3lSkims_MuonEnUp_80X_v1',
#    'MuonEnDown'       : '2016-12-21_Hpp3lSkims_MuonEnDown_80X_v1',
#    'TauEnUp'          : '2016-12-21_Hpp3lSkims_TauEnUp_80X_v1',
#    'TauEnDown'        : '2016-12-21_Hpp3lSkims_TauEnDown_80X_v1',
#    'JetEnUp'          : '2016-12-21_Hpp3lSkims_JetEnUp_80X_v1',
#    'JetEnDown'        : '2016-12-21_Hpp3lSkims_JetEnDown_80X_v1',
#    'JetResUp'         : '2016-12-21_Hpp3lSkims_JetResUp_80X_v1',
#    'JetResDown'       : '2016-12-21_Hpp3lSkims_JetResDown_80X_v1',
#    'UnclusteredEnUp'  : '2016-12-21_Hpp3lSkims_UnclusteredEnUp_80X_v1',
#    'UnclusteredEnDown': '2016-12-21_Hpp3lSkims_UnclusteredEnDown_80X_v1',
#    'lepUp'            : '2016-12-21_Hpp3lSkims_lepUp_80X_v1',
#    'lepDown'          : '2016-12-21_Hpp3lSkims_lepDown_80X_v1',
#    'trigUp'           : '2016-12-21_Hpp3lSkims_trigUp_80X_v1',
#    'trigDown'         : '2016-12-21_Hpp3lSkims_trigDown_80X_v1',
#    'puUp'             : '2016-12-21_Hpp3lSkims_puUp_80X_v1',
#    'puDown'           : '2016-12-21_Hpp3lSkims_puDown_80X_v1',
#    'fakeUp'           : '2016-12-21_Hpp3lSkims_fakeUp_80X_v1',
#    'fakeDown'         : '2016-12-21_Hpp3lSkims_fakeDown_80X_v1',
# Moriond 2017
    #''                 : '2017-05-01_Hpp3lSkims_80X_v1',
    'ElectronEnUp'     : '2018-09-15_Hpp3lSkims_ElectronEnUp_80X_Moriond_v1',
    'ElectronEnDown'   : '2018-09-15_Hpp3lSkims_ElectronEnDown_80X_Moriond_v1',
    'MuonEnUp'         : '2018-09-15_Hpp3lSkims_MuonEnUp_80X_Moriond_v1',
    'MuonEnDown'       : '2018-09-15_Hpp3lSkims_MuonEnDown_80X_Moriond_v1',
    'TauEnUp'          : '2018-09-15_Hpp3lSkims_TauEnUp_80X_Moriond_v1',
    'TauEnDown'        : '2018-09-15_Hpp3lSkims_TauEnDown_80X_Moriond_v1',
    'JetEnUp'          : '2018-09-15_Hpp3lSkims_JetEnUp_80X_Moriond_v1',
    'JetEnDown'        : '2018-09-15_Hpp3lSkims_JetEnDown_80X_Moriond_v1',
    'JetResUp'         : '2018-09-15_Hpp3lSkims_JetResUp_80X_Moriond_v1',
    'JetResDown'       : '2018-09-15_Hpp3lSkims_JetResDown_80X_Moriond_v1',
    'UnclusteredEnUp'  : '2018-09-15_Hpp3lSkims_UnclusteredEnUp_80X_Moriond_v1',
    'UnclusteredEnDown': '2018-09-15_Hpp3lSkims_UnclusteredEnDown_80X_Moriond_v1',
    'lepUp'            : '2018-09-15_Hpp3lSkims_lepUp_80X_Moriond_v1',
    'lepDown'          : '2018-09-15_Hpp3lSkims_lepDown_80X_Moriond_v1',
    'trigUp'           : '2018-09-15_Hpp3lSkims_trigUp_80X_Moriond_v1',
    'trigDown'         : '2018-09-15_Hpp3lSkims_trigDown_80X_Moriond_v1',
    'puUp'             : '2018-09-15_Hpp3lSkims_puUp_80X_Moriond_v1',
    'puDown'           : '2018-09-15_Hpp3lSkims_puDown_80X_Moriond_v1',
    'fakeUp'           : '2018-09-15_Hpp3lSkims_fakeUp_80X_Moriond_v1',
    'fakeDown'         : '2018-09-15_Hpp3lSkims_fakeDown_80X_Moriond_v1',
    'btagUp'           : '2018-09-15_Hpp3lSkims_btagUp_80X_Moriond_v1',
    'btagDown'         : '2018-09-15_Hpp3lSkims_btagDown_80X_Moriond_v1',
    'chargeUp'         : '2018-09-15_Hpp3lSkims_chargeUp_80X_Moriond_v1',
    'chargeDown'       : '2018-09-15_Hpp3lSkims_chargeDown_80X_Moriond_v1',
}
latestSkims['80X']['Hpp4l'] = {
# ICHEP 2016
#    #''                 : '2016-12-21_Hpp4lSkims_80X_v1',
#    'ElectronEnUp'     : '2016-12-21_Hpp4lSkims_ElectronEnUp_80X_v1',
#    'ElectronEnDown'   : '2016-12-21_Hpp4lSkims_ElectronEnDown_80X_v1',
#    'MuonEnUp'         : '2016-12-21_Hpp4lSkims_MuonEnUp_80X_v1',
#    'MuonEnDown'       : '2016-12-21_Hpp4lSkims_MuonEnDown_80X_v1',
#    'TauEnUp'          : '2016-12-21_Hpp4lSkims_TauEnUp_80X_v1',
#    'TauEnDown'        : '2016-12-21_Hpp4lSkims_TauEnDown_80X_v1',
#    'JetEnUp'          : '2016-12-21_Hpp4lSkims_JetEnUp_80X_v1',
#    'JetEnDown'        : '2016-12-21_Hpp4lSkims_JetEnDown_80X_v1',
#    'JetResUp'         : '2016-12-21_Hpp4lSkims_JetResUp_80X_v1',
#    'JetResDown'       : '2016-12-21_Hpp4lSkims_JetResDown_80X_v1',
#    'UnclusteredEnUp'  : '2016-12-21_Hpp4lSkims_UnclusteredEnUp_80X_v1',
#    'UnclusteredEnDown': '2016-12-21_Hpp4lSkims_UnclusteredEnDown_80X_v1',
#    'lepUp'            : '2016-12-21_Hpp4lSkims_lepUp_80X_v1',
#    'lepDown'          : '2016-12-21_Hpp4lSkims_lepDown_80X_v1',
#    'trigUp'           : '2016-12-21_Hpp4lSkims_trigUp_80X_v1',
#    'trigDown'         : '2016-12-21_Hpp4lSkims_trigDown_80X_v1',
#    'puUp'             : '2016-12-21_Hpp4lSkims_puUp_80X_v1',
#    'puDown'           : '2016-12-21_Hpp4lSkims_puDown_80X_v1',
#    'fakeUp'           : '2016-12-21_Hpp4lSkims_fakeUp_80X_v1',
#    'fakeDown'         : '2016-12-21_Hpp4lSkims_fakeDown_80X_v1',
# Moriond 2017
    #''                 : '2017-05-01_Hpp4lSkims_80X_v2',
    'ElectronEnUp'     : '2018-09-15_Hpp4lSkims_ElectronEnUp_80X_Moriond_v1',
    'ElectronEnDown'   : '2018-09-15_Hpp4lSkims_ElectronEnDown_80X_Moriond_v1',
    'MuonEnUp'         : '2018-09-15_Hpp4lSkims_MuonEnUp_80X_Moriond_v1',
    'MuonEnDown'       : '2018-09-15_Hpp4lSkims_MuonEnDown_80X_Moriond_v1',
    'TauEnUp'          : '2018-09-15_Hpp4lSkims_TauEnUp_80X_Moriond_v1',
    'TauEnDown'        : '2018-09-15_Hpp4lSkims_TauEnDown_80X_Moriond_v1',
    'JetEnUp'          : '2018-09-15_Hpp4lSkims_JetEnUp_80X_Moriond_v1',
    'JetEnDown'        : '2018-09-15_Hpp4lSkims_JetEnDown_80X_Moriond_v1',
    'JetResUp'         : '2018-09-15_Hpp4lSkims_JetResUp_80X_Moriond_v1',
    'JetResDown'       : '2018-09-15_Hpp4lSkims_JetResDown_80X_Moriond_v1',
    'UnclusteredEnUp'  : '2018-09-15_Hpp4lSkims_UnclusteredEnUp_80X_Moriond_v1',
    'UnclusteredEnDown': '2018-09-15_Hpp4lSkims_UnclusteredEnDown_80X_Moriond_v1',
    'lepUp'            : '2018-09-15_Hpp4lSkims_lepUp_80X_Moriond_v1',
    'lepDown'          : '2018-09-15_Hpp4lSkims_lepDown_80X_Moriond_v1',
    'trigUp'           : '2018-09-15_Hpp4lSkims_trigUp_80X_Moriond_v1',
    'trigDown'         : '2018-09-15_Hpp4lSkims_trigDown_80X_Moriond_v1',
    'puUp'             : '2018-09-15_Hpp4lSkims_puUp_80X_Moriond_v1',
    'puDown'           : '2018-09-15_Hpp4lSkims_puDown_80X_Moriond_v1',
    'fakeUp'           : '2018-09-15_Hpp4lSkims_fakeUp_80X_Moriond_v1',
    'fakeDown'         : '2018-09-15_Hpp4lSkims_fakeDown_80X_Moriond_v1',
    'btagUp'           : '2018-09-15_Hpp4lSkims_btagUp_80X_Moriond_v1',
    'btagDown'         : '2018-09-15_Hpp4lSkims_btagDown_80X_Moriond_v1',
    'chargeUp'         : '2018-09-15_Hpp4lSkims_chargeUp_80X_Moriond_v1',
    'chargeDown'       : '2018-09-15_Hpp4lSkims_chargeDown_80X_Moriond_v1',
}

def getSkimJson(analysis,sample,version=getCMSSWVersion(),shift=''):
    jfile = 'jsons/{0}/skims/{1}.json'.format(analysis,sample)
    if shift and shift in latestSkims.get(version,{}).get(analysis,{}):
        baseDir = '/hdfs/store/user/dntaylor'
        jpath = os.path.join(baseDir,latestSkims[version][analysis][shift],sample)
        fnames = glob.glob('{0}/*.root'.format(jpath))
        if len(fnames)==0:
            #raise Exception('No such path {0}'.format(jpath))
            logging.warning('No such path {0}'.format(jpath))
        for fname in fnames:
            if 'json' in fname: jfile = fname
    #else:
    #    raise Exception('Unrecognized {0}'.format(':'.join([analysis,sample,version,shift])))
    return jfile

def getSkimPickle(analysis,sample,version=getCMSSWVersion(),shift=''):
    pfile = 'pickles/{0}/skims/{1}.pkl'.format(analysis,sample)
    if shift and shift in latestSkims.get(version,{}).get(analysis,{}):
        baseDir = '/hdfs/store/user/dntaylor'
        ppath = os.path.join(baseDir,latestSkims[version][analysis][shift],sample)
        fnames = glob.glob('{0}/*.root'.format(ppath))
        if len(fnames)==0:
            #raise Exception('No such path {0}'.format(ppath))
            logging.warning('No such path {0}'.format(ppath))
        for fname in fnames:
            if 'pkl' in fname: pfile = fname
    #else:
    #    raise Exception('Unrecognized {0}'.format(':'.join([analysis,sample,version,shift])))
    return pfile

treeMap = {
    ''               : 'Tree',
    'Electron'       : 'ETree',
    'Muon'           : 'MTree',
    'SingleElectron' : 'ETree',
    'SingleMuon'     : 'MTree',
    'Tau'            : 'TTree',
    'ModDY'          : 'DYTree',
}

def getTreeName(analysis):
    return treeMap[analysis] if analysis in treeMap else analysis+'Tree'

def addChannels(params,var,n):
    for hist in params:
        if 'yVariable' not in params[hist]: # add chans on y axis
            params[hist]['yVariable'] = var
            params[hist]['yBinning'] = [n,0,n]
        elif 'zVariable' not in params[hist]: # add chans on z axis
            params[hist]['zVariable'] = var
            params[hist]['zBinning'] = [n,0,n]
    return params

