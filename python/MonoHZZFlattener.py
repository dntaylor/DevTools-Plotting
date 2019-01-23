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
        self.baseCutMap = {
            'pass'  : lambda row: True,
        }

        self.selectionMap = {}
        baseSels = []
        self.selectionMap['default'] = lambda row: all([self.baseCutMap[cut](row) for cut in self.baseCutMap])
        baseSels += ['default']

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

    def getWeight(self,row):
        if row.isData:
            weight = 1.
        else:
            # per event weights
            base = ['genWeight']
            vals = [getattr(row,scale) for scale in base]
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

