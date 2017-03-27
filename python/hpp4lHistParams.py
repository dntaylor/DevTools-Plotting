from copy import deepcopy
from itertools import product, combinations_with_replacement

from DevTools.Plotter.utilities import ZMASS, addChannels
from DevTools.Plotter.higgsUtilities import getChannels, getGenChannels, getSelections

from DevTools.Utilities.utilities import getCMSSWVersion

version = getCMSSWVersion()

genCut = '{0}_genMatch==1 && {0}_genDeltaR<0.1'

def buildHpp4l(selectionParams,sampleSelectionParams,projectionParams,sampleProjectionParams,histParams,sampleHistParams,**kwargs):
    shift = kwargs.pop('shift','')
    countOnly = kwargs.pop('countOnly',False)

    # histogram definitions
    histParams['Hpp4l'] = {
        'count'                       : {'xVariable': '1',                              'xBinning': [1,0,2],                }, # just a count of events passing selection
        'numVertices'                 : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],              },
        #'numVertices_noreweight'      : {'xVariable': 'numVertices',                    'xBinning': [40,0,40],              'mcscale': '1./pileupWeight'},
        #'pileupWeight'                : {'xVariable': 'pileupWeight',                   'xBinning': [40,0,40],              'mcscale': '1./pileupWeight'},
        'met'                         : {'xVariable': 'met_pt',                         'xBinning': [50, 0, 500],           },
        'metPhi'                      : {'xVariable': 'met_phi',                        'xBinning': [50, -3.14159, 3.14159],},
        # h++
        'hppMass'                     : {'xVariable': 'hpp_mass',                       'xBinning': [160, 0, 1600],         },
        'hppMt'                       : {'xVariable': 'hppmet_mt',                      'xBinning': [160, 0, 1600],         },
        'hppPt'                       : {'xVariable': 'hpp_pt',                         'xBinning': [160, 0, 1600],         },
        #'hppEta'                      : {'xVariable': 'hpp_eta',                        'xBinning': [100, -5, 5],           },
        'hppDeltaR'                   : {'xVariable': 'hpp_deltaR',                     'xBinning': [50, 0, 5],             },
        'hppLeadingLeptonPt'          : {'xVariable': 'hpp1_pt',                        'xBinning': [100, 0, 1000],         },
        'hppLeadingLeptonEta'         : {'xVariable': 'hpp1_eta',                       'xBinning': [50, -2.5, 2.5],        },
        'hppSubLeadingLeptonPt'       : {'xVariable': 'hpp2_pt',                        'xBinning': [100, 0, 1000],         },
        'hppSubLeadingLeptonEta'      : {'xVariable': 'hpp2_eta',                       'xBinning': [50, -2.5, 2.5],        },
        # h--
        'hmmMass'                     : {'xVariable': 'hmm_mass',                       'xBinning': [160, 0, 1600],         },
        'hmmMt'                       : {'xVariable': 'hmmmet_mt',                      'xBinning': [160, 0, 1600],         },
        'hmmPt'                       : {'xVariable': 'hmm_pt',                         'xBinning': [160, 0, 1600],         },
        #'hmmEta'                      : {'xVariable': 'hmm_eta',                        'xBinning': [100, -5, 5],           },
        'hmmDeltaR'                   : {'xVariable': 'hmm_deltaR',                     'xBinning': [50, 0, 5],             },
        'hmmLeadingLeptonPt'          : {'xVariable': 'hmm1_pt',                        'xBinning': [100, 0, 1000],         },
        'hmmLeadingLeptonEta'         : {'xVariable': 'hmm1_eta',                       'xBinning': [50, -2.5, 2.5],        },
        'hmmSubLeadingLeptonPt'       : {'xVariable': 'hmm2_pt',                        'xBinning': [100, 0, 1000],         },
        'hmmSubLeadingLeptonEta'      : {'xVariable': 'hmm2_eta',                       'xBinning': [50, -2.5, 2.5],        },
        # best z
        'zMass'                       : {'xVariable': 'z_mass',                         'xBinning': [50, 0, 500],            'selection': 'z_mass>0.',},
        'mllMinusMZ'                  : {'xVariable': 'fabs(z_mass-{0})'.format(ZMASS), 'xBinning': [5, 0, 100],             'selection': 'z_mass>0.',},
        'zPt'                         : {'xVariable': 'z_pt',                           'xBinning': [50, 0, 500],            'selection': 'z_mass>0.',},
        #'zEta'                        : {'xVariable': 'z_eta',                          'xBinning': [100, -5, 5],            'selection': 'z_mass>0.',},
        'zDeltaR'                     : {'xVariable': 'z_deltaR',                       'xBinning': [50, 0, 5],              'selection': 'z_mass>0.',},
        #'zLeadingLeptonPt'            : {'xVariable': 'z1_pt',                          'xBinning': [100, 0, 1000],          'selection': 'z_mass>0.',},
        #'zLeadingLeptonEta'           : {'xVariable': 'z1_eta',                         'xBinning': [50, -2.5, 2.5],         'selection': 'z_mass>0.',},
        #'zSubLeadingLeptonPt'         : {'xVariable': 'z2_pt',                          'xBinning': [100, 0, 1000],          'selection': 'z_mass>0.',},
        #'zSubLeadingLeptonEta'        : {'xVariable': 'z2_eta',                         'xBinning': [50, -2.5, 2.5],         'selection': 'z_mass>0.',},
        # event
        'mass'                        : {'xVariable': '4l_mass',                        'xBinning': [200, 0, 2000],         },
        'st'                          : {'xVariable': 'hpp1_pt+hpp2_pt+hmm1_pt+hmm2_pt','xBinning': [200, 0, 2000],         },
        'nJets'                       : {'xVariable': 'numJetsTight30',                 'xBinning': [11, -0.5, 10.5],        },
        # gen truth
        #'hppLeadingLeptonGenMatch'    : {'xVariable': 'hpp1_genMatch',                  'xBinning': [2, 0, 2],              },
        #'hppLeadingLeptonGenDeltaR'   : {'xVariable': 'hpp1_genDeltaR',                 'xBinning': [50, 0, 5],             },
        #'hppSubLeadingLeptonGenMatch' : {'xVariable': 'hpp2_genMatch',                  'xBinning': [2, 0, 2],              },
        #'hpmSubLeadingLeptonGenDeltaR': {'xVariable': 'hpp2_genDeltaR',                 'xBinning': [50, 0, 5],             },
        #'hmmLeadingLeptonGenMatch'    : {'xVariable': 'hmm1_genMatch',                  'xBinning': [2, 0, 2],              },
        #'hmmLeadingLeptonGenDeltaR'   : {'xVariable': 'hmm1_genDeltaR',                 'xBinning': [50, 0, 5],             },
        #'hmmSubLeadingLeptonGenMatch' : {'xVariable': 'hmm2_genMatch',                  'xBinning': [2, 0, 2],              },
        #'hmmSubLeadingLeptonGenDeltaR': {'xVariable': 'hmm2_genDeltaR',                 'xBinning': [50, 0, 5],             },
    }


    masses = [200,300,400,500,600,700,800,900,1000,1100,1200,1300,1400,1500]
    
    # setup the reco channels
    channels = getChannels('Hpp4l')
    projectionParams['Hpp4l'] = {}
    allChans = []
    for chan in channels:
        projectionParams['Hpp4l'][chan] = channels[chan]
        allChans += channels[chan]
    histParams['Hpp4l'].update(addChannels(deepcopy(histParams['Hpp4l']),'channel',len(allChans)))
    
    leps = ['hpp1','hpp2','hmm1','hmm2']
    hpp4lBaseScaleFactor = '*'.join(['genWeight','pileupWeight','triggerEfficiency'])
    if shift=='trigUp': hpp4lBaseScaleFactor = '*'.join(['genWeight','pileupWeight','triggerEfficiencyUp'])
    if shift=='trigDown': hpp4lBaseScaleFactor = '*'.join(['genWeight','pileupWeight','triggerEfficiencyDown'])
    if shift=='puUp': hpp4lBaseScaleFactor = '*'.join(['genWeight','pileupWeightUp','triggerEfficiency'])
    if shift=='puDown': hpp4lBaseScaleFactor = '*'.join(['genWeight','pileupWeightDown','triggerEfficiency'])

    # setup base selections
    hpp4lBaseCut = '1'
    hpp4lLowMassControl = '{0} && (hpp_mass<100 || hmm_mass<100)'.format(hpp4lBaseCut)
    hpp4lScaleFactor = '*'.join(['{0}_mediumScale'.format(lep) for lep in leps]+[hpp4lBaseScaleFactor])
    if shift=='lepUp': hpp4lScaleFactor = '*'.join(['{0}_mediumScaleUp'.format(lep) for lep in leps]+[hpp4lBaseScaleFactor])
    if shift=='lepDown': hpp4lScaleFactor = '*'.join(['{0}_mediumScaleDown'.format(lep) for lep in leps]+[hpp4lBaseScaleFactor])
    
    # setup fakerate selections
    scaleMap = {
        'P' : '{0}_looseScale',
        'F' : '{0}_mediumScale',
    }
    if shift=='lepUp':
        scaleMap = {
            'P' : '{0}_looseScaleUp',
            'F' : '{0}_mediumScaleUp',
        }
    if shift=='lepDown':
        scaleMap = {
            'P' : '{0}_looseScaleDown',
            'F' : '{0}_mediumScaleDown',
        }


    fakeVal = '{0}_mediumFakeRate'
    if shift=='fakeUp': fakeVal = '{0}_mediumFakeRateUp'
    if shift=='fakeDown': fakeVal = '{0}_mediumFakeRateDown'
    
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
        hpp4lFakeScaleFactorMap[region] = '*'.join(['({0}/(1-{0}))'.format(fakeVal.format(leps[x])) for x in range(4) if region[x]=='F'] + ['-1' if region.count('F')%2==0 and region.count('F')>0 else '1'])
        hpp4lCutMap[region] = '(' + ' && '.join(['{0}=={1}'.format('{0}_passMedium'.format(leps[x]),1 if region[x]=='P' else 0) for x in range(4)]) + ')'
    
    # the default selections
    selectionParams['Hpp4l'] = {
        'default'   : {'args': [hpp4lBaseCut + ' && ' + hpp4lCutMap['PPPP']],                          'kwargs': {'mcscalefactor': hpp4lScaleFactor, 'countOnly': countOnly,}},
        'lowmass'   : {'args': [hpp4lLowMassControl + ' && ' + hpp4lCutMap['PPPP']],                   'kwargs': {'mcscalefactor': hpp4lScaleFactor, 'countOnly': countOnly,}},
        #'st100'     : {'args': [hpp4lBaseCut+' && hpp1_pt+hpp2_pt+hmm1_pt+hmm2_pt>100'],               'kwargs': {'mcscalefactor': hpp4lScaleFactor, 'countOnly': countOnly,}},
        #'st200'     : {'args': [hpp4lBaseCut+' && hpp1_pt+hpp2_pt+hmm1_pt+hmm2_pt>200'],               'kwargs': {'mcscalefactor': hpp4lScaleFactor, 'countOnly': countOnly,}},
        #'st300'     : {'args': [hpp4lBaseCut+' && hpp1_pt+hpp2_pt+hmm1_pt+hmm2_pt>300'],               'kwargs': {'mcscalefactor': hpp4lScaleFactor, 'countOnly': countOnly,}},
        #'zveto'     : {'args': [hpp4lBaseCut+' && (z_mass>0 ? fabs(z_mass-{0})>5 : 1)'.format(ZMASS)], 'kwargs': {'mcscalefactor': hpp4lScaleFactor, 'countOnly': countOnly,}},
    }
    
    # setup working points
    cuts4l = sorted(['st','zveto','dr','mass'])
    #for mass in masses:
    for mass in [500]:
        for hppTaus in range(3):
            for hmmTaus in range(3):
                # old
                #sideband = getSelections('Hpp4l',mass,nTaus=[hppTaus,hmmTaus],cuts=[],invcuts=['mass'],mode='old')
                #massWindow = getSelections('Hpp4l',mass,nTaus=[hppTaus,hmmTaus],cuts=['mass'],mode='old')
                #allSideband = getSelections('Hpp4l',mass,nTaus=[hppTaus,hmmTaus],cuts=['st','zveto','met','dr'],invcuts=['mass'],mode='old')
                #allMassWindow = getSelections('Hpp4l',mass,nTaus=[hppTaus,hmmTaus],cuts=['st','zveto','met','dr','mass'],mode='old')
                #selectionParams['Hpp4l']['old/sideband/{0}/hpp{1}hmm{2}'.format(mass,hppTaus,hmmTaus)] =      {'args': [hpp4lCutMap['PPPP'] + ' && ' + sideband],      'kwargs': {'mcscalefactor': hpp4lScaleFactor, 'countOnly': True}}
                #selectionParams['Hpp4l']['old/massWindow/{0}/hpp{1}hmm{2}'.format(mass,hppTaus,hmmTaus)] =    {'args': [hpp4lCutMap['PPPP'] + ' && ' + massWindow],    'kwargs': {'mcscalefactor': hpp4lScaleFactor, 'countOnly': True}}
                #selectionParams['Hpp4l']['old/allSideband/{0}/hpp{1}hmm{2}'.format(mass,hppTaus,hmmTaus)] =   {'args': [hpp4lCutMap['PPPP'] + ' && ' + allSideband],   'kwargs': {'mcscalefactor': hpp4lScaleFactor, 'countOnly': True}}
                #selectionParams['Hpp4l']['old/allMassWindow/{0}/hpp{1}hmm{2}'.format(mass,hppTaus,hmmTaus)] = {'args': [hpp4lCutMap['PPPP'] + ' && ' + allMassWindow], 'kwargs': {'mcscalefactor': hpp4lScaleFactor, 'countOnly': True}}
                # new
                #sideband = getSelections('Hpp4l',mass,nTaus=[hppTaus,hmmTaus],cuts=[],invcuts=['st','zveto','met','dr','mass'],mode='new')
                #massWindow = getSelections('Hpp4l',mass,nTaus=[hppTaus,hmmTaus],cuts=['mass'],invcuts=['st','zveto','met','dr'],mode='new')
                #allSideband = getSelections('Hpp4l',mass,nTaus=[hppTaus,hmmTaus],cuts=['st','zveto','met','dr'],invcuts=['mass'],mode='new')
                #allMassWindow = getSelections('Hpp4l',mass,nTaus=[hppTaus,hmmTaus],cuts=['st','zveto','met','dr','mass'],invcuts=[],mode='new')
                #selectionParams['Hpp4l']['new/sideband/{0}/hpp{1}hmm{2}'.format(mass,hppTaus,hmmTaus)] =      {'args': [hpp4lCutMap['PPPP'] + ' && ' + sideband],      'kwargs': {'mcscalefactor': hpp4lScaleFactor, 'countOnly': True}}
                #selectionParams['Hpp4l']['new/massWindow/{0}/hpp{1}hmm{2}'.format(mass,hppTaus,hmmTaus)] =    {'args': [hpp4lCutMap['PPPP'] + ' && ' + massWindow],    'kwargs': {'mcscalefactor': hpp4lScaleFactor, 'countOnly': True}}
                #selectionParams['Hpp4l']['new/allSideband/{0}/hpp{1}hmm{2}'.format(mass,hppTaus,hmmTaus)] =   {'args': [hpp4lCutMap['PPPP'] + ' && ' + allSideband],   'kwargs': {'mcscalefactor': hpp4lScaleFactor, 'countOnly': True}}
                #selectionParams['Hpp4l']['new/allMassWindow/{0}/hpp{1}hmm{2}'.format(mass,hppTaus,hmmTaus)] = {'args': [hpp4lCutMap['PPPP'] + ' && ' + allMassWindow], 'kwargs': {'mcscalefactor': hpp4lScaleFactor, 'countOnly': True}}
                # n-1
                nMinusOneMassWindow = getSelections('Hpp4l',mass,nTaus=[hppTaus,hmmTaus],cuts=['st','zveto','met','dr'],invcuts=[],mode='new')
                selectionParams['Hpp4l']['nMinusOne/massWindow/{0}/hpp{1}hmm{2}'.format(mass,hppTaus,hmmTaus)] = {'args': [hpp4lCutMap['PPPP'] + ' && ' + nMinusOneMassWindow], 'kwargs': {'mcscalefactor': hpp4lScaleFactor,}}
    
    # fake regions via modes
    #for nf in range(3): # limit to speed up
    # TODO: change to only add for 4 real leptons and data
    for nf in range(5):
        name = '{0}P{1}F'.format(4-nf,nf)
        name_regular = '{0}P{1}F_regular'.format(4-nf,nf)
        regionCut = '(' + ' || '.join([hpp4lCutMap[reg] for reg in fakeModes[nf]]) + ')'
        regionMCScaleFactor = '*'.join(['({0} ? {1}*{2}*{3}*{4} : 1)'.format(hpp4lCutMap[reg],hpp4lScaleFactorMap[reg],hpp4lFakeScaleFactorMap[reg],hpp4lBaseScaleFactor,'1' if reg=='PPPP' else '-1') for reg in fakeModes[nf]])
        regionMCScaleFactor_regular = '*'.join(['({0} ? {1}*{2} : 1)'.format(hpp4lCutMap[reg],hpp4lScaleFactorMap[reg],hpp4lBaseScaleFactor) for reg in fakeModes[nf]])
        regionDataScaleFactor = '*'.join(['({0} ? {1} : 1)'.format(hpp4lCutMap[reg],hpp4lFakeScaleFactorMap[reg]) for reg in fakeModes[nf]])
        # fake scaled
        selectionParams['Hpp4l'][name] = {
            'args': [hpp4lBaseCut + ' && ' + regionCut],
            'kwargs': {
                'mccut': hpp4lMCCut,
                'mcscalefactor': regionMCScaleFactor,
                'datascalefactor': regionDataScaleFactor,
                'countOnly': countOnly,
            }
        }
        selectionParams['Hpp4l']['{0}/lowmass'.format(name)] = {
            'args': [hpp4lLowMassControl + ' && ' + regionCut],
            'kwargs': {
                'mccut': hpp4lMCCut,
                'mcscalefactor': regionMCScaleFactor,
                'datascalefactor': regionDataScaleFactor,
                'countOnly': countOnly,
            }
        }
        # regular for validation
        selectionParams['Hpp4l'][name_regular] = {
            'args': [hpp4lBaseCut + ' && ' + regionCut],
            'kwargs': {
                'mcscalefactor': regionMCScaleFactor_regular,
                'countOnly': countOnly,
            }
        }
        selectionParams['Hpp4l']['{0}/lowmass'.format(name_regular)] = {
            'args': [hpp4lLowMassControl + ' && ' + regionCut],
            'kwargs': {
                'mcscalefactor': regionMCScaleFactor_regular,
                'countOnly': countOnly,
            }
        }
        # setup working points
        cuts4l = sorted(['st','zveto','dr','mass'])
        #for mass in masses:
        for mass in [500]:
            for hppTaus in range(3):
                for hmmTaus in range(3):
                    # old
                    #sideband = getSelections('Hpp4l',mass,nTaus=[hppTaus,hmmTaus],cuts=[],invcuts=['mass'],mode='old')
                    #massWindow = getSelections('Hpp4l',mass,nTaus=[hppTaus,hmmTaus],cuts=['mass'],mode='old')
                    #allSideband = getSelections('Hpp4l',mass,nTaus=[hppTaus,hmmTaus],cuts=['st','zveto','met','dr'],invcuts=['mass'],mode='old')
                    #allMassWindow = getSelections('Hpp4l',mass,nTaus=[hppTaus,hmmTaus],cuts=['st','zveto','met','dr','mass'],mode='old')
                    #selectionParams['Hpp4l']['old/sideband/{0}/hpp{1}hmm{2}'.format(mass,hppTaus,hmmTaus)] =      {'args': [hpp4lCutMap['PPPP'] + ' && ' + sideband],      'kwargs': {'mcscalefactor': hpp4lScaleFactor, 'countOnly': True}}
                    #selectionParams['Hpp4l']['old/massWindow/{0}/hpp{1}hmm{2}'.format(mass,hppTaus,hmmTaus)] =    {'args': [hpp4lCutMap['PPPP'] + ' && ' + massWindow],    'kwargs': {'mcscalefactor': hpp4lScaleFactor, 'countOnly': True}}
                    #selectionParams['Hpp4l']['old/allSideband/{0}/hpp{1}hmm{2}'.format(mass,hppTaus,hmmTaus)] =   {'args': [hpp4lCutMap['PPPP'] + ' && ' + allSideband],   'kwargs': {'mcscalefactor': hpp4lScaleFactor, 'countOnly': True}}
                    #selectionParams['Hpp4l']['old/allMassWindow/{0}/hpp{1}hmm{2}'.format(mass,hppTaus,hmmTaus)] = {'args': [hpp4lCutMap['PPPP'] + ' && ' + allMassWindow], 'kwargs': {'mcscalefactor': hpp4lScaleFactor, 'countOnly': True}}
                    # new
                    #sideband = getSelections('Hpp4l',mass,nTaus=[hppTaus,hmmTaus],cuts=[],invcuts=['st','zveto','met','dr','mass'],mode='new')
                    #massWindow = getSelections('Hpp4l',mass,nTaus=[hppTaus,hmmTaus],cuts=['mass'],invcuts=['st','zveto','met','dr'],mode='new')
                    #allSideband = getSelections('Hpp4l',mass,nTaus=[hppTaus,hmmTaus],cuts=['st','zveto','met','dr'],invcuts=['mass'],mode='new')
                    #allMassWindow = getSelections('Hpp4l',mass,nTaus=[hppTaus,hmmTaus],cuts=['st','zveto','met','dr','mass'],invcuts=[],mode='new')
                    #selectionParams['Hpp4l']['{3}/new/sideband/{0}/hpp{1}hmm{2}'.format(mass,hppTaus,hmmTaus,name)] =      {
                    #    'args': [hpp4lBaseCut + ' && ' + regionCut + ' && ' + sideband],      
                    #    'kwargs': {
                    #        'mccut': hpp4lMCCut,
                    #        'mcscalefactor': regionMCScaleFactor,
                    #        'datascalefactor': regionDataScaleFactor,
                    #        'countOnly': True,
                    #    },
                    #}
                    #selectionParams['Hpp4l']['{3}/new/massWindow/{0}/hpp{1}hmm{2}'.format(mass,hppTaus,hmmTaus,name)] =    {
                    #    'args': [hpp4lBaseCut + ' && ' + regionCut + ' && ' + massWindow],    
                    #    'kwargs': {
                    #        'mccut': hpp4lMCCut,
                    #        'mcscalefactor': regionMCScaleFactor,
                    #        'datascalefactor': regionDataScaleFactor,
                    #        'countOnly': True,
                    #    },
                    #}
                    #selectionParams['Hpp4l']['{3}/new/allSideband/{0}/hpp{1}hmm{2}'.format(mass,hppTaus,hmmTaus,name)] =   {
                    #    'args': [hpp4lBaseCut + ' && ' + regionCut + ' && ' + allSideband],   
                    #    'kwargs': {
                    #        'mccut': hpp4lMCCut,
                    #        'mcscalefactor': regionMCScaleFactor,
                    #        'datascalefactor': regionDataScaleFactor,
                    #        'countOnly': True,
                    #    },
                    #}
                    #selectionParams['Hpp4l']['{3}/new/allMassWindow/{0}/hpp{1}hmm{2}'.format(mass,hppTaus,hmmTaus,name)] = {
                    #    'args': [hpp4lBaseCut + ' && ' + regionCut + ' && ' + allMassWindow], 
                    #    'kwargs': {
                    #        'mccut': hpp4lMCCut,
                    #        'mcscalefactor': regionMCScaleFactor,
                    #        'datascalefactor': regionDataScaleFactor,
                    #        'countOnly': True,
                    #    },
                    #}
                    # n-1
                    nMinusOneMassWindow = getSelections('Hpp4l',mass,nTaus=[hppTaus,hmmTaus],cuts=['st','zveto','met','dr'],invcuts=[],mode='new')
                    selectionParams['Hpp4l']['{3}/nMinusOne/massWindow/{0}/hpp{1}hmm{2}'.format(mass,hppTaus,hmmTaus,name)] = {
                        'args': [hpp4lBaseCut + ' && ' + regionCut + ' && ' + nMinusOneMassWindow], 
                        'kwargs': {
                            'mccut': hpp4lMCCut,
                            'mcscalefactor': regionMCScaleFactor,
                            'datascalefactor': regionDataScaleFactor,
                        },
                    }
    
    # setup gen channel selections
    genChans = getGenChannels('Hpp4l')
    genChannelsPP = genChans['PP']
    genChannelsAP = genChans['AP']
    
    sampleHistParams['Hpp4l'] = {}
    sampleProjectionParams['Hpp4l'] = {}
    sampleSelectionParams['Hpp4l'] = {}
    for mass in masses:
        # pp
        sampleName = 'HPlusPlusHMinusMinusHTo4L_M-{0}_13TeV-pythia8'.format(mass)
        if version=='80X': sampleName = 'HPlusPlusHMinusMinusHTo4L_M-{0}_TuneCUETP8M1_13TeV_pythia8'.format(mass)
        sampleHistParams['Hpp4l'][sampleName] = addChannels(deepcopy(histParams['Hpp4l']),'genChannel',len(genChannelsPP))
        sampleProjectionParams['Hpp4l'][sampleName] = {}
        for genChan in genChannelsPP:
            sampleProjectionParams['Hpp4l'][sampleName]['gen_{0}'.format(genChan)] = [genChan]
        #sampleSelectionParams['Hpp4l'][sampleName] = deepcopy(selectionParams['Hpp4l'])
        #for sel in selectionParams['Hpp4l']:
        #    if sel.split('/')[0] in ['3P1F','2P2F','1P3F','0P4F']:
        #        sampleSelectionParams['Hpp4l'][sampleName][sel] = {}
        #    if str(mass) in sel.split('/'):
        #        sampleSelectionParams['Hpp4l'][sampleName][sel] = {}
        # ap
        sampleName = 'HPlusPlusHMinusHTo3L_M-{0}_TuneCUETP8M1_13TeV_calchep-pythia8'.format(mass)
        sampleHistParams['Hpp4l'][sampleName] = addChannels(deepcopy(histParams['Hpp4l']),'genChannel',len(genChannelsAP))
        sampleProjectionParams['Hpp4l'][sampleName] = {}
        for genChan in genChannelsAP:
            sampleProjectionParams['Hpp4l'][sampleName]['gen_{0}'.format(genChan)] = [genChan]
        #sampleSelectionParams['Hpp4l'][sampleName] = deepcopy(selectionParams['Hpp4l'])
        #for sel in selectionParams['Hpp4l']:
        #    if sel.split('/')[0] in ['3P1F','2P2F','1P3F','0P4F']:
        #        sampleSelectionParams['Hpp4l'][sampleName][sel] = {}
        #    if str(mass) in sel.split('/'):
        #        sampleSelectionParams['Hpp4l'][sampleName][sel] = {}
    
    # special selections for samples
    # DY-10 0, 1, 2 bins (0 includes 3+)
    # DY-50 0, 1, 2, 3, 4 bins (0 includes 5+)
    sampleCuts = {
        'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'  : '(numGenJets==0 || numGenJets>4)',
        'DY1JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' : 'numGenJets==1',
        'DY2JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' : 'numGenJets==2',
        'DY3JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' : 'numGenJets==3',
        'DY4JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' : 'numGenJets==4',
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
    for sample,cut in sampleCuts.iteritems():
        sampleSelectionParams['Hpp4l'][sample] = deepcopy(selectionParams['Hpp4l'])
        for sel in selectionParams['Hpp4l'].keys():
            sampleSelectionParams['Hpp4l'][sample][sel]['args'][0] += ' && {0}'.format(cut)
    

    # speacial scales for individual samples
    sampleScales = {
        'ZZTo4L_13TeV_powheg_pythia8'       : 'qqZZkfactor/1.1',
        'ZZTo4L_13TeV-amcatnloFXFX-pythia8' : 'qqZZkfactor/1.1',
    }
    for sample,scale in sampleScales.iteritems():
        sampleSelectionParams['Hpp4l'][sample] = deepcopy(selectionParams['Hpp4l'])
        for sel in selectionParams['Hpp4l'].keys():
            sampleSelectionParams['Hpp4l'][sample][sel]['kwargs']['mcscalefactor'] = '*'.join([sampleSelectionParams['Hpp4l'][sample][sel]['kwargs']['mcscalefactor'],scale])
    



