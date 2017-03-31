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
        'numVertices'                 : {'xVariable': 'numVertices',                    'xBinning': [60,0,60],               },
        'met'                         : {'xVariable': 'met_pt',                         'xBinning': [500, 0, 500],           },
        'metPhi'                      : {'xVariable': 'met_phi',                        'xBinning': [500, -3.14159, 3.14159],},
        # z
        'zMass'                       : {'xVariable': 'z_mass',                         'xBinning': [500, 0, 500],           },
        #'mllMinusMZ'                  : {'xVariable': 'fabs(z_mass-{0})'.format(ZMASS), 'xBinning': [200, 0, 200],           },
        'zPt'                         : {'xVariable': 'z_pt',                           'xBinning': [500, 0, 500],           },
        #'zDeltaR'                     : {'xVariable': 'z_deltaR',                       'xBinning': [500, 0, 5],             },
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
        # vbf
        'leadJetPt'                   : {'xVariable': 'leadJet_pt',                     'xBinning': [500, 0, 500],           'selection': 'leadJet_pt>0.',},
        'subleadJetPt'                : {'xVariable': 'subleadJet_pt',                  'xBinning': [500, 0, 500],           'selection': 'subleadJet_pt>0.',},
        'dijetMass'                   : {'xVariable': 'dijet_mass',                     'xBinning': [2000, 0, 2000],         'selection': 'dijet_mass>0.',},
        'dijetDEta'                   : {'xVariable': 'dijet_deltaEta',                 'xBinning': [100, 0, 10],            'selection': 'dijet_deltaEta>0.'},
    }

    # setup the reco channels
    channels = ['eee','eem','mme','mmm']
    projectionParams['WZ'] = {}
    for chan in channels:
        projectionParams['WZ'][chan] =[chan]
    histParams['WZ'].update(addChannels(deepcopy(histParams['WZ']),'channel',len(channels)))
    
    # the cuts
    baseCutMap = {
        'zptCut'   : 'z1_pt>25 && z2_pt>15',
        'wptCut'   : 'w1_pt>20',
        'bvetoCut' : 'numBjetsTight30==0',
        'metCut'   : 'met_pt>30',
        'zmassCut' : 'fabs(z_mass-{0})<15'.format(ZMASS),
        'wmllCut'  : 'w1_z1_mass>4 && w1_z2_mass>4',
        '3lmassCut': '3l_mass>100',
    }
    wzBaseCut = ' && '.join([baseCutMap[x] for x in sorted(baseCutMap.keys())])
    wzBaseScaleFactor = 'genWeight*pileupWeight*triggerEfficiency'
    wzMCCut = ' && '.join([genStatusOneCut.format(l) for l in ['z1','z2','w1']])
    vbsCutMap = {
        'twoJets' : 'dijet_mass>0.',
        'jetPt'   : 'leadJet_pt>50. && subleadJet_pt>50.',
        'jetDEta' : 'dijet_deltaEta>2.5',
        'mjj'     : 'dijet_mass>400.',
    }
    wzVBSCut = ' && '.join([vbsCutMap[x] for x in sorted(vbsCutMap.keys())])
    
    # definitions for scale/selection in fake regions
    wzTightVar = {
        0: 'z1_passTight',
        1: 'z2_passTight',
        2: 'w1_passTight',
    }
    
    wzTightScale = {
        0: 'z1_tightScale',
        1: 'z2_tightScale',
        2: 'w1_tightScale',
    }
    
    wzLooseScale = {
        0: 'z1_looseScale',
        1: 'z2_looseScale',
        2: 'w1_looseScale',
    }
    
    wzFakeRate = {
        0: 'z1_tightFakeRate',
        1: 'z2_tightFakeRate',
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
    dySimpleCut = 'z1_pt>25 && z2_pt>15 && w1_pt>20 && fabs(z_mass-{0})<15 && 3l_mass>100 && met_pt<25 && w_mt<25'.format(ZMASS)
    ttSimpleCut = 'z1_pt>25 && z2_pt>15 && w1_pt>20 && fabs(z_mass-{0})>5 && 3l_mass>100 && numBjetsTight30>0'.format(ZMASS)
    wzCutMap['dy'] = dySimpleCut
    wzCutMap['tt'] = ttSimpleCut
    
    # base selections (no gen matching)
    selectionParams['WZ'] = {
        'default' : {'args': [wzCutMap['PPP']+' && '+wzBaseCut],                 'kwargs': {'mcscalefactor': '*'.join([wzScaleFactorMap['PPP'],wzBaseScaleFactor])}},
        'vbs'     : {'args': [wzCutMap['PPP']+' && '+wzBaseCut+' && '+wzVBSCut], 'kwargs': {'mcscalefactor': '*'.join([wzScaleFactorMap['PPP'],wzBaseScaleFactor])}},
        'dy'      : {'args': [wzCutMap['dy']],                                   'kwargs': {'mcscalefactor': '*'.join([wzScaleFactorMap['loose'],wzBaseScaleFactor]),}},
        'tt'      : {'args': [wzCutMap['tt']],                                   'kwargs': {'mcscalefactor': '*'.join([wzScaleFactorMap['loose'],wzBaseScaleFactor]),}},
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
        selectionParams['WZ']['{0}/vbs'.format(region)] = {
            'args': [wzBaseCut + ' && ' + wzVBSCut + ' && ' + wzCutMap[region]],
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
    for vbsCut in vbsCutMap:
        nMinusOneCut = ' && '.join([cut for key,cut in sorted(vbsCutMap.iteritems()) if key!=vbsCut])
        selectionParams['WZ']['vbs/{0}'.format(vbsCut)] = {
            'args': [nMinusOneCut + ' && ' + wzBaseCut + ' && ' + wzCutMap['PPP']],
            'kwargs': {
                'mcscalefactor': '*'.join([wzScaleFactorMap['PPP'],wzBaseScaleFactor]),
            }
        }
        for region in fakeRegions:
            selectionParams['WZ']['{0}/vbs/{1}'.format(region,vbsCut)] = {
                'args': [nMinusOneCut + ' && ' + wzBaseCut + ' && ' + wzCutMap[region]],
                'kwargs': {
                    'mccut': wzMCCut,
                    'mcscalefactor': '*'.join([wzScaleFactorMap[region],wzFakeScaleFactorMap[region],wzBaseScaleFactor,'1' if region=='PPP' else '-1']),
                    'datascalefactor': wzFakeScaleFactorMap[region],
                }
            }

    # special selections for samples
    # DY-10 0, 1, 2 bins (0 includes 3+)
    # DY-50 0, 1, 2, 3, 4 bins (0 includes 5+)
    sampleCuts = {
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
    sampleSelectionParams['WZ'] = {}
    for sample,cut in sampleCuts.iteritems():
        sampleSelectionParams['WZ'][sample] = deepcopy(selectionParams['WZ'])
        for sel in selectionParams['WZ'].keys():
            sampleSelectionParams['WZ'][sample][sel]['args'][0] += ' && {0}'.format(cut)

