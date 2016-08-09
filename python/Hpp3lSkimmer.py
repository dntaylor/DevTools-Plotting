#!/usr/bin/env python
import argparse
import logging
import sys
import sys
import itertools
import operator

from NtupleSkimmer import NtupleSkimmer
from DevTools.Utilities.utilities import prod, ZMASS

import ROOT

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


class Hpp3lSkimmer(NtupleSkimmer):
    '''
    Hpp3l skimmer
    '''

    def __init__(self,sample,**kwargs):
        super(Hpp3lSkimmer, self).__init__('Hpp3l',sample,**kwargs)

        # setup output files
        self.leps = ['hpp1','hpp2','hm1']

    def getWeight(self,row,doFake=False):
        passMedium = [getattr(row,'{0}_passMedium'.format(lep)) for lep in self.leps]
        if row.isData:
            weight = 1.
        else:
            # per event weights
            base = ['genWeight','pileupWeight','triggerEfficiency']
            if self.shift=='trigUp': base = ['genWeight','pileupWeight','triggerEfficiencyUp']
            if self.shift=='trigDown': base = ['genWeight','pileupWeight','triggerEfficiencyDown']
            if self.shift=='puUp': base = ['genWeight','pileupWeightUp','triggerEfficiency']
            if self.shift=='puDown': base = ['genWeight','pileupWeightDown','triggerEfficiency']
            for lep,p in zip(self.leps,passMedium):
                if self.shift == 'lepUp':
                    base += ['{0}_mediumScaleUp'.format(lep) if p else '{0}_looseScaleUp'.format(lep)]
                elif self.shift == 'lepDown':
                    base += ['{0}_mediumScaleDown'.format(lep) if p else '{0}_looseScaleDown'.format(lep)]
                else:
                    base += ['{0}_mediumScale'.format(lep) if p else '{0}_looseScale'.format(lep)]
            weight = prod([getattr(row,scale) for scale in base])
            # scale to lumi/xsec
            weight *= float(self.intLumi)/self.sampleLumi if self.sampleLumi else 0.
        # fake scales
        if doFake:
            sign = -1 if sum(passMedium)%2==0 and not all(passMedium) else 1
            weight *= sign
            if not row.isData and not all(passMedium): weight *= -1 # subtract off MC in control
            fake = '{0}_mediumFakeRate'
            if self.shift=='fakeUp': fake = '{0}_mediumFakeRateUp'
            if self.shift=='fakeDown': fake = '{0}_mediumFakeRateDown'
            for lep,p in zip(self.leps,passMedium):
                if not p:
                    fakeEff = getattr(row,fake.format(lep))
                    weight *= fakeEff/(1-fakeEff)

        return weight

    def perRowAction(self,row):
        isData = row.isData

        # per sample cuts
        keep = True
        if self.sample=='DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'  : row.numGenJets==0 or row.numGenJets>4
        if self.sample=='DY1JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' : row.numGenJets==1
        if self.sample=='DY2JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' : row.numGenJets==2
        if self.sample=='DY3JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' : row.numGenJets==3
        if self.sample=='DY4JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' : row.numGenJets==4
        if self.sample=='WJetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'       : row.numGenJets==0 or row.numGenJets>4
        if self.sample=='W1JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'      : row.numGenJets==1
        if self.sample=='W2JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'      : row.numGenJets==2
        if self.sample=='W3JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'      : row.numGenJets==3
        if self.sample=='W4JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'      : row.numGenJets==4
        if not keep: return

        # define weights
        w = self.getWeight(row)
        wf = self.getWeight(row,doFake=True)

        # setup channels
        passMedium = [getattr(row,'{0}_passMedium'.format(lep)) for lep in self.leps]
        fakeChan = ''.join(['P' if p else 'F' for p in passMedium])
        fakeName = '{0}P{1}F'.format(fakeChan.count('P'),fakeChan.count('F'))
        recoChan = row.channel
        recoChan = ''.join(sorted(recoChan[:2]) + sorted(recoChan[2:3])) # sort chans so eme and mee are the same
        if isData:
            genChan = 'all'
        else:
            genChan = row.genChannel
            if genChan[0] != 'a':
                if 'HPlusPlusHMinusMinus' in self.sample:
                    genChan = ''.join(sorted(genChan[:2]) + sorted(genChan[2:4]))
                else:
                    genChan = ''.join(sorted(genChan[:2]) + sorted(genChan[2:3]))
            else:
                genChan = 'all'

        # define count regions
        default = True
        lowmass = row.hpp_mass<100
        if not isData:
            genCut = all([getattr(row,'{0}_genMatch'.format(lep)) and getattr(row,'{0}_genDeltaR'.format(lep))<0.1 for lep in self.leps])

        # cut map
        v = {
            'st': row.hpp1_pt+row.hpp2_pt+row.hm1_pt,
            'zdiff': abs(row.z_mass-ZMASS),
            'dr': row.hpp_deltaR,
            'hpp': row.hpp_mass,
            'met': row.met_pt,
        }
        cutRegions = {}
        masses = [200,300,400,500,600,700,800,900,1000,1100,1200,1300,1400,1500]
        for mass in masses:
            cutRegions[mass] = {
                0: {
                    'st'   : v['st']>0.81*mass+88,
                    'zveto': v['zdiff']>80,
                    'dr'   : v['dr']<mass/380.+2.06 if v['hpp']<400 else v['dr']<mass/1200.+2.77,
                    'mass' : v['hpp']>0.9*mass and v['hpp']<1.1*mass,
                },
                1: {
                    'st'   : v['st']>0.58*mass+85,
                    'zveto': v['zdiff']>80,
                    'met'  : v['met']>20,
                    'dr'   : v['dr']<mass/380.+1.96 if v['hpp']<400 else v['dr']<mass/1000.+2.6,
                    'mass' : v['hpp']>0.4*mass and v['hpp']<1.1*mass,
                },
                2: {
                    'st'   : v['st']>0.35*mass+81,
                    'zveto': v['zdiff']>50,
                    'met'  : v['met']>20,
                    'dr'   : v['dr']<mass/380.+1.86 if v['hpp']<400 else v['dr']<mass/750.+2.37,
                    'mass' : v['hpp']>0.3*mass and v['hpp']<1.1*mass,
                },
            }

        # increment counts
        if default:
            if all(passMedium): self.increment('default',w,recoChan,genChan)
            if isData or genCut: self.increment(fakeName,wf,recoChan,genChan)
            self.increment(fakeName+'_regular',w,recoChan,genChan)

            for nTaus in range(3):
                for mass in masses:
                    name = '{0}/hpp{1}'.format(mass,nTaus)
                    sides = []
                    windows = []
                    sides += [cutRegions[mass][nTaus]['st']]
                    sides += [cutRegions[mass][nTaus]['zveto']]
                    if nTaus>0: sides += [cutRegions[mass][nTaus]['met']]
                    sides += [cutRegions[mass][nTaus]['dr']]
                    windows += [cutRegions[mass][nTaus]['mass']]
                    sideband = not all(sides) and not all(windows)
                    massWindow = not all(sides) and all(windows)
                    allSideband = all(sides) and not all(windows)
                    allMassWindow = all(sides) and all(windows)
                    if sideband:
                        if all(passMedium): self.increment('new/sideband/'+name,w,recoChan,genChan)
                        if isData or genCut: self.increment(fakeName+'/new/sideband/'+name,wf,recoChan,genChan)
                    if massWindow:
                        if all(passMedium): self.increment('new/massWindow/'+name,w,recoChan,genChan)
                        if isData or genCut: self.increment(fakeName+'/new/massWindow/'+name,wf,recoChan,genChan)
                    if allSideband:
                        if all(passMedium): self.increment('new/allSideband/'+name,w,recoChan,genChan)
                        if isData or genCut: self.increment(fakeName+'/new/allSideband/'+name,wf,recoChan,genChan)
                    if allMassWindow:
                        if all(passMedium): self.increment('new/allMassWindow/'+name,w,recoChan,genChan)
                        if isData or genCut: self.increment(fakeName+'/new/allMassWindow/'+name,wf,recoChan,genChan)
                    

        if lowmass:
            if all(passMedium): self.increment('lowmass',w,recoChan,genChan)
            if isData or genCut: self.increment(fakeName+'/lowmass',wf,recoChan,genChan)
            self.increment(fakeName+'_regular/lowmass',w,recoChan,genChan)



def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Run skimmer')

    parser.add_argument('sample', type=str, default='HPlusPlusHMinusHTo3L_M-500_TuneCUETP8M1_13TeV_calchep-pythia8', nargs='?', help='Sample to skim')
    parser.add_argument('shift', type=str, default='', nargs='?', help='Shift to apply to scale factors')

    return parser.parse_args(argv)

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = parse_command_line(argv)

    skimmer = Hpp3lSkimmer(
        args.sample,
        shift=args.shift,
    )

    skimmer.skim()

    return 0

if __name__ == "__main__":
    status = main()
    sys.exit(status)

