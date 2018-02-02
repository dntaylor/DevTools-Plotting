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

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


class MuMuTauTauFlattener(NtupleFlattener):
    '''
    MuMuTauTau flattener
    '''

    def __init__(self,sample,**kwargs):
        # controls
        self.datadriven = False
        self.datadrivenRegular = False

        # setup properties
        self.leps = ['am1','am2','ath','atm']
        self.baseCutMap = {
            'ammWindow'  : lambda row: row.amm_mass>1 and row.amm_mass<30,
            'attDR'      : lambda row: row.att_deltaR<0.8,
            'trigger'    : lambda row: row.am1_matches_IsoMu24 or row.am1_matches_IsoTkMu24,
        }
        self.selectionMap = {}
        self.selectionMap['default'] = lambda row: all([self.baseCutMap[cut](row) for cut in self.baseCutMap])
        self.selectionMap['regionA'] = lambda row: all([self.baseCutMap[cut](row) for cut in self.baseCutMap]+[row.am1_isolation<0.15 and row.am2_isolation<0.15 and row.ath_byVLooseIsolationMVArun2v1DBoldDMwLT>0.5])
        self.selectionMap['regionB'] = lambda row: all([self.baseCutMap[cut](row) for cut in self.baseCutMap]+[row.am1_isolation<0.15 and row.am2_isolation<0.15 and row.ath_byVLooseIsolationMVArun2v1DBoldDMwLT<0.5])
        self.selectionMap['regionC'] = lambda row: all([self.baseCutMap[cut](row) for cut in self.baseCutMap]+[row.am1_isolation<0.15 and row.am2_isolation>0.15 and row.ath_byVLooseIsolationMVArun2v1DBoldDMwLT>0.5])
        self.selectionMap['regionD'] = lambda row: all([self.baseCutMap[cut](row) for cut in self.baseCutMap]+[row.am1_isolation<0.15 and row.am2_isolation>0.15 and row.ath_byVLooseIsolationMVArun2v1DBoldDMwLT<0.5])

        self.selections = []
        self.selectionHists = {}
        for sel in self.selectionMap:
            self.selections += [sel]

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
            # att
            'attMass'                     : {'x': lambda row: row.att_mass,                       'xBinning': [300, 0, 300],           },
            'attMassKinFit'               : {'x': lambda row: row.att_massKinFit,                 'xBinning': [300, 0, 300],           },
            'attMt'                       : {'x': lambda row: row.attmet_mt,                      'xBinning': [300, 0, 300],           },
            'attMcat'                     : {'x': lambda row: row.attmet_mcat,                    'xBinning': [300, 0, 300],           },
            'attDeltaR'                   : {'x': lambda row: row.att_deltaR,                     'xBinning': [400, 0, 6.0],           },
            'atmPt'                       : {'x': lambda row: row.atm_pt,                         'xBinning': [500, 0, 500],           },
            'atmDxy'                      : {'x': lambda row: abs(row.atm_dxy),                   'xBinning': [100, 0, 2.5],           },
            'atmDz'                       : {'x': lambda row: abs(row.atm_dz),                    'xBinning': [100, 0, 2.5],           },
            'atmMetDeltaPhi'              : {'x': lambda row: abs(row.atmmet_deltaPhi),           'xBinning': [500, 0, 3.14159],       },
            'athPt'                       : {'x': lambda row: row.ath_pt,                         'xBinning': [500, 0, 500],           },
            'athDxy'                      : {'x': lambda row: abs(row.ath_dxy),                   'xBinning': [100, 0, 2.5],           },
            'athDz'                       : {'x': lambda row: abs(row.ath_dz),                    'xBinning': [100, 0, 2.5],           },
            'athMetDeltaPhi'              : {'x': lambda row: abs(row.athmet_deltaPhi),           'xBinning': [500, 0, 3.14159],       },
            'athJetCSV'                   : {'x': lambda row: row.athjet_CSVv2,                   'xBinning': [500, 0, 1],             },
            'attDeltaPhi'                 : {'x': lambda row: abs(row.att_deltaPhi),              'xBinning': [500, 0, 3.14159],       },
        }

        # initialize flattener
        super(MuMuTauTauFlattener, self).__init__('MuMuTauTau',sample,**kwargs)


        # alternative fakerates
        self.fakekey = '{num}_{denom}'
        self.fakehists = {'muons': {}, 'taus': {},}

        fake_path = '{0}/src/DevTools/Analyzer/data/fakerates_mmtt_tau_13TeV_Run2016BCDEFGH.root'.format(os.environ['CMSSW_BASE'])
        self.fake_haa_rootfile_tau = ROOT.TFile(fake_path)
        self.fakehists['taus'][self.fakekey.format(num='HaaTight', denom='HaaLoose')] = self.fake_haa_rootfile_tau.Get('nearMuonMedium_nearMuon/fakeratePtEta')

    def getFakeRate(self,lep,pt,eta,num,denom,dm=None):
        key = self.fakekey.format(num=num,denom=denom)
        hist = self.fakehists[lep][key]
        if pt > 100.: pt = 99.
        b = hist.FindBin(pt,abs(eta))
        return hist.GetBinContent(b), hist.GetBinError(b)

    def getWeight(self,row,doFake=False,fakeNum=None,fakeDenom=None):
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
        # TODO: add fake
        #if doFake:
        #    chanMap = {'e': 'electrons', 'm': 'muons', 't': 'taus',}
        #    chan = ''.join([x for x in row.channel if x in 'emt'])
        #    pts = [getattr(row,'{0}_pt'.format(x)) for x in self.leps]
        #    etas = [getattr(row,'{0}_eta'.format(x)) for x in self.leps]
        #    region = ''.join(['P' if x else 'F' for x in passID])
        #    sign = -1 if region.count('F')%2==0 and region.count('F')>0 else 1
        #    weight *= sign
        #    if not row.isData and not all(passID): weight *= -1 # subtract off MC in control
        #    for l,lep in enumerate(self.leps):
        #        if not passID[l]:
        #            # recalculate
        #            fakeEff = self.getFakeRate(chanMap[chan[l]], pts[l], etas[l], fakeNum, fakeDenom)[0]
        #            weight *= fakeEff/(1-fakeEff)

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

        # define plot regions
        for sel in self.selectionMap:
            result = self.selectionMap[sel](row)
            if result:
                self.fill(row,sel,w)


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

