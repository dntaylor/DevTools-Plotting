#!/usr/bin/env python
import argparse
import logging
import os
import sys
import itertools
import json
import pickle
import operator
from array import array
import numpy as np
from numpy.linalg import inv
from collections import OrderedDict

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from NtupleFlattener import NtupleFlattener
from DevTools.Utilities.utilities import prod, ZMASS
from DevTools.Plotter.higgsUtilities import *
from DevTools.Analyzer.utilities import deltaR, deltaPhi
from DevTools.Analyzer.BTagScales import BTagScales

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')



class ModDYFlattener(NtupleFlattener):
    '''
    ModDY flattener
    '''

    def __init__(self,sample,**kwargs):

        # controls


        # setup properties
        self.leps = ['z1','z2']
        self.baseCutMap = {
            'zWindow'    : lambda row: row.z_mass>60 and row.z_mass<120,
            #'trigger'    : lambda row: row.z1_matches_IsoMu24 or row.z1_matches_IsoTkMu24,
            'turnon'     : lambda row: row.z1_pt>26,
            'z1iso'      : lambda row: row.z1_isolation<0.25,
            'z2iso'      : lambda row: row.z2_isolation<0.25,
        }

        self.regionMap = {
            'high' : lambda row: row.z2_pt>20.,
            'low'  : lambda row: row.z2_pt>3. and row.z2_pt<20.,
        }

        self.selectionMap = {}
        baseSels = []
        self.selectionMap['default'] = lambda row: all([self.baseCutMap[cut](row) for cut in self.baseCutMap])
        baseSels += ['default']

        self.selections = []
        self.selectionHists = {}
        for sel in self.selectionMap:
            self.selections += [sel]
            self.selections += [sel.replace('default','high')]
            self.selections += [sel.replace('default','low')]

        # setup histogram parameters
        self.histParams = {
            'count'                       : {'x': lambda row: 1,                                  'xBinning': [1,0,2],                 }, # just a count of events passing selection
            'numVertices'                 : {'x': lambda row: row.numVertices,                    'xBinning': [60,0,60],               },
            'met'                         : {'x': lambda row: row.met_pt,                         'xBinning': [500, 0, 500],           },
            'metPhi'                      : {'x': lambda row: row.met_phi,                        'xBinning': [50, -3.14159, 3.14159], },
            # z
            'zMass'                      : {'x': lambda row: row.z_mass,                        'xBinning': [2000, 0, 200],           },
            'zPt'                        : {'x': lambda row: row.z_pt,                          'xBinning': [1000, 0, 1000],           },
            'zDeltaR'                    : {'x': lambda row: row.z_deltaR,                      'xBinning': [600, 0, 6],           },
            'zDeltaPhi'                  : {'x': lambda row: abs(row.z_deltaPhi),               'xBinning': [500, 0, 3.14159],       },
            'z1Pt'                       : {'x': lambda row: row.z1_pt,                         'xBinning': [500, 0, 500],           },
            'z2Pt'                       : {'x': lambda row: row.z2_pt,                         'xBinning': [500, 0, 500],           },
            'z1Eta'                      : {'x': lambda row: row.z1_eta,                        'xBinning': [100, -2.5, 2.5],        },
            'z2Eta'                      : {'x': lambda row: row.z2_eta,                        'xBinning': [100, -2.5, 2.5],        },
            'z1Iso'                      : {'x': lambda row: row.z1_isolation,                  'xBinning': [100, 0, 2],             },
            'z2Iso'                      : {'x': lambda row: row.z2_isolation,                  'xBinning': [100, 0, 2],             },
        }

        # initialize flattener
        super(ModDYFlattener, self).__init__('ModDY',sample,**kwargs)


        # efficiencies
        self.effkey = '{num}_{denom}'
        self.effhists = {'muons': {}, 'taus': {},}

        #  prompt efficiencies loose iso from loose id
        eff_path = '{0}/src/DevTools/Analyzer/data/efficiencies_mmtt_mu_13TeV_Run2016BCDEFGH.root'.format(os.environ['CMSSW_BASE'])
        self.eff_haa_rootfile_mu = ROOT.TFile(eff_path)
        self.effhists['muons'][self.effkey.format(num='HaaTight', denom='HaaLoose')] = self.eff_haa_rootfile_mu.Get('LooseIsoFromLooseIDeffData')

        # scalefactors, note: private, not full pt range (starts at 10)
        path = '{0}/src/DevTools/Analyzer/data/scalefactors_muon_2016.root'.format(os.environ['CMSSW_BASE'])
        self.muon_rootfile = ROOT.TFile(path)
        self.muon_scales = {}
        for idName in ['LooseID','LooseIsoFromLooseID','MediumID','LooseIsoFromMediumID']:
            self.muon_scales[idName] = self.muon_rootfile.Get(idName)

        # from kyle
        path = '{0}/src/DevTools/Analyzer/data/TNP_LowMuPt_EFFICIENCIES.root'.format(os.environ['CMSSW_BASE'])
        self.muon_rootfile_kyle = ROOT.TFile(path)
        self.muon_scales['LooseIDKyle'] = self.muon_rootfile_kyle.Get('hist_EtavsPtLooseID_DatatoMC')
        self.muon_scales['LooseIsoFromLooseIDKyle'] = self.muon_rootfile_kyle.Get('hist_EtavsPtLooseISO_DatatoMC')

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

    def getSummedWeights(self,w):
        return self.summedWeightsMap[w]


    def getEfficiency(self,lep,pt,eta,num,denom,dm=None):
        key = self.effkey.format(num=num,denom=denom)
        hist = self.effhists[lep][key]
        if pt > 100.: pt = 99.
        b = hist.FindBin(pt,abs(eta))
        return hist.GetBinContent(b), hist.GetBinError(b)

    def getMuonScaleFactor(self,id,pt,eta):
        if pt>200: pt = 199
        if pt<3: pt = 3.1
        if pt<20:
            hist = self.muon_scales[id+'Kyle']
            b = hist.FindBin(abs(eta),pt) # Kyle and official
        else:
            hist = self.muon_scales[id]
            b = hist.FindBin(pt,eta) # private devin
        val = hist.GetBinContent(b)
        err = hist.GetBinError(b)
        return val, err
        
    def getWeight(self,row):
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
            # muon
            m1id = self.getMuonScaleFactor('LooseID',row.z1_pt,row.z1_eta)
            m1iso = self.getMuonScaleFactor('LooseIsoFromLooseID',row.z1_pt,row.z1_eta)
            m2id = self.getMuonScaleFactor('LooseID',row.z2_pt,row.z2_eta)
            m2iso = self.getMuonScaleFactor('LooseIsoFromLooseID',row.z2_pt,row.z2_eta) if row.z_deltaR>0.4 else [1.0, 0., 0.]
            if self.shift=='lepUp':
                vals += [m1id[0]+m1id[1], m1iso[0]+m1iso[1]]
                vals += [m2id[0]+m2id[1], m2iso[0]+m2iso[1]]
            elif self.shift=='lepDown':
                vals += [m1id[0]-m1id[1], m1iso[0]-m1iso[1]]
                vals += [m2id[0]-m2id[1], m2iso[0]-m2iso[1]]
            else:
                vals += [m1id[0], m1iso[0]]
                vals += [m2id[0], m2iso[0]]
            for scale,val in zip(base,vals):
                if val != val: logging.warning('{0}: {1} is NaN'.format(row.channel,scale))
            weight = prod([val for val in vals if val==val])
            # scale to lumi/xsec
            weight *= float(self.intLumi)/self.sampleLumi if self.sampleLumi else 0.
            if hasattr(row,'qqZZkfactor'): weight *= row.qqZZkfactor/1.1 # ZZ variable k factor

        return weight



    def perRowAction(self,row):
        isData = row.isData

        event = '{}:{}:{}'.format(row.run,row.lumi,row.event)


        # per sample cuts
        keep = True
        #if self.sample=='DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'  : keep = row.numGenJets==0 or row.numGenJets>4
        #if self.sample=='DY1JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' : keep = row.numGenJets==1
        #if self.sample=='DY2JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' : keep = row.numGenJets==2
        #if self.sample=='DY3JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' : keep = row.numGenJets==3
        #if self.sample=='DY4JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' : keep = row.numGenJets==4
        #if self.sample=='DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'      : keep = row.numGenJets==0 or row.numGenJets>4
        #if self.sample=='DY1JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : keep = row.numGenJets==1
        #if self.sample=='DY2JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : keep = row.numGenJets==2
        #if self.sample=='DY3JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : keep = row.numGenJets==3
        #if self.sample=='DY4JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : keep = row.numGenJets==4
        #if self.sample=='WJetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'           : keep = row.numGenJets==0 or row.numGenJets>4
        #if self.sample=='W1JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          : keep = row.numGenJets==1
        #if self.sample=='W2JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          : keep = row.numGenJets==2
        #if self.sample=='W3JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          : keep = row.numGenJets==3
        #if self.sample=='W4JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          : keep = row.numGenJets==4

        if not keep: return


        # define weights
        w = self.getWeight(row)

        # figure out region
        passRegion = {}
        for r in self.regionMap:
            passRegion[r] = self.regionMap[r](row)

        # define plot regions
        for sel in self.selectionMap:
            result = self.selectionMap[sel](row)
            if result:
                self.fill(row,sel,w)
                for r in passRegion:
                    if passRegion[r]: self.fill(row,sel.replace('default',r),w)


def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Run Flattener')

    parser.add_argument('sample', type=str, default='DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8', nargs='?', help='Sample to flatten')
    parser.add_argument('shift', type=str, default='', nargs='?', help='Shift to apply to scale factors')
    parser.add_argument('--skipHists', action='store_true',help='Skip histograms, only do datasets')

    return parser.parse_args(argv)

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = parse_command_line(argv)

    flattener = ModDYFlattener(
        args.sample,
        shift=args.shift,
        skipHists=args.skipHists,
    )

    flattener.flatten()

    return 0

if __name__ == "__main__":
    status = main()
    sys.exit(status)

