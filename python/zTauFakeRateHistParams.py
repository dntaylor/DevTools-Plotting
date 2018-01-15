from copy import deepcopy
from itertools import product, combinations_with_replacement

from DevTools.Plotter.utilities import ZMASS, addChannels, getLumi, getRunRange

from DevTools.Utilities.utilities import getCMSSWVersion

version = getCMSSWVersion()

def buildZTauFakeRate(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams):

    histParams['ZTauFakeRate'] = {
        'count'                       : {'xVariable': '1',                              'xBinning': [1,0,2],                 }, # just a count of events passing selection
        'numVertices'                 : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],               },
        'numLooseMuons'               : {'xVariable': 'numLooseMuons',                  'xBinning': [4,0,4],                 },
        'numTightMuons'               : {'xVariable': 'numTightMuons',                  'xBinning': [4,0,4],                 },
        'met'                         : {'xVariable': 'met_pt',                         'xBinning': [500, 0, 500],           },
        'metPhi'                      : {'xVariable': 'met_phi',                        'xBinning': [500, -3.14159, 3.14159],},
        # z
        'zMass'                       : {'xVariable': 'z_mass',                         'xBinning': [120, 60, 120],          },
        'zPt'                         : {'xVariable': 'z_pt',                           'xBinning': [500, 0, 500],           },
        'zDeltaR'                     : {'xVariable': 'z_deltaR',                       'xBinning': [500, 0, 5],             },
        'zLeadingLeptonPt'            : {'xVariable': 'z1_pt',                          'xBinning': [1000, 0, 1000],         },
        'zLeadingLeptonEta'           : {'xVariable': 'z1_eta',                         'xBinning': [500, -2.5, 2.5],        },
        'zLeadingLeptonIso'           : {'xVariable': 'z1_isolation',                   'xBinning': [500, 0, 0.5],           },
        'zSubLeadingLeptonPt'         : {'xVariable': 'z2_pt',                          'xBinning': [1000, 0, 1000],         },
        'zSubLeadingLeptonEta'        : {'xVariable': 'z2_eta',                         'xBinning': [500, -2.5, 2.5],        },
        'zSubLeadingLeptonIso'        : {'xVariable': 'z2_isolation',                   'xBinning': [500, 0, 0.5],           },
        # t
        'wtMt'                        : {'xVariable': 'w_mt',                           'xBinning': [500, 0, 500],           },
        'wtPt'                        : {'xVariable': 'w_pt',                           'xBinning': [500, 0, 500],           },
        'tPt'                         : {'xVariable': 't_pt',                           'xBinning': [500, 0, 500],           },
        'tEta'                        : {'xVariable': 't_eta',                          'xBinning': [500, -2.5, 2.5],        },
        'tDM'                         : {'xVariable': 't_decayMode',                    'xBinning': [12, 0 ,12],             },
    }

    frBaseCut = 'z_deltaR>0.02 && z1_pt>25. && z2_pt>20. && z_mass>81 && z_mass<101 && t_decayModeFinding'
    frBaseCutLoose = '{0} && t_passLoose==1'.format(frBaseCut)
    frBaseCutMedium = '{0} && t_passMedium==1'.format(frBaseCut)
    frBaseCutTight = '{0} && t_passTight==1'.format(frBaseCut)
    frScaleFactorLoose = 'z1_mediumScale*z2_mediumScale*t_looseScale*genWeight*pileupWeight*triggerEfficiency'
    frScaleFactorMedium = 'z1_mediumScale*z2_mediumScale*t_mediumScale*genWeight*pileupWeight*triggerEfficiency'
    frScaleFactorTight = 'z1_mediumScale*z2_mediumScale*t_tightScale*genWeight*pileupWeight*triggerEfficiency'

    frNewBaseCut = 'z_deltaR>0.02 && z1_pt>25. && z2_pt>20. && z_mass>81 && z_mass<101'
    frNewBaseCutLoose = '{0}'.format(frNewBaseCut)
    selectionParams['ZTauFakeRate'] = {
        'loose'      : {'args': [frBaseCutLoose],                   'kwargs': {'mcscalefactor': frScaleFactorLoose, }},
        'medium'     : {'args': [frBaseCutMedium],                  'kwargs': {'mcscalefactor': frScaleFactorMedium,}},
        'tight'      : {'args': [frBaseCutTight],                   'kwargs': {'mcscalefactor': frScaleFactorTight, }},
        'newloose'   : {'args': [frNewBaseCutLoose],                'kwargs': {'mcscalefactor': frScaleFactorLoose, }},
    }
    
    subsels = {
        #'WMt'    : 'w_mt<40.',
        'all'    : '1',
    }

    
    for sel in ['loose','medium','tight','newloose']:
        for sub in subsels:
            name = '{0}/{1}'.format(sel,sub)
            selectionParams['ZTauFakeRate'][name] = deepcopy(selectionParams['ZTauFakeRate'][sel])
            args = selectionParams['ZTauFakeRate'][name]['args']
            selectionParams['ZTauFakeRate'][name]['args'][0] = ' && '.join([args[0],subsels[sub]])
            for dm in [0,1,5,6,10]:
                name = '{0}/{1}/dm{2}'.format(sel,sub,dm)
                selectionParams['ZTauFakeRate'][name] = deepcopy(selectionParams['ZTauFakeRate'][sel])
                args = selectionParams['ZTauFakeRate'][name]['args']
                selectionParams['ZTauFakeRate'][name]['args'][0] = ' && '.join([args[0],subsels[sub],'t_decayMode=={0}'.format(dm)])
    
    etaBins = [0.,1.479,2.3]
    
    sels = selectionParams['ZTauFakeRate'].keys()
    for sel in sels:
        for eb in range(len(etaBins)-1):
            name = '{0}/etaBin{1}'.format(sel,eb)
            selectionParams['ZTauFakeRate'][name] = deepcopy(selectionParams['ZTauFakeRate'][sel])
            args = selectionParams['ZTauFakeRate'][name]['args']
            selectionParams['ZTauFakeRate'][name]['args'][0] = ' && '.join([args[0],'fabs(t_eta)>={0} && fabs(t_eta)<{1}'.format(etaBins[eb],etaBins[eb+1])])
            for dm in [0,1,5,6,10]:
                name = '{0}/etaBin{1}/dm{2}'.format(sel,eb,dm)
                selectionParams['ZTauFakeRate'][name] = deepcopy(selectionParams['ZTauFakeRate'][sel])
                args = selectionParams['ZTauFakeRate'][name]['args']
                selectionParams['ZTauFakeRate'][name]['args'][0] = ' && '.join([args[0],'fabs(t_eta)>={0} && fabs(t_eta)<{1} && t_decayMode=={2}'.format(etaBins[eb],etaBins[eb+1],dm)])
                selectionParams['ZTauFakeRate'][name]['kwargs']['hists'] = ['tPt']

