# common utilities for plotting
import os
import sys
import hashlib
import glob

from DevTools.Utilities.utilities import python_mkdir, ZMASS, getCMSSWVersion

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

def getLumi(version=getCMSSWVersion()):
    '''Get the integrated luminosity to scale monte carlo'''
    if version=='76X':
        #return 2263 # december jamboree golden json
        return 2318 # moriond golden json
    else:
        #return 4336.100 # previous "frozen"
        return 12892.762 # ichep dataset golden json


latestNtuples = {}
latestNtuples['76X'] = {
    'Charge'         : '2016-04-23_ChargeAnalysis_v1-merge',
    'DY'             : '2016-05-02_DYAnalysis_v1-merge',       # check variations on minbias cross section (71 best fit)
    'DijetFakeRate'  : '',
    'Electron'       : '2016-04-14_ElectronAnalysis_v1-merge',
    'Hpp3l'          : '2016-05-16_Hpp3lAnalysis_v1-merge',           # fix for gen channel
    'Hpp4l'          : '2016-06-07_Hpp4lAnalysis_76X_WZIDs_v1-merge', # wz ids
    'Muon'           : '2016-04-14_MuonAnalysis_v1-merge',
    'SingleElectron' : '',
    'SingleMuon'     : '',
    'Tau'            : '2016-05-11_TauAnalysis_v1-merge',      # Addition of new DMs
    'TauCharge'      : '',
    'WTauFakeRate'   : '',
    'WFakeRate'      : '',
    'WZ'             : '2016-04-29_WZAnalysis_v1-merge',
}
latestNtuples['80X'] = {
    'Charge'         : '2016-07-24_ChargeAnalysis_80X_v1-merge',
    'DY'             : '2016-07-24_DYAnalysis_80X_v1-merge',
    'DijetFakeRate'  : '2016-07-26_DijetFakeRateAnalysis_80X_v1-merge',
    'Hpp3l'          : '2016-07-24_Hpp3lAnalysis_80X_v1-merge',
    'Hpp4l'          : '2016-07-24_Hpp4lAnalysis_80X_v1-merge',
    'Electron'       : '2016-06-25_ElectronAnalysis_80X_v1-merge',
    'Muon'           : '2016-06-25_MuonAnalysis_80X_v1-merge',
    'Tau'            : '2016-07-06_TauAnalysis_80X_v1-merge',
    'TauCharge'      : '2016-07-24_TauChargeAnalysis_80X_v1-merge',
    'WTauFakeRate'   : '2016-07-24_WTauFakeRateAnalysis_80X_v1-merge',
    'WFakeRate'      : '2016-07-24_WFakeRateAnalysis_80X_v1-merge',
    'ZFakeRate'      : '2016-07-24_ZFakeRateAnalysis_80X_v1-merge',
    'WZ'             : '2016-07-20_WZAnalysis_80X_v1-merge',
    'ZZ'             : '2016-07-13_ZZAnalysis_80X_v1-merge',
}

latestShifts = {}
latestShifts['80X'] = {}
latestShifts['80X']['Hpp3l'] = {
    'ElectronEnUp'     : '2016-07-31_Hpp3lAnalysis_ElectronEnUp_80X_v1-merge',
    'ElectronEnDown'   : '2016-07-31_Hpp3lAnalysis_ElectronEnDown_80X_v1-merge',
    'MuonEnUp'         : '2016-07-31_Hpp3lAnalysis_MuonEnUp_80X_v1-merge',
    'MuonEnDown'       : '2016-07-31_Hpp3lAnalysis_MuonEnDown_80X_v1-merge',
    'TauEnUp'          : '2016-07-31_Hpp3lAnalysis_TauEnUp_80X_v1-merge',
    'TauEnDown'        : '2016-07-31_Hpp3lAnalysis_TauEnDown_80X_v1-merge',
    'JetEnUp'          : '2016-07-31_Hpp3lAnalysis_JetEnUp_80X_v1-merge',
    'JetEnDown'        : '2016-07-31_Hpp3lAnalysis_JetEnDown_80X_v1-merge',
    'JetResUp'         : '2016-07-31_Hpp3lAnalysis_JetResUp_80X_v1-merge',
    'JetResDown'       : '2016-07-31_Hpp3lAnalysis_JetResDown_80X_v1-merge',
    'UnclusteredEnUp'  : '2016-08-01_Hpp3lAnalysis_UnclusteredEnUp_80X_v1-merge',
    'UnclusteredEnDown': '2016-08-01_Hpp3lAnalysis_UnclusteredEnDown_80X_v1-merge',
}
latestShifts['80X']['Hpp4l'] = {
    'ElectronEnUp'     : '2016-07-31_Hpp4lAnalysis_ElectronEnUp_80X_v1-merge',
    'ElectronEnDown'   : '2016-07-31_Hpp4lAnalysis_ElectronEnDown_80X_v1-merge',
    'MuonEnUp'         : '2016-07-31_Hpp4lAnalysis_MuonEnUp_80X_v1-merge',
    'MuonEnDown'       : '2016-07-31_Hpp4lAnalysis_MuonEnDown_80X_v1-merge',
    'TauEnUp'          : '2016-07-31_Hpp4lAnalysis_TauEnUp_80X_v1-merge',
    'TauEnDown'        : '2016-07-31_Hpp4lAnalysis_TauEnDown_80X_v1-merge',
    'JetEnUp'          : '2016-07-31_Hpp4lAnalysis_JetEnUp_80X_v1-merge',
    'JetEnDown'        : '2016-07-31_Hpp4lAnalysis_JetEnDown_80X_v1-merge',
    'JetResUp'         : '2016-07-31_Hpp4lAnalysis_JetResUp_80X_v1-merge',
    'JetResDown'       : '2016-07-31_Hpp4lAnalysis_JetResDown_80X_v1-merge',
    'UnclusteredEnUp'  : '2016-08-01_Hpp4lAnalysis_UnclusteredEnUp_80X_v1-merge',
    'UnclusteredEnDown': '2016-08-01_Hpp4lAnalysis_UnclusteredEnDown_80X_v1-merge',
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

latestHistograms = {}
latestHistograms['80X'] = {}
latestHistograms['80X']['Hpp3l'] = {
    'ElectronEnUp'     : '2016-08-04_Hpp3lHistograms_ElectronEnUp_80X_v1-merge',
    'ElectronEnDown'   : '2016-08-04_Hpp3lHistograms_ElectronEnDown_80X_v1-merge',
    'MuonEnUp'         : '2016-08-04_Hpp3lHistograms_MuonEnUp_80X_v1-merge',
    'MuonEnDown'       : '2016-08-04_Hpp3lHistograms_MuonEnDown_80X_v1-merge',
    'TauEnUp'          : '2016-08-04_Hpp3lHistograms_TauEnUp_80X_v1-merge',
    'TauEnDown'        : '2016-08-04_Hpp3lHistograms_TauEnDown_80X_v1-merge',
    'JetEnUp'          : '2016-08-04_Hpp3lHistograms_JetEnUp_80X_v1-merge',
    'JetEnDown'        : '2016-08-04_Hpp3lHistograms_JetEnDown_80X_v1-merge',
    'JetResUp'         : '2016-08-04_Hpp3lHistograms_JetResUp_80X_v1-merge',
    'JetResDown'       : '2016-08-04_Hpp3lHistograms_JetResDown_80X_v1-merge',
    'UnclusteredEnUp'  : '2016-08-04_Hpp3lHistograms_UnclusteredEnUp_80X_v1-merge',
    'UnclusteredEnDown': '2016-08-04_Hpp3lHistograms_UnclusteredEnDown_80X_v1-merge',
    'lepUp'            : '2016-08-04_Hpp3lHistograms_lepUp_80X_v1-merge',
    'lepDown'          : '2016-08-04_Hpp3lHistograms_lepDown_80X_v1-merge',
    'trigUp'           : '2016-08-04_Hpp3lHistograms_trigUp_80X_v1-merge',
    'trigDown'         : '2016-08-04_Hpp3lHistograms_trigDown_80X_v1-merge',
    'puUp'             : '2016-08-04_Hpp3lHistograms_puUp_80X_v1-merge',
    'puDown'           : '2016-08-04_Hpp3lHistograms_puDown_80X_v1-merge',
    'fakeUp'           : '2016-08-04_Hpp3lHistograms_fakeUp_80X_v1-merge',
    'fakeDown'         : '2016-08-04_Hpp3lHistograms_fakeDown_80X_v1-merge',
}
latestHistograms['80X']['Hpp4l'] = {
    'ElectronEnUp'     : '2016-08-04_Hpp4lHistograms_ElectronEnUp_80X_v1-merge',
    'ElectronEnDown'   : '2016-08-04_Hpp4lHistograms_ElectronEnDown_80X_v1-merge',
    'MuonEnUp'         : '2016-08-04_Hpp4lHistograms_MuonEnUp_80X_v1-merge',
    'MuonEnDown'       : '2016-08-04_Hpp4lHistograms_MuonEnDown_80X_v1-merge',
    'TauEnUp'          : '2016-08-04_Hpp4lHistograms_TauEnUp_80X_v1-merge',
    'TauEnDown'        : '2016-08-04_Hpp4lHistograms_TauEnDown_80X_v1-merge',
    'JetEnUp'          : '2016-08-04_Hpp4lHistograms_JetEnUp_80X_v1-merge',
    'JetEnDown'        : '2016-08-04_Hpp4lHistograms_JetEnDown_80X_v1-merge',
    'JetResUp'         : '2016-08-04_Hpp4lHistograms_JetResUp_80X_v1-merge',
    'JetResDown'       : '2016-08-04_Hpp4lHistograms_JetResDown_80X_v1-merge',
    'UnclusteredEnUp'  : '2016-08-04_Hpp4lHistograms_UnclusteredEnUp_80X_v1-merge',
    'UnclusteredEnDown': '2016-08-04_Hpp4lHistograms_UnclusteredEnDown_80X_v1-merge',
    'lepUp'            : '2016-08-04_Hpp4lHistograms_lepUp_80X_v1-merge',
    'lepDown'          : '2016-08-04_Hpp4lHistograms_lepDown_80X_v1-merge',
    'trigUp'           : '2016-08-04_Hpp4lHistograms_trigUp_80X_v1-merge',
    'trigDown'         : '2016-08-04_Hpp4lHistograms_trigDown_80X_v1-merge',
    'puUp'             : '2016-08-04_Hpp4lHistograms_puUp_80X_v1-merge',
    'puDown'           : '2016-08-04_Hpp4lHistograms_puDown_80X_v1-merge',
    'fakeUp'           : '2016-08-04_Hpp4lHistograms_fakeUp_80X_v1-merge',
    'fakeDown'         : '2016-08-04_Hpp4lHistograms_fakeDown_80X_v1-merge',
}

def getFlatHistograms(analysis,sample,version=getCMSSWVersion(),shift=''):
    flat = 'flat/{0}/{1}.root'.format(analysis,sample)
    if shift in latestHistograms.get(version,{}).get(analysis,{}):
        baseDir = '/hdfs/store/user/dntaylor'
        flatpath = os.path.join(baseDir,latestHistograms[version][analysis][shift],sample)
        for fname in glob.glob('{0}/*.root'.format(flatpath)):
            if 'projection' not in fname: flat = fname
    return flat
        
def getProjectionHistograms(analysis,sample,version=getCMSSWVersion(),shift=''):
    proj = 'projections/{0}/{1}.root'.format(analysis,sample)
    if shift in latestHistograms.get(version,{}).get(analysis,{}):
        baseDir = '/hdfs/store/user/dntaylor'
        projpath = os.path.join(baseDir,latestHistograms[version][analysis][shift],sample)
        for fname in glob.glob('{0}/*.root'.format(projpath)):
            if 'projection' in fname: proj = fname
    return proj
        

treeMap = {
    ''               : 'Tree',
    'Charge'         : 'ChargeTree',
    'DijetFakeRate'  : 'DijetFakeRateTree',
    'DY'             : 'DYTree',
    'Electron'       : 'ETree',
    'Hpp3l'          : 'Hpp3lTree',
    'Hpp4l'          : 'Hpp4lTree',
    'Muon'           : 'MTree',
    'SingleElectron' : 'ETree',
    'SingleMuon'     : 'MTree',
    'Tau'            : 'TTree',
    'TauCharge'      : 'TauChargeTree',
    'WTauFakeRate'   : 'WTauFakeRateTree',
    'WFakeRate'      : 'WFakeRateTree',
    'ZFakeRate'      : 'ZFakeRateTree',
    'WZ'             : 'WZTree',
    'ZZ'             : 'ZZTree',
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

