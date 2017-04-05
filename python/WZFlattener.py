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


logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


class WZFlattener(NtupleFlattener):
    '''
    WZ flattener
    '''

    def __init__(self,sample,**kwargs):
        # controls
        self.datadriven = True
        self.datadrivenRegular = False
        self.dy = True
        self.tt = True
        self.vbs = True
        self.nMinusOne = True
        self.jetPt = False
        # setup properties
        self.leps = ['z1','z2','w1']
        self.channels = ['eee','eem','mme','mmm']
        self.cutMap = {
            'default': {
                'zptCut'   : lambda row: row.z1_pt>25 and row.z2_pt>15,
                'wptCut'   : lambda row: row.w1_pt>20,
                'bvetoCut' : lambda row: row.numBjetsTight30==0,
                'metCut'   : lambda row: row.met_pt>30,
                'zmassCut' : lambda row: abs(row.z_mass-ZMASS)<15,
                'wmllCut'  : lambda row: row.w1_z1_mass>4 and row.w1_z2_mass>4,
                '3lmassCut': lambda row: getattr(row,'3l_mass')>100,
            },
            'vbs': {
                'twoJets' : lambda row: row.dijet_mass>0.,
                'jetPt'   : lambda row: row.leadJet_pt>50. and row.subleadJet_pt>50.,
                'jetDEta' : lambda row: row.dijet_deltaEta>2.5,
                'mjj'     : lambda row: row.dijet_mass>400.,
            },
            'dy': {
                'zptCut'   : lambda row: row.z1_pt>25 and row.z2_pt>15,
                'wptCut'   : lambda row: row.w1_pt>20,
                'metCut'   : lambda row: row.met_pt<25,
                'zmassCut' : lambda row: abs(row.z_mass-ZMASS)<15,
                '3lmassCut': lambda row: getattr(row,'3l_mass')>100,
            },
            'tt': {
                'zptCut'   : lambda row: row.z1_pt>25 and row.z2_pt>15,
                'wptCut'   : lambda row: row.w1_pt>20,
                'bCut'     : lambda row: row.numBjetsTight30>0,
                'metCut'   : lambda row: row.met_pt>25,
                'zvetoCut' : lambda row: abs(row.z_mass-ZMASS)>5,
                '3lmassCut': lambda row: getattr(row,'3l_mass')>100,
            },
        }

        self.toProcess = ['default']
        if self.dy: self.toProcess += ['dy']
        if self.tt: self.toProcess += ['tt']
        if self.vbs: self.toProcess += ['vbs']
        if self.nMinusOne:
            for sel in self.cutMap['default']:
                self.toProcess += ['default/{0}'.format(sel)]
            for sel in self.cutMap['vbs']:
                if self.vbs: self.toProcess += ['vbs/{0}'.format(sel)]

        self.jetPts = [20,25,30,35,40,45,50]

        self.selections = []
        for sel in self.toProcess:
            self.selections += [sel]
            if not self.datadriven: continue
            for fakeChan in ['PPP','PPF','PFP','FPP','PFF','FPF','FFP','FFF']:
                self.selections += ['{0}/{1}'.format(fakeChan,sel)]
                if self.datadrivenRegular: self.selections += ['{0}_regular/{1}'.format(fakeChan,sel)]
                if sel not in ['default','dy','tt']: continue
                for jetPt in self.jetPts:
                    jetName = 'jetPt{0}'.format(jetPt)
                    if self.jetPt: self.selections += ['{0}/{1}/{2}'.format(fakeChan,sel,jetName)]


        # setup histogram parameters
        self.histParams = {
            'count'                       : {'x': lambda row: 1,                      'xBinning': [1,0,2],                 }, # just a count of events passing selection
            'met'                         : {'x': lambda row: row.met_pt,             'xBinning': [500, 0, 500],           },
            'metPhi'                      : {'x': lambda row: row.met_phi,            'xBinning': [500, -3.14159, 3.14159],},
            'zMass'                       : {'x': lambda row: row.z_mass,             'xBinning': [500, 0, 500],           },
            'zPt'                         : {'x': lambda row: row.z_pt,               'xBinning': [500, 0, 500],           },
            'zDeltaR'                     : {'x': lambda row: row.z_deltaR,           'xBinning': [500, 0, 5],             },
            'zLeadingLeptonPt'            : {'x': lambda row: row.z1_pt,              'xBinning': [1000, 0, 1000],         },
            'zLeadingLeptonEta'           : {'x': lambda row: row.z1_eta,             'xBinning': [500, -2.5, 2.5],        },
            'zSubLeadingLeptonPt'         : {'x': lambda row: row.z2_pt,              'xBinning': [1000, 0, 1000],         },
            'zSubLeadingLeptonEta'        : {'x': lambda row: row.z2_eta,             'xBinning': [500, -2.5, 2.5],        },
            'wMass'                       : {'x': lambda row: row.w_mt,               'xBinning': [500, 0, 500],           },
            'wPt'                         : {'x': lambda row: row.w_pt,               'xBinning': [500, 0, 500],           },
            'wLeptonPt'                   : {'x': lambda row: row.w1_pt,              'xBinning': [500, 0, 500],           },
            'wLeptonEta'                  : {'x': lambda row: row.w1_eta,             'xBinning': [500, -2.5, 2.5],        },
            'mass'                        : {'x': lambda row: getattr(row,'3l_mass'), 'xBinning': [500, 0, 500],           },
            'nJets'                       : {'x': lambda row: row.numJetsTight30,     'xBinning': [11, -0.5, 10.5],        },
            'nBjets'                      : {'x': lambda row: row.numBjetsTight30,    'xBinning': [11, -0.5, 10.5],        },
            'leadJetPt'                   : {'x': lambda row: row.leadJet_pt,         'xBinning': [500, 0, 500],           'selection': lambda row: row.leadJet_pt>0.,},
            'subleadJetPt'                : {'x': lambda row: row.subleadJet_pt,      'xBinning': [500, 0, 500],           'selection': lambda row: row.subleadJet_pt>0.,},
            'dijetMass'                   : {'x': lambda row: row.dijet_mass,         'xBinning': [2000, 0, 2000],         'selection': lambda row: row.dijet_mass>0.,},
            'dijetDEta'                   : {'x': lambda row: row.dijet_deltaEta,     'xBinning': [100, 0, 10],            'selection': lambda row: row.dijet_deltaEta>0.},
        }

        # initialize flattener
        super(WZFlattener, self).__init__('WZ',sample,**kwargs)

        self.leps = ['z1','z2','w1']

        self.wzTightVar = {
            0: 'z1_passTight',
            1: 'z2_passTight',
            2: 'w1_passTight',
        }

        self.wzTightScale = {
            0: 'z1_tightScale',
            1: 'z2_tightScale',
            2: 'w1_tightScale',
        }

        self.wzLooseScale = {
            0: 'z1_looseScale',
            1: 'z2_looseScale',
            2: 'w1_looseScale',
        }

        self.wzFakeRate = {
            0: 'z1_tightFakeRate',
            1: 'z2_tightFakeRate',
            2: 'w1_tightFakeRate',
        }

        self.wzScaleMap = {
            'P': self.wzTightScale,
            'F': self.wzLooseScale,
        }

        # alternative fakerates
        self.fakekey = '{num}_{denom}'
        self.fakehists = {'electrons': {}, 'muons': {}, 'taus': {},}
        fake_path = '{0}/src/DevTools/Analyzer/data/fakerates_dijet_hpp_13TeV_Run2016BCDEFGH.root'.format(os.environ['CMSSW_BASE'])
        self.fake_hpp_rootfile = ROOT.TFile(fake_path)
        self.fakehists['electrons'][self.fakekey.format(num='HppMedium',denom='HppLoose')] = self.fake_hpp_rootfile.Get('e/medium_loose/fakeratePtEta')
        self.fakehists['electrons'][self.fakekey.format(num='HppTight',denom='HppLoose')] = self.fake_hpp_rootfile.Get('e/tight_loose/fakeratePtEta')
        self.fakehists['muons'][self.fakekey.format(num='HppMedium',denom='HppLoose')] = self.fake_hpp_rootfile.Get('m/medium_loose/fakeratePtEta')
        self.fakehists['muons'][self.fakekey.format(num='HppTight',denom='HppLoose')] = self.fake_hpp_rootfile.Get('m/tight_loose/fakeratePtEta')
        for jetPt in self.jetPts:
            self.fakehists['electrons'][jetPt] = {
                self.fakekey.format(num='HppMedium',denom='HppLoose') : self.fake_hpp_rootfile.Get('e/medium_loose/fakeratePtEta_jetPt{0}'.format(jetPt)),
                self.fakekey.format(num='HppTight',denom='HppLoose')  : self.fake_hpp_rootfile.Get('e/tight_loose/fakeratePtEta_jetPt{0}'.format(jetPt)),
            }
            self.fakehists['muons'][jetPt] = {
                self.fakekey.format(num='HppMedium',denom='HppLoose') : self.fake_hpp_rootfile.Get('m/medium_loose/fakeratePtEta_jetPt{0}'.format(jetPt)),
                self.fakekey.format(num='HppTight',denom='HppLoose')  : self.fake_hpp_rootfile.Get('m/tight_loose/fakeratePtEta_jetPt{0}'.format(jetPt)),
            }

    def getFakeRate(self,lep,pt,eta,num,denom,jetPt=0):
        key = self.fakekey.format(num=num,denom=denom)
        if jetPt in self.fakehists[lep]:
            hist = self.fakehists[lep][jetPt][key]
        else:
            hist = self.fakehists[lep][key]
        if pt > 100.: pt = 99.
        b = hist.FindBin(pt,abs(eta))
        return hist.GetBinContent(b), hist.GetBinError(b)

    def getWeight(self,row,doFake=False,jetPt=0):
        passID = [getattr(row,self.wzTightVar[l]) for l in range(3)]
        if row.isData:
            weight = 1.
        else:
            # per event weights
            base = ['genWeight','pileupWeight','triggerEfficiency']
            if self.shift=='trigUp': base = ['genWeight','pileupWeight','triggerEfficiencyUp']
            if self.shift=='trigDown': base = ['genWeight','pileupWeight','triggerEfficiencyDown']
            if self.shift=='puUp': base = ['genWeight','pileupWeightUp','triggerEfficiency']
            if self.shift=='puDown': base = ['genWeight','pileupWeightDown','triggerEfficiency']
            for l,p in enumerate(passID):
                if self.shift == 'lepUp':
                    base += [self.wzScaleMap['P' if p else 'F'][l]+'Up']
                elif self.shift == 'lepDown':
                    base += [self.wzScaleMap['P' if p else 'F'][l]+'Down']
                else:
                    base += [self.wzScaleMap['P' if p else 'F'][l]]
            vals = [getattr(row,scale) for scale in base]
            for scale,val in zip(base,vals):
                if val != val: logging.warning('{0}: {1} is NaN'.format(row.channel,scale))
            weight = prod([val for val in vals if val==val])
            # scale to lumi/xsec
            weight *= float(self.intLumi)/self.sampleLumi if self.sampleLumi else 0.
            if hasattr(row,'qqZZkfactor'): weight *= row.qqZZkfactor/1.1 # ZZ variable k factor
        # fake scales
        if doFake:
            chanMap = {'e': 'electrons', 'm': 'muons', 't': 'taus',}
            chan = ''.join([x for x in row.channel if x in 'emt'])
            pts = [getattr(row,'{0}_pt'.format(x)) for x in self.leps]
            etas = [getattr(row,'{0}_eta'.format(x)) for x in self.leps]
            region = ''.join(['P' if x else 'F' for x in passID])
            sign = -1 if region.count('F')%2==0 and region.count('F')>0 else 1
            weight *= sign
            if not row.isData and not all(passID): weight *= -1 # subtract off MC in control
            for l,p in enumerate(passID):
                if not p:
                    if jetPt:
                        # recalculate
                        fakeEff = self.getFakeRate(chanMap[chan[l]], pts[l], etas[l], 'HppTight','HppLoose',jetPt=jetPt)[0]
                    else:
                        # read from tree
                        fake = self.wzFakeRate[l]
                        if self.shift=='fakeUp': fake += 'Up'
                        if self.shift=='fakeDown': fake += 'Down'
                        fakeEff = getattr(row,fake)
                    weight *= fakeEff/(1-fakeEff)

        return weight


    def perRowAction(self,row):
        isData = row.isData

        # per sample cuts
        keep = True
        if self.sample=='DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'  : keep = row.numGenJets==0 or row.numGenJets>4
        if self.sample=='DY1JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' : keep = row.numGenJets==1
        if self.sample=='DY2JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' : keep = row.numGenJets==2
        if self.sample=='DY3JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' : keep = row.numGenJets==3
        if self.sample=='DY4JetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8' : keep = row.numGenJets==4
        if self.sample=='DYJetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'      : keep = row.numGenJets==0 or row.numGenJets>4
        if self.sample=='DY1JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : keep = row.numGenJets==1
        if self.sample=='DY2JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : keep = row.numGenJets==2
        if self.sample=='DY3JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : keep = row.numGenJets==3
        if self.sample=='DY4JetsToLL_M-50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'     : keep = row.numGenJets==4
        if self.sample=='WJetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'           : keep = row.numGenJets==0 or row.numGenJets>4
        if self.sample=='W1JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          : keep = row.numGenJets==1
        if self.sample=='W2JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          : keep = row.numGenJets==2
        if self.sample=='W3JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          : keep = row.numGenJets==3
        if self.sample=='W4JetsToLNu_TuneCUETP8M1_13TeV-madgraphMLM-pythia8'          : keep = row.numGenJets==4
        if not keep: return


        # define weights
        w = self.getWeight(row)
        wf = self.getWeight(row,doFake=True)
        wfMap = {}
        for jetPt in self.jetPts:
            wfMap[jetPt] = self.getWeight(row,doFake=True,jetPt=jetPt)

        # setup channels
        passID = [getattr(row,self.wzTightVar[l]) for l in range(3)]
        fakeChan = ''.join(['P' if p else 'F' for p in passID])
        recoChan = ''.join([x for x in row.channel if x in 'emt'])

        # define count regions
        if not isData:
            genCut = all([getattr(row,'{0}_genMatch'.format(lep)) and getattr(row,'{0}_genDeltaR'.format(lep))<0.1 for lep in self.leps])

        def fill(row,sel):
            if all(passID): self.fill(row,sel,w,recoChan)
            if not self.datadriven: return
            if isData or genCut: self.fill(row,fakeChan+'/'+sel,wf,recoChan)
            if self.datadrivenRegular: self.fill(row,fakeChan+'_regular/'+sel,w,recoChan)
            if sel not in ['default','dy','tt']: return
            for jetPt in self.jetPts:
                if (isData or genCut) and self.jetPt: self.fill(row,fakeChan+'/'+sel+'/jetPt{0}'.format(jetPt),wfMap[jetPt],recoChan)

        #print ''
        #print 'Processing'
        for baseSel in self.cutMap:
            result = all([self.cutMap[baseSel][cut](row) for cut in self.cutMap[baseSel]])
            if baseSel=='vbs': result = result and all([self.cutMap['default'][cut](row) for cut in self.cutMap['default']])
            #print baseSel, result
            if result: fill(row,baseSel)
            if self.nMinusOne and baseSel in ['default','vbs']:
                for sel in self.cutMap[baseSel]:
                     result = all([self.cutMap[baseSel][cut](row) for cut in self.cutMap[baseSel] if cut!=sel])
                     if baseSel=='vbs': result = result and all([self.cutMap['default'][cut](row) for cut in self.cutMap['default']])
                     #print baseSel, sel, result
                     if result: fill(row,'{0}/{1}'.format(baseSel,sel))




def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Run Flattener')

    parser.add_argument('sample', type=str, default='DoubleMuon', nargs='?', help='Sample to flatten')
    parser.add_argument('shift', type=str, default='', nargs='?', help='Shift to apply to scale factors')

    return parser.parse_args(argv)

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = parse_command_line(argv)

    flattener = WZFlattener(
        args.sample,
        shift=args.shift,
    )

    flattener.flatten()

    return 0

if __name__ == "__main__":
    status = main()
    sys.exit(status)

