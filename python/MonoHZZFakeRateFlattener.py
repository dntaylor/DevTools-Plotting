#!/usr/bin/env python
import argparse
import logging
import os
import sys
import itertools
import json
import pickle
import operator
import math
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

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


def deltaR_row(row,a,b):
    aEta = getattr(row,'{}_eta'.format(a))
    aPhi = getattr(row,'{}_phi'.format(a))
    bEta = getattr(row,'{}_eta'.format(b))
    bPhi = getattr(row,'{}_phi'.format(b))
    return deltaR(aEta,aPhi,bEta,bPhi)


class MonoHZZFakeRateFlattener(NtupleFlattener):
    '''
    MonoHZZFakeRate flattener
    '''

    def __init__(self,sample,**kwargs):

        # controls

        # setup properties
        self.leps = ['z1','z2']
        self.channels = ['eee','eem','mme','mmm']

        self.selectionMap = {}
        baseSels = []
        self.selections = []

        self.etaBins = {
            'e': [0,1.479,2.5],
            'm': [0,0.8,1.2,2.4],
        }

        self.regions = {
            'default': lambda row: row.z_mass>81 and row.z_mass<101 and row.met_pt<30,
            'tight'  : lambda row: row.z_mass>81 and row.z_mass<101 and row.met_pt<30 and row.l_passTight,
        }
        for region in self.regions:
            self.selectionMap[region] = self.regions[region]
            baseSels += [region]

        for sel in baseSels:
            self.selections += [sel]
            for e in range(3):
                self.selections += ['{}/etaBin{}'.format(sel,e)]

        # setup histogram parameters
        self.histParams = {
            'count'                       : {'x': lambda row: 1,                                  'xBinning': [1,0,2],                 }, # just a count of events passing selection
            'numVertices'                 : {'x': lambda row: row.numVertices,                    'xBinning': [60,0,60],               },
            'met'                         : {'x': lambda row: row.met_pt,                         'xBinning': [500, 0, 500],           },
            'metPhi'                      : {'x': lambda row: row.met_phi,                        'xBinning': [50, -3.14159, 3.14159], },
            # z1
            'zMass'                       : {'x': lambda row: row.z_mass,                         'xBinning': [120, 0, 120],           },
            'z1Pt'                        : {'x': lambda row: row.z1_pt,                          'xBinning': [500, 0, 500],           },
            'z2Pt'                        : {'x': lambda row: row.z2_pt,                          'xBinning': [500, 0, 500],           },
            # l
            'lPt'                         : {'x': lambda row: row.l_pt,                           'xBinning': [500, 0, 500],           },
        }

        # initialize flattener
        super(MonoHZZFakeRateFlattener, self).__init__('MonoHZZFakeRate',sample,**kwargs)

        self.scalefactors = {}
        muon_path = '{}/src/DevTools/Plotter/data/ScaleFactors_mu_Moriond2018_final.root'.format(os.environ['CMSSW_BASE'])
        electron_path = '{}/src/DevTools/Plotter/data/egammaEffi.txt_EGM2D_Moriond2018v1.root'.format(os.environ['CMSSW_BASE'])
        self.muon_file = ROOT.TFile.Open(muon_path)
        self.electron_file = ROOT.TFile.Open(electron_path)
        self.scalefactors['muon'] = self.muon_file.Get('FINAL')
        self.scalefactors['electron'] = self.electron_file.Get('EGamma_SF2D')

        pileup_path = '{}/src/DevTools/Analyzer/data/pileup_RunIIFall17MiniAODv2-PU2017_12Apr2018_94X_mc2017_realistic_v14.root'.format(os.environ['CMSSW_BASE'])
        self.pileup_file = ROOT.TFile.Open(pileup_path)
        self.pileup = self.pileup_file.Get('pileup_scale')

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

    def getScalefactor(self,flavor,pt,eta):
        flavors = {
            'e': 'electron',
            'm': 'muon',
        }
        hist = self.scalefactors[flavors[flavor]]
        if flavor=='e' and pt>=500: pt = 499
        if flavor=='m' and pt>=200: pt = 199
        val = hist.GetBinContent(hist.FindBin(eta,pt))
        err = hist.GetBinError(hist.FindBin(eta,pt))
        return val, err

    def getPileup(self,nv):
        return self.pileup.GetBinContent(self.pileup.FindBin(nv))

    def getWeight(self,row):
        if row.isData:
            weight = 1.
        else:
            # gen weight
            base = ['genWeight']
            vals = [getattr(row,scale) for scale in base]
            # trigger efficiency: TODO
            # pileup weight
            vals += [self.getPileup(row.numTrueVertices)]
            # lepton efficiency
            for l,lep in enumerate(self.leps):
                pt = getattr(row,'{}_pt'.format(lep))
                eta = getattr(row,'{}_eta'.format(lep))
                f = row.channel[l]
                val,err = self.getScalefactor(f,pt,eta)
                vals += [val]
                #print l, lep, f, pt, eta, val, err
            weight = prod([val for val in vals if val==val])
            # scale to lumi/xsec
            weight *= float(self.intLumi)/self.sampleLumi if self.sampleLumi else 0.

        return weight

    def perRowAction(self,row):
        isData = row.isData

        event = '{}:{}:{}'.format(row.run,row.lumi,row.event)

        # define weights
        w = self.getWeight(row)

        recoChan = ''.join([x for x in row.channel if x in ['e','m']])

        # define plot regions
        for sel in self.selectionMap:
            result = self.selectionMap[sel](row)
            if result:
                self.fill(row,sel,w,recoChan)
                f = recoChan[-1]
                abseta = abs(row.l_eta)
                for e in range(len(self.etaBins[f])):
                    if abseta>=self.etaBins[f][e] and abseta<self.etaBins[f][e+1]:
                        self.fill(row,'{}/etaBin{}'.format(sel,e),w,recoChan)


def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Run Flattener')

    #parser.add_argument('sample', type=str, default='DoubleMuon', nargs='?', help='Sample to flatten')
    parser.add_argument('sample', type=str, default='DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8', nargs='?', help='Sample to flatten')
    parser.add_argument('shift', type=str, default='', nargs='?', help='Shift to apply to scale factors')
    parser.add_argument('--skipHists', action='store_true',help='Skip histograms, only do datasets')

    return parser.parse_args(argv)

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = parse_command_line(argv)

    flattener = MonoHZZFakeRateFlattener(
        args.sample,
        shift=args.shift,
        skipHists=args.skipHists,
    )

    flattener.flatten()

    return 0

if __name__ == "__main__":
    status = main()
    sys.exit(status)

