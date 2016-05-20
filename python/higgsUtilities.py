from itertools import product, combinations_with_replacement
import numpy as np

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
             #'DY1JetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
             #'DY2JetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
             'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8',
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

###########################
### Functions to access ###
###########################
def getSigMap(analysis):
    '''Get a map of plot keys to sample names.'''
    return sigMap

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

def getGenRecoChannelMap(analysis):
    theMap = {}
    for gen in genChannelsPP:
        theMap[gen] = []
        for reco in chans4l:
            good = True
            for r,lep in enumerate(reco):
                if not (lep==gen[r] or gen[r]=='t'):
                    good = False
            if good:
                theMap[gen] += [reco]
    return theMap
