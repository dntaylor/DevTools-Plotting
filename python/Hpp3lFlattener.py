#!/usr/bin/env python
import argparse
import logging
import os
import sys
import itertools
import operator
from array import array

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from NtupleFlattener import NtupleFlattener
from DevTools.Utilities.utilities import prod, ZMASS
from DevTools.Plotter.higgsUtilities import *
from DevTools.Analyzer.BTagScales import BTagScales

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


class Hpp3lFlattener(NtupleFlattener):
    '''
    Hpp3l flattener
    '''

    def __init__(self,sample,**kwargs):
        # controls
        self.new = True # uses NewDMs for tau loose ID
        self.tauFakeMode = 'z' # allowed: w, z
        self.doDMFakes = True
        self.datadriven = True
        self.datadrivenRegular = False
        self.lowmass = True
        self.zveto = True
        self.doGen = True
        self.doBVeto = True
        self.limitOnly = False
        self.mass = 500
        self.btag_scales = BTagScales('80X')

        # setup properties
        self.leps = ['hpp1','hpp2','hm1']
        self.channels = getChannels('Hpp3l')
        if self.doGen:
            gen = getGenChannels('Hpp3l')
            if 'HPlusPlusHMinusMinus' in sample:
                self.genChannels = gen['PP']
            elif 'HPlusPlusHMinus' in sample:
                self.genChannels = gen['AP']
        self.baseCutMap = {
            'pt20'     : lambda row: all([getattr(row,'{0}_pt'.format(l))>20 for l in self.leps]),
            '3lmassCut': lambda row: getattr(row,'3l_mass')>100,
            'looseId'  : lambda row: all([getattr(row,'{0}_passLoose{1}'.format(l,'New' if self.new else ''))>0.5 for l in self.leps]),
            #'bjetveto' : lambda row: row.numBjetsTight30==0,
            #'bjetveto' : lambda row: all([getattr(row,'{0}jet_passCSVv2M'.format(l))<0.5 for l in self.leps]),
        }
        self.lowmassCutMap = {
            'pt20'     : lambda row: all([getattr(row,'{0}_pt'.format(l))>20 for l in self.leps]),
            'hppVeto'  : lambda row: row.hpp_mass<100,
            '3lmassCut': lambda row: getattr(row,'3l_mass')>100,
            'looseId'  : lambda row: all([getattr(row,'{0}_passLoose{1}'.format(l,'New' if self.new else ''))>0.5 for l in self.leps]),
            #'bjetveto' : lambda row: row.numBjetsTight30==0,
            #'bjetveto' : lambda row: all([getattr(row,'{0}jet_passCSVv2M'.format(l))<0.5 for l in self.leps]),
        }
        self.zvetoCutMap = {
            'pt20'     : lambda row: all([getattr(row,'{0}_pt'.format(l))>20 for l in self.leps]),
            '3lmassCut': lambda row: getattr(row,'3l_mass')>100,
            'looseId'  : lambda row: all([getattr(row,'{0}_passLoose{1}'.format(l,'New' if self.new else ''))>0.5 for l in self.leps]),
            'zVeto'    : lambda row: abs(getattr(row,'z_mass')-ZMASS)>10,
            #'bjetveto' : lambda row: row.numBjetsTight30==0,
            #'bjetveto' : lambda row: all([getattr(row,'{0}jet_passCSVv2M'.format(l))<0.5 for l in self.leps]),
        }
        self.selectionMap = {}
        self.selectionMap['default'] = lambda row: all([self.baseCutMap[cut](row) for cut in self.baseCutMap])
        if self.lowmass: self.selectionMap['lowmass'] = lambda row: all([self.lowmassCutMap[cut](row) for cut in self.lowmassCutMap])
        if self.zveto: self.selectionMap['zveto'] = lambda row: all([self.zvetoCutMap[cut](row) for cut in self.zvetoCutMap])

        # sample signal plot
        self.cutRegions = {}
        masses = [200,300,400,500,600,700,800,900,1000,1100,1200,1300,1400,1500] if self.limitOnly else [self.mass]
        for mass in masses:
            self.cutRegions[mass] = getSelectionMap('Hpp3l',mass)
            self.selectionMap['nMinusOne/massWindow/{0}/hpp0'.format(mass)] = lambda row: all([self.cutRegions[mass][0][v](row) for v in ['st','zveto','met','dr']])
            self.selectionMap['nMinusOne/massWindow/{0}/hpp1'.format(mass)] = lambda row: all([self.cutRegions[mass][1][v](row) for v in ['st','zveto','met','dr']])
            self.selectionMap['nMinusOne/massWindow/{0}/hpp2'.format(mass)] = lambda row: all([self.cutRegions[mass][2][v](row) for v in ['st','zveto','met','dr']])
        
        # tight loose ids to test fakerates
        #loose = '{}loose'.format('new' if self.new else 'old')
        #mva = 'tauMVA{}'.format('new' if self.new else 'old')
        #self.selectionMapDM = {}
        #self.selectionMapDM['lowmass/{}_n0p2'.format(loose)] = lambda row: all([self.lowmassCutMap[cut](row) for cut in self.lowmassCutMap]) and all([getattr(row,'{}_{}'.format(l,mva))>-0.2 for l in self.leps if abs(getattr(row,'{}_pdgId'.format(l)))==15])
        #self.selectionMapDM['lowmass/{}_n0p1'.format(loose)] = lambda row: all([self.lowmassCutMap[cut](row) for cut in self.lowmassCutMap]) and all([getattr(row,'{}_{}'.format(l,mva))>-0.1 for l in self.leps if abs(getattr(row,'{}_pdgId'.format(l)))==15])
        #self.selectionMapDM['lowmass/{}_0p0'.format(loose)]  = lambda row: all([self.lowmassCutMap[cut](row) for cut in self.lowmassCutMap]) and all([getattr(row,'{}_{}'.format(l,mva))> 0.0 for l in self.leps if abs(getattr(row,'{}_pdgId'.format(l)))==15])
        #self.selectionMapDM['lowmass/{}_0p1'.format(loose)]  = lambda row: all([self.lowmassCutMap[cut](row) for cut in self.lowmassCutMap]) and all([getattr(row,'{}_{}'.format(l,mva))> 0.1 for l in self.leps if abs(getattr(row,'{}_pdgId'.format(l)))==15])
        #self.selectionMapDM['lowmass/{}_0p2'.format(loose)]  = lambda row: all([self.lowmassCutMap[cut](row) for cut in self.lowmassCutMap]) and all([getattr(row,'{}_{}'.format(l,mva))> 0.2 for l in self.leps if abs(getattr(row,'{}_pdgId'.format(l)))==15])
        #self.selectionMapDM['lowmass/{}_0p3'.format(loose)]  = lambda row: all([self.lowmassCutMap[cut](row) for cut in self.lowmassCutMap]) and all([getattr(row,'{}_{}'.format(l,mva))> 0.3 for l in self.leps if abs(getattr(row,'{}_pdgId'.format(l)))==15])
        #self.selectionMapDM['lowmass/{}_0p4'.format(loose)]  = lambda row: all([self.lowmassCutMap[cut](row) for cut in self.lowmassCutMap]) and all([getattr(row,'{}_{}'.format(l,mva))> 0.4 for l in self.leps if abs(getattr(row,'{}_pdgId'.format(l)))==15])

        self.selections = []
        self.selectionHists = {}
        for sel in self.selectionMap:
            self.selections += [sel]
            if not self.datadriven: continue
            for nf in range(4):
                fakeChan = '{0}P{1}F'.format(3-nf,nf)
                self.selections += ['{0}/{1}'.format(fakeChan,sel)]
                if self.datadrivenRegular: self.selections += ['{0}_regular/{1}'.format(fakeChan,sel)]

        #limitedHists = [
        #    'count',
        #    'hpp1Pt','hpp1Eta','hpp1DecayMode',
        #    'hpp2Pt','hpp2Eta','hpp2DecayMode',
        #    'hm1Pt','hm1Eta', 'hm1DecayMode',
        #]
        #for sel in self.selectionMapDM:
        #    self.selections += [sel]
        #    self.selectionHists[sel] = limitedHists
        #    for nf in range(4):
        #        fakeChan = '{0}P{1}F'.format(3-nf,nf)
        #        self.selections += ['{0}/{1}'.format(fakeChan,sel)]
        #        self.selectionHists['{0}/{1}'.format(fakeChan,sel)] = limitedHists


        # setup histogram parameters
        self.histParams = {
            'count'                       : {'x': lambda row: 1,                                  'xBinning': [1,0,2],                 }, # just a count of events passing selection
            'numVertices'                 : {'x': lambda row: row.numVertices,                    'xBinning': [60,0,60],               },
            'met'                         : {'x': lambda row: row.met_pt,                         'xBinning': [500, 0, 500],           },
            'metPhi'                      : {'x': lambda row: row.met_phi,                        'xBinning': [50, -3.14159, 3.14159], },
            # h++/h--
            'hppMass'                     : {'x': lambda row: row.hpp_mass,                       'xBinning': [1600, 0, 1600],         },
            'hppPt'                       : {'x': lambda row: row.hpp_pt,                         'xBinning': [1600, 0, 1600],         },
            'hppDeltaR'                   : {'x': lambda row: row.hpp_deltaR,                     'xBinning': [50, 0, 5],              },
            'hppLeadingLeptonPt'          : {'x': lambda row: row.hpp1_pt,                        'xBinning': [1000, 0, 1000],         },
            'hppLeadingLeptonEta'         : {'x': lambda row: row.hpp1_eta,                       'xBinning': [50, -2.5, 2.5],         },
            'hppLeadingLeptonDecayMode'   : {'x': lambda row: row.hpp1_decayMode,                 'xBinning': [12, 0, 12],             },
            'hppSubLeadingLeptonPt'       : {'x': lambda row: row.hpp2_pt,                        'xBinning': [1000, 0, 1000],         },
            'hppSubLeadingLeptonEta'      : {'x': lambda row: row.hpp2_eta,                       'xBinning': [50, -2.5, 2.5],         },
            'hppSubLeadingLeptonDecayMode': {'x': lambda row: row.hpp2_decayMode,                 'xBinning': [12, 0, 12],             },
            'hppLeadingLeptonJetCSV'      : {'x': lambda row: row.hpp1jet_CSVv2,                  'xBinning': [50, 0, 1],              },
            'hppSubLeadingLeptonJetCSV'   : {'x': lambda row: row.hpp2jet_CSVv2,                  'xBinning': [50, 0, 1],              },
            # h-/h+
            'hmMass'                      : {'x': lambda row: row.hm_mt,                          'xBinning': [1600, 0, 1600],         },
            'hmPt'                        : {'x': lambda row: row.hm_pt,                          'xBinning': [1600, 0, 1600],         },
            'hmLeptonPt'                  : {'x': lambda row: row.hm1_pt,                         'xBinning': [1000, 0, 1000],         },
            'hmLeptonEta'                 : {'x': lambda row: row.hm1_eta,                        'xBinning': [50, -2.5, 2.5],         },
            'hmLeptonDecayMode'           : {'x': lambda row: row.hm1_decayMode,                  'xBinning': [12, 0, 12],             },
            'hmLeptonJetCSV'              : {'x': lambda row: row.hm1jet_CSVv2,                   'xBinning': [50, 0, 1],              },
            # best z
            'zMass'                       : {'x': lambda row: row.z_mass,                         'xBinning': [500, 0, 500],           'selection': lambda row: row.z_mass>0.,},
            'mllMinusMZ'                  : {'x': lambda row: abs(row.z_mass-ZMASS),              'xBinning': [100, 0, 100],           'selection': lambda row: row.z_mass>0.,},
            'zPt'                         : {'x': lambda row: row.z_pt,                           'xBinning': [500, 0, 500],           'selection': lambda row: row.z_mass>0.,},
            # w
            'wMass'                       : {'x': lambda row: row.w_mt,                           'xBinning': [500, 0, 500],           'selection': lambda row: row.z_mass>0.,},
            'wPt'                         : {'x': lambda row: row.w_pt,                           'xBinning': [500, 0, 500],           'selection': lambda row: row.z_mass>0.,},
            # event
            'mass'                        : {'x': lambda row: getattr(row,'3l_mass'),             'xBinning': [2000, 0, 2000],         },
            'st'                          : {'x': lambda row: row.hpp1_pt+row.hpp2_pt+row.hm1_pt, 'xBinning': [2000, 0, 2000],         },
            'nJets'                       : {'x': lambda row: row.numJetsTight30,                 'xBinning': [11, -0.5, 10.5],        },
            'nBJets'                      : {'x': lambda row: row.numBjetsTight30,                'xBinning': [11, -0.5, 10.5],        },
            # for validating datadriven
            #'hpp1Pt'                      : {'x': lambda row: row.hpp1_pt,                        'xBinning': array('d', [0,20,25,30,40,50,60,100]),},
            #'hpp1Eta'                     : {'x': lambda row: row.hpp1_eta,                       'xBinning': array('d', [-2.5,-1.479,0,1.479,2.5]),},
            #'hpp1DecayMode'               : {'x': lambda row: row.hpp1_decayMode,                 'xBinning': [12, 0, 12],                          },
            #'hpp2Pt'                      : {'x': lambda row: row.hpp2_pt,                        'xBinning': array('d', [0,20,25,30,40,50,60,100]),},
            #'hpp2Eta'                     : {'x': lambda row: row.hpp2_eta,                       'xBinning': array('d', [-2.5,-1.479,0,1.479,2.5]),},
            #'hpp2DecayMode'               : {'x': lambda row: row.hpp2_decayMode,                 'xBinning': [12, 0, 12],                          },
            #'hm1Pt'                       : {'x': lambda row: row.hm1_pt,                         'xBinning': array('d', [0,20,25,30,40,50,60,100]),},
            #'hm1Eta'                      : {'x': lambda row: row.hm1_eta,                        'xBinning': array('d', [-2.5,-1.479,0,1.479,2.5]),},
            #'hm1DecayMode'                : {'x': lambda row: row.hm1_decayMode,                  'xBinning': [12, 0, 12],                          },
            # 2D
            'hppMass_hmMass'              : {'x': lambda row: row.hpp_mass, 'y': lambda row: row.hm_mt,                          'xBinning': [100, 0, 2000], 'yBinning': [100, 0, 2000],},
            'hppMass_st'                  : {'x': lambda row: row.hpp_mass, 'y': lambda row: row.hpp1_pt+row.hpp2_pt+row.hm1_pt, 'xBinning': [100, 0, 2000], 'yBinning': [100, 0, 2000],},
            # for limits
            'hppMassForLimits'            : {'x': lambda row: row.hpp_mass,                       'xBinning': [160, 0, 1600],          'doGen': True,},
        }

        if self.limitOnly:
            self.histParams = {
                'hppMassForLimits'            : {'x': lambda row: row.hpp_mass,                       'xBinning': [160, 0, 1600],          'doGen': True,},
            }

        # initialize flattener
        super(Hpp3lFlattener, self).__init__('Hpp3l',sample,**kwargs)


        # alternative fakerates
        self.fakekey = '{num}_{denom}'
        self.fakehists = {'electrons': {}, 'muons': {}, 'taus': {},}

        fake_path = '{0}/src/DevTools/Analyzer/data/fakerates_dijet_hpp_13TeV_Run2016BCDEFGH.root'.format(os.environ['CMSSW_BASE'])
        self.fake_hpp_rootfile = ROOT.TFile(fake_path)
        self.fakehists['electrons'][self.fakekey.format(num='HppMedium',denom='HppLooseNew')] = self.fake_hpp_rootfile.Get('e/medium_loose/fakeratePtEta')
        self.fakehists['electrons'][self.fakekey.format(num='HppTight', denom='HppLooseNew')] = self.fake_hpp_rootfile.Get('e/tight_loose/fakeratePtEta')
        self.fakehists['electrons'][self.fakekey.format(num='HppMedium',denom='HppLoose')]    = self.fake_hpp_rootfile.Get('e/medium_loose/fakeratePtEta')
        self.fakehists['electrons'][self.fakekey.format(num='HppTight', denom='HppLoose')]    = self.fake_hpp_rootfile.Get('e/tight_loose/fakeratePtEta')
        self.fakehists['electrons'][self.fakekey.format(num='HppTight', denom='HppMedium')]   = self.fake_hpp_rootfile.Get('e/tight_medium/fakeratePtEta')
        self.fakehists['muons'    ][self.fakekey.format(num='HppMedium',denom='HppLooseNew')] = self.fake_hpp_rootfile.Get('m/medium_loose/fakeratePtEta')
        self.fakehists['muons'    ][self.fakekey.format(num='HppTight', denom='HppLooseNew')] = self.fake_hpp_rootfile.Get('m/tight_loose/fakeratePtEta')
        self.fakehists['muons'    ][self.fakekey.format(num='HppMedium',denom='HppLoose')]    = self.fake_hpp_rootfile.Get('m/medium_loose/fakeratePtEta')
        self.fakehists['muons'    ][self.fakekey.format(num='HppTight', denom='HppLoose')]    = self.fake_hpp_rootfile.Get('m/tight_loose/fakeratePtEta')
        self.fakehists['muons'    ][self.fakekey.format(num='HppTight', denom='HppMedium')]   = self.fake_hpp_rootfile.Get('m/tight_medium/fakeratePtEta')

        if self.tauFakeMode=='w':
            fake_path = '{0}/src/DevTools/Analyzer/data/fakerates_w_tau_13TeV_Run2016BCDEFGH.root'.format(os.environ['CMSSW_BASE'])
        elif self.tauFakeMode=='z':
            fake_path = '{0}/src/DevTools/Analyzer/data/fakerates_z_tau_13TeV_Run2016BCDEFGH.root'.format(os.environ['CMSSW_BASE'])
        else:
            logging.error('Undefined tau fake mode {0}'.format(self.tauFakeMode))
            raise
        self.fake_hpp_rootfile_tau = ROOT.TFile(fake_path)
        self.fakehists['taus'][self.fakekey.format(num='HppMedium',denom='HppLooseNew')]     = self.fake_hpp_rootfile_tau.Get('medium_newloose/fakeratePtEta')
        self.fakehists['taus'][self.fakekey.format(num='HppTight', denom='HppLooseNew')]     = self.fake_hpp_rootfile_tau.Get('tight_newloose/fakeratePtEta')
        self.fakehists['taus'][self.fakekey.format(num='HppMedium',denom='HppLooseNewDM0')]  = self.fake_hpp_rootfile_tau.Get('medium_newloose/fakeratePtEtaDM0')
        self.fakehists['taus'][self.fakekey.format(num='HppTight', denom='HppLooseNewDM0')]  = self.fake_hpp_rootfile_tau.Get('tight_newloose/fakeratePtEtaDM0')
        self.fakehists['taus'][self.fakekey.format(num='HppMedium',denom='HppLooseNewDM1')]  = self.fake_hpp_rootfile_tau.Get('medium_newloose/fakeratePtEtaDM1')
        self.fakehists['taus'][self.fakekey.format(num='HppTight', denom='HppLooseNewDM1')]  = self.fake_hpp_rootfile_tau.Get('tight_newloose/fakeratePtEtaDM1')
        self.fakehists['taus'][self.fakekey.format(num='HppMedium',denom='HppLooseNewDM10')] = self.fake_hpp_rootfile_tau.Get('medium_newloose/fakeratePtEtaDM10')
        self.fakehists['taus'][self.fakekey.format(num='HppTight', denom='HppLooseNewDM10')] = self.fake_hpp_rootfile_tau.Get('tight_newloose/fakeratePtEtaDM10')
        self.fakehists['taus'][self.fakekey.format(num='HppMedium',denom='HppLoose')]        = self.fake_hpp_rootfile_tau.Get('medium_loose/fakeratePtEta')
        self.fakehists['taus'][self.fakekey.format(num='HppTight', denom='HppLoose')]        = self.fake_hpp_rootfile_tau.Get('tight_loose/fakeratePtEta')
        self.fakehists['taus'][self.fakekey.format(num='HppMedium',denom='HppLooseDM0')]     = self.fake_hpp_rootfile_tau.Get('medium_loose/fakeratePtEtaDM0')
        self.fakehists['taus'][self.fakekey.format(num='HppTight', denom='HppLooseDM0')]     = self.fake_hpp_rootfile_tau.Get('tight_loose/fakeratePtEtaDM0')
        self.fakehists['taus'][self.fakekey.format(num='HppMedium',denom='HppLooseDM1')]     = self.fake_hpp_rootfile_tau.Get('medium_loose/fakeratePtEtaDM1')
        self.fakehists['taus'][self.fakekey.format(num='HppTight', denom='HppLooseDM1')]     = self.fake_hpp_rootfile_tau.Get('tight_loose/fakeratePtEtaDM1')
        self.fakehists['taus'][self.fakekey.format(num='HppMedium',denom='HppLooseDM10')]    = self.fake_hpp_rootfile_tau.Get('medium_loose/fakeratePtEtaDM10')
        self.fakehists['taus'][self.fakekey.format(num='HppTight', denom='HppLooseDM10')]    = self.fake_hpp_rootfile_tau.Get('tight_loose/fakeratePtEtaDM10')
        self.fakehists['taus'][self.fakekey.format(num='HppTight', denom='HppMedium')]       = self.fake_hpp_rootfile_tau.Get('tight_medium/fakeratePtEta')

        for num in ['medium','tight']:
            for dlab in ['oldloose','newloose']:
                for dcut in ['n0p2','n0p1','0p0','0p1','0p2','0p3','0p4']:
                    denom = '{}_{}'.format(dlab,dcut)
                    self.fakehists['taus'][self.fakekey.format(num=num,denom=denom)]         = self.fake_hpp_rootfile_tau.Get('{}_{}/fakeratePtEta'.format(num,denom))
                    self.fakehists['taus'][self.fakekey.format(num=num,denom=denom+'DM0')]   = self.fake_hpp_rootfile_tau.Get('{}_{}/fakeratePtEtaDM0'.format(num,denom))
                    self.fakehists['taus'][self.fakekey.format(num=num,denom=denom+'DM1')]   = self.fake_hpp_rootfile_tau.Get('{}_{}/fakeratePtEtaDM1'.format(num,denom))
                    self.fakehists['taus'][self.fakekey.format(num=num,denom=denom+'DM10')]  = self.fake_hpp_rootfile_tau.Get('{}_{}/fakeratePtEtaDM10'.format(num,denom))

        self.scaleMap = {
            'F' : '{0}_looseScale',
            'P' : '{0}_mediumScale',
        }

        self.fakeVal = '{0}_mediumNewFakeRate' if self.new else '{0}_mediumFakeRate'

        self.lepID = '{0}_passMedium'
        self.lepIDLoose = '{0}_passLooseNew' if self.new else '{0}_passLoose'


    def getFakeRate(self,lep,pt,eta,num,denom,dm=None):
        if lep=='taus' and self.doDMFakes:
            if dm in [0,5]:
                denom = denom + 'DM0'
            elif dm in [1,6]:
                denom = denom + 'DM1'
            elif dm in [10]:
                denom = denom + 'DM10'
        key = self.fakekey.format(num=num,denom=denom)
        hist = self.fakehists[lep][key]
        if pt > 100.: pt = 99.
        b = hist.FindBin(pt,abs(eta))
        val, err = hist.GetBinContent(b), hist.GetBinError(b)
        #print key, pt, abs(eta), val, err
        return val, err

    def getBTagWeight(self,row):
        op = 1 # medium
        s = 'central'
        if self.shift == 'btagUp': s = 'up'
        if self.shift == 'btagDown': s = 'down'
        w = 1
        for l in self.leps:
            pt = getattr(row,'{0}jet_pt'.format(l))
            if not pt>0: continue
            eta = getattr(row,'{0}jet_eta'.format(l))
            hf = getattr(row,'{}jet_hadronFlavour'.format(l))
            if hf==5: #b
                flavor = 0
            elif hf==4: #c
                flavor = 1
            else: # light
                flavor = 2
            sf = self.btag_scales.get_sf_csv(1,pt,eta,shift=s,flavor=flavor)
            if getattr(row,'{0}jet_passCSVv2M'.format(l))>0.5:
                w *= 1-sf
        return w

    def getWeight(self,row,doFake=False,fakeNum=None,fakeDenom=None):
        if not fakeNum: fakeNum = 'HppMedium'
        if not fakeDenom: fakeDenom = 'HppLoose{0}'.format('New' if self.new else '')
        passID = [getattr(row,self.lepID.format(l)) for l in self.leps]
        if row.isData:
            weight = 1.
        else:
            # per event weights
            base = ['genWeight','pileupWeight','triggerEfficiency']
            if self.shift=='trigUp': base = ['genWeight','pileupWeight','triggerEfficiencyUp']
            if self.shift=='trigDown': base = ['genWeight','pileupWeight','triggerEfficiencyDown']
            if self.shift=='puUp': base = ['genWeight','pileupWeightUp','triggerEfficiency']
            if self.shift=='puDown': base = ['genWeight','pileupWeightDown','triggerEfficiency']
            for l,lep in enumerate(self.leps):
                shiftString = ''
                if self.shift == 'lepUp': shiftString = 'Up'
                if self.shift == 'lepDown': shiftString = 'Down'
                base += [self.scaleMap['P' if passID[l] else 'F'].format(lep)+shiftString]
            vals = [getattr(row,scale) for scale in base]
            for scale,val in zip(base,vals):
                if val != val: logging.warning('{0}: {1} is NaN'.format(row.channel,scale))
            weight = prod([val for val in vals if val==val])
            # scale to lumi/xsec
            weight *= float(self.intLumi)/self.sampleLumi if self.sampleLumi else 0.
            if hasattr(row,'qqZZkfactor'): weight *= row.qqZZkfactor/1.1 # ZZ variable k factor
            # b taggin (veto)
            if self.doBVeto: weight *= self.getBTagWeight(row)
        # fake scales
        if doFake:
            chanMap = {'e': 'electrons', 'm': 'muons', 't': 'taus',}
            chan = ''.join([x for x in row.channel if x in 'emt'])
            pts = [getattr(row,'{0}_pt'.format(x)) for x in self.leps]
            etas = [getattr(row,'{0}_eta'.format(x)) for x in self.leps]
            region = ''.join(['P' if x else 'F' for x in passID])
            sign = -1 if region.count('F')%2==0 and region.count('F')>0 else 1
            weight *= sign
            if not row.isData and not all(passID): weight *= -1 # subtract off MC in control
            for l,lep in enumerate(self.leps):
                if not passID[l]:
                    # recalculate
                    dm = None if chan[l]!='t' else getattr(row,'{0}_decayMode'.format(lep))
                    fn = fakeNum
                    fd = fakeDenom
                    if isinstance(fakeNum,dict): fn = fakeNum[chan[l]]
                    if isinstance(fakeDenom,dict): fd = fakeDenom[chan[l]]
                    fakeEff = self.getFakeRate(chanMap[chan[l]], pts[l], etas[l], fn, fd, dm=dm)[0]

                    # read from tree
                    #fake = self.fakeVal.format(lep)
                    #if self.shift=='fakeUp': fake += 'Up'
                    #if self.shift=='fakeDown': fake += 'Down'
                    #fakeEff = getattr(row,fake)

                    weight *= fakeEff/(1-fakeEff)

        return weight


    def perRowAction(self,row):
        isData = row.isData

        passPt = [getattr(row,'{0}_pt'.format(l))>20 for l in self.leps]
        if not all(passPt): return # all leptons pt>20
        # Don't do for MC, events that pass btag contribute a factor of 1-SF
        passbveto = all([getattr(row,'{0}jet_passCSVv2M'.format(l))<0.5 for l in self.leps])
        if isData and not passbveto and self.doBVeto: return

        # per sample cuts
        keep = True
        if self.sample=='DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'  : keep = row.numGenJets==0 or row.numGenJets>4
        if self.sample=='DY1JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' : keep = row.numGenJets==1
        if self.sample=='DY2JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' : keep = row.numGenJets==2
        if self.sample=='DY3JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' : keep = row.numGenJets==3
        if self.sample=='DY4JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' : keep = row.numGenJets==4
        if self.sample=='DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'      : keep = row.numGenJets==0 or row.numGenJets>4
        if self.sample=='DY1JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : keep = row.numGenJets==1
        if self.sample=='DY2JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : keep = row.numGenJets==2
        if self.sample=='DY3JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : keep = row.numGenJets==3
        if self.sample=='DY4JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : keep = row.numGenJets==4
        if self.sample=='WJetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'           : keep = row.numGenJets==0 or row.numGenJets>4
        if self.sample=='W1JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          : keep = row.numGenJets==1
        if self.sample=='W2JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          : keep = row.numGenJets==2
        if self.sample=='W3JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          : keep = row.numGenJets==3
        if self.sample=='W4JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          : keep = row.numGenJets==4
        if not keep: return


        # define weights
        w = self.getWeight(row)
        wf = self.getWeight(row,doFake=True)
        loose = '{}loose'.format('new' if self.new else 'old')
        wfs = {}
        cuts =  ['n0p2','n0p1','0p0','0p1','0p2','0p3','0p4']
        for cut in cuts:
            fn = {'e': 'HppMedium', 'm': 'HppMedium', 't': 'medium'}
            fd = {'e': 'HppLoose{0}'.format('New' if self.new else ''), 'm': 'HppLoose{0}'.format('New' if self.new else ''), 't': '{}_{}'.format(loose,cut)}
            wfs[cut] = self.getWeight(row,doFake=True,fakeNum=fn,fakeDenom=fd)

        # setup channels
        passID = [getattr(row,self.lepID.format(l)) for l in self.leps]
        passIDLoose = [getattr(row,self.lepIDLoose.format(l)) for l in self.leps]
        region = ''.join(['P' if p else 'F' for p in passID])
        nf = region.count('F')
        fakeChan = '{0}P{1}F'.format(3-nf,nf)
        recoChan = ''.join([x for x in row.channel if x in 'emt'])
        recoChan = ''.join(sorted(recoChan[:2]) + sorted(recoChan[2:3]))
        if isData or not self.doGen:
            genChan = 'all'
        else:
            genChan = row.genChannel
            if 'HPlusPlus' in self.sample:
                if 'HPlusPlusHMinusMinus' in self.sample:
                    genChan = ''.join(sorted(genChan[:2]) + sorted(genChan[2:4]))
                else:
                    genChan = ''.join(sorted(genChan[:2]) + sorted(genChan[2:3]))
            else:
                genChan = 'all'

        # define count regions
        if not isData:
            #genCut = all([getattr(row,'{0}_genMatch'.format(lep)) and getattr(row,'{0}_genDeltaR'.format(lep))<0.1 for lep in self.leps])
            genCut = all([
                (getattr(row,'{0}_genMatch'.format(lep)) and getattr(row,'{0}_genDeltaR'.format(lep))<0.1)
                or
                (getattr(row,'{0}_genJetMatch'.format(lep)) and getattr(row,'{0}_genJetDeltaR'.format(lep))<0.1)
                for lep in self.leps
            ])

        # define plot regions
        for sel in self.selectionMap:
            result = self.selectionMap[sel](row)
            if result:
                if not all(passIDLoose): continue
                if all(passID): self.fill(row,sel,w,recoChan,genChan)
                if not self.datadriven: continue
                if isData or genCut: self.fill(row,fakeChan+'/'+sel,wf,recoChan,genChan)
                if self.datadrivenRegular:self.fill(row,fakeChan+'_regular/'+sel,w,recoChan,genChan)

        #for sel in self.selectionMapDM:
        #    result = self.selectionMapDM[sel](row)
        #    if result:
        #        for cut in cuts:
        #            if '_'+cut not in sel: continue
        #            #if not all(passIDLoose): continue # already in selection
        #            if all(passID): self.fill(row,sel,w,recoChan,genChan)
        #            if not self.datadriven: continue
        #            if isData or genCut: self.fill(row,fakeChan+'/'+sel,wfs[cut],recoChan,genChan)


def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Run Flattener')

    #parser.add_argument('sample', type=str, default='DoubleMuon', nargs='?', help='Sample to flatten')
    parser.add_argument('sample', type=str, default='HPlusPlusHMinusHTo3L_M-500_13TeV-calchep-pythia8', nargs='?', help='Sample to flatten')
    parser.add_argument('shift', type=str, default='', nargs='?', help='Shift to apply to scale factors')

    return parser.parse_args(argv)

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = parse_command_line(argv)

    flattener = Hpp3lFlattener(
        args.sample,
        shift=args.shift,
    )

    flattener.flatten()

    return 0

if __name__ == "__main__":
    status = main()
    sys.exit(status)

