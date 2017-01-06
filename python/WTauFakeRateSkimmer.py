#!/usr/bin/env python
import argparse
import logging
import sys
import sys
import itertools
import operator

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from NtupleSkimmer import NtupleSkimmer
from DevTools.Utilities.utilities import prod, ZMASS


logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


class WTauFakeRateSkimmer(NtupleSkimmer):
    '''
    WTauFakeRate skimmer
    '''

    def __init__(self,sample,**kwargs):
        super(WTauFakeRateSkimmer, self).__init__('WTauFakeRate',sample,**kwargs)

        # setup properties
        self.leps = ['t']

    def getWeight(self,row,cut='loose'):
        if row.isData:
            weight = 1.
        else:
            # per event weights
            base = ['genWeight','pileupWeight','triggerEfficiency']
            if self.shift=='trigUp': base = ['genWeight','pileupWeight','triggerEfficiencyUp']
            if self.shift=='trigDown': base = ['genWeight','pileupWeight','triggerEfficiencyDown']
            if self.shift=='puUp': base = ['genWeight','pileupWeightUp','triggerEfficiency']
            if self.shift=='puDown': base = ['genWeight','pileupWeightDown','triggerEfficiency']
            for lep in zip(self.leps):
                if self.shift == 'lepUp':
                    base += ['{0}_{1}ScaleUp'.format(lep,cut)]
                elif self.shift == 'lepDown':
                    base += ['{0}_{1}ScaleDown'.format(lep,cut)]
                else:
                    base += ['{0}_{1}Scale'.format(lep,cut)]
            base += ['m_mediumScale']
            vals = [getattr(row,scale) for scale in base]
            for scale,val in zip(base,vals):
                if val != val: logging.warning('{0}: {1} is NaN'.format(row.channel,scale))
            weight = prod([val for val in vals if val==val])
            # scale to lumi/xsec
            weight *= float(self.intLumi)/self.sampleLumi if self.sampleLumi else 0.
            if hasattr(row,'qqZZkfactor'): weight *= row.qqZZkfactor/1.1 # ZZ variable k factor

        return weight

    def perRowAction(self,row):
        isData = row.isData

        # per sample cuts
        keep = True
        if self.sample=='DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'  : keep = row.numGenJets==0 or row.numGenJets>4
        if self.sample=='DY1JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' : keep = row.numGenJets==1
        if self.sample=='DY2JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' : keep = row.numGenJets==2
        if self.sample=='DY3JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' : keep = row.numGenJets==3
        if self.sample=='DY4JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' : keep = row.numGenJets==4
        if self.sample=='WJetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'       : keep = row.numGenJets==0 or row.numGenJets>4
        if self.sample=='W1JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'      : keep = row.numGenJets==1
        if self.sample=='W2JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'      : keep = row.numGenJets==2
        if self.sample=='W3JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'      : keep = row.numGenJets==3
        if self.sample=='W4JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'      : keep = row.numGenJets==4
        if not keep: return

        # define weights
        wl = self.getWeight(row,cut='loose')
        wm = self.getWeight(row,cut='medium')
        wt = self.getWeight(row,cut='tight')

        # setup channels
        passMedium = row.t_passMedium
        passTight = row.t_passTight
        recoChan = ''.join([x for x in row.channel if x in 'emt'])

        # define count regions
        default = row.z_deltaR>0.02 and row.m_pt>25. and (row.z_mass<40 or row.z_mass>100) and row.wm_mt>60. and row.t_charge==row.m_charge


        # increment counts
        if default:
            self.increment('loose',wl,recoChan)
            if passMedium: self.increment('medium',wm,recoChan)
            if passTight: self.increment('tight',wt,recoChan)




def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Run skimmer')

    parser.add_argument('sample', type=str, default='SingleMuon', nargs='?', help='Sample to skim')
    parser.add_argument('shift', type=str, default='', nargs='?', help='Shift to apply to scale factors')

    return parser.parse_args(argv)

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = parse_command_line(argv)

    skimmer = WTauFakeRateSkimmer(
        args.sample,
        shift=args.shift,
    )

    skimmer.skim()

    return 0

if __name__ == "__main__":
    status = main()
    sys.exit(status)

