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
from DevTools.Analyzer.utilities import deltaR, deltaPhi

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


def deltaR_row(row,a,b):
    aEta = getattr(row,'{}_eta'.format(a))
    aPhi = getattr(row,'{}_phi'.format(a))
    bEta = getattr(row,'{}_eta'.format(b))
    bPhi = getattr(row,'{}_phi'.format(b))
    return deltaR(aEta,aPhi,bEta,bPhi)

def passTauIso(row,lep):
    #return getattr(row,'{}_byMediumIsolationMVArun2v1DBoldDMwLT'.format(lep))>0.5
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
            'taubveto'   : lambda row: row.athjet_passCSVv2M<0.5,
            'mmDR'       : lambda row: row.amm_deltaR<1,
            'm1tmDR'     : lambda row: deltaR_row(row,'am1','atm')>0.4,
            'm1thDR'     : lambda row: deltaR_row(row,'am1','ath')>0.8,
            'm2tmDR'     : lambda row: deltaR_row(row,'am2','atm')>0.4,
            'm2thDR'     : lambda row: deltaR_row(row,'am2','ath')>0.8,
            #'muonIso'    : lambda row: row.am1_isolation<self.isoCut and row.am2_isolation<self.isoCut,
            #'tauMVA'     : lambda row: row.ath_byIsolationMVArun2v1DBoldDMwLTraw>self.mvaCut,
        }
        self.selectionMap = {}
        self.selectionMap['default'] = lambda row: all([self.baseCutMap[cut](row) for cut in self.baseCutMap])
        self.selectionMap['regionA'] = lambda row: all([self.baseCutMap[cut](row) for cut in self.baseCutMap]+[row.am1_isolation<0.25 and row.am2_isolation<0.25 and passTauIso(row,'ath')])
        self.selectionMap['regionB'] = lambda row: all([self.baseCutMap[cut](row) for cut in self.baseCutMap]+[row.am1_isolation<0.25 and row.am2_isolation<0.25 and not passTauIso(row,'ath')])
        self.selectionMap['regionC'] = lambda row: all([self.baseCutMap[cut](row) for cut in self.baseCutMap]+[row.am1_isolation<0.25 and row.am2_isolation>0.25 and passTauIso(row,'ath')])
        self.selectionMap['regionD'] = lambda row: all([self.baseCutMap[cut](row) for cut in self.baseCutMap]+[row.am1_isolation<0.25 and row.am2_isolation>0.25 and not passTauIso(row,'ath')])
        if self.doLowMass:
            self.selectionMap['lowmass/default'] = lambda row: row.amm_mass<4 and all([self.baseCutMap[cut](row) for cut in self.baseCutMap])
            self.selectionMap['lowmass/regionA'] = lambda row: row.amm_mass<4 and all([self.baseCutMap[cut](row) for cut in self.baseCutMap]+[row.am1_isolation<0.25 and row.am2_isolation<0.25 and passTauIso(row,'ath')])
            self.selectionMap['lowmass/regionB'] = lambda row: row.amm_mass<4 and all([self.baseCutMap[cut](row) for cut in self.baseCutMap]+[row.am1_isolation<0.25 and row.am2_isolation<0.25 and not passTauIso(row,'ath')])
            self.selectionMap['lowmass/regionC'] = lambda row: row.amm_mass<4 and all([self.baseCutMap[cut](row) for cut in self.baseCutMap]+[row.am1_isolation<0.25 and row.am2_isolation>0.25 and passTauIso(row,'ath')])
            self.selectionMap['lowmass/regionD'] = lambda row: row.amm_mass<4 and all([self.baseCutMap[cut](row) for cut in self.baseCutMap]+[row.am1_isolation<0.25 and row.am2_isolation>0.25 and not passTauIso(row,'ath')])

        self.selections = []
        self.selectionHists = {}
        for sel in self.selectionMap:
            self.selections += [sel]
        if self.doDatadriven:
            self.selections += ['regionB_fakeForA']
            self.selections += ['regionC_fakeForA']
            self.selections += ['regionD_fakeForA']
            self.selections += ['regionD_fakeForB']
            self.selections += ['regionD_fakeForC']
            if self.doLowMass:
                self.selections += ['lowmass/regionB_fakeForA']
                self.selections += ['lowmass/regionC_fakeForA']
                self.selections += ['lowmass/regionD_fakeForA']
                self.selections += ['lowmass/regionD_fakeForB']
                self.selections += ['lowmass/regionD_fakeForC']

            for newloose in self.newloose:
                self.selections += ['regionB_fakeForA{:.1f}'.format(newloose)]
                self.selections += ['regionC_fakeForA{:.1f}'.format(newloose)]
                self.selections += ['regionD_fakeForA{:.1f}'.format(newloose)]
                self.selections += ['regionD_fakeForB{:.1f}'.format(newloose)]
                self.selections += ['regionD_fakeForC{:.1f}'.format(newloose)]
                if self.doLowMass:
                    self.selections += ['lowmass/regionB_fakeForA{:.1f}'.format(newloose)]
                    self.selections += ['lowmass/regionC_fakeForA{:.1f}'.format(newloose)]
                    self.selections += ['lowmass/regionD_fakeForA{:.1f}'.format(newloose)]
                    self.selections += ['lowmass/regionD_fakeForB{:.1f}'.format(newloose)]
                    self.selections += ['lowmass/regionD_fakeForC{:.1f}'.format(newloose)]

        # setup histogram parameters
        self.histParams = {
            'count'                       : {'x': lambda row: 1,                                  'xBinning': [1,0,2],                 }, # just a count of events passing selection
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
            'attMass'                     : {'x': lambda row: row.att_mass,                       'xBinning': [300, 0, 300],           },
            'attMassKinFit'               : {'x': lambda row: row.att_massKinFit,                 'xBinning': [300, 0, 300],           },
            'attMt'                       : {'x': lambda row: row.attmet_mt,                      'xBinning': [300, 0, 300],           },
            'attMcat'                     : {'x': lambda row: row.attmet_mcat,                    'xBinning': [300, 0, 300],           },
            'attDeltaR'                   : {'x': lambda row: row.att_deltaR,                     'xBinning': [400, 0, 6.0],           },
            'atmPt'                       : {'x': lambda row: row.atm_pt,                         'xBinning': [500, 0, 500],           },
            'atmEta'                      : {'x': lambda row: row.atm_eta,                        'xBinning': [100, -2.5, 2.5],        },
            'atmDxy'                      : {'x': lambda row: abs(row.atm_dxy),                   'xBinning': [100, 0, 2.5],           },
            'atmDz'                       : {'x': lambda row: abs(row.atm_dz),                    'xBinning': [100, 0, 2.5],           },
            'atmMetDeltaPhi'              : {'x': lambda row: abs(row.atmmet_deltaPhi),           'xBinning': [500, 0, 3.14159],       },
            'athPt'                       : {'x': lambda row: row.ath_pt,                         'xBinning': [500, 0, 500],           },
            'athEta'                      : {'x': lambda row: row.ath_eta,                        'xBinning': [100, -2.5, 2.5],        },
            'athDxy'                      : {'x': lambda row: abs(row.ath_dxy),                   'xBinning': [100, 0, 2.5],           },
            'athDz'                       : {'x': lambda row: abs(row.ath_dz),                    'xBinning': [100, 0, 2.5],           },
            'athMetDeltaPhi'              : {'x': lambda row: abs(row.athmet_deltaPhi),           'xBinning': [500, 0, 3.14159],       },
            'athJetCSV'                   : {'x': lambda row: row.athjet_CSVv2,                   'xBinning': [500, 0, 1],             },
            'attDeltaPhi'                 : {'x': lambda row: abs(row.att_deltaPhi),              'xBinning': [500, 0, 3.14159],       },
            'athIso'                      : {'x': lambda row: row.ath_byIsolationMVArun2v1DBoldDMwLTraw, 'xBinning': [100, -1, 1],     },
            'atmIso'                      : {'x': lambda row: row.atm_isolation,                  'xBinning': [100, 0, 2],             },
            'athAgainstMuonLoose'         : {'x': lambda row: row.ath_againstMuonLoose3,          'xBinning': [2, -0.5, 1.5],          },
            'athAgainstMuonTight'         : {'x': lambda row: row.ath_againstMuonTight3,          'xBinning': [2, -0.5, 1.5],          },
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
        }

        # initialize flattener
        super(MuMuTauTauFlattener, self).__init__('MuMuTauTau',sample,**kwargs)


        # alternative fakerates
        self.fakekey = '{num}_{denom}'
        self.fakehists = {'muons': {}, 'taus': {},}

        fake_path = '{0}/src/DevTools/Analyzer/data/fakerates_mmtt_mu_13TeV_Run2016BCDEFGH.root'.format(os.environ['CMSSW_BASE'])
        self.fake_haa_rootfile_mu = ROOT.TFile(fake_path)
        self.fakehists['muons'][self.fakekey.format(num='HaaTight', denom='HaaLoose')] = self.fake_haa_rootfile_mu.Get('iso0.25_default/fakeratePtEta')
        #self.fakehists['muons'][self.fakekey.format(num='HaaTight', denom='HaaLoose')] = self.fake_haa_rootfile_mu.Get('iso0.25_iso0.40/fakeratePtEta')

        fake_path = '{0}/src/DevTools/Analyzer/data/fakerates_mmtt_tau_13TeV_Run2016BCDEFGH.root'.format(os.environ['CMSSW_BASE'])
        self.fake_haa_rootfile_tau = ROOT.TFile(fake_path)
        #self.fakehists['taus'][self.fakekey.format(num='HaaTight', denom='HaaLoose')] = self.fake_haa_rootfile_tau.Get('nearMuonMedium_nearMuon/fakeratePtEta')
        self.fakehists['taus'][self.fakekey.format(num='HaaTight', denom='HaaLoose')] = self.fake_haa_rootfile_tau.Get('nearMuonVLoose_nearMuon/fakeratePtEta')
        #self.fakehists['taus'][self.fakekey.format(num='HaaTight', denom='HaaLoose')] = self.fake_haa_rootfile_tau.Get('nearMuonMedium_nearMuonWithMVA/fakeratePtEta')
        for newloose in self.newloose:
            self.fakehists['taus'][self.fakekey.format(num='HaaTight', denom='HaaLoose{:.1f}'.format(newloose))] = self.fake_haa_rootfile_tau.Get('nearMuonMedium_nearMuonWithMVA{:.1f}/fakeratePtEta'.format(newloose))

    def getFakeRate(self,lep,pt,eta,num,denom,dm=None):
        key = self.fakekey.format(num=num,denom=denom)
        hist = self.fakehists[lep][key]
        if pt > 100.: pt = 99.
        b = hist.FindBin(pt,abs(eta))
        return hist.GetBinContent(b), hist.GetBinError(b)

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
            # TODO: add lep efficiencies
            #for l,lep in enumerate(self.leps):
            #    shiftString = ''
            #    if self.shift == 'lepUp': shiftString = 'Up'
            #    if self.shift == 'lepDown': shiftString = 'Down'
            #    base += [self.scaleMap['P' if passID[l] else 'F'].format(lep)+shiftString]
            vals = [getattr(row,scale) for scale in base]
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
                if l in ['am2']:
                    fakeEff = self.getFakeRate('muons', row.am2_pt, row.am2_eta, n, d)[0]
                elif l in ['ath']:
                    fakeEff = self.getFakeRate('taus', row.ath_pt, row.ath_eta, n, d)[0]
                else:
                     fakeEff = 0
                if fakeEff: weight *= fakeEff/(1-fakeEff)

        return weight


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
        if not keep: return


        # define weights
        w = self.getWeight(row)
        wb = self.getWeight(row,doFake=True,fakeLeps=['ath']) # region B ath
        wc = self.getWeight(row,doFake=True,fakeLeps=['am1']) # region C am1
        wd = self.getWeight(row,doFake=True,fakeLeps=['am2','ath']) # region D ath, am2

        wbs = {}
        wcs = {}
        wds = {}
        for newloose in self.newloose:
            wbs[newloose] = self.getWeight(row,doFake=True,fakeDenom='HaaLoose{:.1f}'.format(newloose),fakeLeps=['ath']) # region B ath
            wcs[newloose] = self.getWeight(row,doFake=True,fakeLeps=['am2']) # region c am2
            wds[newloose] = self.getWeight(row,doFake=True,fakeDenom={'ath':'HaaLoose{:.1f}'.format(newloose),'am2':'HaaLoose'},fakeLeps=['am2','ath']) # region d am2, ath
            

        # define plot regions
        passMVALoose = row.ath_byIsolationMVArun2v1DBoldDMwLTraw>self.mvaCut
        for sel in self.selectionMap:
            result = self.selectionMap[sel](row)
            if result:
                if passMVALoose: self.fill(row,sel,w)
                if not self.doDatadriven: continue
                if 'regionB' in sel:
                    if passMVALoose: self.fill(row,sel+'_fakeForA',wb)
                    for newloose in self.newloose:
                        if row.ath_byIsolationMVArun2v1DBoldDMwLTraw<newloose: continue
                        self.fill(row,sel+'_fakeForA{:.1f}'.format(newloose),wbs[newloose])
                if 'regionC' in sel:
                    if passMVALoose: self.fill(row,sel+'_fakeForA',wc)
                    for newloose in self.newloose:
                        if row.ath_byIsolationMVArun2v1DBoldDMwLTraw<newloose: continue
                        self.fill(row,sel+'_fakeForA{:.1f}'.format(newloose),wcs[newloose])
                if 'regionD' in sel:
                    if passMVALoose: self.fill(row,sel+'_fakeForA',wd)
                    if passMVALoose: self.fill(row,sel+'_fakeForB',wc)
                    if passMVALoose: self.fill(row,sel+'_fakeForC',wb)
                    for newloose in self.newloose:
                        if row.ath_byIsolationMVArun2v1DBoldDMwLTraw<newloose: continue
                        self.fill(row,sel+'_fakeForA{:.1f}'.format(newloose),wds[newloose])
                        self.fill(row,sel+'_fakeForB{:.1f}'.format(newloose),wcs[newloose])
                        self.fill(row,sel+'_fakeForC{:.1f}'.format(newloose),wbs[newloose])


def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Run Flattener')

    parser.add_argument('sample', type=str, default='SingleMuon', nargs='?', help='Sample to flatten')
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

