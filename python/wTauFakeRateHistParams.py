from copy import deepcopy
from itertools import product, combinations_with_replacement

from DevTools.Plotter.utilities import ZMASS, addChannels, getLumi, getRunRange

from DevTools.Utilities.utilities import getCMSSWVersion

version = getCMSSWVersion()

def buildWTauFakeRate(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams):

    histParams['WTauFakeRate'] = {
        'count'                       : {'xVariable': '1',                              'xBinning': [1,0,2],                 }, # just a count of events passing selection
        'numVertices'                 : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],               },
        'numLooseMuons'               : {'xVariable': 'numLooseMuons',                  'xBinning': [4,0,4],                 },
        'numTightMuons'               : {'xVariable': 'numTightMuons',                  'xBinning': [4,0,4],                 },
        'met'                         : {'xVariable': 'met_pt',                         'xBinning': [500, 0, 500],           },
        'metPhi'                      : {'xVariable': 'met_phi',                        'xBinning': [500, -3.14159, 3.14159],},
        # z
        'zMass'                       : {'xVariable': 'z_mass',                         'xBinning': [500, 0, 500],           },
        'mllMinusMZ'                  : {'xVariable': 'fabs(z_mass-{0})'.format(ZMASS), 'xBinning': [200, 0, 200],           },
        'zPt'                         : {'xVariable': 'z_pt',                           'xBinning': [500, 0, 500],           },
        'zDeltaR'                     : {'xVariable': 'z_deltaR',                       'xBinning': [500, 0, 5],             },
        # t
        'wtMt'                        : {'xVariable': 'wt_mt',                          'xBinning': [500, 0, 500],           },
        'wtPt'                        : {'xVariable': 'wt_pt',                          'xBinning': [500, 0, 500],           },
        'tPt'                         : {'xVariable': 't_pt',                           'xBinning': [500, 0, 500],           },
        'tEta'                        : {'xVariable': 't_eta',                          'xBinning': [500, -2.5, 2.5],        },
        'tDM'                         : {'xVariable': 't_decayMode',                    'xBinning': [12, 0 ,12],             },
        # m
        'wmMt'                        : {'xVariable': 'wm_mt',                          'xBinning': [500, 0, 500],           },
        'wmPt'                        : {'xVariable': 'wm_pt',                          'xBinning': [500, 0, 500],           },
        'mPt'                         : {'xVariable': 'm_pt',                           'xBinning': [500, 0, 500],           },
        'mEta'                        : {'xVariable': 'm_eta',                          'xBinning': [500, -2.5, 2.5],        },
    }

    #intLumi = getLumi()
    #for r in ['B','C','D','E','F','G','H']:
    #    run = 'Run2016{0}'.format(r)
    #    runLumi = getLumi(run=run)
    #    mcscale = '{0}/{1}'.format(runLumi,intLumi)
    #    runRange = getRunRange(run=run)
    #    datacut = 'run>={0} && run<={1}'.format(*runRange)
    #    histParams['WTauFakeRate']['wmMt_{0}'.format(run)] = {'xVariable': 'wm_mt', 'xBinning': [500,0,500], 'datacut': datacut, 'mcscale': mcscale}

    frBaseCut = 'z_deltaR>0.02 && m_pt>25. && t_decayModeFinding'
    frBaseCutLoose = '{0} && t_passLoose==1'.format(frBaseCut)
    frBaseCutMedium = '{0} && t_passMedium==1'.format(frBaseCut)
    frBaseCutTight = '{0} && t_passTight==1'.format(frBaseCut)
    frScaleFactorLoose = 'm_tightScale*t_looseScale*genWeight*pileupWeight*triggerEfficiency'
    frScaleFactorMedium = 'm_tightScale*t_mediumScale*genWeight*pileupWeight*triggerEfficiency'
    frScaleFactorTight = 'm_tightScale*t_tightScale*genWeight*pileupWeight*triggerEfficiency'

    frNewBaseCut = 'z_deltaR>0.02 && m_pt>25.'
    frNewBaseCutLoose = '{0}'.format(frNewBaseCut)
    selectionParams['WTauFakeRate'] = {
        'loose'      : {'args': [frBaseCutLoose],                   'kwargs': {'mcscalefactor': frScaleFactorLoose, }},
        'medium'     : {'args': [frBaseCutMedium],                  'kwargs': {'mcscalefactor': frScaleFactorMedium,}},
        'tight'      : {'args': [frBaseCutTight],                   'kwargs': {'mcscalefactor': frScaleFactorTight, }},
        'newloose'   : {'args': [frNewBaseCutLoose],                'kwargs': {'mcscalefactor': frScaleFactorLoose, }},
    }
    
    subsels = {
        #'SS'     : 't_charge==m_charge', # included
        'ZVeto'  : '(z_mass<40 || z_mass>100)',
        'WMt'    : 'wm_mt>60.',
        'all'    : '(z_mass<40 || z_mass>100) && wm_mt>60. && t_charge==m_charge',
    }

    
    for sel in ['loose','medium','tight','newloose']:
        for sub in subsels:
            name = '{0}/{1}'.format(sel,sub)
            selectionParams['WTauFakeRate'][name] = deepcopy(selectionParams['WTauFakeRate'][sel])
            args = selectionParams['WTauFakeRate'][name]['args']
            selectionParams['WTauFakeRate'][name]['args'][0] = ' && '.join([args[0],subsels[sub]])
            for dm in [0,1,2,5,6,7,10,11]:
                name = '{0}/{1}/dm{2}'.format(sel,sub,dm)
                selectionParams['WTauFakeRate'][name] = deepcopy(selectionParams['WTauFakeRate'][sel])
                args = selectionParams['WTauFakeRate'][name]['args']
                selectionParams['WTauFakeRate'][name]['args'][0] = ' && '.join([args[0],subsels[sub],'t_decayMode=={0}'.format(dm)])
    
    etaBins = [0.,1.479,2.3]
    
    sels = selectionParams['WTauFakeRate'].keys()
    for sel in sels:
        for eb in range(len(etaBins)-1):
            name = '{0}/etaBin{1}'.format(sel,eb)
            selectionParams['WTauFakeRate'][name] = deepcopy(selectionParams['WTauFakeRate'][sel])
            args = selectionParams['WTauFakeRate'][name]['args']
            selectionParams['WTauFakeRate'][name]['args'][0] = ' && '.join([args[0],'fabs(t_eta)>={0} && fabs(t_eta)<{1}'.format(etaBins[eb],etaBins[eb+1])])

