from itertools import product, combinations_with_replacement
import numpy as np
from DevTools.Utilities.utilities import ZMASS, getCMSSWVersion

version = getCMSSWVersion()

######################
### Category names ###
######################
cats = ['I','II','III','IV','V','VI']
catLabelMap = {
    'I'  : 'Cat I',
    'II' : 'Cat II',
    'III': 'Cat III',
    'IV' : 'Cat IV',
    'V'  : 'Cat V',
    'VI' : 'Cat VI',
}
catLabels = [catLabelMap[cat] for cat in cats]
# based on number of taus in each higgs
catContentMap = {
    'Hpp4l': {
        'I'  : [0,0],
        'II' : [0,1],
        'III': [0,2],
        'IV' : [1,1],
        'V'  : [1,2],
        'VI' : [2,2],
    },
    'Hpp3l': {
        'I'  : [0,0],
        'II' : [0,1],
        'III': [1,0],
        'IV' : [1,1],
        'V'  : [2,0],
        'VI' : [2,1],
    },
}
# based on flavor of light lepton relative to first
# 0,1,2 = e/m,m/e,t
# each cat = [n,n,n,n], [n,n,n]
subCats = {
    'Hpp4l' : {
        'I' : {
            'a': [0,0,0,0], # all same flavor
            'b': [0,0,0,1], # one different flavor
            'c': [0,0,1,1], # hpp and hmm same flavor (cleanest)
            'd': [0,1,0,1], # hpp and hmm flavor violating
        },
        'II' : {
            'a': [0,0,0,2], # single tau, rest same
            'b': [0,0,1,2], # one higgs same flavor, other to opposite flavor/tau
            'c': [0,1,0,2], # one flavor violating, other to light + tau
        },
        'III' : {
            'a': [0,0,2,2], # one same, other taus
            'b': [0,1,2,2], # one flavor violating, other taus
        },
        'IV' : {
            'a': [0,2,0,2], # each to same light plus tau
            'b': [0,2,1,2], # each to different light plus tau
        },
        'V' : {
            'a': [0,2,2,2], # to three taus + light
        },
        'VI' : {
            'a': [2,2,2,2], # to 4 taus
        },
   },
   'Hpp3l' : {
       'I' : {
           'a': [0,0,0], # all same flavor
           'b': [0,0,1], # one different flavor in h-
           'c': [0,1,0], # one different flavor in h++
       },
       'II' : {
           'a': [0,0,2], # h++ same h- tau
           'b': [0,1,2], # h++ different h- tau
       },
       'III' : {
           'a': [0,2,0], # h++ one tau, same h-
           'b': [0,2,1], # h++ one tau, different h-
       },
       'IV' : {
           'a': [0,2,2], # h++ one tau, h- tau
       },
       'V' : {
           'a': [2,2,0], # h++ two tau, h- light
       },
       'VI' : {
           'a': [2,2,2], # all tau
       },
   },
}
subCatLabelMap = {
    'Hpp4l' : {
        'I' : {
            'a': 'llll',
            'b': 'llll\'',
            'c': 'lll\'l\'',
            'd': 'll\'ll\'',
        },
        'II' : {
            'a': 'lll#tau',
            'b': 'lll\'#tau',
            'c': 'll\'l#tau',
        },
        'III' : {
            'a': 'll#tau#tau',
            'b': 'll\'#tau#tau',
        },
        'IV' : {
            'a': 'l#tau l#tau',
            'b': 'l#tau l\'#tau',
        },
        'V' : {
            'a': 'l#tau#tau#tau',
        },
        'VI' : {
            'a': '#tau#tau#tau#tau',
        },
    },
    'Hpp3l' : {
        'I' : {
            'a': 'lll',
            'b': 'lll\'',
            'c': 'll\'l',
        },
        'II' : {
            'a': 'll#tau',
            'b': 'll\'#tau',
        },
        'III' : {
            'a': 'l#tau l',
            'b': 'l#tau l\'',
        },
        'IV' : {
            'a': 'l#tau#tau',
        },
        'V' : {
            'a': '#tau#tau l',
        },
        'VI' : {
            'a': '#tau#tau#tau',
        },
    },
}

###########################
### Build category maps ###
###########################
subCatChannels = {}
for analysis in ['Hpp3l','Hpp4l']:
    subCatChannels[analysis] = {}
    for cat in cats:
        subCatChannels[analysis][cat] = {}
        for subCat in subCats[analysis][cat]:
            strings = []
            for i,l in enumerate(subCats[analysis][cat][subCat]):
                if i==0 and l==0:                          # start with a light lepton
                    strings = ['e','m']
                elif i==0 and l==2:                        # start with a tau
                    strings = ['t']
                elif i>0:                                  # add a character
                    if l==2:                               # add a tau
                        for s in range(len(strings)):
                            strings[s] += 't'
                    else:                                  # add a light lepton
                        for s in range(len(strings)):
                            if l==subCats[analysis][cat][subCat][0]: # add the same light lepton
                                strings[s] += strings[s][0]
                            else:                          # add a different light lepton
                                strings[s] += 'e' if strings[s][0]=='m' else 'm'
            result = []
            if analysis in ['Hpp4l']:
                for string in strings:
                    hpphmm = ''.join(sorted(string[:2]) + sorted(string[2:]))
                    if hpphmm not in result: result += [hpphmm]
                    hmmhpp = ''.join(sorted(string[2:]) + sorted(string[:2]))
                    if hmmhpp not in result: result += [hmmhpp]
            elif analysis in ['Hpp3l']:
                for string in strings:
                    hpphm = ''.join(sorted(string[:2]) + sorted(string[2:]))
                    if hpphm not in result: result += [hpphm]
            subCatChannels[analysis][cat][subCat] = result

##############
### Scales ###
##############
class Scales(object):
    def __init__(self, br_ee, br_em, br_et, br_mm, br_mt, br_tt):
        self.a_3l = np.array([br_ee, br_em, br_et, br_mm, br_mt, br_tt], dtype=float)
        self.m_4l = np.outer(self.a_3l, self.a_3l)
        self.index = {"ee": 0, "em": 1, "et": 2, "mm": 3, "mt": 4, "tt": 5}
    def scale_Hpp4l(self, hpp, hmm):
        i = self.index[hpp]
        j = self.index[hmm]
        return self.m_4l[i,j] * 36.0
    def scale_Hpp3l(self, hpp, hm='a'):
        i = self.index[hpp]
        scale = 9./2
        if hpp in ['ee','mm','tt']: scale = 9.
        return self.a_3l[i] * scale

scales = {
    'ee100': Scales(1., 0., 0., 0., 0., 0.),
    'em100': Scales(0., 1., 0., 0., 0., 0.),
    'et100': Scales(0., 0., 1., 0., 0., 0.),
    'mm100': Scales(0., 0., 0., 1., 0., 0.),
    'mt100': Scales(0., 0., 0., 0., 1., 0.),
    'tt100': Scales(0., 0., 0., 0., 0., 1.),
    'BP1'  : Scales(0, 0.01, 0.01, 0.3, 0.38, 0.3),
    'BP2'  : Scales(1./2., 0, 0, 1./8., 1./4., 1./8.),
    'BP3'  : Scales(1./3., 0, 0, 1./3., 0, 1./3.),
    'BP4'  : Scales(1./6., 1./6., 1./6., 1./6., 1./6., 1./6.),
}

#####################
### Reco channels ###
#####################
chans3l = {}
chans4l = {}
hppChannels = [''.join(x) for x in product('emt',repeat=2)]
hmChannels  = [''.join(x) for x in product('emt',repeat=1)]
for hpp in hppChannels:
    for hmm in hppChannels:
        chanString = ''.join(sorted(hpp))+''.join(sorted(hmm))
        if chanString not in chans4l:
            chans4l[chanString] = []
        chans4l[chanString] += [hpp+hmm]
for hpp in hppChannels:
    for hm in hmChannels:
        chanString = ''.join(sorted(hpp))+''.join(sorted(hm))
        if chanString not in chans3l:
            chans3l[chanString] = []
        chans3l[chanString] += [hpp+hm]

####################
### Gen Channels ###
####################
genChannelsPP = []
genChannelsAP = []
genHiggsChannels = [''.join(x) for x in combinations_with_replacement('emt',2)]
genHiggsChannels2 = [''.join(x) for x in combinations_with_replacement('emt',1)]
for hpp in genHiggsChannels:
    for hmm in genHiggsChannels:
        genChannelsPP += [hpp+hmm]
    for hm in genHiggsChannels2:
        genChannelsAP += [hpp+hm]

##################
### Signal map ###
##################

sigMaps = {
    'Hpp4l': {
        'Z'   : [
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
                 'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
                 'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
                ],
        'TT'  : [
                 'TTJets_DiLept_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
                 'TTJets_SingleLeptFromT_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
                 'TTJets_SingleLeptFromTbar_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
                ],
        'WZ' : [
                 #'WZTo3LNu_TuneCUETP8M1_13TeV-powheg-pythia8',
                 'WZTo3LNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8', # more stats but neg weights
                 'WZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8',
                 'WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8',
                ],
        'ZZ' : [
                 'ZZTo4L_13TeV_powheg_pythia8',
                 'ZZTo2L2Nu_13TeV_powheg_pythia8',
                 'ZZTo2L2Q_13TeV_powheg_pythia8',
                 'GluGluToContinToZZTo2e2mu_13TeV_MCFM701_pythia8',
                 'GluGluToContinToZZTo2mu2tau_13TeV_MCFM701_pythia8',
                 'GluGluToContinToZZTo4e_13TeV_MCFM701_pythia8',
                 'GluGluToContinToZZTo4mu_13TeV_MCFM701_pythia8',
                 'GluGluToContinToZZTo4tau_13TeV_MCFM701_pythia8',
                 #'ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8',
                ],
        'TTV' : [
                 #'ttWJets_13TeV_madgraphMLM',
                 'TTWJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8',
                 'ttZJets_13TeV_madgraphMLM-pythia8',
                 'tZq_ll_4f_13TeV-amcatnlo-pythia8',
                ],
        'VVV' : [
                 'WWW_4F_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
                 'WWZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
                 'WZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
                 'ZZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
                ],

    },
    'Hpp4lDataDriven' : {
        'ZZ' : [
                 'ZZTo4L_13TeV_powheg_pythia8',
                 #'ZZTo2L2Nu_13TeV_powheg_pythia8',
                 #'ZZTo2L2Q_13TeV_powheg_pythia8',
                 'GluGluToContinToZZTo2e2mu_13TeV_MCFM701_pythia8',
                 'GluGluToContinToZZTo2mu2tau_13TeV_MCFM701_pythia8',
                 'GluGluToContinToZZTo4e_13TeV_MCFM701_pythia8',
                 'GluGluToContinToZZTo4mu_13TeV_MCFM701_pythia8',
                 'GluGluToContinToZZTo4tau_13TeV_MCFM701_pythia8',
                ],
        'TTV' : [
                 #'TTWJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8',
                 'ttZJets_13TeV_madgraphMLM-pythia8',
                 #'tZq_ll_4f_13TeV-amcatnlo-pythia8',
                 #'TTJets_DiLept_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
                 #'TTJets_SingleLeptFromT_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
                 #'TTJets_SingleLeptFromTbar_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
                ],
        'VVV' : [
                 #'WWW_4F_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
                 'WWZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
                 'WZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
                 'ZZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
                ],

    },
    'Hpp3l' : {
        'T'   : [
                 #'ST_s-channel_4f_leptonDecays_13TeV-amcatnlo-pythia8_TuneCUETP8M1',
                 #'ST_t-channel_4f_leptonDecays_13TeV-amcatnlo-pythia8_TuneCUETP8M1',
                 #'ST_t-channel_antitop_4f_leptonDecays_13TeV-powheg-pythia8_TuneCUETP8M1',
                 #'ST_t-channel_top_4f_leptonDecays_13TeV-powheg-pythia8_TuneCUETP8M1',
                 'ST_tW_antitop_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1',
                 'ST_tW_top_5f_inclusiveDecays_13TeV-powheg-pythia8_TuneCUETP8M1',
                ],
        'W'   : [
                 'WJetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
                 'W1JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
                 'W2JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
                 'W3JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
                 'W4JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
                ],
        'Z'   : [
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
                 'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
                 'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
                ],
        'WW'  : [
                 'WWTo2L2Nu_13TeV-powheg',
                 'WWToLNuQQ_13TeV-powheg',
                 #'GluGluWWTo2L2Nu_MCFM_13TeV',
                ],
        'TT'  : [
                 'TTJets_DiLept_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
                 'TTJets_SingleLeptFromT_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
                 'TTJets_SingleLeptFromTbar_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
                ],
        'WZ' : [
                 #'WZTo3LNu_TuneCUETP8M1_13TeV-powheg-pythia8',
                 'WZTo3LNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8', # more stats but neg weights
                 'WZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8',
                 'WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8',
                ],
        'ZZ' : [
                 'ZZTo4L_13TeV_powheg_pythia8',
                 'ZZTo2L2Nu_13TeV_powheg_pythia8',
                 'ZZTo2L2Q_13TeV_powheg_pythia8',
                 'GluGluToContinToZZTo2e2mu_13TeV_MCFM701_pythia8',
                 'GluGluToContinToZZTo2mu2tau_13TeV_MCFM701_pythia8',
                 'GluGluToContinToZZTo4e_13TeV_MCFM701_pythia8',
                 'GluGluToContinToZZTo4mu_13TeV_MCFM701_pythia8',
                 'GluGluToContinToZZTo4tau_13TeV_MCFM701_pythia8',
                 #'ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8',
                ],
        'TTV' : [
                 'TTWJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8',
                 #'ttWJets_13TeV_madgraphMLM',
                 'ttZJets_13TeV_madgraphMLM-pythia8',
                 'tZq_ll_4f_13TeV-amcatnlo-pythia8',
                ],
        'VVV' : [
                 'WWW_4F_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
                 'WWZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
                 'WZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
                 'ZZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
                ],

    },
    'Hpp3lDataDriven' : {
        'WZ' : [
                 #'WZTo3LNu_TuneCUETP8M1_13TeV-powheg-pythia8',
                 'WZTo3LNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8', # more stats but neg weights
                 #'WZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8',
                 #'WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8',
                ],
        'ZZ' : [
                 'ZZTo4L_13TeV_powheg_pythia8',
                 #'ZZTo2L2Nu_13TeV_powheg_pythia8',
                 #'ZZTo2L2Q_13TeV_powheg_pythia8',
                 'GluGluToContinToZZTo2e2mu_13TeV_MCFM701_pythia8',
                 'GluGluToContinToZZTo2mu2tau_13TeV_MCFM701_pythia8',
                 'GluGluToContinToZZTo4e_13TeV_MCFM701_pythia8',
                 'GluGluToContinToZZTo4mu_13TeV_MCFM701_pythia8',
                 'GluGluToContinToZZTo4tau_13TeV_MCFM701_pythia8',
                ],
        'TTV' : [
                 'TTWJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8',
                 #'ttWJets_13TeV_madgraphMLM',
                 'ttZJets_13TeV_madgraphMLM-pythia8',
                 'tZq_ll_4f_13TeV-amcatnlo-pythia8',
                 #'TTJets_DiLept_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
                 #'TTJets_SingleLeptFromT_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
                 #'TTJets_SingleLeptFromTbar_TuneCUETP8M1_13TeV-madgraphMLM-pythia8',
                ],
        'VVV' : [
                 'WWW_4F_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
                 'WWZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
                 'WZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
                 'ZZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8',
                ],

    },
}


for sigMap in sigMaps:
    sigMaps[sigMap]['data'] = [
                               'DoubleMuon',
                               'DoubleEG',
                               'MuonEG',
                               'SingleMuon',
                               'SingleElectron',
                               'Tau',
                              ]

    sigMaps[sigMap]['HppHmm200GeV']  = ['HPlusPlusHMinusMinusHTo4L_M-200_TuneCUETP8M1_13TeV_pythia8'] if version=='80X' else ['HPlusPlusHMinusMinusHTo4L_M-200_13TeV-pythia8']
    sigMaps[sigMap]['HppHmm300GeV']  = ['HPlusPlusHMinusMinusHTo4L_M-300_TuneCUETP8M1_13TeV_pythia8'] if version=='80X' else ['HPlusPlusHMinusMinusHTo4L_M-300_13TeV-pythia8']
    sigMaps[sigMap]['HppHmm400GeV']  = ['HPlusPlusHMinusMinusHTo4L_M-400_TuneCUETP8M1_13TeV_pythia8'] if version=='80X' else ['HPlusPlusHMinusMinusHTo4L_M-400_13TeV-pythia8']
    sigMaps[sigMap]['HppHmm500GeV']  = ['HPlusPlusHMinusMinusHTo4L_M-500_TuneCUETP8M1_13TeV_pythia8'] if version=='80X' else ['HPlusPlusHMinusMinusHTo4L_M-500_13TeV-pythia8']
    sigMaps[sigMap]['HppHmm600GeV']  = ['HPlusPlusHMinusMinusHTo4L_M-600_TuneCUETP8M1_13TeV_pythia8'] if version=='80X' else ['HPlusPlusHMinusMinusHTo4L_M-600_13TeV-pythia8']
    sigMaps[sigMap]['HppHmm700GeV']  = ['HPlusPlusHMinusMinusHTo4L_M-700_TuneCUETP8M1_13TeV_pythia8'] if version=='80X' else ['HPlusPlusHMinusMinusHTo4L_M-700_13TeV-pythia8']
    sigMaps[sigMap]['HppHmm800GeV']  = ['HPlusPlusHMinusMinusHTo4L_M-800_TuneCUETP8M1_13TeV_pythia8'] if version=='80X' else ['HPlusPlusHMinusMinusHTo4L_M-800_13TeV-pythia8']
    sigMaps[sigMap]['HppHmm900GeV']  = ['HPlusPlusHMinusMinusHTo4L_M-900_TuneCUETP8M1_13TeV_pythia8'] if version=='80X' else ['HPlusPlusHMinusMinusHTo4L_M-900_13TeV-pythia8']
    sigMaps[sigMap]['HppHmm1000GeV'] = ['HPlusPlusHMinusMinusHTo4L_M-1000_TuneCUETP8M1_13TeV_pythia8'] if version=='80X' else ['HPlusPlusHMinusMinusHTo4L_M-1000_13TeV-pythia8']
    sigMaps[sigMap]['HppHmm1100GeV'] = ['HPlusPlusHMinusMinusHTo4L_M-1100_TuneCUETP8M1_13TeV_pythia8'] if version=='80X' else []
    sigMaps[sigMap]['HppHmm1200GeV'] = ['HPlusPlusHMinusMinusHTo4L_M-1200_TuneCUETP8M1_13TeV_pythia8'] if version=='80X' else []
    sigMaps[sigMap]['HppHmm1300GeV'] = ['HPlusPlusHMinusMinusHTo4L_M-1300_TuneCUETP8M1_13TeV_pythia8'] if version=='80X' else []
    sigMaps[sigMap]['HppHmm1400GeV'] = ['HPlusPlusHMinusMinusHTo4L_M-1400_TuneCUETP8M1_13TeV_pythia8'] if version=='80X' else []
    sigMaps[sigMap]['HppHmm1500GeV'] = ['HPlusPlusHMinusMinusHTo4L_M-1500_TuneCUETP8M1_13TeV_pythia8'] if version=='80X' else []

    sigMaps[sigMap]['HppHmmR200GeV']  = ['HPlusPlusHMinusMinusHRTo4L_M-200_TuneCUETP8M1_13TeV-pythia8']
    sigMaps[sigMap]['HppHmmR300GeV']  = ['HPlusPlusHMinusMinusHRTo4L_M-300_TuneCUETP8M1_13TeV-pythia8']
    sigMaps[sigMap]['HppHmmR400GeV']  = ['HPlusPlusHMinusMinusHRTo4L_M-400_TuneCUETP8M1_13TeV-pythia8']
    sigMaps[sigMap]['HppHmmR500GeV']  = ['HPlusPlusHMinusMinusHRTo4L_M-500_TuneCUETP8M1_13TeV-pythia8']
    sigMaps[sigMap]['HppHmmR600GeV']  = ['HPlusPlusHMinusMinusHRTo4L_M-600_TuneCUETP8M1_13TeV-pythia8']
    sigMaps[sigMap]['HppHmmR700GeV']  = ['HPlusPlusHMinusMinusHRTo4L_M-700_TuneCUETP8M1_13TeV-pythia8']
    sigMaps[sigMap]['HppHmmR800GeV']  = ['HPlusPlusHMinusMinusHRTo4L_M-800_TuneCUETP8M1_13TeV-pythia8']
    sigMaps[sigMap]['HppHmmR900GeV']  = ['HPlusPlusHMinusMinusHRTo4L_M-900_TuneCUETP8M1_13TeV-pythia8']
    sigMaps[sigMap]['HppHmmR1000GeV'] = ['HPlusPlusHMinusMinusHRTo4L_M-1000_TuneCUETP8M1_13TeV-pythia8']
    sigMaps[sigMap]['HppHmmR1100GeV'] = ['HPlusPlusHMinusMinusHRTo4L_M-1100_TuneCUETP8M1_13TeV-pythia8']
    sigMaps[sigMap]['HppHmmR1200GeV'] = ['HPlusPlusHMinusMinusHRTo4L_M-1200_TuneCUETP8M1_13TeV-pythia8']
    sigMaps[sigMap]['HppHmmR1300GeV'] = ['HPlusPlusHMinusMinusHRTo4L_M-1300_TuneCUETP8M1_13TeV-pythia8']
    sigMaps[sigMap]['HppHmmR1400GeV'] = ['HPlusPlusHMinusMinusHRTo4L_M-1400_TuneCUETP8M1_13TeV-pythia8']
    sigMaps[sigMap]['HppHmmR1500GeV'] = ['HPlusPlusHMinusMinusHRTo4L_M-1500_TuneCUETP8M1_13TeV-pythia8']

    sigMaps[sigMap]['HppHm200GeV']   = ['HPlusPlusHMinusHTo3L_M-200_TuneCUETP8M1_13TeV_calchep-pythia8' ] if version=='76X' else ['HPlusPlusHMinusHTo3L_M-200_13TeV-calchep-pythia8']
    sigMaps[sigMap]['HppHm300GeV']   = ['HPlusPlusHMinusHTo3L_M-300_TuneCUETP8M1_13TeV_calchep-pythia8' ] if version=='76X' else ['HPlusPlusHMinusHTo3L_M-300_13TeV-calchep-pythia8']
    sigMaps[sigMap]['HppHm400GeV']   = ['HPlusPlusHMinusHTo3L_M-400_TuneCUETP8M1_13TeV_calchep-pythia8' ] if version=='76X' else ['HPlusPlusHMinusHTo3L_M-400_13TeV-calchep-pythia8']
    sigMaps[sigMap]['HppHm500GeV']   = ['HPlusPlusHMinusHTo3L_M-500_TuneCUETP8M1_13TeV_calchep-pythia8' ] if version=='76X' else ['HPlusPlusHMinusHTo3L_M-500_13TeV-calchep-pythia8']
    sigMaps[sigMap]['HppHm600GeV']   = ['HPlusPlusHMinusHTo3L_M-600_TuneCUETP8M1_13TeV_calchep-pythia8' ] if version=='76X' else ['HPlusPlusHMinusHTo3L_M-600_13TeV-calchep-pythia8']
    sigMaps[sigMap]['HppHm700GeV']   = ['HPlusPlusHMinusHTo3L_M-700_TuneCUETP8M1_13TeV_calchep-pythia8' ] if version=='76X' else ['HPlusPlusHMinusHTo3L_M-700_13TeV-calchep-pythia8']
    sigMaps[sigMap]['HppHm800GeV']   = ['HPlusPlusHMinusHTo3L_M-800_TuneCUETP8M1_13TeV_calchep-pythia8' ] if version=='76X' else ['HPlusPlusHMinusHTo3L_M-800_13TeV-calchep-pythia8']
    sigMaps[sigMap]['HppHm900GeV']   = ['HPlusPlusHMinusHTo3L_M-900_TuneCUETP8M1_13TeV_calchep-pythia8' ] if version=='76X' else ['HPlusPlusHMinusHTo3L_M-900_13TeV-calchep-pythia8']
    sigMaps[sigMap]['HppHm1000GeV']  = ['HPlusPlusHMinusHTo3L_M-1000_TuneCUETP8M1_13TeV_calchep-pythia8'] if version=='76X' else ['HPlusPlusHMinusHTo3L_M-1000_13TeV-calchep-pythia8']
    sigMaps[sigMap]['HppHm1100GeV']  = ['HPlusPlusHMinusHTo3L_M-1100_TuneCUETP8M1_13TeV_calchep-pythia8'] if version=='76X' else ['HPlusPlusHMinusHTo3L_M-1100_13TeV-calchep-pythia8']
    sigMaps[sigMap]['HppHm1200GeV']  = ['HPlusPlusHMinusHTo3L_M-1200_TuneCUETP8M1_13TeV_calchep-pythia8'] if version=='76X' else ['HPlusPlusHMinusHTo3L_M-1200_13TeV-calchep-pythia8']
    sigMaps[sigMap]['HppHm1300GeV']  = ['HPlusPlusHMinusHTo3L_M-1300_TuneCUETP8M1_13TeV_calchep-pythia8'] if version=='76X' else ['HPlusPlusHMinusHTo3L_M-1300_13TeV-calchep-pythia8']
    sigMaps[sigMap]['HppHm1400GeV']  = ['HPlusPlusHMinusHTo3L_M-1400_TuneCUETP8M1_13TeV_calchep-pythia8'] if version=='76X' else ['HPlusPlusHMinusHTo3L_M-1400_13TeV-calchep-pythia8']
    sigMaps[sigMap]['HppHm1500GeV']  = ['HPlusPlusHMinusHTo3L_M-1500_TuneCUETP8M1_13TeV_calchep-pythia8'] if version=='76X' else ['HPlusPlusHMinusHTo3L_M-1500_13TeV-calchep-pythia8']

##################
### Selections ###
##################
#selections = {
#    'old' : {
#        'Hpp3l': {
#            0: {
#                'st'   : 'hpp1_pt+hpp2_pt+hm1_pt>1.07*{mass}+45',
#                'zveto': 'fabs(z_mass-{0})>80'.format(ZMASS),
#                'dr'   : '(h{sign}_mass<400 ? h{sign}_deltaR<{mass}/380.+2.06 : h{sign}_deltaR<{mass}/1200.+2.77)',
#                'mass' : 'h{sign}_mass>0.9*{mass} && h{sign}_mass<1.1*{mass}',
#            },
#            1: {
#                'st'   : 'hpp1_pt+hpp2_pt+hm1_pt>0.72*{mass}+50',
#                'zveto': 'fabs(z_mass-{0})>80'.format(ZMASS),
#                'met'  : 'met_pt>20',
#                'dr'   : '(h{sign}_mass<400 ? h{sign}_deltaR<{mass}/380.+1.96 : h{sign}_deltaR<{mass}/1000.+2.6)',
#                'mass' : 'h{sign}_mass>0.5*{mass} && h{sign}_mass<1.1*{mass}',
#            },
#            2: {
#                'st'   : 'hpp1_pt+hpp2_pt+hm1_pt>0.44*{mass}+65',
#                'zveto': 'fabs(z_mass-{0})>50'.format(ZMASS),
#                'met'  : 'met_pt>20',
#                'dr'   : '(h{sign}_mass<400 ? h{sign}_deltaR<{mass}/380.+1.86 : h{sign}_deltaR<{mass}/750.+2.37)',
#                'mass' : 'h{sign}_mass>0.5*{mass} && h{sign}_mass<1.1*{mass}',
#            },
#        },
#        'Hpp4l': {
#            0: {
#                'st'   : 'hpp1_pt+hpp2_pt+hmm1_pt+hmm2_pt>0.6*{mass}+130',
#                'mass' : 'h{sign}_mass>0.9*{mass} && h{sign}_mass<1.1*{mass}',
#            },
#            1: {
#                'st'   : '(hpp1_pt+hpp2_pt+hmm1_pt+hmm2_pt>{mass}+100 || hpp1_pt+hpp2_pt+hmm1_pt+hmm2_pt>400)',
#                'zveto': 'fabs(z_mass-{0})>10'.format(ZMASS),
#                'mass' : 'h{sign}_mass>0.5*{mass} && h{sign}_mass<1.1*{mass}',
#            },
#            2: {
#                'st'   : '(hpp1_pt+hpp2_pt+hmm1_pt+hmm2_pt>120)',
#                'zveto': 'fabs(z_mass-{0})>50'.format(ZMASS),
#                'dr'   : 'h{sign}_deltaR<{mass}/1400.+2.43',
#                'mass' : 'h{sign}_mass>0.5*{mass} && h{sign}_mass<1.1*{mass}',
#            },
#        },
#    },
#    'new' : {
#        'Hpp3l': {
#            0: {
#                #'st'   : 'hpp1_pt+hpp2_pt+hm1_pt>0.81*{mass}+88',
#                'st'   : 'hpp1_pt+hpp2_pt+hm1_pt>0.99*{mass}-35',
#                #'zveto': 'fabs(z_mass-{0})>80'.format(ZMASS),
#                'zveto': 'fabs(z_mass-{0})>10'.format(ZMASS),
#                #'dr'   : '(h{sign}_mass<400 ? h{sign}_deltaR<{mass}/380.+2.06 : h{sign}_deltaR<{mass}/1200.+2.77)',
#                'mass' : 'h{sign}_mass>0.9*{mass} && h{sign}_mass<1.1*{mass}',
#            },
#            1: {
#                #'st'   : 'hpp1_pt+hpp2_pt+hm1_pt>0.58*{mass}+85',
#                'st'   : 'hpp1_pt+hpp2_pt+hm1_pt>1.15*{mass}+2',
#                #'zveto': 'fabs(z_mass-{0})>80'.format(ZMASS),
#                'zveto': 'fabs(z_mass-{0})>20'.format(ZMASS),
#                'met'  : 'met_pt>20',
#                #'dr'   : '(h{sign}_mass<400 ? h{sign}_deltaR<{mass}/380.+1.96 : h{sign}_deltaR<{mass}/1000.+2.6)',
#                'dr'   : 'h{sign}_deltaR<3.2',
#                'mass' : 'h{sign}_mass>0.4*{mass} && h{sign}_mass<1.1*{mass}',
#            },
#            2: {
#                #'st'   : 'hpp1_pt+hpp2_pt+hm1_pt>0.35*{mass}+81',
#                'st'   : 'hpp1_pt+hpp2_pt+hm1_pt>0.98*{mass}+91',
#                #'zveto': 'fabs(z_mass-{0})>50'.format(ZMASS),
#                'zveto': 'fabs(z_mass-{0})>25'.format(ZMASS),
#                #'met'  : 'met_pt>20',
#                'met'  : 'met_pt>50',
#                'dr'   : '(h{sign}_mass<400 ? h{sign}_deltaR<{mass}/380.+1.86 : h{sign}_deltaR<{mass}/750.+2.37)',
#                'mass' : 'h{sign}_mass>0.3*{mass} && h{sign}_mass<1.1*{mass}',
#            },
#        },
#        'Hpp4l': {
#            0: {
#                'st'   : 'hpp1_pt+hpp2_pt+hmm1_pt+hmm2_pt>1.23*{mass}+54',
#                'mass' : 'h{sign}_mass>0.9*{mass} && h{sign}_mass<1.1*{mass}',
#            },
#            1: {
#                'st'   : 'hpp1_pt+hpp2_pt+hmm1_pt+hmm2_pt>0.88*{mass}+73',
#                'zveto': 'fabs(z_mass-{0})>10'.format(ZMASS),
#                'mass' : 'h{sign}_mass>0.4*{mass} && h{sign}_mass<1.1*{mass}',
#            },
#            2: {
#                'st'   : 'hpp1_pt+hpp2_pt+hmm1_pt+hmm2_pt>0.46*{mass}+108',
#                #'zveto': 'fabs(z_mass-{0})>50'.format(ZMASS),
#                'zveto': 'fabs(z_mass-{0})>25'.format(ZMASS),
#                'dr'   : 'h{sign}_deltaR<{mass}/1400.+2.43',
#                'mass' : 'h{sign}_mass>0.3*{mass} && h{sign}_mass<1.1*{mass}',
#            },
#        },
#    },
#}

def getSelectionMap(analysis,mass):
    if analysis=='Hpp3l':
        cutRegions = {
            0: {
                'st'   : lambda row: (row.hpp1_pt+row.hpp2_pt+row.hm1_pt)>1.38*mass-94,
                'zveto': lambda row: abs(row.z_mass-ZMASS)>10,
                'met'  : lambda row: True,
                'dr'   : lambda row: row.hpp_deltaR<2.9,
                'mass' : lambda row: row.hpp_mass>0.9*mass and row.hpp_mass<1.1*mass,
            },
            1: {
                'st'   : lambda row: (row.hpp1_pt+row.hpp2_pt+row.hm1_pt)>1.07*mass+36,
                'zveto': lambda row: abs(row.z_mass-ZMASS)>10,
                'met'  : lambda row: row.met_pt>80,
                'dr'   : lambda row: row.hpp_deltaR<2.9,
                'mass' : lambda row: row.hpp_mass>0.4*mass and row.hpp_mass<1.1*mass,
            },
            2: {
                'st'   : lambda row: (row.hpp1_pt+row.hpp2_pt+row.hm1_pt)>1.24*mass-14,
                'zveto': lambda row: abs(row.z_mass-ZMASS)>10,
                'met'  : lambda row: row.met_pt>80,
                'dr'   : lambda row: row.hpp_deltaR<2.5,
                'mass' : lambda row: row.hpp_mass>0.3*mass and row.hpp_mass<1.1*mass,
            },
        }
    elif analysis=='Hpp4l':
        cutRegions = {
            0: {
                'st'   : lambda row: (row.hpp1_pt+row.hpp2_pt+row.hmm1_pt+row.hmm2_pt)>1.23*mass+54,
                'zveto': lambda row: abs(row.z_mass-ZMASS)>10,
                'drpp' : lambda row: True,
                'drmm' : lambda row: True,
                'hpp'  : lambda row: row.hpp_mass>0.9*mass and row.hpp_mass<1.1*mass,
                'hmm'  : lambda row: row.hmm_mass>0.9*mass and row.hmm_mass<1.1*mass,
            },
            1: {
                'st'   : lambda row: (row.hpp1_pt+row.hpp2_pt+row.hmm1_pt+row.hmm2_pt)>1.30*mass-34,
                'zveto': lambda row: abs(row.z_mass-ZMASS)>10,
                'drpp' : lambda row: row.hpp_deltaR<3.3,
                'drmm' : lambda row: row.hmm_deltaR<3.3,
                'hpp'  : lambda row: row.hpp_mass>0.4*mass and row.hpp_mass<1.1*mass,
                'hmm'  : lambda row: row.hmm_mass>0.4*mass and row.hmm_mass<1.1*mass,
            },
            2: {
                'st'   : lambda row: (row.hpp1_pt+row.hpp2_pt+row.hmm1_pt+row.hmm2_pt)>0.56*mass+194,
                'zveto': lambda row: abs(row.z_mass-ZMASS)>10,
                'drpp' : lambda row: row.hpp_deltaR<2.5,
                'drmm' : lambda row: row.hmm_deltaR<2.5,
                'hpp'  : lambda row: row.hpp_mass>0.3*mass and row.hpp_mass<1.1*mass,
                'hmm'  : lambda row: row.hmm_mass>0.3*mass and row.hmm_mass<1.1*mass,
            },
        }

    else:
        cutRegions = {}
    return cutRegions

###########################
### Functions to access ###
###########################
#def getSelections(analysis,mass,nTaus=[0,0],cuts=['st','zveto','met','dr','mass'],invcuts=[],mode='old'):
#    selString = ''
#    if analysis=='Hpp3l':
#        # hpp/hmm
#        cutMap = selections[mode][analysis][nTaus[0]]
#        cutlist = []
#        cutlist += [cutMap[cutName].format(sign='pp',mass=mass) for cutName in cuts if cutName in cutMap]
#        cutlist += ['!({0})'.format(cutMap[cutName].format(sign='pp',mass=mass)) for cutName in invcuts if cutName in cutMap]
#        selString = ' && '.join(cutlist)
#    if analysis=='Hpp4l':
#        cutlist = []
#        for cut in cuts:
#            if cut in ['st','zveto','met']:
#                cutMap = selections[mode][analysis][max(nTaus)]
#                if cut in cutMap: cutlist += [cutMap[cut].format(mass=mass)]
#            else:
#                cutMapPP = selections[mode][analysis][nTaus[0]]
#                cutMapMM = selections[mode][analysis][nTaus[1]]
#                if cut in cutMapPP: cutlist += [cutMapPP[cut].format(sign='pp',mass=mass)]
#                if cut in cutMapMM: cutlist += [cutMapMM[cut].format(sign='mm',mass=mass)]
#        for cut in invcuts:
#            if cut in ['st','zveto','met']:
#                cutMap = selections[mode][analysis][max(nTaus)]
#                if cut in cutMap: cutlist += ['!({0})'.format(cutMap[cut].format(mass=mass))]
#            else:
#                cutMapPP = selections[mode][analysis][nTaus[0]]
#                cutMapMM = selections[mode][analysis][nTaus[1]]
#                if cut in cutMapPP and cut in cutMapMM: cutlist += ['!({0} && {1})'.format(cutMapPP[cut].format(sign='pp',mass=mass),cutMapMM[cut].format(sign='mm',mass=mass))]
#        selString = ' && '.join(cutlist)
#    return selString
        

def getSigMap(analysis,datadriven=False):
    '''Get a map of plot keys to sample names.'''
    return sigMaps[analysis+'DataDriven'] if datadriven else sigMaps[analysis]

def getScales(mode):
    return scales[mode]

def getCategories(analysis):
    '''Get categories'''
    return cats

def getCategoryLabels(analysis):
    '''Get category labels'''
    return catLabels

def getSubCategories(analysis):
    '''Get subcategories'''
    return subCatChannels[analysis] if analysis in subCatChannels else {}

def getSubCategoryLabels(analysis):
    '''Get subcategory labels'''
    if analysis not in subCatLabelMap: return []
    subCatLabelList = []
    for cat in cats:
        for subCat in sorted(subCatLabelMap[analysis][cat]):
            subCatLabelList += [subCatLabelMap[analysis][cat][subCat]]
    return subCatLabelList

def getChannels(analysis):
    '''Get channel strings for analysis'''
    if analysis=='Hpp4l':
        return chans4l
    if analysis=='Hpp3l':
        return chans3l
    return {}

def getChannelLabels(analysis):
    '''Get channel labels'''
    labelMap = {
        'e': 'e',
        'm': '#mu',
        't': '#tau',
    }
    chanLabels = [''.join([labelMap[c] for c in chan]) for chan in sorted(getChannels(analysis).keys())]
    return chanLabels

def getGenChannels(analysis):
    return {'PP':genChannelsPP,'AP':genChannelsAP}

goodMap = {
    'ee': ['ee'],
    'em': ['em'],
    'mm': ['mm'],
    'et': ['ee','em','et'],
    'mt': ['em','mm','mt'],
    'tt': ['ee','em','et','mm','mt','tt'],
    'e': ['e'],
    'm': ['m'],
    't': ['e','m','t'],
}

def getGenRecoChannelMap(analysis):
    '''A map of gen channels and possible reco channels
    A tau (t) can be either an electron (e) or muon (m) at reco.
    For Hpp4l:
        4 gen leptons -> 4 reco leptons
    For Hpp3l:
        3 gen leptons -> 3 reco leptons
        4 gen leptons -> 3 reco leptons
           * special case, a lepton is lost
           here the first two reco must match either
           the first pair gen or the second pair gen
           the third reco must match one of the other pair
    '''
    theMap = {}
    for gen in genChannelsPP:
        theMap[gen] = []
        if analysis=='Hpp4l':
            for reco in chans4l:
                hpp = reco[:2]
                hmm = reco[2:]
                if hpp in goodMap[gen[:2]] and hmm in goodMap[gen[2:]]:
                    theMap[gen] += [reco]
                #good = True
                #for r,lep in enumerate(reco):
                #    if not (lep==gen[r] or gen[r]=='t'):
                #        good = False
                #if good:
                #    theMap[gen] += [reco]
        if analysis=='Hpp3l':
            for reco in chans3l:
                hpp = reco[:2]
                hm = reco[2:]
                if hpp in goodMap[gen[:2]] and hm in goodMap[gen[2:3]]+goodMap[gen[3:4]]:
                    theMap[gen] += [reco]
                elif hpp in goodMap[gen[2:]] and hm in goodMap[gen[:1]]+goodMap[gen[1:2]]:
                    theMap[gen] += [reco]
                #good = False
                #if ((reco[0]==gen[0] or gen[0]=='t')
                #    and (reco[1]==gen[1] or gen[1]=='t')
                #    and (reco[2] in gen[2:] or 't' in gen[2:])): # matches first
                #        good = True
                #if ((reco[0]==gen[2] or gen[2]=='t')
                #    and (reco[1]==gen[3] or gen[3]=='t')
                #    and (reco[2] in gen[:2] or 't' in gen[:2])): # matches second
                #        good = True
                #if good:
                #    theMap[gen] += [reco]
    for gen in genChannelsAP:
        theMap[gen] = []
        if analysis=='Hpp3l':
            for reco in chans3l:
                hpp = reco[:2]
                hm = reco[2:]
                if hpp in goodMap[gen[:2]] and hm in goodMap[gen[2:3]]:
                    theMap[gen] += [reco]
    return theMap
