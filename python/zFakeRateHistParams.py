from copy import deepcopy
from itertools import product, combinations_with_replacement

from DevTools.Plotter.utilities import ZMASS, addChannels

from DevTools.Utilities.utilities import getCMSSWVersion

version = getCMSSWVersion()

genCut = '{0}_genMatch==1 && {0}_genDeltaR<0.1'

def buildZFakeRate(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams):

    histParams['ZFakeRate'] = {
        'count'                       : {'xVariable': '1',                              'xBinning': [1,0,2],                 }, # just a count of events passing selection
        'numVertices'                 : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],               },
        'met'                         : {'xVariable': 'met_pt',                         'xBinning': [500, 0, 500],           },
        'metPhi'                      : {'xVariable': 'met_phi',                        'xBinning': [500, -3.14159, 3.14159],},
        # z
        'zMass'                       : {'xVariable': 'z_mass',                         'xBinning': [500, 0, 500],           },
        'mllMinusMZ'                  : {'xVariable': 'fabs(z_mass-{0})'.format(ZMASS), 'xBinning': [200, 0, 200],           },
        'zPt'                         : {'xVariable': 'z_pt',                           'xBinning': [500, 0, 500],           },
        'zDeltaR'                     : {'xVariable': 'z_deltaR',                       'xBinning': [500, 0, 5],             },
        'z1Pt'                        : {'xVariable': 'z1_pt',                          'xBinning': [500, 0, 500],           },
        'z1Eta'                       : {'xVariable': 'z1_eta',                         'xBinning': [500, -2.5, 2.5],        },
        'z2Pt'                        : {'xVariable': 'z2_pt',                          'xBinning': [500, 0, 500],           },
        'z2Eta'                       : {'xVariable': 'z2_eta',                         'xBinning': [500, -2.5, 2.5],        },
        # l
        'wMt'                         : {'xVariable': 'w_mt',                           'xBinning': [500, 0, 500],           },
        'wPt'                         : {'xVariable': 'w_pt',                           'xBinning': [500, 0, 500],           },
        'lPt'                         : {'xVariable': 'l1_pt',                          'xBinning': [500, 0, 500],           },
        'lEta'                        : {'xVariable': 'l1_eta',                         'xBinning': [500, -2.5, 2.5],        },
    }

    # setup the reco channels
    channels = ['mme','mmm','eem','eee']
    projectionParams['ZFakeRate'] = {}
    for chan in channels:
        projectionParams['ZFakeRate'][chan] = [chan]
    histParams['ZFakeRate'].update(addChannels(deepcopy(histParams['ZFakeRate']),'channel',len(channels)))


    frBaseCut = 'z_deltaR>0.02 && z1_pt>25. && z2_pt>20 && z1_passMedium && z2_passMedium'
    frBaseCutLoose = '{0}'.format(frBaseCut)
    frBaseCutMedium = '{0} && l1_passMedium==1'.format(frBaseCut)
    frBaseCutTight = '{0} && l1_passTight==1'.format(frBaseCut)
    frScaleFactorLoose  = 'z1_mediumScale*z2_mediumScale*l1_looseScale*genWeight*pileupWeight'
    frScaleFactorMedium = 'z1_mediumScale*z2_mediumScale*l1_mediumScale*genWeight*pileupWeight'
    frScaleFactorTight  = 'z1_mediumScale*z2_mediumScale*l1_tightScale*genWeight*pileupWeight'
    selectionParams['ZFakeRate'] = {
        'loose'      : {'args': [frBaseCutLoose],                   'kwargs': {'mcscalefactor': frScaleFactorLoose, }},
        'medium'     : {'args': [frBaseCutMedium],                  'kwargs': {'mcscalefactor': frScaleFactorMedium,}},
        'tight'      : {'args': [frBaseCutTight],                   'kwargs': {'mcscalefactor': frScaleFactorTight, }},
    }
    
    subsels = {
        'wMtSel'  : 'w_mt<50',
        'zMassSel': 'z_mass<105 && z_mass>75',
        'fullSel' : 'w_mt<50 && z_mass<105 && z_mass>75',
    }
    
    for sel in ['loose','medium','tight']:
        for sub in subsels:
            name = '{0}/{1}'.format(sel,sub)
            selectionParams['ZFakeRate'][name] = deepcopy(selectionParams['ZFakeRate'][sel])
            args = selectionParams['ZFakeRate'][name]['args']
            selectionParams['ZFakeRate'][name]['args'][0] = ' && '.join([args[0],subsels[sub]])
    
