from copy import deepcopy
from itertools import product, combinations_with_replacement

from DevTools.Plotter.utilities import ZMASS, addChannels

from DevTools.Utilities.utilities import getCMSSWVersion

version = getCMSSWVersion()

genCut = '{0}_genMatch==1 && {0}_genDeltaR<0.1'
genStatusOneCut = '{0}_genMatch==1 && {0}_genStatus==1 && {0}_genDeltaR<0.1'

def buildWZ(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams):

    histParams['WZ'] = {
        'count'                       : {'xVariable': '1',                              'xBinning': [1,0,2],                 }, # just a count of events passing selection
        'numVertices'                 : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],               },
        'numVertices_noreweight'      : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': '1./pileupWeight'},
        'met'                         : {'xVariable': 'met_pt',                         'xBinning': [500, 0, 500],           },
        'metPhi'                      : {'xVariable': 'met_phi',                        'xBinning': [500, -3.14159, 3.14159],},
        # z
        'zMass'                       : {'xVariable': 'z_mass',                         'xBinning': [500, 0, 500],           },
        'mllMinusMZ'                  : {'xVariable': 'fabs(z_mass-{0})'.format(ZMASS), 'xBinning': [200, 0, 200],           },
        'zPt'                         : {'xVariable': 'z_pt',                           'xBinning': [500, 0, 500],           },
        'zDeltaR'                     : {'xVariable': 'z_deltaR',                       'xBinning': [500, 0, 5],             },
        'zLeadingLeptonPt'            : {'xVariable': 'z1_pt',                          'xBinning': [500, 0, 500],           },
        'zLeadingLeptonEta'           : {'xVariable': 'z1_eta',                         'xBinning': [500, -2.5, 2.5],        },
        'zSubLeadingLeptonPt'         : {'xVariable': 'z2_pt',                          'xBinning': [500, 0, 500],           },
        'zSubLeadingLeptonEta'        : {'xVariable': 'z2_eta',                         'xBinning': [500, -2.5, 2.5],        },
        # w
        'wMass'                       : {'xVariable': 'w_mt',                           'xBinning': [500, 0, 500],           },
        'wPt'                         : {'xVariable': 'w_pt',                           'xBinning': [500, 0, 500],           },
        'wLeptonPt'                   : {'xVariable': 'w1_pt',                          'xBinning': [500, 0, 500],           },
        'wLeptonEta'                  : {'xVariable': 'w1_eta',                         'xBinning': [500, -2.5, 2.5],        },
        # event
        'mass'                        : {'xVariable': '3l_mass',                        'xBinning': [500, 0, 500],           },
        'nJets'                       : {'xVariable': 'numJetsTight30',                 'xBinning': [11, -0.5, 10.5],        },
        'nBjets'                      : {'xVariable': 'numBjetsTight30',                'xBinning': [10, 0, 10],             },
    }

    # setup the reco channels
    channels = ['eee','eem','mme','mmm']
    projectionParams['WZ'] = {}
    for chan in channels:
        projectionParams['WZ'][chan] =[chan]
    histParams['WZ'].update(addChannels(deepcopy(histParams['WZ']),'channel',len(channels)))
    
    # the cuts
    baseCutMap = {
        'zptCut'   : 'z1_pt>20 && z2_pt>10',
        'wptCut'   : 'w1_pt>20',
        'bvetoCut' : 'numBjetsTight30==0',
        'metCut'   : 'met_pt>30',
        'zmassCut' : 'fabs(z_mass-{0})<15'.format(ZMASS),
        '3lmassCut': '3l_mass>100',
    }
    wzBaseCut = ' && '.join([baseCutMap[x] for x in sorted(baseCutMap.keys())])
    wzBaseScaleFactor = 'genWeight*pileupWeight*triggerEfficiency'
    wzMCCut = ' && '.join([genStatusOneCut.format(l) for l in ['z1','z2','w1']])
    
    # definitions for scale/selection in fake regions
    wzTightVar = {
        0: 'z1_passMedium',
        1: 'z2_passMedium',
        2: 'w1_passTight',
    }
    
    wzTightScale = {
        0: 'z1_mediumScale',
        1: 'z2_mediumScale',
        2: 'w1_tightScale',
    }
    
    wzLooseScale = {
        0: 'z1_looseScale',
        1: 'z2_looseScale',
        2: 'w1_looseScale',
    }
    
    wzFakeRate = {
        0: 'z1_mediumFakeRate',
        1: 'z2_mediumFakeRate',
        2: 'w1_tightFakeRate',
    }
    
    wzScaleMap = {
        'P': wzTightScale,
        'F': wzLooseScale,
    }
    
    # build the cuts for each fake region
    wzScaleFactorMap = {}
    wzFakeScaleFactorMap = {}
    wzCutMap = {}
    fakeRegions = ['PPP','PPF','PFP','FPP','PFF','FPF','FFP','FFF']
    for region in fakeRegions:
        wzScaleFactorMap[region] = '*'.join([wzScaleMap[region[x]][x] for x in range(3)])
        wzFakeScaleFactorMap[region] = '*'.join(['{0}/(1-{0})'.format(wzFakeRate[f]) for f in range(3) if region[f]=='F'] + ['-1' if region.count('F')%2==0 and region.count('F')>0 else '1'])
        wzCutMap[region] = ' && '.join(['{0}=={1}'.format(wzTightVar[x],1 if region[x]=='P' else 0) for x in range(3)])
    
    # dy/tt all loose
    wzScaleFactorMap['loose'] = '*'.join(['{0}_looseScale'.format(x) for x in ['z1','z2','w1']])
    wzScaleFactorMap['medium'] = '*'.join(['{0}_mediumScale'.format(x) for x in ['z1','z2','w1']])
    wzScaleFactorMap['tight'] = '*'.join(['{0}_tightScale'.format(x) for x in ['z1','z2','w1']])
    dySimpleCut = 'z1_pt>20 && z2_pt>10 && w1_pt>20 && fabs(z_mass-{0})<15 && 3l_mass>100 && met_pt<25 && w_mt<25'.format(ZMASS)
    ttSimpleCut = 'z1_pt>20 && z2_pt>10 && w1_pt>20 && fabs(z_mass-{0})>5 && 3l_mass>100 && numBjetsTight30>0'.format(ZMASS)
    wzCutMap['dy'] = dySimpleCut
    wzCutMap['tt'] = ttSimpleCut
    
    # base selections (no gen matching)
    selectionParams['WZ'] = {
        'default' : {'args': [wzCutMap['PPP']+' && '+wzBaseCut], 'kwargs': {'mcscalefactor': '*'.join([wzScaleFactorMap['PPP'],wzBaseScaleFactor])}},
        'dy'      : {'args': [wzCutMap['dy']],                   'kwargs': {'mcscalefactor': '*'.join([wzScaleFactorMap['loose'],wzBaseScaleFactor]),}},
        'tt'      : {'args': [wzCutMap['tt']],                   'kwargs': {'mcscalefactor': '*'.join([wzScaleFactorMap['loose'],wzBaseScaleFactor]),}},
    }
    
    # fake regions, gen match leptons in MC
    for region in fakeRegions:
        selectionParams['WZ'][region] = {
            'args': [wzBaseCut + ' && ' + wzCutMap[region]],
            'kwargs': {
                'mccut': wzMCCut,
                'mcscalefactor': '*'.join([wzScaleFactorMap[region],wzFakeScaleFactorMap[region],wzBaseScaleFactor,'1' if region=='PPP' else '-1']),
                'datascalefactor': wzFakeScaleFactorMap[region],
            }
        }
        for control in ['dy','tt']:
            selectionParams['WZ']['{0}/{1}'.format(region,control)] = {
                'args': [wzCutMap[region] + ' && ' + wzCutMap[control]],
                'kwargs': {
                    'mccut': wzMCCut,
                    'mcscalefactor': '*'.join([wzScaleFactorMap[region],wzFakeScaleFactorMap[region],wzBaseScaleFactor,'1' if region=='PPP' else '-1']),
                    'datascalefactor': wzFakeScaleFactorMap[region],
                }
            }
    
    # n-1 plots
    for baseCut in baseCutMap:
        nMinusOneCut = ' && '.join([cut for key,cut in sorted(baseCutMap.iteritems()) if key!=baseCut])
        selectionParams['WZ']['default/{0}'.format(baseCut)] = {
            'args': [nMinusOneCut + ' && ' + wzCutMap['PPP']],
            'kwargs': {
                'mcscalefactor': '*'.join([wzScaleFactorMap['PPP'],wzBaseScaleFactor]),
            }
        }
        for region in fakeRegions:
            selectionParams['WZ']['{0}/{1}'.format(region,baseCut)] = {
                'args': [nMinusOneCut + ' && ' + wzCutMap[region]],
                'kwargs': {
                    'mccut': wzMCCut,
                    'mcscalefactor': '*'.join([wzScaleFactorMap[region],wzFakeScaleFactorMap[region],wzBaseScaleFactor,'1' if region=='PPP' else '-1']),
                    'datascalefactor': wzFakeScaleFactorMap[region],
                }
            }

