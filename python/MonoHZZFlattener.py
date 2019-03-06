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


class MonoHZZFlattener(NtupleFlattener):
    '''
    MonoHZZ flattener
    '''

    def __init__(self,sample,**kwargs):

        # controls

        # setup properties
        self.leps = ['z11','z12','z21','z22']
        self.channels = ['eeee','eemm','mmee','mmmm']

        self.selectionMap = {}
        baseSels = []
        self.selections = []

        self.baseSelections = {
            'default': lambda row: True,
            '4P0F'   : lambda row: row.z11_passTight and row.z12_passTight and row.z21_passTight and row.z22_passTight and row.z21_charge!=row.z22_charge,
            'CR_SS'  : lambda row: row.z11_passTight and row.z12_passTight and row.z21_charge==row.z22_charge,
            '3P1F'   : lambda row: row.z11_passTight and row.z12_passTight and ((row.z21_passTight and not row.z22_passTight) or (not row.z21_passTight and row.z22_passTight)) and row.z21_charge!=row.z22_charge,
            '2P2F'   : lambda row: row.z11_passTight and row.z12_passTight and not row.z21_passTight and not row.z22_passTight and row.z21_charge!=row.z22_charge,
        }
        for sel in self.baseSelections:
            self.selectionMap[sel] = self.baseSelections[sel]
            baseSels += [sel]
        baseSels += ['for4P0F/3P1F']
        baseSels += ['for4P0F/2P2F']
        baseSels += ['for3P1F/2P2F']

        self.regions = {
            'hzz4l' : lambda row: row.h_mass>115 and row.h_mass<135,
            'z4l'   : lambda row: row.h_mass>81 and row.h_mass<101,
            'zz4l'  : lambda row: row.h_mass>170,
        }

        for sel in baseSels:
            self.selections += [sel]
            for region in self.regions:
                self.selections += ['{}/{}'.format(sel,region)]


        # setup histogram parameters
        self.histParams = {
            'count'                       : {'x': lambda row: 1,                                  'xBinning': [1,0,2],                 }, # just a count of events passing selection
            'numVertices'                 : {'x': lambda row: row.numVertices,                    'xBinning': [60,0,60],               },
            'met'                         : {'x': lambda row: row.met_pt,                         'xBinning': [500, 0, 500],           },
            'metPhi'                      : {'x': lambda row: row.met_phi,                        'xBinning': [50, -3.14159, 3.14159], },
            # h
            'hMass'                       : {'x': lambda row: row.h_mass,                         'xBinning': [1000, 0, 1000],         },
            'hPt'                         : {'x': lambda row: row.h_pt,                           'xBinning': [500, 0, 500],           },
            # z1
            'z1Mass'                      : {'x': lambda row: row.z1_mass,                        'xBinning': [120, 0, 120],           },
            'z1Pt'                        : {'x': lambda row: row.z1_pt,                          'xBinning': [500, 0, 500],           },
            'z11Pt'                       : {'x': lambda row: row.z11_pt,                         'xBinning': [500, 0, 500],           },
            'z11Eta'                      : {'x': lambda row: row.z11_eta,                        'xBinning': [500, -2.5, 2.5],        },
            'z12Pt'                       : {'x': lambda row: row.z12_pt,                         'xBinning': [500, 0, 500],           },
            'z12Eta'                      : {'x': lambda row: row.z12_eta,                        'xBinning': [500, -2.5, 2.5],        },
            # z2
            'z2Mass'                      : {'x': lambda row: row.z2_mass,                        'xBinning': [120, 0, 120],           },
            'z2Pt'                        : {'x': lambda row: row.z2_pt,                          'xBinning': [500, 0, 500],           },
            'z21Pt'                       : {'x': lambda row: row.z21_pt,                         'xBinning': [500, 0, 500],           },
            'z21Eta'                      : {'x': lambda row: row.z21_eta,                        'xBinning': [500, -2.5, 2.5],        },
            'z22Pt'                       : {'x': lambda row: row.z22_pt,                         'xBinning': [500, 0, 500],           },
            'z22Eta'                      : {'x': lambda row: row.z22_eta,                        'xBinning': [500, -2.5, 2.5],        },
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

        self.fakerates = {}
        fake_path = '{}/src/DevTools/Plotter/data/fakerates_hzz.root'.format(os.environ['CMSSW_BASE'])
        self.fake_file = ROOT.TFile.Open(fake_path)
        self.fakerates['electron'] = self.fake_file.Get('e/fakeratePtEta')
        self.fakerates['muon'] = self.fake_file.Get('m/fakeratePtEta')

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

    def getFakeRate(self,flavor,pt,eta):
        flavors = {
            'e': 'electron',
            'm': 'muon',
        }
        hist = self.fakerates[flavors[flavor]]
        if pt>=100: pt = 99
        val = hist.GetBinContent(hist.FindBin(pt,abs(eta)))
        err = hist.GetBinError(hist.FindBin(pt,abs(eta)))
        return val, err

    def getPileup(self,nv):
        return self.pileup.GetBinContent(self.pileup.FindBin(nv))

    def getWeight(self,row,fakeLeps=[]):
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
        for lep in fakeLeps:
            pt = getattr(row,'{}_pt'.format(lep))
            eta = getattr(row,'{}_eta'.format(lep))
            f = row.channel[self.leps.index(lep)]
            val,err = self.getFakeRate(f,pt,eta)
            weight *= val/(1-val)

        return weight

    def perRowAction(self,row):
        isData = row.isData

        event = '{}:{}:{}'.format(row.run,row.lumi,row.event)

        # define weights
        w = self.getWeight(row)
        wFF = self.getWeight(row,fakeLeps=['z21','z22'])
        wFP = self.getWeight(row,fakeLeps=['z21'])
        wPF = self.getWeight(row,fakeLeps=['z22'])

        recoChan = ''.join([x for x in row.channel if x in ['e','m']])

        def fill(row,sel):
            self.fill(row,sel,w,recoChan)
            if '3P1F' in sel:
                # 3P1F contribution to 4P
                w3P1F = wFP if not row.z21_passTight else wPF
                if not isData: w3P1F = -1*w3P1F
                self.fill(row,'for4P0F/{}'.format(sel),w3P1F,recoChan)
            if '2P2F' in sel:
                # 2P2F contribution to 4P
                w2P2F = wFF
                if isData: w2P2F = -1*w2P2F
                self.fill(row,'for4P0F/{}'.format(sel),w2P2F,recoChan)
                # 2P2F contribution to 3P1F
                w2P2F = wFP
                if not isData: w2P2F = -1*w2P2F
                self.fill(row,'for3P1F/{}'.format(sel),w2P2F,recoChan)
                w2P2F = wPF
                if not isData: w2P2F = -1*w2P2F
                self.fill(row,'for3P1F/{}'.format(sel),w2P2F,recoChan)

        regionResults = {}
        for region in self.regions:
            regionResults[region] = self.regions[region](row)

        # define plot regions
        for sel in self.selectionMap:
            result = self.selectionMap[sel](row)
            if result:
                fill(row,sel)
                for region in self.regions:
                    if regionResults[region]:
                        fill(row,'{}/{}'.format(sel,region))


def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Run Flattener')

    #parser.add_argument('sample', type=str, default='DoubleMuon', nargs='?', help='Sample to flatten')
    parser.add_argument('sample', type=str, default='ZZTo4L_13TeV_powheg_pythia8', nargs='?', help='Sample to flatten')
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

