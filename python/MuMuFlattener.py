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
from DevTools.Analyzer.BTagScales import BTagScales

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


def deltaR_row(row,a,b):
    aEta = getattr(row,'{}_eta'.format(a))
    aPhi = getattr(row,'{}_phi'.format(a))
    bEta = getattr(row,'{}_eta'.format(b))
    bPhi = getattr(row,'{}_phi'.format(b))
    return deltaR(aEta,aPhi,bEta,bPhi)


class MuMuFlattener(NtupleFlattener):
    '''
    MuMu flattener
    '''

    def __init__(self,sample,**kwargs):

        # controls
        self.doThreeMuon = True


        # setup properties
        self.leps = ['m1','m2']
        self.baseCutMap = {
            'mmWindow'  : lambda row: row.mm_mass>1 and row.amm_mass<30,
            'trigger'   : lambda row: row.m1_matches_IsoMu24 or row.m1_matches_IsoTkMu24,
            #'mmDR'       : lambda row: row.mm_deltaR<1,
        }

        self.selectionMap = {}
        baseSels = []
        self.selectionMap['default'] = lambda row: all([self.baseCutMap[cut](row) for cut in self.baseCutMap])
        baseSels += ['default']
        if self.doThreeMuon:
            self.selectionMap['threeMuon/default']  = lambda row: row.numMuons>2  and all([self.baseCutMap[cut](row) for cut in self.baseCutMap])
            baseSels += ['threeMuon']

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
            # amm
            'mmMass'                     : {'x': lambda row: row.amm_mass,                       'xBinning': [3000, 0, 30],           },
            'mmDeltaR'                   : {'x': lambda row: row.amm_deltaR,                     'xBinning': [100, 0, 1.5],           },
            'mmDeltaPhi'                 : {'x': lambda row: abs(row.amm_deltaPhi),              'xBinning': [500, 0, 3.14159],       },
            'm1Pt'                       : {'x': lambda row: row.am1_pt,                         'xBinning': [500, 0, 500],           },
            'm2Pt'                       : {'x': lambda row: row.am2_pt,                         'xBinning': [500, 0, 500],           },
            'm1Eta'                      : {'x': lambda row: row.am1_eta,                        'xBinning': [100, -2.5, 2.5],        },
            'm2Eta'                      : {'x': lambda row: row.am2_eta,                        'xBinning': [100, -2.5, 2.5],        },
            'm1Iso'                      : {'x': lambda row: row.am1_isolation,                  'xBinning': [100, 0, 2],             },
            'm2Iso'                      : {'x': lambda row: row.am2_isolation,                  'xBinning': [100, 0, 2],             },
        }

        # initialize flattener
        super(MuMuFlattener, self).__init__('MuMu',sample,**kwargs)



    def perRowAction(self,row):
        isData = row.isData

        for sel in self.selectionMap:
            result = self.selectionMap[sel](row)
            if result:
                self.fill(row,sel,w)


def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Run Flattener')

    parser.add_argument('sample', type=str, default='SingleMuon', nargs='?', help='Sample to flatten')
    parser.add_argument('shift', type=str, default='', nargs='?', help='Shift to apply to scale factors')
    parser.add_argument('--skipHists', action='store_true',help='Skip histograms, only do datasets')

    return parser.parse_args(argv)

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = parse_command_line(argv)

    flattener = MuMuFlattener(
        args.sample,
        shift=args.shift,
        skipHists=args.skipHists,
    )

    flattener.flatten()

    return 0

if __name__ == "__main__":
    status = main()
    sys.exit(status)

