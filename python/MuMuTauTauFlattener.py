#!/usr/bin/env python
import argparse
import logging
import os
import sys
import itertools
import operator
from array import array
import numpy as np
from numpy.linalg import inv

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from NtupleFlattener import NtupleFlattener
from DevTools.Utilities.utilities import prod, ZMASS
from DevTools.Plotter.higgsUtilities import *
from DevTools.Analyzer.utilities import deltaR, deltaPhi

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


def deltaR_row(row,a,b):
    aEta = getattr(row,'{}_eta'.format(a))
    aPhi = getattr(row,'{}_phi'.format(a))
    bEta = getattr(row,'{}_eta'.format(b))
    bPhi = getattr(row,'{}_phi'.format(b))
    return deltaR(aEta,aPhi,bEta,bPhi)

doMedium = True
doCutbased = False
def passTauIso(row,lep):
    if doMedium:
        return getattr(row,'{}_byMediumIsolationMVArun2v1DBoldDMwLT'.format(lep))>0.5
    else:
        return getattr(row,'{}_byVLooseIsolationMVArun2v1DBoldDMwLT'.format(lep))>0.5


class MuMuTauTauFlattener(NtupleFlattener):
    '''
    MuMuTauTau flattener
    '''

    def __init__(self,sample,**kwargs):
        # controls
        self.doDatadriven = True
        self.datadrivenRegular = False
        self.doLowMass = True
        self.doHighMass = True
        self.doBVeto = True
        self.doDM = True
        self.doPerDM = True
        self.doMedium = doMedium
        self.doCutbased = doCutbased
        self.doMediumMuon = False
        self.doGenMatch = False

        if self.doMediumMuon:
            logging.error('Cannot use medium muon yet')
            raise

        #self.newloose = [-1,-0.2,-0.1,0.0,0.1,0.2,0.3,0.4]
        #self.newloose = [-1,-0.2,0.0,0.2,0.4]
        self.newloose = []

        self.mvaCut = -1
        self.isoCut = 0.4

        # setup properties
        self.leps = ['am1','am2','ath','atm']
        self.baseCutMap = {
            'ammWindow'  : lambda row: row.amm_mass>1 and row.amm_mass<30,
            'attDR'      : lambda row: row.att_deltaR<0.8,
            'trigger'    : lambda row: row.am1_matches_IsoMu24 or row.am1_matches_IsoTkMu24,
            'mmDR'       : lambda row: row.amm_deltaR<1,
            'm1tmDR'     : lambda row: deltaR_row(row,'am1','atm')>0.4,
            'm1thDR'     : lambda row: deltaR_row(row,'am1','ath')>0.8,
            'm2tmDR'     : lambda row: deltaR_row(row,'am2','atm')>0.4,
            'm2thDR'     : lambda row: deltaR_row(row,'am2','ath')>0.8,
            #'tPt'        : lambda row: row.ath_pt>20,
            #'muonIso'    : lambda row: row.am1_isolation<self.isoCut and row.am2_isolation<self.isoCut,
            #'tauMVA'     : lambda row: row.ath_byIsolationMVArun2v1DBoldDMwLTraw>self.mvaCut,
        }
        if self.doBVeto:
            self.baseCutMap['taubveto'] = lambda row: row.athjet_passCSVv2M<0.5
        if self.doMediumMuon:
            self.baseCutMap['medMuon'] = lambda row: row.am1_isMediumMuonICHEP and row.am2_isMediumMuonICHEP and row.atm_isMediumMuonICHEP

        self.regionMap = {
            'regionA' : lambda row: row.am1_isolation<0.25 and row.am2_isolation<0.25 and passTauIso(row,'ath'),
            'regionB' : lambda row: row.am1_isolation<0.25 and row.am2_isolation<0.25 and not passTauIso(row,'ath'),
            'regionC' : lambda row: row.am1_isolation<0.25 and row.am2_isolation>0.25 and passTauIso(row,'ath'),
            'regionD' : lambda row: row.am1_isolation<0.25 and row.am2_isolation>0.25 and not passTauIso(row,'ath'),
        }

        self.selectionMap = {}
        baseSels = []
        self.selectionMap['default'] = lambda row: all([self.baseCutMap[cut](row) for cut in self.baseCutMap])
        baseSels += ['default']
        if self.doPerDM:
            self.selectionMap['dm0/default']  = lambda row: row.ath_decayMode==0  and all([self.baseCutMap[cut](row) for cut in self.baseCutMap])
            self.selectionMap['dm1/default']  = lambda row: row.ath_decayMode==1  and all([self.baseCutMap[cut](row) for cut in self.baseCutMap])
            self.selectionMap['dm10/default'] = lambda row: row.ath_decayMode==10 and all([self.baseCutMap[cut](row) for cut in self.baseCutMap])
            baseSels += ['dm0']
            baseSels += ['dm1']
            baseSels += ['dm10']
        if self.doLowMass:
            self.selectionMap['lowmass/default'] = lambda row: row.amm_mass<4 and all([self.baseCutMap[cut](row) for cut in self.baseCutMap])
            baseSels += ['lowmass']
            if self.doPerDM:
                self.selectionMap['lowmassdm0/default']  = lambda row: row.ath_decayMode==0  and row.amm_mass<4 and all([self.baseCutMap[cut](row) for cut in self.baseCutMap])
                self.selectionMap['lowmassdm1/default']  = lambda row: row.ath_decayMode==1  and row.amm_mass<4 and all([self.baseCutMap[cut](row) for cut in self.baseCutMap])
                self.selectionMap['lowmassdm10/default'] = lambda row: row.ath_decayMode==10 and row.amm_mass<4 and all([self.baseCutMap[cut](row) for cut in self.baseCutMap])
                baseSels += ['lowmassdm0']
                baseSels += ['lowmassdm1']
                baseSels += ['lowmassdm10']
        if self.doHighMass:
            self.selectionMap['highmass/default'] = lambda row: row.amm_mass>25 and all([self.baseCutMap[cut](row) for cut in self.baseCutMap])
            baseSels += ['highmass']
            if self.doPerDM:
                self.selectionMap['highmassdm0/default']  = lambda row: row.ath_decayMode==0  and row.amm_mass>25 and all([self.baseCutMap[cut](row) for cut in self.baseCutMap])
                self.selectionMap['highmassdm1/default']  = lambda row: row.ath_decayMode==1  and row.amm_mass>25 and all([self.baseCutMap[cut](row) for cut in self.baseCutMap])
                self.selectionMap['highmassdm10/default'] = lambda row: row.ath_decayMode==10 and row.amm_mass>25 and all([self.baseCutMap[cut](row) for cut in self.baseCutMap])
                baseSels += ['highmassdm0']
                baseSels += ['highmassdm1']
                baseSels += ['highmassdm10']

        self.selections = []
        self.selectionHists = {}
        for sel in self.selectionMap:
            self.selections += [sel]
            self.selections += [sel.replace('default','regionA')]
            self.selections += [sel.replace('default','regionB')]
            self.selections += [sel.replace('default','regionC')]
            self.selections += [sel.replace('default','regionD')]
        if self.doDatadriven:
            for b in baseSels:
                tag = '' if b=='default' else '{}/'.format(b)
                self.selections += ['{}regionB_fakeForA'.format(tag)]
                self.selections += ['{}regionC_fakeForA'.format(tag)]
                self.selections += ['{}regionD_fakeForA'.format(tag)]
                self.selections += ['{}regionD_fakeForB'.format(tag)]
                self.selections += ['{}regionD_fakeForC'.format(tag)]
                self.selections += ['matrixP/{}regionA_forA'.format(tag)]
                self.selections += ['matrixP/{}regionC_forA'.format(tag)]
                self.selections += ['matrixF/{}regionA_forA'.format(tag)]
                self.selections += ['matrixF/{}regionC_forA'.format(tag)]
                self.selections += ['matrixP/{}regionA_forA_p'.format(tag)]
                self.selections += ['matrixP/{}regionC_forA_p'.format(tag)]
                self.selections += ['matrixF/{}regionA_forA_f'.format(tag)]
                self.selections += ['matrixF/{}regionC_forA_f'.format(tag)]
                self.selections += ['matrixP/{}regionB_forB'.format(tag)]
                self.selections += ['matrixP/{}regionD_forB'.format(tag)]
                self.selections += ['matrixF/{}regionB_forB'.format(tag)]
                self.selections += ['matrixF/{}regionD_forB'.format(tag)]
                self.selections += ['matrixP/{}regionB_forB_p'.format(tag)]
                self.selections += ['matrixP/{}regionD_forB_p'.format(tag)]
                self.selections += ['matrixF/{}regionB_forB_f'.format(tag)]
                self.selections += ['matrixF/{}regionD_forB_f'.format(tag)]
                self.selections += ['matrixP/{}regionB_forB_fakeForA'.format(tag)]
                self.selections += ['matrixP/{}regionD_forB_fakeForA'.format(tag)]
                self.selections += ['matrixF/{}regionB_forB_fakeForA'.format(tag)]
                self.selections += ['matrixF/{}regionD_forB_fakeForA'.format(tag)]

                for newloose in self.newloose:
                    self.selections += ['{}regionB_fakeForA{:.1f}'.format(tag,newloose)]
                    self.selections += ['{}regionC_fakeForA{:.1f}'.format(tag,newloose)]
                    self.selections += ['{}regionD_fakeForA{:.1f}'.format(tag,newloose)]
                    self.selections += ['{}regionD_fakeForB{:.1f}'.format(tag,newloose)]
                    self.selections += ['{}regionD_fakeForC{:.1f}'.format(tag,newloose)]

        # setup histogram parameters
        self.histParams = {
            'count'                       : {'x': lambda row: 1,                                  'xBinning': [1,0,2],                 }, # just a count of events passing selection
            'genChannel'                  : {'x': lambda row: 'xxxx' if len(row.genChannel)<4 else ''.join(sorted(row.genChannel[:2])+sorted(row.genChannel[2:4])), 
                                             'xBinning': ['mmhm', 'mmem', 'mmmm','mmhh','mmeh','mmee','xxxx']},
            'numVertices'                 : {'x': lambda row: row.numVertices,                    'xBinning': [60,0,60],               },
            'met'                         : {'x': lambda row: row.met_pt,                         'xBinning': [500, 0, 500],           },
            'metPhi'                      : {'x': lambda row: row.met_phi,                        'xBinning': [50, -3.14159, 3.14159], },
            # h
            'hMass'                       : {'x': lambda row: row.h_mass,                         'xBinning': [1000, 0, 1000],         },
            'hMassKinFit'                 : {'x': lambda row: row.h_massKinFit,                   'xBinning': [1000, 0, 1000],         },
            'hMt'                         : {'x': lambda row: row.hmet_mt,                        'xBinning': [1000, 0, 1000],         },
            'hMcat'                       : {'x': lambda row: row.hmet_mcat,                      'xBinning': [1000, 0, 1000],         },
            'hDeltaMass'                  : {'x': lambda row: row.amm_mass-row.att_mass,          'xBinning': [1000, -500, 500],       },
            'hDeltaMt'                    : {'x': lambda row: row.amm_mass-row.attmet_mt,         'xBinning': [1000, -500, 500],       },
            # amm
            'ammMass'                     : {'x': lambda row: row.amm_mass,                       'xBinning': [3000, 0, 30],           },
            'ammDeltaR'                   : {'x': lambda row: row.amm_deltaR,                     'xBinning': [100, 0, 1.5],           },
            'ammDeltaPhi'                 : {'x': lambda row: abs(row.amm_deltaPhi),              'xBinning': [500, 0, 3.14159],       },
            'am1Pt'                       : {'x': lambda row: row.am1_pt,                         'xBinning': [500, 0, 500],           },
            'am2Pt'                       : {'x': lambda row: row.am2_pt,                         'xBinning': [500, 0, 500],           },
            'am1Eta'                      : {'x': lambda row: row.am1_eta,                        'xBinning': [100, -2.5, 2.5],        },
            'am2Eta'                      : {'x': lambda row: row.am2_eta,                        'xBinning': [100, -2.5, 2.5],        },
            'am1Iso'                      : {'x': lambda row: row.am1_isolation,                  'xBinning': [100, 0, 2],             },
            'am2Iso'                      : {'x': lambda row: row.am2_isolation,                  'xBinning': [100, 0, 2],             },
            #'am1MatchesTrigger'           : {'x': lambda row: row.am1_matches_IsoMu24 or row.am1_matches_IsoTkMu24, 'xBinning': [2, -0.5, 1.5],},
            #'am1PassMedium'               : {'x': lambda row: row.am1_isMediumMuonICHEP,          'xBinning': [2, -0.5, 1.5],          },
            #'am2PassMedium'               : {'x': lambda row: row.am2_isMediumMuonICHEP,          'xBinning': [2, -0.5, 1.5],          },
            # att
            'attMass'                     : {'x': lambda row: row.att_mass,                       'xBinning': [3000, 0, 60],           },
            'attMassKinFit'               : {'x': lambda row: row.att_massKinFit,                 'xBinning': [3000, 0, 60],           },
            'attMt'                       : {'x': lambda row: row.attmet_mt,                      'xBinning': [3000, 0, 60],           },
            'attMcat'                     : {'x': lambda row: row.attmet_mcat,                    'xBinning': [3000, 0, 60],           },
            'attDeltaR'                   : {'x': lambda row: row.att_deltaR,                     'xBinning': [400, 0, 6.0],           },
            'atmPt'                       : {'x': lambda row: row.atm_pt,                         'xBinning': [500, 0, 500],           },
            'atmEta'                      : {'x': lambda row: row.atm_eta,                        'xBinning': [100, -2.5, 2.5],        },
            #'atmDxy'                      : {'x': lambda row: abs(row.atm_dxy),                   'xBinning': [100, 0, 2.5],           },
            #'atmDz'                       : {'x': lambda row: abs(row.atm_dz),                    'xBinning': [100, 0, 2.5],           },
            'atmMetDeltaPhi'              : {'x': lambda row: abs(row.atmmet_deltaPhi),           'xBinning': [500, 0, 3.14159],       },
            'athPt'                       : {'x': lambda row: row.ath_pt,                         'xBinning': [500, 0, 500],           },
            'athEta'                      : {'x': lambda row: row.ath_eta,                        'xBinning': [100, -2.5, 2.5],        },
            #'athDxy'                      : {'x': lambda row: abs(row.ath_dxy),                   'xBinning': [100, 0, 2.5],           },
            #'athDz'                       : {'x': lambda row: abs(row.ath_dz),                    'xBinning': [100, 0, 2.5],           },
            'athDM'                       : {'x': lambda row: row.ath_decayMode,                  'xBinning': [15, 0, 15],             },
            'athMetDeltaPhi'              : {'x': lambda row: abs(row.athmet_deltaPhi),           'xBinning': [500, 0, 3.14159],       },
            'athJetCSV'                   : {'x': lambda row: row.athjet_CSVv2,                   'xBinning': [500, 0, 1],             },
            'attDeltaPhi'                 : {'x': lambda row: abs(row.att_deltaPhi),              'xBinning': [500, 0, 3.14159],       },
            'athIso'                      : {'x': lambda row: row.ath_byIsolationMVArun2v1DBoldDMwLTraw,        'xBinning': [100, -1, 1], },
            'athIsoCB'                    : {'x': lambda row: row.ath_byCombinedIsolationDeltaBetaCorrRaw3Hits, 'xBinning': [10, 0, 10],  },
            'atmIso'                      : {'x': lambda row: row.atm_isolation,                  'xBinning': [100, 0, 2],             },
            #'athAgainstMuonLoose'         : {'x': lambda row: row.ath_againstMuonLoose3,          'xBinning': [2, -0.5, 1.5],          },
            #'athAgainstMuonTight'         : {'x': lambda row: row.ath_againstMuonTight3,          'xBinning': [2, -0.5, 1.5],          },
            # cross terms
            'am1atmDeltaR'                : {'x': lambda row: deltaR_row(row,'am1','atm'),        'xBinning': [400, 0, 6.0],           },
            'am1athDeltaR'                : {'x': lambda row: deltaR_row(row,'am1','ath'),        'xBinning': [400, 0, 6.0],           },
            'am2atmDeltaR'                : {'x': lambda row: deltaR_row(row,'am2','atm'),        'xBinning': [400, 0, 6.0],           },
            'am2athDeltaR'                : {'x': lambda row: deltaR_row(row,'am2','ath'),        'xBinning': [400, 0, 6.0],           },
            # 2D
            'ammMass_attMass'             : {'x': lambda row: row.amm_mass, 'y': lambda row: row.att_mass,     'xBinning': [60, 0, 30], 'yBinning': [60, 0, 60]   },
            'ammMass_hMass'               : {'x': lambda row: row.amm_mass, 'y': lambda row: row.h_mass,       'xBinning': [60, 0, 30], 'yBinning': [50, 0, 1000] },
            'ammMass_hMassKinFit'         : {'x': lambda row: row.amm_mass, 'y': lambda row: row.h_massKinFit, 'xBinning': [60, 0, 30], 'yBinning': [50, 0, 1000] },
            'am2Iso_athIso'               : {'x': lambda row: row.am2_isolation, 'y': lambda row: row.ath_byIsolationMVArun2v1DBoldDMwLTraw,    'xBinning': [40,0,2], 'yBinning': [40,-1,1] },
            'am2Iso_athPassIso'           : {'x': lambda row: row.am2_isolation, 'y': lambda row: row.ath_byMediumIsolationMVArun2v1DBoldDMwLT, 'xBinning': [40,0,2], 'yBinning': [2,-0.5,1.5] },
            'genChannel_athDM'            : {'x': lambda row: 'xxxx' if len(row.genChannel)<4 else ''.join(sorted(row.genChannel[:2])+sorted(row.genChannel[2:4])), 
                                             'y': lambda row: str(int(row.ath_decayMode)),
                                             'xBinning': ['mmhm', 'mmem', 'mmmm','mmhh','mmeh','mmee','xxxx'], 'yBinning': ['0','1','5','6','10']},
        }

        # initialize flattener
        super(MuMuTauTauFlattener, self).__init__('MuMuTauTau',sample,**kwargs)


        # alternative fakerates
        self.fakekey = '{num}_{denom}'
        self.fakehists = {'muons': {}, 'taus': {},}

        fake_path = '{0}/src/DevTools/Analyzer/data/fakerates_mmtt_mu_13TeV_Run2016BCDEFGH.root'.format(os.environ['CMSSW_BASE'])
        self.fake_haa_rootfile_mu = ROOT.TFile(fake_path)
        self.fakehists['muons'][self.fakekey.format(num='HaaTight',     denom='HaaLoose')]     = self.fake_haa_rootfile_mu.Get('iso0.25_default/fakeratePtEta')
        self.fakehists['muons'][self.fakekey.format(num='HaaTightTrig', denom='HaaLooseTrig')] = self.fake_haa_rootfile_mu.Get('iso0.25trig_defaulttrig/fakeratePtEta')
        if self.doMediumMuon:
            self.fakehists['muons'][self.fakekey.format(num='HaaTight',     denom='HaaLoose')]     = self.fake_haa_rootfile_mu.Get('mediumiso0.25_mediumdefault/fakeratePtEta')
            self.fakehists['muons'][self.fakekey.format(num='HaaTightTrig', denom='HaaLooseTrig')] = self.fake_haa_rootfile_mu.Get('mediumiso0.25trig_mediumdefaulttrig/fakeratePtEta')

        fake_path = '{0}/src/DevTools/Analyzer/data/fakerates_mmtt_tau_13TeV_Run2016BCDEFGH.root'.format(os.environ['CMSSW_BASE'])
        self.fake_haa_rootfile_tau = ROOT.TFile(fake_path)
        #self.fakehists['taus'][self.fakekey.format(num='HaaTight', denom='HaaLoose')] = self.fake_haa_rootfile_tau.Get('nearMuonMedium_nearMuon/fakeratePtEta')
        self.fakehists['taus'][self.fakekey.format(num='HaaTight', denom='HaaLoose')]        = self.fake_haa_rootfile_tau.Get('nearMuonVLoose_nearMuon/fakeratePtEta')
        self.fakehists['taus'][self.fakekey.format(num='HaaTight', denom='HaaLoose')+'DM0']  = self.fake_haa_rootfile_tau.Get('nearMuonVLoose_nearMuon/fakeratePtEta_DM0')
        self.fakehists['taus'][self.fakekey.format(num='HaaTight', denom='HaaLoose')+'DM1']  = self.fake_haa_rootfile_tau.Get('nearMuonVLoose_nearMuon/fakeratePtEta_DM1')
        self.fakehists['taus'][self.fakekey.format(num='HaaTight', denom='HaaLoose')+'DM10'] = self.fake_haa_rootfile_tau.Get('nearMuonVLoose_nearMuon/fakeratePtEta_DM10')
        if self.doMedium:
            self.fakehists['taus'][self.fakekey.format(num='HaaTight', denom='HaaLoose')]        = self.fake_haa_rootfile_tau.Get('nearMuonMedium_nearMuon/fakeratePtEta')
            self.fakehists['taus'][self.fakekey.format(num='HaaTight', denom='HaaLoose')+'DM0']  = self.fake_haa_rootfile_tau.Get('nearMuonMedium_nearMuon/fakeratePtEta_DM0')
            self.fakehists['taus'][self.fakekey.format(num='HaaTight', denom='HaaLoose')+'DM1']  = self.fake_haa_rootfile_tau.Get('nearMuonMedium_nearMuon/fakeratePtEta_DM1')
            self.fakehists['taus'][self.fakekey.format(num='HaaTight', denom='HaaLoose')+'DM10'] = self.fake_haa_rootfile_tau.Get('nearMuonMedium_nearMuon/fakeratePtEta_DM10')
        if not self.doBVeto:
            self.fakehists['taus'][self.fakekey.format(num='HaaTight', denom='HaaLoose')]        = self.fake_haa_rootfile_tau.Get('noBVeto/nearMuonVLoose_nearMuon/fakeratePtEta')
            self.fakehists['taus'][self.fakekey.format(num='HaaTight', denom='HaaLoose')+'DM0']  = self.fake_haa_rootfile_tau.Get('noBVeto/nearMuonVLoose_nearMuon/fakeratePtEta_DM0')
            self.fakehists['taus'][self.fakekey.format(num='HaaTight', denom='HaaLoose')+'DM1']  = self.fake_haa_rootfile_tau.Get('noBVeto/nearMuonVLoose_nearMuon/fakeratePtEta_DM1')
            self.fakehists['taus'][self.fakekey.format(num='HaaTight', denom='HaaLoose')+'DM10'] = self.fake_haa_rootfile_tau.Get('noBVeto/nearMuonVLoose_nearMuon/fakeratePtEta_DM10')
        for newloose in self.newloose:
            self.fakehists['taus'][self.fakekey.format(num='HaaTight', denom='HaaLoose{:.1f}'.format(newloose))] = self.fake_haa_rootfile_tau.Get('nearMuonMedium_nearMuonWithMVA{:.1f}/fakeratePtEta'.format(newloose))

        # efficiencies
        self.effkey = '{num}_{denom}'
        self.effhists = {'muons': {}, 'taus': {},}

        #  prompt efficiencies loose iso from loose id
        #  TODO: updated for medium
        eff_path = '{0}/src/DevTools/Analyzer/data/efficiencies_mmtt_mu_13TeV_Run2016BCDEFGH.root'.format(os.environ['CMSSW_BASE'])
        self.eff_haa_rootfile_mu = ROOT.TFile(eff_path)
        self.effhists['muons'][self.effkey.format(num='HaaTight', denom='HaaLoose')] = self.eff_haa_rootfile_mu.Get('LooseIsoFromLooseIDeffData')

        # scalefactors, note: private, not full pt range (starts at 10)
        path = '{0}/src/DevTools/Analyzer/data/scalefactors_muon_2016.root'.format(os.environ['CMSSW_BASE'])
        self.muon_rootfile = ROOT.TFile(path)
        self.muon_scales = {}
        for idName in ['LooseID','LooseIsoFromLooseID','MediumID','LooseIsoFromMediumID']:
            self.muon_scales[idName] = self.muon_rootfile.Get(idName)

        # tracking
        path = '{0}/src/DevTools/Analyzer/data/Tracking_EfficienciesAndSF_BCDEFGH.root'.format(os.environ['CMSSW_BASE'])
        rootfile = ROOT.TFile(path)
        self.tracking_pog_scales = {}
        self.tracking_pog_scales['TrackingVtx']    = self.__parseAsymmErrors(rootfile.Get('ratio_eff_vtx_dr030e030_corr'))
        self.tracking_pog_scales['TrackingEta']    = self.__parseAsymmErrors(rootfile.Get('ratio_eff_eta3_dr030e030_corr'))
        rootfile.Close()

    def __parseAsymmErrors(self,graph):
        vals = []
        x,y = ROOT.Double(0), ROOT.Double(0)
        for i in range(graph.GetN()):
            graph.GetPoint(i,x,y)
            val = {
                'x'        : float(x),
                'y'        : float(y),
                'errx_up'  : float(graph.GetErrorXhigh(i)),
                'errx_down': float(graph.GetErrorXlow(i)),
                'erry_up'  : float(graph.GetErrorYhigh(i)),
                'erry_down': float(graph.GetErrorYlow(i)),
            }
            vals += [val]
        return vals

    def getFakeRate(self,lep,pt,eta,num,denom,dm=None):
        key = self.fakekey.format(num=num,denom=denom)
        if lep=='taus' and dm in [0,1,10] and self.doDM:
            key += 'DM{}'.format(dm)
        hist = self.fakehists[lep][key]
        if pt > 100.: pt = 99.
        b = hist.FindBin(pt,abs(eta))
        return hist.GetBinContent(b), hist.GetBinError(b)

    def getEfficiency(self,lep,pt,eta,num,denom,dm=None):
        key = self.effkey.format(num=num,denom=denom)
        hist = self.effhists[lep][key]
        if pt > 100.: pt = 99.
        b = hist.FindBin(pt,abs(eta))
        return hist.GetBinContent(b), hist.GetBinError(b)

    def getMuonScaleFactor(self,id,pt,eta):
        if pt>200: pt = 199
        if pt<10: pt = 11
        hist = self.muon_scales[id]
        b = hist.FindBin(pt,eta)
        val = hist.GetBinContent(b)
        err = hist.GetBinError(b)
        return val, err
        
    def getTrackingScaleFactor(self,eta):
        etaName = 'TrackingEta'
        for valDict in self.tracking_pog_scales[etaName]:
            etaLow = valDict['x'] - valDict['errx_down']
            etaHigh = valDict['x'] + valDict['errx_up']
            if eta>=etaLow and eta<=etaHigh:
                valEta = valDict['y']
                errEta = (valDict['erry_up']+valDict['erry_down'])/2.
        return valEta, errEta

    def getWeight(self,row,doFake=False,fakeNum=None,fakeDenom=None,fakeLeps=[]):
        if not fakeNum: fakeNum = 'HaaTight'
        if not fakeDenom: fakeDenom = 'HaaLoose'
        if row.isData:
            weight = 1.
        else:
            # per event weights
            base = ['genWeight','pileupWeight','triggerEfficiency']
            if self.shift=='trigUp': base = ['genWeight','pileupWeight','triggerEfficiencyUp']
            if self.shift=='trigDown': base = ['genWeight','pileupWeight','triggerEfficiencyDown']
            if self.shift=='puUp': base = ['genWeight','pileupWeightUp','triggerEfficiency']
            if self.shift=='puDown': base = ['genWeight','pileupWeightDown','triggerEfficiency']
            vals = [getattr(row,scale) for scale in base]
            # tau id: 0.99 for VL/L, 0.97 for M
            vals += [0.99]
            # muon
            m1id = self.getMuonScaleFactor('LooseID',row.am1_pt,row.am1_eta)
            m1iso = self.getMuonScaleFactor('LooseIsoFromLooseID',row.am1_pt,row.am1_eta)
            m2id = self.getMuonScaleFactor('LooseID',row.am2_pt,row.am2_eta)
            m2iso = self.getMuonScaleFactor('LooseIsoFromLooseID',row.am2_pt,row.am2_eta)
            m3id = self.getMuonScaleFactor('LooseID',row.atm_pt,row.atm_eta)
            if self.doMediumMuon:
                m1id = self.getMuonScaleFactor('MediumID',row.am1_pt,row.am1_eta)
                m1iso = self.getMuonScaleFactor('LooseIsoFromMediumID',row.am1_pt,row.am1_eta)
                m2id = self.getMuonScaleFactor('MediumID',row.am2_pt,row.am2_eta)
                m2iso = self.getMuonScaleFactor('LooseIsoFromMediumID',row.am2_pt,row.am2_eta)
                m3id = self.getMuonScaleFactor('MediumID',row.atm_pt,row.atm_eta)
            m1tr = self.getTrackingScaleFactor(row.am1_eta)
            m2tr = self.getTrackingScaleFactor(row.am2_eta)
            m3tr = self.getTrackingScaleFactor(row.atm_eta)
            if self.shift=='lepUp':
                vals += [m1tr[0]+m1tr[1], m1id[0]+m1id[1], m1iso[0]+m1iso[1]]
                vals += [m2tr[0]+m2tr[1], m2id[0]+m2id[1], m2iso[0]+m2iso[1]]
                vals += [m3tr[0]+m3tr[1], m3id[0]+m3id[1]]
            elif self.shift=='lepDown':
                vals += [m1tr[0]-m1tr[1], m1id[0]-m1id[1], m1iso[0]-m1iso[1]]
                vals += [m2tr[0]-m2tr[1], m2id[0]-m2id[1], m2iso[0]-m2iso[1]]
                vals += [m3tr[0]-m3tr[1], m3id[0]-m3id[1]]
            else:
                vals += [m1tr[0], m1id[0], m1iso[0]]
                vals += [m2tr[0], m2id[0], m2iso[0]]
                vals += [m3tr[0], m3id[0]]
            for scale,val in zip(base,vals):
                if val != val: logging.warning('{0}: {1} is NaN'.format(row.channel,scale))
            weight = prod([val for val in vals if val==val])
            # scale to lumi/xsec
            weight *= float(self.intLumi)/self.sampleLumi if self.sampleLumi else 0.
            if hasattr(row,'qqZZkfactor'): weight *= row.qqZZkfactor/1.1 # ZZ variable k factor
        # fake scales
        if doFake:
            if not row.isData: weight *= -1
            for l in fakeLeps:
                n = fakeNum[l] if isinstance(fakeNum,dict) else fakeNum
                d = fakeDenom[l] if isinstance(fakeDenom,dict) else fakeDenom
                coll = 'taus' if l in ['ath'] else 'muons'
                if coll=='taus' and self.doDM:
                    fake = self.getFakeRate(coll, getattr(row,'{}_pt'.format(l)), getattr(row,'{}_eta'.format(l)), n, d, dm=getattr(row,'{}_decayMode'.format(l)))
                else:
                    fake = self.getFakeRate(coll, getattr(row,'{}_pt'.format(l)), getattr(row,'{}_eta'.format(l)), n, d)
                fakeEff = fake[0]
                if self.shift=='fakeUp': fakeEff = fake[0]+fake[1]
                if self.shift=='fakeDown': fakeEff = fake[0]-fake[1]
                if fakeEff>0 and fakeEff<1:
                    weight *= fakeEff/(1-fakeEff)
                else:
                    logging.warning('invalid fake eff = {} for {} {} {}'.format(fakeeff,l,n,d))


        return weight

    def getMatrix(self,row,fakeNum=None,fakeDenom=None,leps=[]):
        if not fakeNum: fakeNum = 'HaaTight'
        if not fakeDenom: fakeDenom = 'HaaLoose'
        f = {}
        p = {}
        for l in leps:
            n = fakeNum[l] if isinstance(fakeNum,dict) else fakeNum
            d = fakeDenom[l] if isinstance(fakeDenom,dict) else fakeDenom
            coll = 'taus' if l in ['ath'] else 'muons'
            fake = self.getFakeRate(  coll, getattr(row,'{}_pt'.format(l)), getattr(row,'{}_eta'.format(l)), n, d)
            f[l] = fake[0]
            if self.shift=='fakeUp': f[l] = fake[0]+fake[1]
            if self.shift=='fakeDown': f[l] = fake[0]-fake[1]
            prompt = self.getEfficiency(coll, getattr(row,'{}_pt'.format(l)), getattr(row,'{}_eta'.format(l)), n, d)
            p[l] = prompt[0]
            if self.shift=='lepUp': p[l] = prompt[0]+prompt[1]
            if self.shift=='lepDown': p[l] = prompt[0]-prompt[1]
        # PF = Prompt/Fake
        # pf = pass/fail
        mat = []
        for r,Npf in enumerate(itertools.product('pf', repeat=len(leps))):
            row = []
            for c,NPF in enumerate(itertools.product('PF', repeat=len(leps))):
                weight = 1
                for l, lep in enumerate(leps):
                    # if pass and prompt: p
                    if Npf[l]=='p' and NPF[l]=='P': weight *= p[lep]
                    # if fail and prompt: 1-p
                    if Npf[l]=='f' and NPF[l]=='P': weight *= (1-p[lep])
                    # if pass and fake:   f
                    if Npf[l]=='p' and NPF[l]=='F': weight *= f[lep]
                    # if fail and fake:   1-f
                    if Npf[l]=='f' and NPF[l]=='F': weight *= (1-f[lep])
                row += [weight]
            mat += [row]
        a = np.matrix(mat)
        ainv = inv(a)
        return ainv, p, f


                


    def perRowAction(self,row):
        isData = row.isData

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

        if self.doGenMatch and 'SUSY' in self.sample:
            genchan = 'xxxx' if len(row.genChannel)<4 else ''.join(sorted(row.genChannel[:2])+sorted(row.genChannel[2:4]))
            if genchan not in ['mmhm']: keep = False
            if row.am1_genTruthDeltaR>0.1: keep = False
            if row.am2_genTruthDeltaR>0.1: keep = False
            if row.atm_genTruthDeltaR>0.1: keep = False
            if row.ath_genTruthDeltaR>0.1: keep = False

        if not keep: return


        # define weights
        w = self.getWeight(row)
        wb = self.getWeight(row,doFake=True,fakeLeps=['ath']) # region B ath
        wc = self.getWeight(row,doFake=True,fakeLeps=['am2']) # region C am2
        wd = self.getWeight(row,doFake=True,fakeLeps=['am2','ath']) # region D ath, am2
        mat_bd, p_bd, f_bd = self.getMatrix(row,leps=['am2']) # region A/B from C/D matrix

        wbs = {}
        wcs = {}
        wds = {}
        for newloose in self.newloose:
            wbs[newloose] = self.getWeight(row,doFake=True,fakeDenom='HaaLoose{:.1f}'.format(newloose),fakeLeps=['ath']) # region B ath
            wcs[newloose] = self.getWeight(row,doFake=True,fakeLeps=['am2']) # region c am2
            wds[newloose] = self.getWeight(row,doFake=True,fakeDenom={'ath':'HaaLoose{:.1f}'.format(newloose),'am2':'HaaLoose'},fakeLeps=['am2','ath']) # region d am2, ath
            

        # figure out region
        passRegion = {}
        for r in self.regionMap:
            passRegion[r] = self.regionMap[r](row)

        # define plot regions
        passMVALoose = row.ath_byIsolationMVArun2v1DBoldDMwLTraw>self.mvaCut
        for sel in self.selectionMap:
            result = self.selectionMap[sel](row)
            if result:
                if passMVALoose: self.fill(row,sel,w)
                for r in passRegion:
                    if passRegion[r] and passMVALoose: self.fill(row,sel.replace('default',r),w)
                if not self.doDatadriven: continue
                if passRegion['regionA']:
                    if passMVALoose:
                        self.fill(row,'matrixP/'+sel.replace('default','regionA')+'_forA',w*mat_bd.item(0,0))
                        self.fill(row,'matrixF/'+sel.replace('default','regionA')+'_forA',w*mat_bd.item(1,0))
                        self.fill(row,'matrixP/'+sel.replace('default','regionA')+'_forA_p',w*mat_bd.item(0,0)*p_bd['am2'])
                        self.fill(row,'matrixF/'+sel.replace('default','regionA')+'_forA_f',w*mat_bd.item(1,0)*f_bd['am2'])
                if passRegion['regionB']:
                    if passMVALoose:
                        self.fill(row,sel.replace('default','regionB')+'_fakeForA',wb)
                        self.fill(row,'matrixP/'+sel.replace('default','regionB')+'_forB',w*mat_bd.item(0,0))
                        self.fill(row,'matrixF/'+sel.replace('default','regionB')+'_forB',w*mat_bd.item(1,0))
                        self.fill(row,'matrixP/'+sel.replace('default','regionB')+'_forB_p',w*mat_bd.item(0,0)*p_bd['am2'])
                        self.fill(row,'matrixF/'+sel.replace('default','regionB')+'_forB_f',w*mat_bd.item(1,0)*f_bd['am2'])
                        self.fill(row,'matrixP/'+sel.replace('default','regionB')+'_forB_fakeForA',wb*mat_bd.item(0,0))
                        self.fill(row,'matrixF/'+sel.replace('default','regionB')+'_forB_fakeForA',wb*mat_bd.item(1,0))
                    for newloose in self.newloose:
                        if row.ath_byIsolationMVArun2v1DBoldDMwLTraw<newloose: continue
                        self.fill(row,sel.replace('default','regionB')+'_fakeForA{:.1f}'.format(newloose),wbs[newloose])
                if passRegion['regionC']:
                    if passMVALoose:
                        self.fill(row,sel.replace('default','regionC')+'_fakeForA',wc)
                        self.fill(row,'matrixP/'+sel.replace('default','regionC')+'_forA',w*mat_bd.item(0,1))
                        self.fill(row,'matrixF/'+sel.replace('default','regionC')+'_forA',w*mat_bd.item(1,1))
                        self.fill(row,'matrixP/'+sel.replace('default','regionC')+'_forA_p',w*mat_bd.item(0,1)*p_bd['am2'])
                        self.fill(row,'matrixF/'+sel.replace('default','regionC')+'_forA_f',w*mat_bd.item(1,1)*f_bd['am2'])
                    for newloose in self.newloose:
                        if row.ath_byIsolationMVArun2v1DBoldDMwLTraw<newloose: continue
                        self.fill(row,sel.replace('default','regionC')+'_fakeForA{:.1f}'.format(newloose),wcs[newloose])
                if passRegion['regionD']:
                    if passMVALoose:
                        self.fill(row,sel.replace('default','regionD')+'_fakeForA',wd)
                        self.fill(row,sel.replace('default','regionD')+'_fakeForB',wc)
                        self.fill(row,sel.replace('default','regionD')+'_fakeForC',wb)
                        self.fill(row,'matrixP/'+sel.replace('default','regionD')+'_forB',w*mat_bd.item(0,1))
                        self.fill(row,'matrixF/'+sel.replace('default','regionD')+'_forB',w*mat_bd.item(1,1))
                        self.fill(row,'matrixP/'+sel.replace('default','regionD')+'_forB_p',w*mat_bd.item(0,1)*p_bd['am2'])
                        self.fill(row,'matrixF/'+sel.replace('default','regionD')+'_forB_f',w*mat_bd.item(1,1)*f_bd['am2'])
                        self.fill(row,'matrixP/'+sel.replace('default','regionD')+'_forB_fakeForA',wb*mat_bd.item(0,1))
                        self.fill(row,'matrixF/'+sel.replace('default','regionD')+'_forB_fakeForA',wb*mat_bd.item(1,1))
                    for newloose in self.newloose:
                        if row.ath_byIsolationMVArun2v1DBoldDMwLTraw<newloose: continue
                        self.fill(row,sel.replace('default','regionD')+'_fakeForA{:.1f}'.format(newloose),wds[newloose])
                        self.fill(row,sel.replace('default','regionD')+'_fakeForB{:.1f}'.format(newloose),wcs[newloose])
                        self.fill(row,sel.replace('default','regionD')+'_fakeForC{:.1f}'.format(newloose),wbs[newloose])


def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Run Flattener')

    #parser.add_argument('sample', type=str, default='SingleMuon', nargs='?', help='Sample to flatten')
    parser.add_argument('sample', type=str, default='SUSYGluGluToHToAA_AToMuMu_AToTauTau_M-15_TuneCUETP8M1_13TeV_madgraph_pythia8', nargs='?', help='Sample to flatten')
    parser.add_argument('shift', type=str, default='', nargs='?', help='Shift to apply to scale factors')

    return parser.parse_args(argv)

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = parse_command_line(argv)

    flattener = MuMuTauTauFlattener(
        args.sample,
        shift=args.shift,
    )

    flattener.flatten()

    return 0

if __name__ == "__main__":
    status = main()
    sys.exit(status)

