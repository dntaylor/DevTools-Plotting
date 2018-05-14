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
        self.doDeltaR = True
        self.doIso = True
        self.doAntiIso = True


        # setup properties
        self.leps = ['m1','m2']
        self.baseCutMap = {
            'mmWindow'  : lambda row: row.mm_mass>1 and row.mm_mass<30,
            'trigger'   : lambda row: row.m1_matches_IsoMu24 or row.m1_matches_IsoTkMu24,
        }

        self.cuts = {}
        if self.doThreeMuon: self.cuts['threeMuon'] = lambda row: row.numMuons>2
        if self.doDeltaR:    self.cuts['deltaR']    = lambda row: row.mm_deltaR<1
        if self.doIso:       self.cuts['iso']       = lambda row: row.m2_isolation<0.25
        if self.doAntiIso:   self.cuts['antiiso']   = lambda row: row.m2_isolation>0.25

        self.selectionMap = {}
        baseSels = []
        self.selectionMap['default'] = lambda row: all([self.baseCutMap[cut](row) for cut in self.baseCutMap])
        baseSels += ['default']

        self.selections = []
        self.selectionHists = {}
        for sel in self.selectionMap:
            self.selections += [sel]
            
        for i in range(len(self.cuts)):
            for cuts in itertools.combinations(self.cuts,i+1):
                if 'iso' in cuts and 'antiiso' in cuts: continue
                name = '_'.join(sorted(cuts))
                cutsel = '{}/default'.format(name)
                self.selections += [cutsel]


        # setup histogram parameters
        self.histParams = {
            #'count'                       : {'x': lambda row: 1,                                  'xBinning': [1,0,2],                 }, # just a count of events passing selection
            #'numVertices'                 : {'x': lambda row: row.numVertices,                    'xBinning': [60,0,60],               },
            #'met'                         : {'x': lambda row: row.met_pt,                         'xBinning': [500, 0, 500],           },
            #'metPhi'                      : {'x': lambda row: row.met_phi,                        'xBinning': [50, -3.14159, 3.14159], },
            # mm
            'mmMass'                     : {'x': lambda row: row.mm_mass,                        'xBinning': [3000, 0, 30],           },
            'mmDeltaR'                   : {'x': lambda row: row.mm_deltaR,                      'xBinning': [100, 0, 1.5],           },
            #'mmDeltaPhi'                 : {'x': lambda row: abs(row.mm_deltaPhi),               'xBinning': [500, 0, 3.14159],       },
            'm1Pt'                       : {'x': lambda row: row.m1_pt,                          'xBinning': [500, 0, 500],           },
            'm2Pt'                       : {'x': lambda row: row.m2_pt,                          'xBinning': [500, 0, 500],           },
            'm1Eta'                      : {'x': lambda row: row.m1_eta,                         'xBinning': [100, -2.5, 2.5],        },
            'm2Eta'                      : {'x': lambda row: row.m2_eta,                         'xBinning': [100, -2.5, 2.5],        },
            'm1Iso'                      : {'x': lambda row: row.m1_isolation,                   'xBinning': [100, 0, 2],             },
            'm2Iso'                      : {'x': lambda row: row.m2_isolation,                   'xBinning': [100, 0, 2],             },
        }

        self.datasetParams = {
            'mmMass_dataset'             : {'wVar': ROOT.RooRealVar('w','w',-999999,999999), 'x': lambda row: row.mm_mass,     'xVar': ROOT.RooRealVar('x','x',0,30),   },
        }

        # initialize flattener
        super(MuMuFlattener, self).__init__('MuMu',sample,**kwargs)



    def perRowAction(self,row):
        isData = row.isData
        w = 1
        cutVals = {}
        for sel in self.selectionMap:
            result = self.selectionMap[sel](row)
            if result:
                self.fill(row,sel,w)
                for cut in self.cuts:
                    cutVals[cut] = self.cuts[cut](row)
                for i in range(len(self.cuts)):
                    for cuts in itertools.combinations(self.cuts,i+1):
                        if 'iso' in cuts and 'antiiso' in cuts: continue
                        name = '_'.join(sorted(cuts))
                        cutsel = '{}/default'.format(name)
                        cutresult = all([cutVals[c] for c in cuts])
                        if cutresult:
                            self.fill(row,cutsel,w)
                


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

