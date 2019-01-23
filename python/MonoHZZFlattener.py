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

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


def deltaR_row(row,a,b):
    aEta = getattr(row,'{}_eta'.format(a))
    aPhi = getattr(row,'{}_phi'.format(a))
    bEta = getattr(row,'{}_eta'.format(b))
    bPhi = getattr(row,'{}_phi'.format(b))
    return deltaR(aEta,aPhi,bEta,bPhi)


class MonoHZZFlattener(NtupleFlattener):
    '''
    MonoHZZ flattener
    '''

    def __init__(self,sample,**kwargs):

        # controls

        # setup properties
        self.leps = ['z11','z12','z21','z22']

        self.selectionMap = {}
        baseSels = []

        self.regions = {
            'default': lambda row: True,
            'full'   : lambda row: row.z11_passTight and row.z12_passTight and row.z21_passTight and row.z22_passsTight and row.z21_charge!=row.z22_charge,
            'CR_SS'  : lambda row: row.z11_passTight and row.z12_passTight and row.z21_charge==row.z22_charge,
            '3P1F'   : lambda row: row.z11_passTight and row.z12_passTight and ((row.z21_passTight and not row.z22_passsTight) or (not row.z21_passTight and row.z22_passsTight)) and row.z21_charge!=row.z22_charge,
            '2P2F'   : lambda row: row.z11_passTight and row.z12_passTight and not row.z21_passTight and not row.z22_passsTight and row.z21_charge!=row.z22_charge,
        }
        for region in self.regions:
            self.selectionMap[region] = self.regions[region]
            baseSels += [region]

        # setup histogram parameters
        self.histParams = {
            'count'                       : {'x': lambda row: 1,                                  'xBinning': [1,0,2],                 }, # just a count of events passing selection
            'numVertices'                 : {'x': lambda row: row.numVertices,                    'xBinning': [60,0,60],               },
            'met'                         : {'x': lambda row: row.met_pt,                         'xBinning': [500, 0, 500],           },
            'metPhi'                      : {'x': lambda row: row.met_phi,                        'xBinning': [50, -3.14159, 3.14159], },
            # h
            'hMass'                       : {'x': lambda row: getattr(row,'4l_mass'),             'xBinning': [1000, 0, 1000],         },
            # z1
            'z1Mass'                      : {'x': lambda row: row.z1_mass,                        'xBinning': [120, 0, 120],           },
            'z11Pt'                       : {'x': lambda row: row.z11_pt,                         'xBinning': [500, 0, 500],           },
            'z12Pt'                       : {'x': lambda row: row.z12_pt,                         'xBinning': [500, 0, 500],           },
            # z2
            'z2Mass'                      : {'x': lambda row: row.z2_mass,                        'xBinning': [120, 0, 120],           },
            'z21Pt'                       : {'x': lambda row: row.z21_pt,                         'xBinning': [500, 0, 500],           },
            'z22Pt'                       : {'x': lambda row: row.z22_pt,                         'xBinning': [500, 0, 500],           },
        }

        # initialize flattener
        super(MonoHZZFlattener, self).__init__('MonoHZZ',sample,**kwargs)

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
        err = hist.GetBinErr(hist.FindBin(eta,pt))
        return val, err

    def getWeight(self,row):
        if row.isData:
            weight = 1.
        else:
            # gen weight
            base = ['genWeight']
            vals = [getattr(row,scale) for scale in base]
            # trigger efficiency: TODO
            # pileup weight
            vals += [self.pileup[int(floor(row.numTrueVertices))]]
            # lepton efficiency
            for l,lep in self.leps:
                pt = getattr(row,'{}_pt'.format(lep))
                eta = getattr(row,'{}_eta'.format(lep))
                f = row.channel[l]
                val,err = self.getScaleFactor(f,pt,eta)
                vals += [val]
            weight = prod([val for val in vals if val==val])
            # scale to lumi/xsec
            weight *= float(self.intLumi)/self.sampleLumi if self.sampleLumi else 0.

        return weight

    def perRowAction(self,row):
        isData = row.isData

        event = '{}:{}:{}'.format(row.run,row.lumi,row.event)

        # define weights
        w = self.getWeight(row)

        # define plot regions
        for sel in self.selectionMap:
            result = self.selectionMap[sel](row)
            if result:
                self.fill(row,sel,w)


def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Run Flattener')

    parser.add_argument('sample', type=str, default='DoubleMuon', nargs='?', help='Sample to flatten')
    parser.add_argument('shift', type=str, default='', nargs='?', help='Shift to apply to scale factors')
    parser.add_argument('--skipHists', action='store_true',help='Skip histograms, only do datasets')

    return parser.parse_args(argv)

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = parse_command_line(argv)

    flattener = MonoHZZFlattener(
        args.sample,
        shift=args.shift,
        skipHists=args.skipHists,
    )

    flattener.flatten()

    return 0

if __name__ == "__main__":
    status = main()
    sys.exit(status)

