#!/usr/bin/env python
import argparse
import logging
import os
import sys
import itertools
import operator

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from NtupleFlattener import NtupleFlattener
from DevTools.Utilities.utilities import prod, ZMASS
from DevTools.Plotter.higgsUtilities import *

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


class ZTauFakeRateFlattener(NtupleFlattener):
    '''
    ZTauFakeRate flattener
    '''

    def __init__(self,sample,**kwargs):
        # setup properties
        self.baseCutMap = {
            'zPt'      : lambda row: row.z1_pt>25 and row.z2_pt>20,
            'zMass'    : lambda row: row.z_mass>76 or row.z_mass<106,
            'oldDM'    : lambda row: row.t_decayModeFinding,
        }
        self.baseCutMapNew = {
            'zPt'      : lambda row: row.z1_pt>25 and row.z2_pt>20,
            'zMass'    : lambda row: row.z_mass>76 or row.z_mass<106,
        }
        self.selectionMap = {}
        self.selectionMap['loose'] = lambda row: all([self.baseCutMap[cut](row) for cut in self.baseCutMap]) and row.t_passLoose
        self.selectionMap['medium'] = lambda row: all([self.baseCutMap[cut](row) for cut in self.baseCutMap]) and row.t_passMedium
        self.selectionMap['tight'] = lambda row: all([self.baseCutMap[cut](row) for cut in self.baseCutMap]) and row.t_passTight
        self.selectionMap['newloose'] = lambda row: all([self.baseCutMapNew[cut](row) for cut in self.baseCutMapNew])
        self.selectionMap['oldloose_n0p2'] = lambda row: all([self.baseCutMap[cut](row) for cut in self.baseCutMap]) and row.t_byIsolationMVArun2v1DBoldDMwLTraw>-0.2
        self.selectionMap['oldloose_n0p1'] = lambda row: all([self.baseCutMap[cut](row) for cut in self.baseCutMap]) and row.t_byIsolationMVArun2v1DBoldDMwLTraw>-0.1
        self.selectionMap['oldloose_0p0']  = lambda row: all([self.baseCutMap[cut](row) for cut in self.baseCutMap]) and row.t_byIsolationMVArun2v1DBoldDMwLTraw>0.0
        self.selectionMap['oldloose_0p1']  = lambda row: all([self.baseCutMap[cut](row) for cut in self.baseCutMap]) and row.t_byIsolationMVArun2v1DBoldDMwLTraw>0.1
        self.selectionMap['oldloose_0p2']  = lambda row: all([self.baseCutMap[cut](row) for cut in self.baseCutMap]) and row.t_byIsolationMVArun2v1DBoldDMwLTraw>0.2
        self.selectionMap['oldloose_0p3']  = lambda row: all([self.baseCutMap[cut](row) for cut in self.baseCutMap]) and row.t_byIsolationMVArun2v1DBoldDMwLTraw>0.3
        self.selectionMap['oldloose_0p4']  = lambda row: all([self.baseCutMap[cut](row) for cut in self.baseCutMap]) and row.t_byIsolationMVArun2v1DBoldDMwLTraw>0.4
        self.selectionMap['newloose_n0p2'] = lambda row: all([self.baseCutMapNew[cut](row) for cut in self.baseCutMapNew]) and row.t_byIsolationMVArun2v1DBnewDMwLTraw>-0.2
        self.selectionMap['newloose_n0p1'] = lambda row: all([self.baseCutMapNew[cut](row) for cut in self.baseCutMapNew]) and row.t_byIsolationMVArun2v1DBnewDMwLTraw>-0.1
        self.selectionMap['newloose_0p0']  = lambda row: all([self.baseCutMapNew[cut](row) for cut in self.baseCutMapNew]) and row.t_byIsolationMVArun2v1DBnewDMwLTraw>0.0
        self.selectionMap['newloose_0p1']  = lambda row: all([self.baseCutMapNew[cut](row) for cut in self.baseCutMapNew]) and row.t_byIsolationMVArun2v1DBnewDMwLTraw>0.1
        self.selectionMap['newloose_0p2']  = lambda row: all([self.baseCutMapNew[cut](row) for cut in self.baseCutMapNew]) and row.t_byIsolationMVArun2v1DBnewDMwLTraw>0.2
        self.selectionMap['newloose_0p3']  = lambda row: all([self.baseCutMapNew[cut](row) for cut in self.baseCutMapNew]) and row.t_byIsolationMVArun2v1DBnewDMwLTraw>0.3
        self.selectionMap['newloose_0p4']  = lambda row: all([self.baseCutMapNew[cut](row) for cut in self.baseCutMapNew]) and row.t_byIsolationMVArun2v1DBnewDMwLTraw>0.4

        self.etaBins = [0,1.479,2.3]
        self.dms = [0,1,5,6,10]

        self.selections = []
        for sel in self.selectionMap:
            self.selections += [sel]
            for dm in self.dms:
                self.selections += ['{0}/dm{1}'.format(sel,dm)]
            for eb in range(len(self.etaBins)-1):
                self.selections += ['{0}/etaBin{1}'.format(sel,eb)]
                for dm in self.dms:
                    self.selections += ['{0}/etaBin{1}/dm{2}'.format(sel,eb,dm)]

        # setup histogram parameters
        self.histParams = {
            'count'                       : {'x': lambda row: 1,                                  'xBinning': [1,0,2],                 }, # just a count of events passing selection
            #'numVertices'                 : {'x': lambda row: row.numVertices,                    'xBinning': [60,0,60],               },
            #'met'                         : {'x': lambda row: row.met_pt,                         'xBinning': [500, 0, 500],           },
            #'metPhi'                      : {'x': lambda row: row.met_phi,                        'xBinning': [50, -3.14159, 3.14159], },
            #'numLooseMuons'               : {'x': lambda row: row.numLooseMuons,                  'xBinning': [4,0,4],                 },
            #'numTightMuons'               : {'x': lambda row: row.numTightMuons,                  'xBinning': [4,0,4],                 },
            # z
            #'zMass'                       : {'x': lambda row: row.z_mass,                         'xBinning': [500, 0, 500],           },
            #'mllMinusMZ'                  : {'x': lambda row: abs(row.z_mass-ZMASS),              'xBinning': [200, 0, 200],           },
            #'zPt'                         : {'x': lambda row: row.z_pt,                           'xBinning': [500, 0, 500],           },
            #'zDeltaR'                     : {'x': lambda row: row.z_deltaR,                       'xBinning': [500, 0, 5],             },
            # t
            #'wtMt'                        : {'x': lambda row: row.wt_mt,                          'xBinning': [500, 0, 500],           },
            #'wtPt'                        : {'x': lambda row: row.wt_pt,                          'xBinning': [500, 0, 500],           },
            'tPt'                         : {'x': lambda row: row.t_pt,                           'xBinning': [500, 0, 500],           },
            'tEta'                        : {'x': lambda row: row.t_eta,                          'xBinning': [500, -2.5, 2.5],        },
            'tDM'                         : {'x': lambda row: row.t_decayMode,                    'xBinning': [12, 0 ,12],             },
            # m
            #'wmMt'                        : {'x': lambda row: row.wm_mt,                          'xBinning': [500, 0, 500],           },
            #'wmPt'                        : {'x': lambda row: row.wm_pt,                          'xBinning': [500, 0, 500],           },
            #'mPt'                         : {'x': lambda row: row.m_pt,                           'xBinning': [500, 0, 500],           },
            #'mEta'                        : {'x': lambda row: row.m_eta,                          'xBinning': [500, -2.5, 2.5],        },
        }

        # initialize flattener
        super(ZTauFakeRateFlattener, self).__init__('ZTauFakeRate',sample,**kwargs)


    def getWeight(self,row):
        if row.isData:
            weight = 1.
        else:
            # per event weights
            base = ['genWeight','pileupWeight','triggerEfficiency','z1_mediumScale','z2_mediumScale']
            vals = [getattr(row,scale) for scale in base]
            for scale,val in zip(base,vals):
                if val != val: logging.warning('{0}: {1} is NaN'.format(row.channel,scale))
            weight = prod([val for val in vals if val==val])
            # scale to lumi/xsec
            weight *= float(self.intLumi)/self.sampleLumi if self.sampleLumi else 0.
        return weight


    def perRowAction(self,row):
        isData = row.isData


        # define weights
        w = self.getWeight(row)
        thisDM = row.t_decayMode

        # define plot regions
        for sel in self.selectionMap:
            result = self.selectionMap[sel](row)
            if result:
                thisW = w
                if sel=='loose':  thisW = w * row.t_looseScale
                if sel=='medium': thisW = w * row.t_mediumScale
                if sel=='tight':  thisW = w * row.t_tightScale
                self.fill(row,sel,thisW)
                # dms
                for dm in self.dms:
                    if thisDM==dm: self.fill(row,'{0}/dm{1}'.format(sel,dm),thisW)
                # etabins
                for eb in range(len(self.etaBins)-1):
                    if abs(row.t_eta)>=self.etaBins[eb] and abs(row.t_eta)<self.etaBins[eb+1]:
                        self.fill(row,'{0}/etaBin{1}'.format(sel,eb),thisW)
                        for dm in self.dms:
                            if thisDM==dm: self.fill(row,'{0}/etaBin{1}/dm{2}'.format(sel,eb,dm),thisW)



def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Run Flattener')

    parser.add_argument('sample', type=str, default='DoubleMuon', nargs='?', help='Sample to flatten')
    parser.add_argument('shift', type=str, default='', nargs='?', help='Shift to apply to scale factors')

    return parser.parse_args(argv)

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = parse_command_line(argv)

    flattener = ZTauFakeRateFlattener(
        args.sample,
        shift=args.shift,
    )

    flattener.flatten()

    return 0

if __name__ == "__main__":
    status = main()
    sys.exit(status)

