from copy import deepcopy
from itertools import product, combinations_with_replacement

from DevTools.Plotter.utilities import ZMASS, addChannels

from DevTools.Utilities.utilities import getCMSSWVersion

version = getCMSSWVersion()

genCut = '{0}_genMatch==1 && {0}_genDeltaR<0.1'

def buildWFakeRate(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams):

    histParams['WFakeRate'] = {
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
        # l
        'wlMt'                        : {'xVariable': 'wl_mt',                          'xBinning': [500, 0, 500],           },
        'wlPt'                        : {'xVariable': 'wl_pt',                          'xBinning': [500, 0, 500],           },
        'lPt'                         : {'xVariable': 'l_pt',                           'xBinning': [500, 0, 500],           },
        'lEta'                        : {'xVariable': 'l_eta',                          'xBinning': [500, -2.5, 2.5],        },
        # m
        'wmMt'                        : {'xVariable': 'wm_mt',                          'xBinning': [500, 0, 500],           },
        'wmPt'                        : {'xVariable': 'wm_pt',                          'xBinning': [500, 0, 500],           },
        'mPt'                         : {'xVariable': 'm_pt',                           'xBinning': [500, 0, 500],           },
        'mEta'                        : {'xVariable': 'm_eta',                          'xBinning': [500, -2.5, 2.5],        },
    }

    # setup the reco channels
    channels = ['me','mm']
    projectionParams['WFakeRate'] = {}
    for chan in channels:
        projectionParams['WFakeRate'][chan] = [chan]
    histParams['WFakeRate'].update(addChannels(deepcopy(histParams['WFakeRate']),'channel',len(channels)))


    frBaseCut = 'z_deltaR>0.02 && m_pt>25.'
    frBaseCutLoose = '{0}'.format(frBaseCut)
    frBaseCutMedium = '{0} && l_passMedium==1'.format(frBaseCut)
    frBaseCutTight = '{0} && l_passTight==1'.format(frBaseCut)
    frScaleFactorLoose = 'm_tightScale*l_looseScale*genWeight*pileupWeight*triggerEfficiency'
    frScaleFactorMedium = 'm_tightScale*l_mediumScale*genWeight*pileupWeight*triggerEfficiency'
    frScaleFactorTight = 'm_tightScale*l_tightScale*genWeight*pileupWeight*triggerEfficiency'
    selectionParams['WFakeRate'] = {
        'loose'      : {'args': [frBaseCutLoose],                   'kwargs': {'mcscalefactor': frScaleFactorLoose, }},
        'medium'     : {'args': [frBaseCutMedium],                  'kwargs': {'mcscalefactor': frScaleFactorMedium,}},
        'tight'      : {'args': [frBaseCutTight],                   'kwargs': {'mcscalefactor': frScaleFactorTight, }},
    }
    
    subsels = {
        'SS'     : 'l_charge==m_charge',
        'ZVeto'  : '(z_mass<60 || z_mass>120)',
        'WMt'    : 'wm_mt>60.',
        'full'   : '(z_mass<60 || z_mass>120) && wm_mt>60.',
    }
    
    for sel in ['loose','medium','tight']:
        for sub in subsels:
            name = '{0}/{1}'.format(sel,sub)
            selectionParams['WFakeRate'][name] = deepcopy(selectionParams['WFakeRate'][sel])
            args = selectionParams['WFakeRate'][name]['args']
            selectionParams['WFakeRate'][name]['args'][0] = ' && '.join([args[0],subsels[sub]])
    
    etaBins = [0.,0.8,1.479,2.3]
    
    sels = selectionParams['WFakeRate'].keys()
    for sel in sels:
        for eb in range(len(etaBins)-1):
            name = '{0}/etaBin{1}'.format(sel,eb)
            selectionParams['WFakeRate'][name] = deepcopy(selectionParams['WFakeRate'][sel])
            args = selectionParams['WFakeRate'][name]['args']
            selectionParams['WFakeRate'][name]['args'][0] = ' && '.join([args[0],'fabs(l_eta)>={0} && fabs(l_eta)<{1}'.format(etaBins[eb],etaBins[eb+1])])

