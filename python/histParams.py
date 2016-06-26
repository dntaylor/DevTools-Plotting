# histParams.py
'''
A map of histogram params.
'''
from copy import deepcopy
from itertools import product, combinations_with_replacement

from DevTools.Plotter.utilities import ZMASS
from DevTools.Plotter.higgsUtilities import getChannels, getGenChannels, getOldSelections

from DevTools.Utilities.utilities import getCMSSWVersion

version = getCMSSWVersion()

#############
### hists ###
#############
histParams = {
    # overrides for Electron
    'Electron': {
        'count'                       : {'xVariable': '1',                              'xBinning': [1,0,2],                 }, # just a count of events passing selection
        'pt'                          : {'xVariable': 'e_pt',                           'xBinning': [2000,0,2000],           },
        'eta'                         : {'xVariable': 'e_eta',                          'xBinning': [600,-3.,3.],            },
    },
    # overrides for Muon
    'Muon': {
        'count'                       : {'xVariable': '1',                              'xBinning': [1,0,2],                 }, # just a count of events passing selection
        'pt'                          : {'xVariable': 'm_pt',                           'xBinning': [2000,0,2000],           },
        'eta'                         : {'xVariable': 'm_eta',                          'xBinning': [600,-3.,3.],            },
    },
    # overrides for Tau
    'Tau': {
        'count'                       : {'xVariable': '1',                              'xBinning': [1,0,2],                 }, # just a count of events passing selection
        'pt'                          : {'xVariable': 't_pt',                           'xBinning': [2000,0,2000],           },
        'eta'                         : {'xVariable': 't_eta',                          'xBinning': [600,-3.,3.],            },
    },
    # overrides for DijetFakeRate
    'DijetFakeRate': {
        'count'                       : {'xVariable': '1',                              'xBinning': [1,0,2],                 }, # just a count of events passing selection
        'numVertices'                 : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],               },
        'numVertices_noreweight'      : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': '1./pileupWeight'},
        'met'                         : {'xVariable': 'met_pt',                         'xBinning': [500, 0, 500],           },
        'metPhi'                      : {'xVariable': 'met_phi',                        'xBinning': [500, -3.14159, 3.14159],},
        'pt'                          : {'xVariable': 'l1_pt',                          'xBinning': [2000,0,2000],           },
        'eta'                         : {'xVariable': 'l1_eta',                         'xBinning': [600,-3.,3.],            },
        'wMass'                       : {'xVariable': 'w_mt',                           'xBinning': [500, 0, 500],           },
    },
    # overrides for DY
    'DY' : {
        'count'                       : {'xVariable': '1',                              'xBinning': [1,0,2],                 }, # just a count of events passing selection
        'numVertices'                 : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],               },
        'numVertices_noreweight'      : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': '1./pileupWeight'},
        #'numVertices_65000'           : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': 'pileupWeight_65000/pileupWeight'},
        #'numVertices_66000'           : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': 'pileupWeight_66000/pileupWeight'},
        #'numVertices_67000'           : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': 'pileupWeight_67000/pileupWeight'},
        #'numVertices_68000'           : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': 'pileupWeight_68000/pileupWeight'},
        #'numVertices_69000'           : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': 'pileupWeight_69000/pileupWeight'},
        #'numVertices_70000'           : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': 'pileupWeight_70000/pileupWeight'},
        #'numVertices_71000'           : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': 'pileupWeight_71000/pileupWeight'},
        #'numVertices_72000'           : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': 'pileupWeight_72000/pileupWeight'},
        #'numVertices_73000'           : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': 'pileupWeight_73000/pileupWeight'},
        #'numVertices_74000'           : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': 'pileupWeight_74000/pileupWeight'},
        #'numVertices_75000'           : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': 'pileupWeight_75000/pileupWeight'},
        #'numVertices_76000'           : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': 'pileupWeight_76000/pileupWeight'},
        #'numVertices_77000'           : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': 'pileupWeight_77000/pileupWeight'},
        #'numVertices_78000'           : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': 'pileupWeight_78000/pileupWeight'},
        #'numVertices_79000'           : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': 'pileupWeight_79000/pileupWeight'},
        #'numVertices_80000'           : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': 'pileupWeight_80000/pileupWeight'},
        'met'                         : {'xVariable': 'met_pt',                         'xBinning': [500, 0, 500],           },
        'metPhi'                      : {'xVariable': 'met_phi',                        'xBinning': [500, -3.14159, 3.14159],},
        'zMass'                       : {'xVariable': 'z_mass',                         'xBinning': [5000, 0, 500],          },
        'mllMinusMZ'                  : {'xVariable': 'fabs(z_mass-{0})'.format(ZMASS), 'xBinning': [2000, 0, 200],          },
        'zPt'                         : {'xVariable': 'z_pt',                           'xBinning': [5000, 0, 500],          },
        'zEta'                        : {'xVariable': 'z_eta',                          'xBinning': [1000, -5, 5],           },
        'zDeltaR'                     : {'xVariable': 'z_deltaR',                       'xBinning': [500, 0, 5],             },
        'zLeadingLeptonPt'            : {'xVariable': 'z1_pt',                          'xBinning': [10000, 0, 1000],        },
        'zLeadingLeptonEta'           : {'xVariable': 'z1_eta',                         'xBinning': [500, -2.5, 2.5],        },
        'zSubLeadingLeptonPt'         : {'xVariable': 'z2_pt',                          'xBinning': [10000, 0, 1000],        },
        'zSubLeadingLeptonEta'        : {'xVariable': 'z2_eta',                         'xBinning': [500, -2.5, 2.5],        },
    },
    # overrides for Charge
    'Charge' : {
        'count'                       : {'xVariable': '1',                              'xBinning': [1,0,2],                 }, # just a count of events passing selection
        'numVertices'                 : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],               },
        'numVertices_noreweight'      : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': '1./pileupWeight'},
        'met'                         : {'xVariable': 'met_pt',                         'xBinning': [500, 0, 500],           },
        'metPhi'                      : {'xVariable': 'met_phi',                        'xBinning': [500, -3.14159, 3.14159],},
        'zMass'                       : {'xVariable': 'z_mass',                         'xBinning': [5000, 0, 500],          },
        'mllMinusMZ'                  : {'xVariable': 'fabs(z_mass-{0})'.format(ZMASS), 'xBinning': [2000, 0, 200],          },
        'zPt'                         : {'xVariable': 'z_pt',                           'xBinning': [5000, 0, 500],          },
        'zEta'                        : {'xVariable': 'z_eta',                          'xBinning': [1000, -5, 5],           },
        'zDeltaR'                     : {'xVariable': 'z_deltaR',                       'xBinning': [500, 0, 5],             },
        'zLeadingLeptonPt'            : {'xVariable': 'z1_pt',                          'xBinning': [10000, 0, 1000],        },
        'zLeadingLeptonEta'           : {'xVariable': 'z1_eta',                         'xBinning': [500, -2.5, 2.5],        },
        'zSubLeadingLeptonPt'         : {'xVariable': 'z2_pt',                          'xBinning': [10000, 0, 1000],        },
        'zSubLeadingLeptonEta'        : {'xVariable': 'z2_eta',                         'xBinning': [500, -2.5, 2.5],        },
    },
    # overrides for TauCharge
    'TauCharge' : {
        'count'                       : {'xVariable': '1',                              'xBinning': [1,0,2],                 }, # just a count of events passing selection
        'numVertices'                 : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],               },
        'numVertices_noreweight'      : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': '1./pileupWeight'},
        'met'                         : {'xVariable': 'met_pt',                         'xBinning': [500, 0, 500],           },
        'metPhi'                      : {'xVariable': 'met_phi',                        'xBinning': [500, -3.14159, 3.14159],},
        'zMass'                       : {'xVariable': 'z_mass',                         'xBinning': [5000, 0, 500],          },
        'zPt'                         : {'xVariable': 'z_pt',                           'xBinning': [5000, 0, 500],          },
        'zEta'                        : {'xVariable': 'z_eta',                          'xBinning': [1000, -5, 5],           },
        'zDeltaR'                     : {'xVariable': 'z_deltaR',                       'xBinning': [500, 0, 5],             },
        'zTauMuPt'                    : {'xVariable': 'z1_pt',                          'xBinning': [10000, 0, 1000],        },
        'zTauMuEta'                   : {'xVariable': 'z1_eta',                         'xBinning': [500, -2.5, 2.5],        },
        'zTauHadPt'                   : {'xVariable': 'z2_pt',                          'xBinning': [10000, 0, 1000],        },
        'zTauHadEta'                  : {'xVariable': 'z2_eta',                         'xBinning': [500, -2.5, 2.5],        },
        'tauMuMt'                     : {'xVariable': 'w1_mt',                          'xBinning': [5000, 0, 500],          },
        'tauHadMt'                    : {'xVariable': 'w2_mt',                          'xBinning': [5000, 0, 500],          },
    },
    # overrides for WTauFakeRate      
    'WTauFakeRate' : {
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
        # t
        'wtMt'                        : {'xVariable': 'wt_mt',                          'xBinning': [500, 0, 500],           },
        'wtPt'                        : {'xVariable': 'wt_pt',                          'xBinning': [500, 0, 500],           },
        'tPt'                         : {'xVariable': 't_pt',                           'xBinning': [500, 0, 500],           },
        'tEta'                        : {'xVariable': 't_eta',                          'xBinning': [500, -2.5, 2.5],        },
        # m
        'wmMt'                        : {'xVariable': 'wm_mt',                          'xBinning': [500, 0, 500],           },
        'wmPt'                        : {'xVariable': 'wm_pt',                          'xBinning': [500, 0, 500],           },
        'mPt'                         : {'xVariable': 'm_pt',                           'xBinning': [500, 0, 500],           },
        'mEta'                        : {'xVariable': 'm_eta',                          'xBinning': [500, -2.5, 2.5],        },
    },
    # overrides for WZ
    'WZ' : {
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
        'nJets'                       : {'xVariable': 'numJetsTight30',                 'xBinning': [10, 0, 10],             },
        'nBjets'                      : {'xVariable': 'numBjetsTight30',                'xBinning': [10, 0, 10],             },
    },
    # overrides for Hpp4l
    'Hpp4l' : {
        'count'                       : {'xVariable': '1',                              'xBinning': [1,0,2],                }, # just a count of events passing selection
        'numVertices'                 : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],              },
        'numVertices_noreweight'      : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': '1./pileupWeight'},
        'met'                         : {'xVariable': 'met_pt',                         'xBinning': [50, 0, 500],           },
        'metPhi'                      : {'xVariable': 'met_phi',                        'xBinning': [50, -3.14159, 3.14159],},
        # h++
        'hppMass'                     : {'xVariable': 'hpp_mass',                       'xBinning': [120, 0, 1200],         },
        'hppMt'                       : {'xVariable': 'hppmet_mt',                      'xBinning': [120, 0, 1200],         },
        'hppPt'                       : {'xVariable': 'hpp_pt',                         'xBinning': [120, 0, 1200],         },
        'hppEta'                      : {'xVariable': 'hpp_eta',                        'xBinning': [100, -5, 5],           },
        'hppDeltaR'                   : {'xVariable': 'hpp_deltaR',                     'xBinning': [50, 0, 5],             },
        'hppLeadingLeptonPt'          : {'xVariable': 'hpp1_pt',                        'xBinning': [100, 0, 1000],         },
        'hppLeadingLeptonEta'         : {'xVariable': 'hpp1_eta',                       'xBinning': [50, -2.5, 2.5],        },
        'hppSubLeadingLeptonPt'       : {'xVariable': 'hpp2_pt',                        'xBinning': [100, 0, 1000],         },
        'hppSubLeadingLeptonEta'      : {'xVariable': 'hpp2_eta',                       'xBinning': [50, -2.5, 2.5],        },
        # h--
        'hmmMass'                     : {'xVariable': 'hmm_mass',                       'xBinning': [120, 0, 1200],         },
        'hmmMt'                       : {'xVariable': 'hmmmet_mt',                      'xBinning': [120, 0, 1200],         },
        'hmmPt'                       : {'xVariable': 'hmm_pt',                         'xBinning': [120, 0, 1200],         },
        'hmmEta'                      : {'xVariable': 'hmm_eta',                        'xBinning': [100, -5, 5],           },
        'hmmDeltaR'                   : {'xVariable': 'hmm_deltaR',                     'xBinning': [50, 0, 5],             },
        'hmmLeadingLeptonPt'          : {'xVariable': 'hmm1_pt',                        'xBinning': [100, 0, 1000],         },
        'hmmLeadingLeptonEta'         : {'xVariable': 'hmm1_eta',                       'xBinning': [50, -2.5, 2.5],        },
        'hmmSubLeadingLeptonPt'       : {'xVariable': 'hmm2_pt',                        'xBinning': [100, 0, 1000],         },
        'hmmSubLeadingLeptonEta'      : {'xVariable': 'hmm2_eta',                       'xBinning': [50, -2.5, 2.5],        },
        # best z
        'zMass'                       : {'xVariable': 'z_mass',                         'xBinning': [50, 0, 500],            'selection': 'z_mass>0.',},
        'mllMinusMZ'                  : {'xVariable': 'fabs(z_mass-{0})'.format(ZMASS), 'xBinning': [5, 0, 100],             'selection': 'z_mass>0.',},
        'zPt'                         : {'xVariable': 'z_pt',                           'xBinning': [50, 0, 500],            'selection': 'z_mass>0.',},
        'zEta'                        : {'xVariable': 'z_eta',                          'xBinning': [100, -5, 5],            'selection': 'z_mass>0.',},
        'zDeltaR'                     : {'xVariable': 'z_deltaR',                       'xBinning': [50, 0, 5],              'selection': 'z_mass>0.',},
        'zLeadingLeptonPt'            : {'xVariable': 'z1_pt',                          'xBinning': [100, 0, 1000],          'selection': 'z_mass>0.',},
        'zLeadingLeptonEta'           : {'xVariable': 'z1_eta',                         'xBinning': [50, -2.5, 2.5],         'selection': 'z_mass>0.',},
        'zSubLeadingLeptonPt'         : {'xVariable': 'z2_pt',                          'xBinning': [100, 0, 1000],          'selection': 'z_mass>0.',},
        'zSubLeadingLeptonEta'        : {'xVariable': 'z2_eta',                         'xBinning': [50, -2.5, 2.5],         'selection': 'z_mass>0.',},
        # event
        'mass'                        : {'xVariable': '4l_mass',                        'xBinning': [200, 0, 2000],         },
        'st'                          : {'xVariable': 'hpp1_pt+hpp2_pt+hmm1_pt+hmm2_pt','xBinning': [200, 0, 2000],         },
        # gen truth
        #'hppLeadingLeptonGenMatch'    : {'xVariable': 'hpp1_genMatch',                  'xBinning': [2, 0, 2],              },
        'hppLeadingLeptonGenDeltaR'   : {'xVariable': 'hpp1_genDeltaR',                 'xBinning': [50, 0, 5],             },
        #'hppSubLeadingLeptonGenMatch' : {'xVariable': 'hpp2_genMatch',                  'xBinning': [2, 0, 2],              },
        'hpmSubLeadingLeptonGenDeltaR': {'xVariable': 'hpp2_genDeltaR',                 'xBinning': [50, 0, 5],             },
        #'hmmLeadingLeptonGenMatch'    : {'xVariable': 'hmm1_genMatch',                  'xBinning': [2, 0, 2],              },
        'hmmLeadingLeptonGenDeltaR'   : {'xVariable': 'hmm1_genDeltaR',                 'xBinning': [50, 0, 5],             },
        #'hmmSubLeadingLeptonGenMatch' : {'xVariable': 'hmm2_genMatch',                  'xBinning': [2, 0, 2],              },
        'hmmSubLeadingLeptonGenDeltaR': {'xVariable': 'hmm2_genDeltaR',                 'xBinning': [50, 0, 5],             },
    },
    # overrides for Hpp3l
    'Hpp3l' : {
        'count'                       : {'xVariable': '1',                              'xBinning': [1,0,2],                 }, # just a count of events passing selection
        'numVertices'                 : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],               },
        'numVertices_noreweight'      : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],                'mcscale': '1./pileupWeight'},
        'met'                         : {'xVariable': 'met_pt',                         'xBinning': [500, 0, 500],           },
        'metPhi'                      : {'xVariable': 'met_phi',                        'xBinning': [500, -3.14159, 3.14159],},
        # h++/h--
        'hppMass'                     : {'xVariable': 'hpp_mass',                       'xBinning': [1200, 0, 1200],         },
        'hppPt'                       : {'xVariable': 'hpp_pt',                         'xBinning': [1200, 0, 1200],         },
        'hppEta'                      : {'xVariable': 'hpp_eta',                        'xBinning': [1000, -5, 5],           },
        'hppDeltaR'                   : {'xVariable': 'hpp_deltaR',                     'xBinning': [500, 0, 5],             },
        'hppLeadingLeptonPt'          : {'xVariable': 'hpp1_pt',                        'xBinning': [1000, 0, 1000],         },
        'hppLeadingLeptonEta'         : {'xVariable': 'hpp1_eta',                       'xBinning': [500, -2.5, 2.5],        },
        'hppSubLeadingLeptonPt'       : {'xVariable': 'hpp2_pt',                        'xBinning': [1000, 0, 1000],         },
        'hppSubLeadingLeptonEta'      : {'xVariable': 'hpp2_eta',                       'xBinning': [500, -2.5, 2.5],        },
        # h-/h+
        'hmMass'                      : {'xVariable': 'hm_mt',                          'xBinning': [1200, 0, 1200],         },
        'hmPt'                        : {'xVariable': 'hm_pt',                          'xBinning': [1200, 0, 1200],         },
        'hmEta'                       : {'xVariable': 'hm_eta',                         'xBinning': [1000, -5, 5],           },
        'hmLeptonPt'                  : {'xVariable': 'hm1_pt',                         'xBinning': [1000, 0, 1000],         },
        'hmLeptonEta'                 : {'xVariable': 'hm1_eta',                        'xBinning': [500, -2.5, 2.5],        },
        # best z
        'zMass'                       : {'xVariable': 'z_mass',                         'xBinning': [500, 0, 500],           'selection': 'z_mass>0.',},
        'mllMinusMZ'                  : {'xVariable': 'fabs(z_mass-{0})'.format(ZMASS), 'xBinning': [200, 0, 200],           'selection': 'z_mass>0.',},
        'zPt'                         : {'xVariable': 'z_pt',                           'xBinning': [500, 0, 500],           'selection': 'z_mass>0.',},
        'zEta'                        : {'xVariable': 'z_eta',                          'xBinning': [1000, -5, 5],           'selection': 'z_mass>0.',},
        'zLeadingLeptonPt'            : {'xVariable': 'z1_pt',                          'xBinning': [1000, 0, 1000],         'selection': 'z_mass>0.',},
        'zLeadingLeptonEta'           : {'xVariable': 'z1_eta',                         'xBinning': [500, -2.5, 2.5],        'selection': 'z_mass>0.',},
        'zSubLeadingLeptonPt'         : {'xVariable': 'z2_pt',                          'xBinning': [1000, 0, 1000],         'selection': 'z_mass>0.',},
        'zSubLeadingLeptonEta'        : {'xVariable': 'z2_eta',                         'xBinning': [500, -2.5, 2.5],        'selection': 'z_mass>0.',},
        # w
        'wMass'                       : {'xVariable': 'w_mt',                           'xBinning': [500, 0, 500],           'selection': 'z_mass>0.',},
        'wPt'                         : {'xVariable': 'w_pt',                           'xBinning': [500, 0, 500],           'selection': 'z_mass>0.',},
        'wEta'                        : {'xVariable': 'w_eta',                          'xBinning': [1000, -5, 5],           'selection': 'z_mass>0.',},
        'wLeptonPt'                   : {'xVariable': 'w1_pt',                          'xBinning': [1000, 0, 1000],         'selection': 'z_mass>0.',},
        'wLeptonEta'                  : {'xVariable': 'w1_eta',                         'xBinning': [500, -2.5, 2.5],        'selection': 'z_mass>0.',},
        # event
        'mass'                        : {'xVariable': '3l_mass',                        'xBinning': [2000, 0, 2000],         },
        'st'                          : {'xVariable': 'hpp1_pt+hpp2_pt+hm1_pt',         'xBinning': [2000, 0, 2000],         },
        # gen truth
        #'hppLeadingLeptonGenMatch'    : {'xVariable': 'hpp1_genMatch',                  'xBinning': [2, 0, 2],               },
        'hppLeadingLeptonGenDeltaR'   : {'xVariable': 'hpp1_genDeltaR',                 'xBinning': [1000, 0, 5],            },
        #'hppSubLeadingLeptonGenMatch' : {'xVariable': 'hpp2_genMatch',                  'xBinning': [2, 0, 2],               },
        'hpmSubLeadingLeptonGenDeltaR': {'xVariable': 'hpp2_genDeltaR',                 'xBinning': [1000, 0, 5],            },
        #'hmLeptonGenMatch'            : {'xVariable': 'hm1_genMatch',                   'xBinning': [2, 0, 2],               },
        'hmLeptonGenDeltaR'           : {'xVariable': 'hm1_genDeltaR',                  'xBinning': [1000, 0, 5],            },
    },
}

sampleHistParams = {}

def addChannels(params,var,n):
    for hist in params:
        if 'yVariable' not in params[hist]: # add chans on y axis
            params[hist]['yVariable'] = var
            params[hist]['yBinning'] = [n,0,n]
        elif 'zVariable' not in params[hist]: # add chans on z axis
            params[hist]['zVariable'] = var
            params[hist]['zBinning'] = [n,0,n]
    return params

###################
### Projections ###
###################
projectionParams = {
    'common' : {
        'all' : [], # empty list defaults to sum all channels
    },
}
sampleProjectionParams = {}

##################
### selections ###
##################
selectionParams = {}
sampleSelectionParams = {}

#########################
### some utility cuts ###
#########################
eBarrelCut = 'fabs({0}_eta)<1.479'
eEndcapCut = 'fabs({0}_eta)>1.479'
promptCut = '{0}_genMatch==1 && {0}_genIsPrompt==1 && {0}_genDeltaR<0.1'
promptTauCut = '{0}_genMatch==1 && {0}_genDeltaR<0.1'
genStatusOneCut = '{0}_genMatch==1 && {0}_genStatus==1 && {0}_genDeltaR<0.1'
genCut = '{0}_genMatch==1 && {0}_genDeltaR<0.1'
fakeCut = '({0}_genMatch==0 || ({0}_genMatch==1 && {0}_genIsFromHadron && {0}_genDeltaR<0.1))'
fakeTauCut = '({0}_genMatch==0 || ({0}_genMatch==1 && {0}_genDeltaR>0.1))'

#########################
### electron specific ###
#########################
selectionParams['Electron'] = {
    'default/prompt' : {'args': [promptCut.format('e')],                                       'kwargs': {}},
    'default/fake'   : {'args': [fakeCut.format('e')],                                         'kwargs': {}},
    #'barrel/prompt'  : {'args': [' && '.join([promptCut.format('e'),eBarrelCut.format('e')])], 'kwargs': {}},
    #'barrel/fake'    : {'args': [' && '.join([fakeCut.format('e'),eBarrelCut.format('e')])],   'kwargs': {}},
    #'endcap/prompt'  : {'args': [' && '.join([promptCut.format('e'),eEndcapCut.format('e')])], 'kwargs': {}},
    #'edncap/fake'    : {'args': [' && '.join([fakeCut.format('e'),eEndcapCut.format('e')])],   'kwargs': {}},
}

sels = selectionParams['Electron'].keys()
idCuts = {
    'cutBasedVeto'   : 'e_cutBasedVeto==1',
    'cutBasedLoose'  : 'e_cutBasedLoose==1',
    'cutBasedMedium' : 'e_cutBasedMedium==1',
    'cutBasedTight'  : 'e_cutBasedTight==1',
    'wwLoose'        : 'e_wwLoose==1',
    'heepV60'        : 'e_heepV60==1',
    'NonTrigWP80'    : 'e_mvaNonTrigWP80==1',
    'NonTrigWP90'    : 'e_mvaNonTrigWP90==1',
    'TrigPre'        : 'e_mvaTrigPre==1',
    'TrigWP80'       : 'e_mvaTrigPre==1 && e_mvaTrigWP80==1',
    'TrigWP90'       : 'e_mvaTrigPre==1 && e_mvaTrigWP90==1',
}
for sel in sels:
    for idName in idCuts:
        name = '{0}/{1}'.format(sel,idName)
        selectionParams['Electron'][name] = deepcopy(selectionParams['Electron'][sel])
        args = selectionParams['Electron'][name]['args']
        selectionParams['Electron'][name]['args'][0] = args[0] + ' && ' + idCuts[idName]

#####################
### muon specific ###
#####################
selectionParams['Muon'] = {
    'default/prompt' : {'args': [promptCut.format('m')], 'kwargs': {}},
    'default/fake'   : {'args': [fakeCut.format('m')],   'kwargs': {}},
}

sels = selectionParams['Muon'].keys()
idCuts = {
    'isLooseMuon_looseIso'  : 'm_isLooseMuon==1 && m_isolation<0.4',
    'isMediumMuon_tightIso' : 'm_isMediumMuon==1 && m_isolation<0.15',
    'isTightMuon_tightIso'  : 'm_isTightMuon==1 && m_isolation<0.15',
    'isHighPtMuon_tightIso' : 'm_isHighPtMuon==1 && m_isolation<0.15',
    'wzLooseMuon'           : 'm_isMediumMuon==1 && m_trackRelIso<0.4 && m_isolation<0.4',
    'wzMediumMuon'          : 'm_isMediumMuon==1 && m_trackRelIso<0.4 && m_isolation<0.15 && m_dz<0.1 && (m_pt<20 ? m_dxy<0.01 : m_dxy<0.02)',
}
for sel in sels:
    for idName in idCuts:
        name = '{0}/{1}'.format(sel,idName)
        selectionParams['Muon'][name] = deepcopy(selectionParams['Muon'][sel])
        args = selectionParams['Muon'][name]['args']
        selectionParams['Muon'][name]['args'][0] = args[0] + ' && ' + idCuts[idName]

####################
### tau specific ###
####################
selectionParams['Tau'] = {
    'default/prompt' : {'args': [promptTauCut.format('t')], 'kwargs': {}},
    'default/fake'   : {'args': [fakeTauCut.format('t')],   'kwargs': {}},
}

sels = selectionParams['Tau'].keys()
againstElectron = {
    'vloose': 't_againstElectronVLooseMVA6==1',
    'loose' : 't_againstElectronLooseMVA6==1',
    'medium': 't_againstElectronMediumMVA6==1',
    'tight' : 't_againstElectronTightMVA6==1',
    'vtight': 't_againstElectronVTightMVA6==1',
}
againstMuon = {
    'loose' : 't_againstMuonLoose3==1',
    'tight' : 't_againstMuonTight3==1',
}
oldId = 't_decayModeFinding==1'
oldIsolation = {
    'loose' : 't_byLooseIsolationMVArun2v1DBoldDMwLT==1',
    'medium': 't_byMediumIsolationMVArun2v1DBoldDMwLT==1',
    'tight' : 't_byTightIsolationMVArun2v1DBoldDMwLT==1',
    'vtight': 't_byVTightIsolationMVArun2v1DBoldDMwLT==1',
}
newId = 't_decayModeFindingNewDMs==1'
newIsolation = {
    'loose' : 't_byLooseIsolationMVArun2v1DBnewDMwLT==1',
    'medium': 't_byMediumIsolationMVArun2v1DBnewDMwLT==1',
    'tight' : 't_byTightIsolationMVArun2v1DBnewDMwLT==1',
    'vtight': 't_byVTightIsolationMVArun2v1DBnewDMwLT==1',
}
idCuts = {}
cutLists = [
    ('vloose','loose','loose'),
    ('vloose','loose','tight'),
    ('vloose','loose','vtight'),
    ('tight','tight','loose'),
    ('tight','tight','tight'),
    ('tight','tight','vtight'),
]
for cl in cutLists:
    el,mu,iso = cl
    idCuts['old_{0}Electron_{1}Muon_{2}Isolation'.format(el,mu,iso)] = ' && '.join([oldId, againstElectron[el], againstMuon[mu], oldIsolation[iso]])
    idCuts['new_{0}Electron_{1}Muon_{2}Isolation'.format(el,mu,iso)] = ' && '.join([newId, againstElectron[el], againstMuon[mu], newIsolation[iso]])
    idCuts['old_{0}Electron_{1}Muon_noIsolation'.format(el,mu)] = ' && '.join([oldId, againstElectron[el], againstMuon[mu]])
    idCuts['new_{0}Electron_{1}Muon_noIsolation'.format(el,mu)] = ' && '.join([newId, againstElectron[el], againstMuon[mu]])
    if iso!='vtight': continue
    idCuts['old_{0}Electron_noMuon_{1}Isolation'.format(el,iso)] = ' && '.join([oldId, againstElectron[el], oldIsolation[iso]])
    idCuts['new_{0}Electron_noMuon_{1}Isolation'.format(el,iso)] = ' && '.join([newId, againstElectron[el], newIsolation[iso]])
    idCuts['old_noElectron_{0}Muon_{1}Isolation'.format(el,mu,iso)] = ' && '.join([oldId, againstMuon[mu], oldIsolation[iso]])
    idCuts['new_noElectron_{0}Muon_{1}Isolation'.format(el,mu,iso)] = ' && '.join([newId, againstMuon[mu], newIsolation[iso]])

for sel in sels:
    for idName in idCuts:
        name = '{0}/{1}'.format(sel,idName)
        selectionParams['Tau'][name] = deepcopy(selectionParams['Tau'][sel])
        args = selectionParams['Tau'][name]['args']
        selectionParams['Tau'][name]['args'][0] = args[0] + ' && ' + idCuts[idName]

##############################
### DijetFakeRate specific ###
##############################
frBaseCut = 'w_mt<25 && met_pt<25'
frBaseCutLoose = '{0}'.format(frBaseCut)
frBaseCutMedium = '{0} && l1_passMedium==1'.format(frBaseCut)
frBaseCutTight = '{0} && l1_passTight==1'.format(frBaseCut)
frScaleFactorLoose = 'l1_looseScale*genWeight*pileupWeight*triggerEfficiency'#/triggerPrescale'
frScaleFactorMedium = 'l1_mediumScale*genWeight*pileupWeight*triggerEfficiency'#/triggerPrescale'
frScaleFactorTight = 'l1_tightScale*genWeight*pileupWeight*triggerEfficiency'#/triggerPrescale'
dataScaleFactor = 'triggerPrescale'
selectionParams['DijetFakeRate'] = {
    'loose'      : {'args': [frBaseCutLoose],                   'kwargs': {'mcscalefactor': frScaleFactorLoose,  'datascalefactor': dataScaleFactor}},
    'medium'     : {'args': [frBaseCutMedium],                  'kwargs': {'mcscalefactor': frScaleFactorMedium, 'datascalefactor': dataScaleFactor}},
    'tight'      : {'args': [frBaseCutTight],                   'kwargs': {'mcscalefactor': frScaleFactorTight,  'datascalefactor': dataScaleFactor}},
    'loose/pt20' : {'args': [frBaseCutLoose + ' && l1_pt>20'],  'kwargs': {'mcscalefactor': frScaleFactorLoose,  'datascalefactor': dataScaleFactor}},
    'medium/pt20': {'args': [frBaseCutMedium + ' && l1_pt>20'], 'kwargs': {'mcscalefactor': frScaleFactorMedium, 'datascalefactor': dataScaleFactor}},
    'tight/pt20' : {'args': [frBaseCutTight + ' && l1_pt>20'],  'kwargs': {'mcscalefactor': frScaleFactorTight,  'datascalefactor': dataScaleFactor}},
}

channels = ['e','m']

etaBins = {
    'e': [0.,0.5,1.0,1.479,2.0,2.5],
    'm': [0.,1.2,2.4],
}
ptBins = {
    'e': [10,15,20,25,30,40,50,60,80,100,2000],
    'm': [10,15,20,25,30,40,50,60,80,100,2000],
}

jetPtBins = [10,15,20,25,30,35,40,45,50]

for sel in ['loose','medium','tight','loose/pt20','medium/pt20','tight/pt20']:
    for chan in channels:
        name = '{0}/{1}'.format(sel,chan)
        selectionParams['DijetFakeRate'][name] = deepcopy(selectionParams['DijetFakeRate'][sel])
        args = selectionParams['DijetFakeRate'][name]['args']
        selectionParams['DijetFakeRate'][name]['args'][0] = args[0] + '&& channel=="{0}"'.format(chan)
        for jetPt in jetPtBins:
            name = '{0}/{1}/jetPt{2}'.format(sel,chan,jetPt)
            selectionParams['DijetFakeRate'][name] = deepcopy(selectionParams['DijetFakeRate'][sel])
            args = selectionParams['DijetFakeRate'][name]['args']
            selectionParams['DijetFakeRate'][name]['args'][0] = args[0] + '&& channel=="{0}" && leadJet_pt>{1}'.format(chan,jetPt)
        if 'pt20' in sel: continue
        for eb in range(len(etaBins[chan])-1):
            directory = '{0}/{1}/etaBin{2}'.format('/'.join(sel.split('_')),chan,eb)
            name = '{0}/{1}/etaBin{2}'.format(sel,chan,eb)
            selectionParams['DijetFakeRate'][name] = deepcopy(selectionParams['DijetFakeRate'][sel])
            args = selectionParams['DijetFakeRate'][name]['args']
            selectionParams['DijetFakeRate'][name]['args'][0] = args[0] + '&& channel=="{0}" && fabs(l1_eta)>={1} && fabs(l1_eta)<{2}'.format(chan,etaBins[chan][eb],etaBins[chan][eb+1])

#############################
### WTauFakeRate specific ###
#############################
frBaseCut = 'z_deltaR>0.02 && m_pt>25.'
frBaseCutLoose = '{0}'.format(frBaseCut)
frBaseCutMedium = '{0} && t_passMedium==1'.format(frBaseCut)
frBaseCutTight = '{0} && t_passTight==1'.format(frBaseCut)
frScaleFactorLoose = 'm_tightScale*t_looseScale*genWeight*pileupWeight*triggerEfficiency'
frScaleFactorMedium = 'm_tightScale*t_mediumScale*genWeight*pileupWeight*triggerEfficiency'
frScaleFactorTight = 'm_tightScale*t_tightScale*genWeight*pileupWeight*triggerEfficiency'
selectionParams['WTauFakeRate'] = {
    'loose'      : {'args': [frBaseCutLoose],                   'kwargs': {'mcscalefactor': frScaleFactorLoose, }},
    'medium'     : {'args': [frBaseCutMedium],                  'kwargs': {'mcscalefactor': frScaleFactorMedium,}},
    'tight'      : {'args': [frBaseCutTight],                   'kwargs': {'mcscalefactor': frScaleFactorTight, }},
}

subsels = {
    'SS'     : 't_charge==m_charge',
    'ZVeto'  : '(z_mass<40 || z_mass>100)',
    'WMt'    : 'wm_mt>60.',
    'all'    : '(z_mass<40 || z_mass>100) && wm_mt>60.',
}

for sel in ['loose','medium','tight']:
    for sub in subsels:
        name = '{0}/{1}'.format(sel,sub)
        selectionParams['WTauFakeRate'][name] = deepcopy(selectionParams['WTauFakeRate'][sel])
        args = selectionParams['WTauFakeRate'][name]['args']
        selectionParams['WTauFakeRate'][name]['args'][0] = ' && '.join([args[0],subsels[sub]])

etaBins = [0.,0.8,1.479,2.3]

sels = selectionParams['WTauFakeRate'].keys()
for sel in sels:
    for eb in range(len(etaBins)-1):
        name = '{0}/etaBin{1}'.format(sel,eb)
        selectionParams['WTauFakeRate'][name] = deepcopy(selectionParams['WTauFakeRate'][sel])
        args = selectionParams['WTauFakeRate'][name]['args']
        selectionParams['WTauFakeRate'][name]['args'][0] = ' && '.join([args[0],'fabs(t_eta)>={0} && fabs(t_eta)<{1}'.format(etaBins[eb],etaBins[eb+1])])

###################
### DY specific ###
###################
dyBaseCut = 'z1_passMedium==1 && z2_passMedium==1 && z_deltaR>0.02 && z_mass>12. && z1_pt>25. && z2_pt>20. && z_mass>50.'
dyScaleFactor = 'z1_mediumScale*z2_mediumScale*genWeight*pileupWeight*triggerEfficiency'

bbCut = 'fabs(z1_eta)<1.479 && fabs(z2_eta)<1.479'
ebCut = '((fabs(z1_eta)<1.479 && fabs(z2_eta)>1.479) || (fabs(z1_eta)>1.479 && fabs(z2_eta)<1.479))'
eeCut = 'fabs(z1_eta)>1.479 && fabs(z2_eta)>1.479'

selectionParams['DY'] = {
    'default' : {'args': [dyBaseCut],              'kwargs': {'mcscalefactor': dyScaleFactor}},
    'bbCut'   : {'args': [dyBaseCut+' && '+bbCut], 'kwargs': {'mcscalefactor': dyScaleFactor}},
    'ebCut'   : {'args': [dyBaseCut+' && '+ebCut], 'kwargs': {'mcscalefactor': dyScaleFactor}},
    'eeCut'   : {'args': [dyBaseCut+' && '+eeCut], 'kwargs': {'mcscalefactor': dyScaleFactor}},
}

channels = ['ee','mm']
projectionParams['DY'] = {}
for chan in channels:
    projectionParams['DY'][chan] = [chan]
histParams['DY'].update(addChannels(deepcopy(histParams['DY']),'channel',len(channels)))


#######################
### Charge specific ###
#######################
chargeBaseCut = 'z1_passMedium==1 && z2_passMedium==1 && z_deltaR>0.02 && z1_pt>20. && z2_pt>10.'
OS = 'z1_charge!=z2_charge'
SS = 'z1_charge==z2_charge'
chargeOS = '{0} && {1}'.format(chargeBaseCut,OS)
chargeSS = '{0} && {1}'.format(chargeBaseCut,SS)
emZMassCut = 'fabs(z_mass-{1})<10.'.format(chargeBaseCut,ZMASS)
chargeScaleFactor = 'z1_mediumScale*z2_mediumScale*genWeight*pileupWeight*triggerEfficiency'
selectionParams['Charge'] = {}
temp = {
    'OS' : {'args': [chargeOS],        'kwargs': {'mcscalefactor': chargeScaleFactor}},
    'SS' : {'args': [chargeSS],        'kwargs': {'mcscalefactor': chargeScaleFactor}},
}

channelMap = {
    'ee': ['ee'],
    'mm': ['mm'],
}
projectionParams['Charge'] = {}
for chan in channelMap:
    projectionParams['Charge'][chan] = channelMap[chan]
histParams['Charge'].update(addChannels(deepcopy(histParams['Charge']),'channel',len(channels)))


##########################
### TauCharge specific ###
##########################
chargeBaseCut = 'z1_passMedium==1 && z2_passMedium==1 && z_deltaR>0.02 && z1_pt>20. && z2_pt>20.'
OS = 'z1_charge!=z2_charge'
SS = 'z1_charge==z2_charge'
chargeOS = '{0} && {1}'.format(chargeBaseCut,OS)
chargeSS = '{0} && {1}'.format(chargeBaseCut,SS)
tZMassCut = 'fabs(z_mass-60)<25.'.format(chargeBaseCut)
chargeScaleFactor = 'z1_mediumScale*z2_mediumScale*genWeight*pileupWeight*triggerEfficiency'
selectionParams['TauCharge'] = {}
temp = {
    'OS'       : {'args': [chargeOS],                   'kwargs': {'mcscalefactor': chargeScaleFactor}},
    'SS'       : {'args': [chargeSS],                   'kwargs': {'mcscalefactor': chargeScaleFactor}},
    'OS/mtCut' : {'args': [chargeOS + ' && w1_mt<40.'], 'kwargs': {'mcscalefactor': chargeScaleFactor}},
    'SS/mtCut' : {'args': [chargeSS + ' && w1_mt<40.'], 'kwargs': {'mcscalefactor': chargeScaleFactor}},
}

channelMap = {
    'tt': ['mt','tm'],
}
projectionParams['TauCharge'] = {}
for chan in channelMap:
    projectionParams['TauCharge'][chan] = channelMap[chan]
histParams['TauCharge'].update(addChannels(deepcopy(histParams['TauCharge']),'channel',len(channels)))


#########################
### wz specific stuff ###
#########################
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


#############
### hpp4l ###
#############
masses = [200,300,400,500,600,700,800,900,1000]

# setup the reco channels
channels = getChannels('Hpp4l')
projectionParams['Hpp4l'] = {}
allChans = []
for chan in channels:
    projectionParams['Hpp4l'][chan] = channels[chan]
    allChans += channels[chan]
histParams['Hpp4l'].update(addChannels(deepcopy(histParams['Hpp4l']),'channel',len(allChans)))

# setup base selections
hpp4lBaseCut = '1'
hpp4lLowMassControl = '{0} && (hpp_mass<100 || hmm_mass<100)'.format(hpp4lBaseCut)
hpp4lScaleFactor = 'hpp1_mediumScale*hpp2_mediumScale*hmm1_mediumScale*hmm2_mediumScale*genWeight*pileupWeight*triggerEfficiency'

# setup fakerate selections
leps = ['hpp1','hpp2','hmm1','hmm2']
scaleMap = {
    'P' : '{0}_looseScale',
    'F' : '{0}_mediumScale',
}

hpp4lBaseScaleFactor = 'genWeight*pileupWeight*triggerEfficiency'
hpp4lMCCut = ' && '.join([genCut.format(l) for l in leps])

# build the cuts for each fake region
hpp4lScaleFactorMap = {}
hpp4lFakeScaleFactorMap = {}
hpp4lCutMap = {}
hpp4lFakeRegions = [''.join(x) for x in product('PF',repeat=4)]
fakeModes = {
    0 : [],
    1 : [],
    2 : [],
    3 : [],
    4 : [],
}
for region in hpp4lFakeRegions:
    fakeModes[region.count('F')] += [region]
    hpp4lScaleFactorMap[region] = '*'.join([scaleMap[region[x]].format(leps[x]) for x in range(4)])
    hpp4lFakeScaleFactorMap[region] = '*'.join(['({0}/(1-{0}))'.format('{0}_mediumFakeRate'.format(leps[x])) for x in range(4) if region[x]=='F'] + ['-1' if region.count('F')%2==0 and region.count('F')>0 else '1'])
    hpp4lCutMap[region] = '(' + ' && '.join(['{0}=={1}'.format('{0}_passMedium'.format(leps[x]),1 if region[x]=='P' else 0) for x in range(4)]) + ')'


# the default selections
selectionParams['Hpp4l'] = {
    'default'   : {'args': [hpp4lBaseCut + ' && ' + hpp4lCutMap['PPPP']],                          'kwargs': {'mcscalefactor': hpp4lScaleFactor}},
    'lowmass'   : {'args': [hpp4lLowMassControl + ' && ' + hpp4lCutMap['PPPP']],                   'kwargs': {'mcscalefactor': hpp4lScaleFactor}},
    #'st100'     : {'args': [hpp4lBaseCut+' && hpp1_pt+hpp2_pt+hmm1_pt+hmm2_pt>100'],               'kwargs': {'mcscalefactor': hpp4lScaleFactor}},
    #'st200'     : {'args': [hpp4lBaseCut+' && hpp1_pt+hpp2_pt+hmm1_pt+hmm2_pt>200'],               'kwargs': {'mcscalefactor': hpp4lScaleFactor}},
    #'st300'     : {'args': [hpp4lBaseCut+' && hpp1_pt+hpp2_pt+hmm1_pt+hmm2_pt>300'],               'kwargs': {'mcscalefactor': hpp4lScaleFactor}},
    #'zveto'     : {'args': [hpp4lBaseCut+' && (z_mass>0 ? fabs(z_mass-{0})>5 : 1)'.format(ZMASS)], 'kwargs': {'mcscalefactor': hpp4lScaleFactor}},
}

# setup old working points
cuts4l = sorted(['st','zveto','dr','mass'])
for mass in masses:
    for hppTaus in range(3):
        for hmmTaus in range(3):
            sideband = getOldSelections('Hpp4l',mass,nTaus=[hppTaus,hmmTaus],cuts=[],invcuts=['mass'])
            massWindow = getOldSelections('Hpp4l',mass,nTaus=[hppTaus,hmmTaus],cuts=['mass'])
            allSideband = getOldSelections('Hpp4l',mass,nTaus=[hppTaus,hmmTaus],cuts=['st','zveto','met','dr'],invcuts=['mass'])
            allMassWindow = getOldSelections('Hpp4l',mass,nTaus=[hppTaus,hmmTaus],cuts=['st','zveto','met','dr','mass'])
            selectionParams['Hpp4l']['old/sideband/{0}/hpp{1}hmm{2}'.format(mass,hppTaus,hmmTaus)] =      {'args': [hpp4lCutMap['PPPP'] + ' && ' + sideband],      'kwargs': {'mcscalefactor': hpp4lScaleFactor, 'countOnly': True}}
            selectionParams['Hpp4l']['old/massWindow/{0}/hpp{1}hmm{2}'.format(mass,hppTaus,hmmTaus)] =    {'args': [hpp4lCutMap['PPPP'] + ' && ' + massWindow],    'kwargs': {'mcscalefactor': hpp4lScaleFactor, 'countOnly': True}}
            selectionParams['Hpp4l']['old/allSideband/{0}/hpp{1}hmm{2}'.format(mass,hppTaus,hmmTaus)] =   {'args': [hpp4lCutMap['PPPP'] + ' && ' + allSideband],   'kwargs': {'mcscalefactor': hpp4lScaleFactor, 'countOnly': True}}
            selectionParams['Hpp4l']['old/allMassWindow/{0}/hpp{1}hmm{2}'.format(mass,hppTaus,hmmTaus)] = {'args': [hpp4lCutMap['PPPP'] + ' && ' + allMassWindow], 'kwargs': {'mcscalefactor': hpp4lScaleFactor, 'countOnly': True}}
            #for cuta in cuts4l:
            #    sel = getOldSelections('Hpp4l',mass,nTaus=[hppTaus,hmmTaus],cuts=[cuta])
            #    if not sel: continue
            #    selectionParams['Hpp4l']['old/{0}Only/{1}/hpp{2}hmm{3}'.format(cuta,mass,hppTaus,hmmTaus)] = {'args': [hpp4lCutMap['PPPP'] + ' && ' + sel], 'kwargs': {'mcscalefactor': hpp4lScaleFactor, 'countOnly': True}}
            #    for cutb in cuts4l:
            #        if cuts4l.index(cutb)<cuts4l.index(cuta): continue
            #        sel = getOldSelections('Hpp4l',mass,nTaus=[hppTaus,hmmTaus],cuts=[cuta,cutb])
            #        if not sel: continue
            #        selectionParams['Hpp4l']['old/{0}_{1}/{2}/hpp{3}hmm{4}'.format(cuta,cutb,mass,hppTaus,hmmTaus)] = {'args': [hpp4lCutMap['PPPP'] + ' && ' + sel], 'kwargs': {'mcscalefactor': hpp4lScaleFactor, 'countOnly': True}}

## fake regions via modes
#for nf in range(5):
#    name = '{0}P{1}F'.format(4-nf,nf)
#    name_regular = '{0}P{1}F_regular'.format(4-nf,nf)
#    regionCut = '(' + ' || '.join([hpp4lCutMap[reg] for reg in fakeModes[nf]]) + ')'
#    regionMCScaleFactor = '*'.join(['({0} ? {1}*{2}*{3}*{4} : 1)'.format(hpp4lCutMap[reg],hpp4lScaleFactorMap[reg],hpp4lFakeScaleFactorMap[reg],hpp4lBaseScaleFactor,'1' if reg=='PPPP' else '-1') for reg in fakeModes[nf]])
#    regionMCScaleFactor_regular = '*'.join(['({0} ? {1}*{2} : 1)'.format(hpp4lCutMap[reg],hpp4lScaleFactorMap[reg],hpp4lBaseScaleFactor) for reg in fakeModes[nf]])
#    regionDataScaleFactor = '*'.join(['({0} ? {1} : 1)'.format(hpp4lCutMap[reg],hpp4lFakeScaleFactorMap[reg]) for reg in fakeModes[nf]])
#    # fake scaled
#    selectionParams['Hpp4l'][name] = {
#        'args': [hpp4lBaseCut + ' && ' + regionCut],
#        'kwargs': {
#            'mccut': hpp4lMCCut,
#            'mcscalefactor': regionMCScaleFactor,
#            'datascalefactor': regionDataScaleFactor,
#        }
#    }
#    selectionParams['Hpp4l']['{0}/lowmass'.format(name)] = {
#        'args': [hpp4lLowMassControl + ' && ' + regionCut],
#        'kwargs': {
#            'mccut': hpp4lMCCut,
#            'mcscalefactor': regionMCScaleFactor,
#            'datascalefactor': regionDataScaleFactor,
#        }
#    }
#    # regular for validation
#    selectionParams['Hpp4l'][name_regular] = {
#        'args': [hpp4lBaseCut + ' && ' + regionCut],
#        'kwargs': {
#            'mcscalefactor': regionMCScaleFactor_regular,
#        }
#    }
#    selectionParams['Hpp4l']['{0}/lowmass'.format(name_regular)] = {
#        'args': [hpp4lLowMassControl + ' && ' + regionCut],
#        'kwargs': {
#            'mcscalefactor': regionMCScaleFactor_regular,
#        }
#    }

# setup gen channel selections
genChans = getGenChannels('Hpp4l')
genChannelsPP = genChans['PP']
genChannelsAP = genChans['AP']

sampleHistParams['Hpp4l'] = {}
sampleProjectionParams['Hpp4l'] = {}
sampleSelectionParams['Hpp4l'] = {}
for mass in masses:
    sampleName = 'HPlusPlusHMinusMinusHTo4L_M-{0}_13TeV-pythia8'.format(mass)
    if version=='80X': sampleName = 'HPlusPlusHMinusMinusHTo4L_M-{0}_TuneCUETP8M1_13TeV_pythia8'.format(mass)
    sampleHistParams['Hpp4l'][sampleName] = addChannels(deepcopy(histParams['Hpp4l']),'genChannel',len(genChannelsPP))
    sampleProjectionParams['Hpp4l'][sampleName] = {}
    for genChan in genChannelsPP:
        sampleProjectionParams['Hpp4l'][sampleName]['gen_{0}'.format(genChan)] = [genChan]

# special selections for samples
# DY-10 0, 1, 2 bins (0 includes 3+)
# DY-50 0, 1, 2, 3, 4 bins (0 includes 5+)
# NOTE: extensions have more stats than exclusive bins, using them
sampleCuts = {
    #'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8' : '(numGenJets==0 || numGenJets>2)',
    #'DY1JetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8': 'numGenJets==1',
    #'DY2JetsToLL_M-10to50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8': 'numGenJets==2',
    #'DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8'     : '(numGenJets==0 || numGenJets>4)',
    #'DY1JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : 'numGenJets==1',
    #'DY2JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : 'numGenJets==2',
    #'DY3JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : 'numGenJets==3',
    #'DY4JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : 'numGenJets==4',
}
for sample,cut in sampleCuts.iteritems():
    sampleSelectionParams['Hpp4l'][sample] = deepcopy(selectionParams['Hpp4l'])
    for sel in selectionParams['Hpp4l'].keys():
        sampleSelectionParams['Hpp4l'][sample][sel]['args'][0] += ' && {0}'.format(cut)

#############
### hpp3l ###
#############
# setup the reco channels
channels = getChannels('Hpp3l')
projectionParams['Hpp3l'] = {}
allChans = []
for chan in channels:
    projectionParams['Hpp3l'][chan] = channels[chan]
    allChans += channels[chan]
histParams['Hpp3l'].update(addChannels(deepcopy(histParams['Hpp3l']),'channel',len(allChans)))

# setup base selections
hpp3lBaseCut = 'hpp1_passMedium==1 && hpp2_passMedium==1 && hm1_passMedium==1'
hpp3lLowMassControl = '{0} && hpp_mass<100'.format(hpp3lBaseCut)
hpp3lScaleFactor = 'hpp1_mediumScale*hpp2_mediumScale*hm1_mediumScale*genWeight*pileupWeight*triggerEfficiency'
selectionParams['Hpp3l'] = {
    'default' : {'args': [hpp3lBaseCut],        'kwargs': {'mcscalefactor': hpp3lScaleFactor}},
    'lowmass' : {'args': [hpp3lLowMassControl], 'kwargs': {'mcscalefactor': hpp3lScaleFactor}},
}

# setup gen channel selections
genChans = getGenChannels('Hpp3l')
genChannelsPP = genChans['PP']
genChannelsAP = genChans['AP']

masses = [200,300,400,500,600,700,800,900,1000]

sampleHistParams['Hpp3l'] = {}
sampleProjectionParams['Hpp3l'] = {}
sampleSelectionParams['Hpp3l'] = {}
for mass in masses:
    sampleName = 'HPlusPlusHMinusMinusHTo4L_M-{0}_13TeV-pythia8'.format(mass)
    if version=='80X': sampleName = 'HPlusPlusHMinusMinusHTo4L_M-{0}_TuneCUETP8M1_13TeV_pythia8'.format(mass)
    sampleHistParams['Hpp3l'][sampleName] = addChannels(deepcopy(histParams['Hpp3l']),'genChannel',len(genChannelsPP))
    sampleProjectionParams['Hpp3l'][sampleName] = {}
    for genChan in genChannelsPP:
        sampleProjectionParams['Hpp3l'][sampleName]['gen_{0}'.format(genChan)] = [genChan]


#############################
### functions to retrieve ###
#############################
def getHistParams(analysis,sample=''):
    params = {}
    if analysis in histParams:
        params.update(histParams[analysis])
    if analysis in sampleHistParams:
        if sample in sampleHistParams[analysis]:
            params.update(sampleHistParams[analysis][sample])
    return params

def getHistSelections(analysis,sample=''):
    params = {}
    if analysis in selectionParams:
        params.update(selectionParams[analysis])
    if analysis in sampleSelectionParams:
        if sample in sampleSelectionParams[analysis]:
            params.update(sampleSelectionParams[analysis][sample])
    return params

def getProjectionParams(analysis,sample=''):
    params = deepcopy(projectionParams['common'])
    if analysis in projectionParams:
        params.update(projectionParams[analysis])
    if analysis in sampleProjectionParams:
        if sample in sampleProjectionParams[analysis]:
            params.update(sampleProjectionParams[analysis][sample])
    return params
