from copy import deepcopy
from itertools import product, combinations_with_replacement

from DevTools.Plotter.utilities import ZMASS, addChannels

from DevTools.Utilities.utilities import getCMSSWVersion

version = getCMSSWVersion()

def buildMuMuTauFakeRate(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams):

    histParams['MuMuTauFakeRate'] = {
        'count'                       : {'xVariable': '1',                              'xBinning': [1,0,2],                 }, # just a count of events passing selection
        #'numVertices'                 : {'xVariable': 'numVertices',                    'xBinning': [60,0,60],               },
        #'numVertices_noreweight'      : {'xVariable': 'numVertices',                    'xBinning': [60,0,60],                'mcscale': '1./pileupWeight'},
        #'met'                         : {'xVariable': 'met_pt',                         'xBinning': [500, 0, 500],           },
        #'metPhi'                      : {'xVariable': 'met_phi',                        'xBinning': [100, -3.14159, 3.14159],},
        # z
        'zMass'                       : {'xVariable': 'z_mass',                         'xBinning': [120, 60, 120],          },
        'z1Pt'                        : {'xVariable': 'z1_pt',                          'xBinning': [500, 0, 500],           },
        'z2Pt'                        : {'xVariable': 'z2_pt',                          'xBinning': [500, 0, 500],           },
        # t
        'tPt'                         : {'xVariable': 't_pt',                           'xBinning': [500, 0, 500],           },
        'tDM'                         : {'xVariable': 't_decayMode',                    'xBinning': [15, 0, 15],             },
    }

    baseCut = 'z_mass>81 && z_mass<101 && !(tjet_passCSVv2M>0.5)'
    baseCutNoBVeto = 'z_mass>81 && z_mass<101'
    scaleFactor = 'genWeight*pileupWeight*triggerEfficiency'
    
    selectionParams['MuMuTauFakeRate'] = {
        # MVA
        'default'                         : {'args': [baseCut],                                                                                          'kwargs': {'mcscalefactor': scaleFactor}},
        #'vloose'                          : {'args': [baseCut + ' && t_byVLooseIsolationMVArun2v1DBoldDMwLT>0.5'],                                       'kwargs': {'mcscalefactor': scaleFactor}},
        #'loose'                           : {'args': [baseCut + ' && t_byLooseIsolationMVArun2v1DBoldDMwLT>0.5'],                                        'kwargs': {'mcscalefactor': scaleFactor}},
        'medium'                          : {'args': [baseCut + ' && t_byMediumIsolationMVArun2v1DBoldDMwLT>0.5'],                                       'kwargs': {'mcscalefactor': scaleFactor}},
        'notMedium'                       : {'args': [baseCut + ' && t_byMediumIsolationMVArun2v1DBoldDMwLT<0.5'],                                       'kwargs': {'mcscalefactor': scaleFactor}},
        #'tight'                           : {'args': [baseCut + ' && t_byTightIsolationMVArun2v1DBoldDMwLT>0.5'],                                        'kwargs': {'mcscalefactor': scaleFactor}},
        'nearMuon'                        : {'args': [baseCut + ' && m_pt>0 && mt_deltaR<0.8'],                                                          'kwargs': {'mcscalefactor': scaleFactor}},
        #'nearMuonVLoose'                  : {'args': [baseCut + ' && m_pt>0 && mt_deltaR<0.8 && t_byVLooseIsolationMVArun2v1DBoldDMwLT>0.5'],            'kwargs': {'mcscalefactor': scaleFactor}},
        #'nearMuonLoose'                   : {'args': [baseCut + ' && m_pt>0 && mt_deltaR<0.8 && t_byLooseIsolationMVArun2v1DBoldDMwLT>0.5'],             'kwargs': {'mcscalefactor': scaleFactor}},
        'nearMuonMedium'                  : {'args': [baseCut + ' && m_pt>0 && mt_deltaR<0.8 && t_byMediumIsolationMVArun2v1DBoldDMwLT>0.5'],            'kwargs': {'mcscalefactor': scaleFactor}},
        'nearMuonNotMedium'               : {'args': [baseCut + ' && m_pt>0 && mt_deltaR<0.8 && t_byMediumIsolationMVArun2v1DBoldDMwLT<0.5'],            'kwargs': {'mcscalefactor': scaleFactor}},
        #'nearMuonTight'                   : {'args': [baseCut + ' && m_pt>0 && mt_deltaR<0.8 && t_byTightIsolationMVArun2v1DBoldDMwLT>0.5'],             'kwargs': {'mcscalefactor': scaleFactor}},
        'noBVeto/default'                 : {'args': [baseCutNoBVeto],                                                                                   'kwargs': {'mcscalefactor': scaleFactor}},
        #'noBVeto/vloose'                  : {'args': [baseCutNoBVeto + ' && t_byVLooseIsolationMVArun2v1DBoldDMwLT>0.5'],                                'kwargs': {'mcscalefactor': scaleFactor}},
        #'noBVeto/loose'                   : {'args': [baseCutNoBVeto + ' && t_byLooseIsolationMVArun2v1DBoldDMwLT>0.5'],                                 'kwargs': {'mcscalefactor': scaleFactor}},
        'noBVeto/medium'                  : {'args': [baseCutNoBVeto + ' && t_byMediumIsolationMVArun2v1DBoldDMwLT>0.5'],                                'kwargs': {'mcscalefactor': scaleFactor}},
        'noBVeto/notMedium'               : {'args': [baseCutNoBVeto + ' && t_byMediumIsolationMVArun2v1DBoldDMwLT<0.5'],                                'kwargs': {'mcscalefactor': scaleFactor}},
        #'noBVeto/tight'                   : {'args': [baseCutNoBVeto + ' && t_byTightIsolationMVArun2v1DBoldDMwLT>0.5'],                                 'kwargs': {'mcscalefactor': scaleFactor}},
        'noBVeto/nearMuon'                : {'args': [baseCutNoBVeto + ' && m_pt>0 && mt_deltaR<0.8'],                                                   'kwargs': {'mcscalefactor': scaleFactor}},
        #'noBVeto/nearMuonVLoose'          : {'args': [baseCutNoBVeto + ' && m_pt>0 && mt_deltaR<0.8 && t_byVLooseIsolationMVArun2v1DBoldDMwLT>0.5'],     'kwargs': {'mcscalefactor': scaleFactor}},
        #'noBVeto/nearMuonLoose'           : {'args': [baseCutNoBVeto + ' && m_pt>0 && mt_deltaR<0.8 && t_byLooseIsolationMVArun2v1DBoldDMwLT>0.5'],      'kwargs': {'mcscalefactor': scaleFactor}},
        'noBVeto/nearMuonMedium'          : {'args': [baseCutNoBVeto + ' && m_pt>0 && mt_deltaR<0.8 && t_byMediumIsolationMVArun2v1DBoldDMwLT>0.5'],     'kwargs': {'mcscalefactor': scaleFactor}},
        'noBVeto/nearMuonNotMedium'       : {'args': [baseCutNoBVeto + ' && m_pt>0 && mt_deltaR<0.8 && t_byMediumIsolationMVArun2v1DBoldDMwLT<0.5'],     'kwargs': {'mcscalefactor': scaleFactor}},
        #'noBVeto/nearMuonTight'           : {'args': [baseCutNoBVeto + ' && m_pt>0 && mt_deltaR<0.8 && t_byTightIsolationMVArun2v1DBoldDMwLT>0.5'],      'kwargs': {'mcscalefactor': scaleFactor}},
        # cutbased
        #'cutbased/loose'                  : {'args': [baseCut + ' && t_byCombinedIsolationDeltaBetaCorrRaw3Hits<2.5'],                                   'kwargs': {'mcscalefactor': scaleFactor}},
        #'cutbased/medium'                 : {'args': [baseCut + ' && t_byCombinedIsolationDeltaBetaCorrRaw3Hits<1.5'],                                   'kwargs': {'mcscalefactor': scaleFactor}},
        #'cutbased/tight'                  : {'args': [baseCut + ' && t_byCombinedIsolationDeltaBetaCorrRaw3Hits<0.8'],                                   'kwargs': {'mcscalefactor': scaleFactor}},
        #'cutbased/nearMuonLoose'          : {'args': [baseCut + ' && m_pt>0 && mt_deltaR<0.8 && t_byCombinedIsolationDeltaBetaCorrRaw3Hits<2.5'],        'kwargs': {'mcscalefactor': scaleFactor}},
        #'cutbased/nearMuonMedium'         : {'args': [baseCut + ' && m_pt>0 && mt_deltaR<0.8 && t_byCombinedIsolationDeltaBetaCorrRaw3Hits<1.5'],        'kwargs': {'mcscalefactor': scaleFactor}},
        #'cutbased/nearMuonTight'          : {'args': [baseCut + ' && m_pt>0 && mt_deltaR<0.8 && t_byCombinedIsolationDeltaBetaCorrRaw3Hits<0.8'],        'kwargs': {'mcscalefactor': scaleFactor}},
        #'noBVeto/cutbased/loose'          : {'args': [baseCutNoBVeto + ' && t_byCombinedIsolationDeltaBetaCorrRaw3Hits<2.5'],                            'kwargs': {'mcscalefactor': scaleFactor}},
        #'noBVeto/cutbased/medium'         : {'args': [baseCutNoBVeto + ' && t_byCombinedIsolationDeltaBetaCorrRaw3Hits<1.5'],                            'kwargs': {'mcscalefactor': scaleFactor}},
        #'noBVeto/cutbased/tight'          : {'args': [baseCutNoBVeto + ' && t_byCombinedIsolationDeltaBetaCorrRaw3Hits<0.8'],                            'kwargs': {'mcscalefactor': scaleFactor}},
        #'noBVeto/cutbased/nearMuonLoose'  : {'args': [baseCutNoBVeto + ' && m_pt>0 && mt_deltaR<0.8 && t_byCombinedIsolationDeltaBetaCorrRaw3Hits<2.5'], 'kwargs': {'mcscalefactor': scaleFactor}},
        #'noBVeto/cutbased/nearMuonMedium' : {'args': [baseCutNoBVeto + ' && m_pt>0 && mt_deltaR<0.8 && t_byCombinedIsolationDeltaBetaCorrRaw3Hits<1.5'], 'kwargs': {'mcscalefactor': scaleFactor}},
        #'noBVeto/cutbased/nearMuonTight'  : {'args': [baseCutNoBVeto + ' && m_pt>0 && mt_deltaR<0.8 && t_byCombinedIsolationDeltaBetaCorrRaw3Hits<0.8'], 'kwargs': {'mcscalefactor': scaleFactor}},
    }

    for loosecut in [-0.5]:
        selectionParams['MuMuTauFakeRate']['nearMuonWithMVA{:.1f}'.format(loosecut)] = {
            'args': [baseCut + ' && m_pt>0 && mt_deltaR<0.8 && t_byIsolationMVArun2v1DBoldDMwLTraw>{}'.format(loosecut)],
            'kwargs': {'mcscalefactor': scaleFactor},
        }
        selectionParams['MuMuTauFakeRate']['withMVA{:.1f}'.format(loosecut)] = {
            'args': [baseCut + ' && t_byIsolationMVArun2v1DBoldDMwLTraw>{}'.format(loosecut)],
            'kwargs': {'mcscalefactor': scaleFactor},
        }

    for sel in selectionParams['MuMuTauFakeRate'].keys():
        for ptcut in [[10,20],[20]]:
            if len(ptcut)==1:
                name = '{}/pt{}'.format(sel,*ptcut)
                selcut = 't_pt>{}'.format(*ptcut)
            else:
                name = '{}/pt{}to{}'.format(sel,*ptcut)
                selcut = 't_pt>{} && t_pt<{}'.format(*ptcut)
            selectionParams['MuMuTauFakeRate'][name] = deepcopy(selectionParams['MuMuTauFakeRate'][sel])
            args = selectionParams['MuMuTauFakeRate'][name]['args']
            selectionParams['MuMuTauFakeRate'][name]['args'][0] = args[0] + ' && ' + selcut

    for sel in selectionParams['MuMuTauFakeRate'].keys():
        for dm in [0,1,10]:
            name = '{0}/dm{1}'.format(sel,dm)
            selectionParams['MuMuTauFakeRate'][name] = deepcopy(selectionParams['MuMuTauFakeRate'][sel])
            args = selectionParams['MuMuTauFakeRate'][name]['args']
            selectionParams['MuMuTauFakeRate'][name]['args'][0] = args[0] + ' && t_decayMode=={0}'.format(dm)

    etaBins = [0.,1.479,2.3]

    for sel in selectionParams['MuMuTauFakeRate'].keys():
        for eb in range(len(etaBins)-1):
            name = '{0}/etaBin{1}'.format(sel,eb)
            selectionParams['MuMuTauFakeRate'][name] = deepcopy(selectionParams['MuMuTauFakeRate'][sel])
            args = selectionParams['MuMuTauFakeRate'][name]['args']
            selectionParams['MuMuTauFakeRate'][name]['args'][0] = args[0] + ' && fabs(t_eta)>={0} && fabs(t_eta)<{1}'.format(etaBins[eb],etaBins[eb+1])

    # special scales for individual samples
    sampleSelectionParams['MuMuTauFakeRate'] = {}
    sampleScales = {
        'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8'   : 'zPtWeight',
        'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8'       : 'zPtWeight',
    }
    for sample,scale in sampleScales.iteritems():
        sampleSelectionParams['MuMuTauFakeRate'][sample] = deepcopy(selectionParams['MuMuTauFakeRate'])
        for sel in selectionParams['MuMuTauFakeRate'].keys():
            sampleSelectionParams['MuMuTauFakeRate'][sample][sel]['kwargs']['mcscalefactor'] = '*'.join([sampleSelectionParams['MuMuTauFakeRate'][sample][sel]['kwargs']['mcscalefactor'],scale])

    # drell yan special selections
    for sample in sampleScales:
        for sel in selectionParams['MuMuTauFakeRate'].keys():
            sampleSelectionParams['MuMuTauFakeRate'][sample]['fakeTau/{}'.format(sel)] = deepcopy(sampleSelectionParams['MuMuTauFakeRate'][sample][sel])
            sampleSelectionParams['MuMuTauFakeRate'][sample]['fakeTau/{}'.format(sel)]['args'][0] += ' && (t_tauGenMatch2==6 || t_tauGenMatch2<0)'
            sampleSelectionParams['MuMuTauFakeRate'][sample]['hadronicTau/{}'.format(sel)] = deepcopy(sampleSelectionParams['MuMuTauFakeRate'][sample][sel])
            sampleSelectionParams['MuMuTauFakeRate'][sample]['hadronicTau/{}'.format(sel)]['args'][0] += ' && (t_tauGenMatch2==5)'
            sampleSelectionParams['MuMuTauFakeRate'][sample]['leptonicTau/{}'.format(sel)] = deepcopy(sampleSelectionParams['MuMuTauFakeRate'][sample][sel])
            sampleSelectionParams['MuMuTauFakeRate'][sample]['leptonicTau/{}'.format(sel)]['args'][0] += ' && (t_tauGenMatch2<5 && t_tauGenMatch2>0)'

