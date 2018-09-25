#!/usr/bin/env python
import argparse
import logging
import os
import sys
import itertools
import operator

from NtupleSkimmer import NtupleSkimmer
from DevTools.Utilities.utilities import prod, ZMASS
from DevTools.Plotter.higgsUtilities import *
from DevTools.Analyzer.BTagScales import BTagScales

import ROOT

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


class Hpp3lSkimmer(NtupleSkimmer):
    '''
    Hpp3l skimmer
    '''

    def __init__(self,sample,**kwargs):
        super(Hpp3lSkimmer, self).__init__('Hpp3l',sample,**kwargs)

        # test if we want to run the optimization routine
        self.new = True # uses NewDMs for tau loose ID
        self.tauFakeMode = 'z' # allowed: w, z
        self.doDMFakes = True
        self.optimize = False
        self.var = 'st'
        self.doBVeto = True
        self.doBScales = False
        self.zveto = True
        self.btag_scales = BTagScales('80X')

        # setup properties
        self.leps = ['hpp1','hpp2','hm1']
        self.isSignal = 'HPlusPlusHMinus' in self.sample
        self.masses = [200,300,400,500,600,700,800,900,1000,1100,1200,1300,1400,1500]
        if self.isSignal:
            self.masses = [mass for mass in self.masses if 'M-{0}'.format(mass) in self.sample]

        # alternative fakerates
        self.fakekey = '{num}_{denom}'
        self.fakehists = {'electrons': {}, 'muons': {}, 'taus': {},}

        fake_path = '{0}/src/DevTools/Analyzer/data/fakerates_dijet_hpp_13TeV_Run2016BCDEFGH.root'.format(os.environ['CMSSW_BASE'])
        self.fake_hpp_rootfile = ROOT.TFile(fake_path)
        self.fakehists['electrons'][self.fakekey.format(num='HppMedium',denom='HppLooseNew')] = self.fake_hpp_rootfile.Get('e/medium_loose/fakeratePtEta')
        self.fakehists['electrons'][self.fakekey.format(num='HppTight',denom='HppLooseNew')] = self.fake_hpp_rootfile.Get('e/tight_loose/fakeratePtEta')
        self.fakehists['electrons'][self.fakekey.format(num='HppMedium',denom='HppLoose')] = self.fake_hpp_rootfile.Get('e/medium_loose/fakeratePtEta')
        self.fakehists['electrons'][self.fakekey.format(num='HppTight',denom='HppLoose')] = self.fake_hpp_rootfile.Get('e/tight_loose/fakeratePtEta')
        self.fakehists['electrons'][self.fakekey.format(num='HppTight',denom='HppMedium')] = self.fake_hpp_rootfile.Get('e/tight_medium/fakeratePtEta')
        self.fakehists['muons'][self.fakekey.format(num='HppMedium',denom='HppLooseNew')] = self.fake_hpp_rootfile.Get('m/medium_loose/fakeratePtEta')
        self.fakehists['muons'][self.fakekey.format(num='HppTight',denom='HppLooseNew')] = self.fake_hpp_rootfile.Get('m/tight_loose/fakeratePtEta')
        self.fakehists['muons'][self.fakekey.format(num='HppMedium',denom='HppLoose')] = self.fake_hpp_rootfile.Get('m/medium_loose/fakeratePtEta')
        self.fakehists['muons'][self.fakekey.format(num='HppTight',denom='HppLoose')] = self.fake_hpp_rootfile.Get('m/tight_loose/fakeratePtEta')
        self.fakehists['muons'][self.fakekey.format(num='HppTight',denom='HppMedium')] = self.fake_hpp_rootfile.Get('m/tight_medium/fakeratePtEta')

        if self.tauFakeMode=='w':
            fake_path = '{0}/src/DevTools/Analyzer/data/fakerates_w_tau_13TeV_Run2016BCDEFGH.root'.format(os.environ['CMSSW_BASE'])
        elif self.tauFakeMode=='z':
            fake_path = '{0}/src/DevTools/Analyzer/data/fakerates_z_tau_13TeV_Run2016BCDEFGH.root'.format(os.environ['CMSSW_BASE'])
        else:
            logging.error('Undefined tau fake mode {0}'.format(self.tauFakeMode))
            raise
        self.fake_hpp_rootfile_tau = ROOT.TFile(fake_path)
        self.fakehists['taus'][self.fakekey.format(num='HppMedium',denom='HppLooseNew')]     = self.fake_hpp_rootfile_tau.Get('medium_newloose/fakeratePtEta')
        self.fakehists['taus'][self.fakekey.format(num='HppTight', denom='HppLooseNew')]     = self.fake_hpp_rootfile_tau.Get('tight_newloose/fakeratePtEta')
        self.fakehists['taus'][self.fakekey.format(num='HppMedium',denom='HppLooseNewDM0')]  = self.fake_hpp_rootfile_tau.Get('medium_newloose/fakeratePtEtaDM0')
        self.fakehists['taus'][self.fakekey.format(num='HppTight', denom='HppLooseNewDM0')]  = self.fake_hpp_rootfile_tau.Get('tight_newloose/fakeratePtEtaDM0')
        self.fakehists['taus'][self.fakekey.format(num='HppMedium',denom='HppLooseNewDM1')]  = self.fake_hpp_rootfile_tau.Get('medium_newloose/fakeratePtEtaDM1')
        self.fakehists['taus'][self.fakekey.format(num='HppTight', denom='HppLooseNewDM1')]  = self.fake_hpp_rootfile_tau.Get('tight_newloose/fakeratePtEtaDM1')
        self.fakehists['taus'][self.fakekey.format(num='HppMedium',denom='HppLooseNewDM10')] = self.fake_hpp_rootfile_tau.Get('medium_newloose/fakeratePtEtaDM10')
        self.fakehists['taus'][self.fakekey.format(num='HppTight', denom='HppLooseNewDM10')] = self.fake_hpp_rootfile_tau.Get('tight_newloose/fakeratePtEtaDM10')
        self.fakehists['taus'][self.fakekey.format(num='HppMedium',denom='HppLoose')]        = self.fake_hpp_rootfile_tau.Get('medium_loose/fakeratePtEta')
        self.fakehists['taus'][self.fakekey.format(num='HppTight', denom='HppLoose')]        = self.fake_hpp_rootfile_tau.Get('tight_loose/fakeratePtEta')
        self.fakehists['taus'][self.fakekey.format(num='HppMedium',denom='HppLooseDM0')]     = self.fake_hpp_rootfile_tau.Get('medium_loose/fakeratePtEtaDM0')
        self.fakehists['taus'][self.fakekey.format(num='HppTight', denom='HppLooseDM0')]     = self.fake_hpp_rootfile_tau.Get('tight_loose/fakeratePtEtaDM0')
        self.fakehists['taus'][self.fakekey.format(num='HppMedium',denom='HppLooseDM1')]     = self.fake_hpp_rootfile_tau.Get('medium_loose/fakeratePtEtaDM1')
        self.fakehists['taus'][self.fakekey.format(num='HppTight', denom='HppLooseDM1')]     = self.fake_hpp_rootfile_tau.Get('tight_loose/fakeratePtEtaDM1')
        self.fakehists['taus'][self.fakekey.format(num='HppMedium',denom='HppLooseDM10')]    = self.fake_hpp_rootfile_tau.Get('medium_loose/fakeratePtEtaDM10')
        self.fakehists['taus'][self.fakekey.format(num='HppTight', denom='HppLooseDM10')]    = self.fake_hpp_rootfile_tau.Get('tight_loose/fakeratePtEtaDM10')
        self.fakehists['taus'][self.fakekey.format(num='HppTight', denom='HppMedium')]       = self.fake_hpp_rootfile_tau.Get('tight_medium/fakeratePtEta')

        for num in ['medium','tight']:
            for dlab in ['oldloose','newloose']:
                for dcut in ['n0p2','n0p1','0p0','0p1','0p2','0p3','0p4']:
                    denom = '{}_{}'.format(dlab,dcut)
                    self.fakehists['taus'][self.fakekey.format(num=num,denom=denom)]         = self.fake_hpp_rootfile_tau.Get('{}_{}/fakeratePtEta'.format(num,denom))
                    self.fakehists['taus'][self.fakekey.format(num=num,denom=denom+'DM0')]   = self.fake_hpp_rootfile_tau.Get('{}_{}/fakeratePtEtaDM0'.format(num,denom))
                    self.fakehists['taus'][self.fakekey.format(num=num,denom=denom+'DM1')]   = self.fake_hpp_rootfile_tau.Get('{}_{}/fakeratePtEtaDM1'.format(num,denom))
                    self.fakehists['taus'][self.fakekey.format(num=num,denom=denom+'DM10')]  = self.fake_hpp_rootfile_tau.Get('{}_{}/fakeratePtEtaDM10'.format(num,denom))

        self.scaleMap = {
            'F' : '{0}_looseScale',
            'P' : '{0}_mediumScale',
        }

        self.fakeVal = '{0}_mediumNewFakeRate' if self.new else '{0}_mediumFakeRate'

        self.lepID = '{0}_passMedium'
        self.lepIDLoose = '{0}_passLooseNew' if self.new else '{0}_passLoose'

        # charge
        charge_path = '{0}/src/DevTools/Analyzer/data/scalefactors_charge_2016.root'.format(os.environ['CMSSW_BASE'])
        self.charge_rootfile = ROOT.TFile(charge_path)
        self.chargehists = {'electrons': {}}
        self.chargehists['electrons']['OppositeSign'] = self.charge_rootfile.Get('OppositeSign')

    def getFakeRate(self,lep,pt,eta,num,denom,dm=None):
        if lep=='taus' and self.doDMFakes:
            if dm in [0,5]:
                denom = denom + 'DM0'
            elif dm in [1,6]:
                denom = denom + 'DM1'
            elif dm in [10]:
                denom = denom + 'DM10'
        key = self.fakekey.format(num=num,denom=denom)
        hist = self.fakehists[lep][key]
        if pt > 100.: pt = 99.
        b = hist.FindBin(pt,abs(eta))
        return hist.GetBinContent(b), hist.GetBinError(b)

    def getBTagWeight(self,row):
        op = 1 # medium
        s = 'central'
        if self.shift == 'btagUp': s = 'up'
        if self.shift == 'btagDown': s = 'down'
        w = 1
        for l in self.leps:
            pt = getattr(row,'{0}jet_pt'.format(l))
            if not pt>0: continue
            eta = getattr(row,'{0}jet_eta'.format(l))
            hf = getattr(row,'{}jet_hadronFlavour'.format(l))
            if hf==5: #b
                flavor = 0
            elif hf==4: #c
                flavor = 1
            else: # light
                flavor = 2
            sf = self.btag_scales.get_sf_csv(1,pt,eta,shift=s,flavor=flavor)
            if getattr(row,'{0}jet_passCSVv2M'.format(l))>0.5:
                w *= 1-sf
        return w

    def getCharge(self,lep,pt,eta):
        if lep=='electrons':
            hist = self.chargehists['electrons']['OppositeSign']
            if pt > 500: pt = 499
            b = hist.FindBin(pt,abs(eta))
            val, err = hist.GetBinContent(b), hist.GetBinError(b)
            result = val
            if self.shift=='chargeUp': result = val + err
            if self.shift=='chargeDown': resutl =  val - err
            if result < 0: result = 0
            return result
        return 1

    def getWeight(self,row,doFake=False,fakeNum=None,fakeDenom=None):
        chanMap = {'e': 'electrons', 'm': 'muons', 't': 'taus',}
        chan = ''.join([x for x in row.channel if x in 'emt'])
        if not fakeNum: fakeNum = 'HppMedium'
        if not fakeDenom: fakeDenom = 'HppLoose{0}'.format('New' if self.new else '')
        passID = [getattr(row,self.lepID.format(l)) for l in self.leps]
        if row.isData:
            weight = 1.
        else:
            # per event weights
            base = ['genWeight','pileupWeight','triggerEfficiency']
            if self.shift=='trigUp': base = ['genWeight','pileupWeight','triggerEfficiencyUp']
            if self.shift=='trigDown': base = ['genWeight','pileupWeight','triggerEfficiencyDown']
            if self.shift=='puUp': base = ['genWeight','pileupWeightUp','triggerEfficiency']
            if self.shift=='puDown': base = ['genWeight','pileupWeightDown','triggerEfficiency']
            for l,lep in enumerate(self.leps):
                shiftString = ''
                if self.shift == 'lepUp': shiftString = 'Up'
                if self.shift == 'lepDown': shiftString = 'Down'
                base += [self.scaleMap['P' if passID[l] else 'F'].format(lep)+shiftString]
            vals = [getattr(row,scale) for scale in base]
            for scale,val in zip(base,vals):
                if val != val: logging.warning('{0}: {1} is NaN'.format(row.channel,scale))
            weight = prod([val for val in vals if val==val])
            # scale to lumi/xsec
            weight *= float(self.intLumi)/self.sampleLumi if self.sampleLumi else 0.
            if hasattr(row,'qqZZkfactor'): weight *= row.qqZZkfactor/1.1 # ZZ variable k factor
            # b tagging (veto)
            if self.doBScales: weight *= self.getBTagWeight(row)
            for l, lep in enumerate(self.leps):
                weight *= self.getCharge(chanMap[chan[l]], getattr(row, '{}_pt'.format(lep)), getattr(row, '{}_eta'.format(lep)))
        # fake scales
        if doFake:
            pts = [getattr(row,'{0}_pt'.format(x)) for x in self.leps]
            etas = [getattr(row,'{0}_eta'.format(x)) for x in self.leps]
            region = ''.join(['P' if x else 'F' for x in passID])
            sign = -1 if region.count('F')%2==0 and region.count('F')>0 else 1
            weight *= sign
            if not row.isData and not all(passID): weight *= -1 # subtract off MC in control
            for l,lep in enumerate(self.leps):
                if not passID[l]:
                    # recalculate
                    dm = None if chan[l]!='taus' else getattr(row,'{0}_decayMode'.format(lep))
                    fn = fakeNum
                    fd = fakeDenom
                    if isinstance(fakeNum,dict): fn = fakeNum[chan[l]]
                    if isinstance(fakeDenom,dict): fd = fakeDenom[chan[l]]
                    fakeEff = self.getFakeRate(chanMap[chan[l]], pts[l], etas[l], fn, fd, dm=dm)[0]

                    # read from tree
                    #fake = self.fakeVal.format(lep)
                    #if self.shift=='fakeUp': fake += 'Up'
                    #if self.shift=='fakeDown': fake += 'Down'
                    #fakeEff = getattr(row,fake)

                    weight *= fakeEff/(1-fakeEff)

        return weight

    def perRowAction(self,row):
        isData = row.isData

        passPt = [getattr(row,'{0}_pt'.format(l))>20 for l in self.leps]
        if not all(passPt): return # all leptons pt>20
        pass3l = getattr(row,'3l_mass')>100
        if not pass3l: return # m3l>100
        passLooseId = all([getattr(row,'{0}_passLoose{1}'.format(l,'New' if self.new else ''))>0.5 for l in self.leps])
        if not passLooseId: return 
        if self.zveto:
            if abs(row.z_mass-ZMASS)<10: return
        # Don't do for MC, events that pass btag contribute a factor of 1-SF
        passbveto = all([getattr(row,'{0}jet_passCSVv2M'.format(l))<0.5 for l in self.leps])
        if self.doBScales:
            if isData and not passbveto and self.doBVeto: return
        else:
            if not passbveto and self.doBVeto: return

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

        # setup channels
        passID = [getattr(row,self.lepID.format(l)) for l in self.leps]
        region = ''.join(['P' if p else 'F' for p in passID])
        nf = region.count('F')
        fakeChan = '{0}P{1}F'.format(3-nf,nf)
        recoChan = ''.join([x for x in row.channel if x in 'emt'])
        recoChan = ''.join(sorted(recoChan[:2]) + sorted(recoChan[2:3]))
        if isData:
            genChan = 'all'
        else:
            genChan = row.genChannel
            if 'HPlusPlus' in self.sample:
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
            #genCut = all([getattr(row,'{0}_genMatch'.format(lep)) and getattr(row,'{0}_genDeltaR'.format(lep))<0.1 for lep in self.leps])
            genCut = all([
                (getattr(row,'{0}_genMatch'.format(lep)) and getattr(row,'{0}_genDeltaR'.format(lep))<0.1)
                or
                (getattr(row,'{0}_genJetMatch'.format(lep)) and getattr(row,'{0}_genJetDeltaR'.format(lep))<0.1)
                for lep in self.leps
            ])
            genCut = True # temp to test bug

        # cut map
        v = {
            'st': row.hpp1_pt+row.hpp2_pt+row.hm1_pt,
            'zdiff': abs(row.z_mass-ZMASS),
            'dr': row.hpp_deltaR,
            'hpp': row.hpp_mass,
            'met': row.met_pt,
        }
        cutRegions = {}
        for mass in self.masses:
            cutRegions[mass] = getSelectionMap('Hpp3l',mass)

        # optimization ranges
        stRange = [x*20 for x in range(100)]
        zvetoRange = [x*5 for x in range(25)]
        drRange = [1.5+x*0.1 for x in range(50)]
        metRange = [x*5 for x in range(40)]

        # increment counts
        if default:
            if all(passID): self.increment('default',w,recoChan,genChan)
            if isData or genCut: self.increment(fakeChan,wf,recoChan,genChan)
            self.increment(fakeChan+'_regular',w,recoChan,genChan)

            for nTaus in range(3):
                for mass in self.masses:
                    name = '{0}/hpp{1}'.format(mass,nTaus)
                    sides = []
                    windows = []
                    sides += [cutRegions[mass][nTaus]['st'](row)]
                    #sides += [cutRegions[mass][nTaus]['zveto'](row)]
                    sides += [cutRegions[mass][nTaus]['met'](row)]
                    sides += [cutRegions[mass][nTaus]['dr'](row)]
                    windows += [cutRegions[mass][nTaus]['mass'](row)]
                    massWindowOnly = all(windows)
                    sideband = not all(sides) and not all(windows)
                    massWindow = not all(sides) and all(windows)
                    allSideband = all(sides) and not all(windows)
                    allMassWindow = all(sides) and all(windows)
                    if not self.optimize:
                        if sideband:
                            if all(passID): self.increment('new/sideband/'+name,w,recoChan,genChan)
                            if isData or genCut: self.increment(fakeChan+'/new/sideband/'+name,wf,recoChan,genChan)
                        if massWindow:
                            if all(passID): self.increment('new/massWindow/'+name,w,recoChan,genChan)
                            if isData or genCut: self.increment(fakeChan+'/new/massWindow/'+name,wf,recoChan,genChan)
                        if allSideband:
                            if all(passID): self.increment('new/allSideband/'+name,w,recoChan,genChan)
                            if isData or genCut: self.increment(fakeChan+'/new/allSideband/'+name,wf,recoChan,genChan)
                        if allMassWindow:
                            if all(passID): self.increment('new/allMassWindow/'+name,w,recoChan,genChan)
                            if isData or genCut: self.increment(fakeChan+'/new/allMassWindow/'+name,wf,recoChan,genChan)
                    # run the grid of values
                    if self.optimize:
                        if not massWindowOnly: continue
                        nMinusOneSt = all([cutRegions[mass][nTaus]['zveto'](row), cutRegions[mass][nTaus]['dr'](row), cutRegions[mass][nTaus]['met'](row), cutRegions[mass][nTaus]['mass'](row)])
                        nMinusOneZveto = all([cutRegions[mass][nTaus]['st'](row), cutRegions[mass][nTaus]['dr'](row), cutRegions[mass][nTaus]['met'](row), cutRegions[mass][nTaus]['mass'](row)])
                        nMinusOneDR = all([cutRegions[mass][nTaus]['zveto'](row), cutRegions[mass][nTaus]['st'](row), cutRegions[mass][nTaus]['met'](row), cutRegions[mass][nTaus]['mass'](row)])
                        nMinusOneMet = all([cutRegions[mass][nTaus]['zveto'](row), cutRegions[mass][nTaus]['dr'](row), cutRegions[mass][nTaus]['st'](row), cutRegions[mass][nTaus]['mass'](row)])
                        # 1D no cuts
                        if self.var=='st':
                            for stCutVal in stRange:
                                if v['st']>stCutVal and nMinusOneSt:
                                    if all(passID): self.increment('optimize/st/{0}/{1}'.format(stCutVal,name),w,recoChan,genChan)
                                    if isData or genCut: self.increment(fakeChan+'/optimize/st/{0}/{1}'.format(stCutVal,name),wf,recoChan,genChan)
                        if self.var=='zveto':
                            for zvetoCutVal in zvetoRange:
                                if v['zdiff']>zvetoCutVal and nMinusOneZveto:
                                    if all(passID): self.increment('optimize/zveto/{0}/{1}'.format(zvetoCutVal,name),w,recoChan,genChan)
                                    if isData or genCut: self.increment(fakeChan+'/optimize/zveto/{0}/{1}'.format(zvetoCutVal,name),wf,recoChan,genChan)
                        if self.var=='dr':
                            for drCutVal in drRange:
                                if v['dr']<drCutVal and nMinusOneDR:
                                    if all(passID): self.increment('optimize/dr/{0}/{1}'.format(drCutVal,name),w,recoChan,genChan)
                                    if isData or genCut: self.increment(fakeChan+'/optimize/dr/{0}/{1}'.format(drCutVal,name),wf,recoChan,genChan)
                        if self.var=='met':
                            for metCutVal in metRange:
                                if v['met']>metCutVal and nMinusOneMet:
                                    if all(passID): self.increment('optimize/met/{0}/{1}'.format(metCutVal,name),w,recoChan,genChan)
                                    if isData or genCut: self.increment(fakeChan+'/optimize/met/{0}/{1}'.format(metCutVal,name),wf,recoChan,genChan)
                        # nD
                        #for stCutVal in stRange:
                        #    if v['st']<stCutVal: continue
                        #    for zvetoCutVal in zvetoRange:
                        #        if v['zdiff']<zvetoCutVal: continue
                        #        for drCutVal in drRange:
                        #            if v['dr']>drCutVal: continue
                        #            for metCutVal in metRange:
                        #                if v['met']<metCutVal: continue
                        #                if all(passID): self.increment('optimize/st{0}/zveto{1}/dr{2}/met{3}/{4}'.format(stCutVal,zvetoCutVal,drCutVal,metCutVal,name),w,recoChan,genChan)
                        #                if isData or genCut: self.increment(fakeChan+'optimize/st{0}/zveto{1}/dr{2}/met{3}/{4}'.format(stCutVal,zvetoCutVal,drCutVal,metCutVal,name),wf,recoChan,genChan)


        if lowmass:
            if all(passID): self.increment('lowmass',w,recoChan,genChan)
            if isData or genCut: self.increment(fakeChan+'/lowmass',wf,recoChan,genChan)
            self.increment(fakeChan+'_regular/lowmass',w,recoChan,genChan)



def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Run skimmer')

    parser.add_argument('sample', type=str, default='HPlusPlusHMinusHTo3L_M-500_13TeV-calchep-pythia8', nargs='?', help='Sample to skim')
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

