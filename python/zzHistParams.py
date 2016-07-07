from copy import deepcopy
from itertools import product, combinations_with_replacement

from DevTools.Plotter.utilities import ZMASS, addChannels

from DevTools.Utilities.utilities import getCMSSWVersion

version = getCMSSWVersion()

genCut = '{0}_genMatch==1 && {0}_genDeltaR<0.1'

def buildZZ(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams):

    # histogram definitions
    histParams['ZZ'] = {
        'count'                       : {'xVariable': '1',                              'xBinning': [1,0,2],                }, # just a count of events passing selection
        'numVertices'                 : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],              },
        'numVertices_noreweight'      : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': '1./pileupWeight'},
        'met'                         : {'xVariable': 'met_pt',                         'xBinning': [50, 0, 500],           },
        'metPhi'                      : {'xVariable': 'met_phi',                        'xBinning': [50, -3.14159, 3.14159],},
        # z1
        'z1Mass'                      : {'xVariable': 'z1_mass',                        'xBinning': [160, 0, 1600],         },
        'z1Pt'                        : {'xVariable': 'z1_pt',                          'xBinning': [160, 0, 1600],         },
        'z1Eta'                       : {'xVariable': 'z1_eta',                         'xBinning': [100, -5, 5],           },
        'z1DeltaR'                    : {'xVariable': 'z1_deltaR',                      'xBinning': [50, 0, 5],             },
        'z1LeadingLeptonPt'           : {'xVariable': 'z11_pt',                         'xBinning': [100, 0, 1000],         },
        'z1LeadingLeptonEta'          : {'xVariable': 'z11_eta',                        'xBinning': [50, -2.5, 2.5],        },
        'z1SubLeadingLeptonPt'        : {'xVariable': 'z12_pt',                         'xBinning': [100, 0, 1000],         },
        'z1SubLeadingLeptonEta'       : {'xVariable': 'z12_eta',                        'xBinning': [50, -2.5, 2.5],        },
        # z2
        'z2Mass'                      : {'xVariable': 'z2_mass',                        'xBinning': [160, 0, 1600],         },
        'z2Pt'                        : {'xVariable': 'z2_pt',                          'xBinning': [160, 0, 1600],         },
        'z2Eta'                       : {'xVariable': 'z2_eta',                         'xBinning': [100, -5, 5],           },
        'z2DeltaR'                    : {'xVariable': 'z2_deltaR',                      'xBinning': [50, 0, 5],             },
        'z2LeadingLeptonPt'           : {'xVariable': 'z21_pt',                         'xBinning': [100, 0, 1000],         },
        'z2LeadingLeptonEta'          : {'xVariable': 'z21_eta',                        'xBinning': [50, -2.5, 2.5],        },
        'z2SubLeadingLeptonPt'        : {'xVariable': 'z22_pt',                         'xBinning': [100, 0, 1000],         },
        'z2SubLeadingLeptonEta'       : {'xVariable': 'z22_eta',                        'xBinning': [50, -2.5, 2.5],        },
        # event
        'mass'                        : {'xVariable': '4l_mass',                        'xBinning': [200, 0, 2000],         },
        'st'                          : {'xVariable': 'z11_pt+z12_pt+z21_pt+z22_pt',    'xBinning': [200, 0, 2000],         },
        'nJets'                       : {'xVariable': 'numJetsTight30',                 'xBinning': [11, -0.5, 10.5],        },
    }


    
    # setup the reco channels
    channels = {'eeee':['eeee'],'eemm':['eemm','mmee'],'mmmm':['mmmm']}
    projectionParams['ZZ'] = {}
    allChans = []
    for chan in channels:
        projectionParams['ZZ'][chan] = channels[chan]
        allChans += channels[chan]
    histParams['ZZ'].update(addChannels(deepcopy(histParams['ZZ']),'channel',len(allChans)))
    
    # setup base selections
    zzBaseCut = '1'
    zWindow = 'z1_mass>60 && z1_mass<120 && z2_mass>60 && z2_mass<120'
    zzScaleFactor = 'z11_mediumScale*z12_mediumScale*z21_mediumScale*z22_mediumScale*genWeight*pileupWeight*triggerEfficiency'
    
    # setup fakerate selections
    leps = ['z11','z12','z21','z22']
    scaleMap = {
        'P' : '{0}_looseScale',
        'F' : '{0}_mediumScale',
    }
    
    zzBaseScaleFactor = 'genWeight*pileupWeight*triggerEfficiency'
    zzMCCut = ' && '.join([genCut.format(l) for l in leps])
    
    # build the cuts for each fake region
    zzScaleFactorMap = {}
    zzFakeScaleFactorMap = {}
    zzCutMap = {}
    zzFakeRegions = [''.join(x) for x in product('PF',repeat=4)]
    fakeModes = {
        0 : [],
        1 : [],
        2 : [],
        3 : [],
        4 : [],
    }
    for region in zzFakeRegions:
        fakeModes[region.count('F')] += [region]
        zzScaleFactorMap[region] = '*'.join([scaleMap[region[x]].format(leps[x]) for x in range(4)])
        zzFakeScaleFactorMap[region] = '*'.join(['({0}/(1-{0}))'.format('{0}_mediumFakeRate'.format(leps[x])) for x in range(4) if region[x]=='F'] + ['-1' if region.count('F')%2==0 and region.count('F')>0 else '1'])
        zzCutMap[region] = '(' + ' && '.join(['{0}=={1}'.format('{0}_passMedium'.format(leps[x]),1 if region[x]=='P' else 0) for x in range(4)]) + ')'
    
    # the default selections
    selectionParams['ZZ'] = {
        'default'   : {'args': [zzBaseCut + ' && ' + zzCutMap['PPPP']],                    'kwargs': {'mcscalefactor': zzScaleFactor}},
        'zWindow'   : {'args': [zzBaseCut + ' && ' + zzCutMap['PPPP'] + ' && ' + zWindow], 'kwargs': {'mcscalefactor': zzScaleFactor}},
    }
    
    # fake regions via modes
    for nf in range(5):
        name = '{0}P{1}F'.format(4-nf,nf)
        name_regular = '{0}P{1}F_regular'.format(4-nf,nf)
        regionCut = '(' + ' || '.join([zzCutMap[reg] for reg in fakeModes[nf]]) + ')'
        regionMCScaleFactor = '*'.join(['({0} ? {1}*{2}*{3}*{4} : 1)'.format(zzCutMap[reg],zzScaleFactorMap[reg],zzFakeScaleFactorMap[reg],zzBaseScaleFactor,'1' if reg=='PPPP' else '-1') for reg in fakeModes[nf]])
        regionMCScaleFactor_regular = '*'.join(['({0} ? {1}*{2} : 1)'.format(zzCutMap[reg],zzScaleFactorMap[reg],zzBaseScaleFactor) for reg in fakeModes[nf]])
        regionDataScaleFactor = '*'.join(['({0} ? {1} : 1)'.format(zzCutMap[reg],zzFakeScaleFactorMap[reg]) for reg in fakeModes[nf]])
        # fake scaled
        selectionParams['ZZ'][name] = {
            'args': [zzBaseCut + ' && ' + regionCut],
            'kwargs': {
                'mccut': zzMCCut,
                'mcscalefactor': regionMCScaleFactor,
                'datascalefactor': regionDataScaleFactor,
            }
        }
        selectionParams['ZZ']['{0}/zWindow'.format(name)] = {
            'args': [zWindow + ' && ' + regionCut],
            'kwargs': {
                'mccut': zzMCCut,
                'mcscalefactor': regionMCScaleFactor,
                'datascalefactor': regionDataScaleFactor,
            }
        }
        # regular for validation
        selectionParams['ZZ'][name_regular] = {
            'args': [zzBaseCut + ' && ' + regionCut],
            'kwargs': {
                'mcscalefactor': regionMCScaleFactor_regular,
            }
        }
        selectionParams['ZZ']['{0}/lowmass'.format(name_regular)] = {
            'args': [zWindow + ' && ' + regionCut],
            'kwargs': {
                'mcscalefactor': regionMCScaleFactor_regular,
            }
        }
    
    
    # special selections for samples
    # DY-10 0, 1, 2 bins (0 includes 3+)
    # DY-50 0, 1, 2, 3, 4 bins (0 includes 5+)
    sampleCuts = {
        #'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8' : '(numGenJets==0 || numGenJets>2)',
        #'DY1JetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8': 'numGenJets==1',
        #'DY2JetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8': 'numGenJets==2',
        'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'      : '(numGenJets==0 || numGenJets>4)',
        'DY1JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : 'numGenJets==1',
        'DY2JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : 'numGenJets==2',
        'DY3JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : 'numGenJets==3',
        'DY4JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : 'numGenJets==4',
        'WJetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'           : '(numGenJets==0 || numGenJets>4)',
        'W1JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          : 'numGenJets==1',
        'W2JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          : 'numGenJets==2',
        'W3JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          : 'numGenJets==3',
        'W4JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          : 'numGenJets==4',
    }
    sampleSelectionParams['ZZ'] = {}
    for sample,cut in sampleCuts.iteritems():
        sampleSelectionParams['ZZ'][sample] = deepcopy(selectionParams['ZZ'])
        for sel in selectionParams['ZZ'].keys():
            sampleSelectionParams['ZZ'][sample][sel]['args'][0] += ' && {0}'.format(cut)
    
