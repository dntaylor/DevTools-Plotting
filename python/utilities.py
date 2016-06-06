# common utilities for plotting
import os
import sys
import hashlib

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

def getLumi():
    '''Get the integrated luminosity to scale monte carlo'''
    version = getCMSSWVersion()
    if version=='76X':
        #return 2263 # december jamboree golden json
        return 2318 # moriond golden json
    else:
        #return 221 # first golden json 80X
        #return 589 # second golden json 80X
        return 804.2 # third golden json 80X

latestNtuples = {}
latestNtuples['76X'] = {
    'Charge'         : '2016-04-23_ChargeAnalysis_v1-merge',
    'DY'             : '2016-05-02_DYAnalysis_v1-merge',       # check variations on minbias cross section (71 best fit)
    'DijetFakeRate'  : '',
    'Electron'       : '2016-04-14_ElectronAnalysis_v1-merge',
    #'Hpp3l'          : '2016-05-02_Hpp3lAnalysis_v1-merge',           # Tau no iso for loose
    #'Hpp3l'          : '2016-05-12_Hpp3lAnalysis_v1-merge',           # only 1 fake taus allowed
    #'Hpp3l'          : '2016-05-13_Hpp3lAnalysis_newDMs_v1-merge',    # new DMs
    'Hpp3l'          : '2016-05-16_Hpp3lAnalysis_v1-merge',           # fix for gen channel
    #'Hpp4l'          : '2016-05-02_Hpp4lAnalysis_v1-merge',           # Tau no iso for loose
    #'Hpp4l'          : '2016-05-12_Hpp4lAnalysis_v1-merge',           # only 2 fake taus allowed
    #'Hpp4l'          : '2016-05-13_Hpp4lAnalysis_newDMs_v1-merge',    # new DMs
    #'Hpp4l'          : '2016-05-16_Hpp4lAnalysis_v1-merge',           # fix for gen channel
    #'Hpp4l'          : '2016-06-04_Hpp4lAnalysis_76X_HZZIDs_v1-merge',# hzz ids (with wrong lepton scale factors)
    'Hpp4l'          : '2016-06-04_Hpp4lAnalysis_76X_WZIDs_v1-merge', # wz ids
    'Muon'           : '2016-04-14_MuonAnalysis_v1-merge',
    'SingleElectron' : '',
    'SingleMuon'     : '',
    'Tau'            : '2016-05-11_TauAnalysis_v1-merge',      # Addition of new DMs
    'TauCharge'      : '',
    'WTauFakeRate'   : '',
    'WZ'             : '2016-04-29_WZAnalysis_v1-merge',
}
latestNtuples['80X'] = {
    'Charge'         : '2016-05-28_ChargeAnalysis_80X_v1-merge',
    'DY'             : '2016-05-28_DYAnalysis_80X_v1-merge',
    'DijetFakeRate'  : '2016-05-28_DijetFakeRateAnalysis_80X_v1-merge',
    'Electron'       : '2016-05-28_ElectronAnalysis_80X_v1-merge',
    'Hpp3l'          : '2016-05-28_Hpp3lAnalysis_80X_v1-merge',
    'Hpp4l'          : '2016-05-28_Hpp4lAnalysis_80X_v1-merge',
    'Muon'           : '2016-05-28_MuonAnalysis_80X_v1-merge',
    'Tau'            : '2016-05-28_TauAnalysis_80X_v1-merge',
    'TauCharge'      : '2016-05-28_TauChargeAnalysis_80X_v1-merge',
    'WTauFakeRate'   : '2016-05-28_WTauFakeRateAnalysis_80X_v1-merge',
    'WZ'             : '2016-05-28_WZAnalysis_80X_v1-merge',
}

def getNtupleDirectory(analysis,local=True):
    # first grab the local one
    if local:
        #ntupleDir = '{0}/src/ntuples/{0}'.format(CMSSW_BASE,analysis)
        ntupleDir = 'ntuples/{0}'.format(analysis)
        if os.path.exists(ntupleDir):
            return ntupleDir
    # if not read from hdfs
    baseDir = '/hdfs/store/user/dntaylor'
    ver = getCMSSWVersion()
    if analysis in latestNtuples[ver] and latestNtuples[ver][analysis]:
        return os.path.join(baseDir,latestNtuples[ver][analysis])

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
    'WZ'             : 'WZTree',
}

def getTreeName(analysis):
    return treeMap[analysis] if analysis in treeMap else ''
