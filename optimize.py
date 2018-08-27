#!/usr/bin/env python
import argparse
import logging
import os
import sys
import json
import pickle
import operator

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from DevTools.Utilities.utilities import *
from DevTools.Limits.Optimizer import Optimizer
from DevTools.Plotter.Counter import Counter
from DevTools.Plotter.higgsUtilities import *


logger = logging.getLogger("Optimizer")
logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Optimize a selection')

    parser.add_argument('analysis', type=str, help='Analysis to optimize')
    parser.add_argument('variable', type=str, help='Variable to optimize')

    return parser.parse_args(argv)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = parse_command_line(argv)

    modes = ['ee100','em100','et100','mm100','mt100','tt100']
    masses = [200,300,400,500,600,700,800,900,1000,1100,1200,1300,1400,1500]
    
    cats = getCategories(args.analysis)
    catLabels = getCategoryLabels(args.analysis)
    subCatChannels = getSubCategories(args.analysis)
    subCatLabels = getSubCategoryLabels(args.analysis)
    chans = getChannels(args.analysis)
    chanLabels = getChannelLabels(args.analysis)
    genRecoMap = getGenRecoChannelMap(args.analysis)
    sigMap = getSigMap(args.analysis)
    sigMapDD = getSigMap(args.analysis,datadriven=True)
    
    scales = {}
    for mode in modes:
        scales[mode] = getScales(mode)
    
    samples = ['TTV','VVV','ZZ','WZ']
    allsamples = ['W','T','TT','TTV','Z','WW','VVV','ZZ','WZ']
    if args.analysis=='Hpp4l':
        samples = ['TTV','VVV','ZZ']
        allsamples = ['TT','TTV','Z','WZ','VVV','ZZ']
    signalsAP = ['HppHm{0}GeV'.format(mass) for mass in masses]
    signalsPP = ['HppHmm{0}GeV'.format(mass) for mass in masses]
    backgrounds = ['datadriven']
    
    datadrivenSamples = []
    for s in samples + ['data']:
        datadrivenSamples += sigMap[s]
    
    def getPoisson(entries):
        if entries<0: entries = 0
        chisqr = ROOT.TMath.ChisquareQuantile
        ey_low = entries - 0.5 * chisqr(0.1586555, 2. * entries)
        ey_high = 0.5 * chisqr(
            1. - 0.1586555, 2. * (entries + 1)) - entries
        return ey_high

    def getCount(counters,sig,directory,shift=''):
        tot, totErr = counters[sig+shift].getCount(sig,directory)
        return (tot,totErr)
    
    def getBackgroundCount(counters,directory,datadriven=False,shift=''):
        tot = 0
        totErr2 = 0
        if datadriven:
            dirdirs = directory.split('/')
            for s in samples:
                if args.analysis=='Hpp3l':
                    val,err = getCount(counters,s,'/'.join(['3P0F']+dirdirs),shift=shift)
                else:
                    val,err = getCount(counters,s,'/'.join(['4P0F']+dirdirs),shift=shift)
                tot += val
                totErr2 += err**2
            for s in samples+['data']:
                #regions = ['2P1F','1P2F','0P3F'] if args.analysis=='Hpp3l' else ['3P1F','2P2F','1P3F','0P4F']
                regions = ['2P1F','1P2F','0P3F'] if args.analysis=='Hpp3l' else ['3P1F','2P2F','1P3F']
                for reg in regions:
                    val,err = getCount(counters,s,'/'.join([reg]+dirdirs),shift=shift)
                    tot += val
                    totErr2 += err**2
        else:
            for s in allsamples:
                val,err = getCount(counters,s,directory,shift=shift)
                tot += val
                totErr2 += err**2
        if tot<0:
            tot = 0
        if tot<10:
            perr = getPoisson(int(tot))
            if perr**2 > totErr2:
                totErr2 = perr**2
        return (tot,totErr2**0.5)

    def getRecoChans(mode):
        # find out what reco/gen channels can exist for this mode
        recoChans = set()
        for gen in genRecoMap:
            if len(gen)==3:
                s = scales[mode].scale_Hpp3l(gen[:2],gen[2:])
            else:
                s = scales[mode].scale_Hpp4l(gen[:2],gen[2:])
            if not s: continue
            recoChans.update(genRecoMap[gen])
        return recoChans

    counters = {}
    
    # TODO, think if this is what we want
    modeMap = {
        'ee100': [0,0],
        'em100': [0,0],
        'et100': [1,1],
        'mm100': [0,0],
        'mt100': [1,1],
        'tt100': [2,2],
        'BP1'  : [2,2],
        'BP2'  : [2,2],
        'BP3'  : [2,2],
        'BP4'  : [2,2],
    }
    

    signalsAP = ['HppHm{0}GeV'.format(mass) for mass in masses]
    signalsPP = ['HppHmm{0}GeV'.format(mass) for mass in masses]

    # counters
    counters = {}
    for s in allsamples:
        counters[s] = Counter(args.analysis)
        counters[s].addProcess(s,sigMap[s])
    
    for s in signalsAP:
        counters[s] = Counter(args.analysis)
        counters[s].addProcess(s,sigMap[s],signal=True)
    
    for s in signalsPP:
        counters[s] = Counter(args.analysis)
        counters[s].addProcess(s,sigMap[s],signal=True)
    
    counters['data'] = Counter(args.analysis)
    counters['data'].addProcess('data',sigMap['data'])

    optVars = {
        'st':    [x*20 for x in range(4,100)],
        'zveto': [x*5 for x in range(25)],
        'dr':    [1.5+x*0.1 for x in range(50)],
        'met':   [x*5 for x in range(40)],

    }


    values = {}
    for mode in modes:
        values[mode] = {}
        for mass in masses:
            values[mode][mass] = {}
    
            recoChans = getRecoChans(mode)
    
            signalsAP = ['HppHm{0}GeV'.format(mass)]
            signalsPP = ['HppHmm{0}GeV'.format(mass)]
    
            for optVar in [args.variable]:
                allSOverB = {}
                allPois = {}
                allPoisErr = {}
                allAsimov = {}
                allAsimovErr = {}
                allBg = {}
                allSig = {}
                for optVal in optVars[optVar]:
                    bgTot, bgTotErr2 = 0., 0.
                    sigTot, sigTotErr2 = 0., 0.
                    for reco in recoChans:
                        hpphm = 'hpp{0}'.format(modeMap[mode][0])
                        hpphmm = 'hpp{0}hmm{1}'.format(modeMap[mode][0],modeMap[mode][1])
                        # background
                        #bg,bgErr = getBackgroundCount(counters,'optimize/{0}/{1}/{2}/{3}/{4}'.format(optVar,optVal,mass,hpphm if args.analysis=='Hpp3l' else hpphmm ,reco),datadriven=reco.count('t')>=2)
                        bg,bgErr = getBackgroundCount(counters,'optimize/{0}/{1}/{2}/{3}/{4}'.format(optVar,optVal,mass,hpphm if args.analysis=='Hpp3l' else hpphmm ,reco),datadriven=True)
                        bgTot += bg
                        bgTotErr2 += bgErr**2
                        # signal
                        proc = signalsAP[0] if args.analysis=='Hpp3l' else signalsPP[0]
                        sig = 0.
                        sigErr2 = 0.
                        nl = 3 if args.analysis=='Hpp3l' else 4
                        for gen in genRecoMap:
                            if len(gen)!=nl: continue # 3 for AP, 4 for PP
                            if reco not in genRecoMap[gen]: continue
                            value,err = getCount(counters,proc,'optimize/{0}/{1}/{2}/{3}/{4}/gen_{5}'.format(optVar,optVal,mass,hpphm if args.analysis=='Hpp3l' else hpphmm ,reco,gen))
                            scale = scales[mode].scale_Hpp3l(gen[:2],gen[2:]) if args.analysis=='Hpp3l' else scales[mode].scale_Hpp4l(gen[:2],gen[2:])
                            sig += scale*value
                            sigErr2 += (scale*err)**2
                        sigErr = sigErr2**0.5
                        sigTot += sig
                        sigTotErr2 += sigErr2
                    bgTotErr = bgTotErr2**0.5
                    if bgTot < bgTotErr: bgTot = bgTotErr
                    sigTotErr = sigTotErr2**0.5
                    sig = (sigTot, sigTotErr)
                    bg = (bgTot, bgTotErr)
                    sob = sOverB(sig,bg)
                    pois = poissonSignificance(sig,bg)
                    poisErr = poissonSignificanceWithError(sig,bg)
                    asimov = asimovSignificance(sig,bg)
                    asimovErr = asimovSignificanceWithError(sig,bg)
                    print mode, mass, optVar, optVal, sigTot, bgTot, sob, pois, poisErr, asimov, asimovErr
                    allSOverB[optVal] = sob
                    allPois[optVal] = pois
                    allPoisErr[optVal] = poisErr
                    allAsimov[optVal] = asimov
                    allAsimovErr[optVal] = asimovErr
                    allBg[optVal] = bg
                    allSig[optVal] = sig
                bestSOverB = max(allSOverB.iteritems(), key=operator.itemgetter(1))[0]
                print mode, mass, optVar, 'best sOverB', bestSOverB
                bestPois = max(allPoisErr.iteritems(), key=operator.itemgetter(1))[0] 
                print mode, mass, optVar, 'best poisson significance', bestPois
                bestAsimov = max(allAsimovErr.iteritems(), key=operator.itemgetter(1))[0] 
                print mode, mass, optVar, 'best asimov significance', bestAsimov
                values[mode][mass][optVar] = {
                    'sOverB': allSOverB,
                    'pois': allPois,
                    'poisErr': allPoisErr,
                    'asimov': allAsimov,
                    'asimovErr': allAsimovErr,
                    'sig': allSig,
                    'bg': allBg,
                    'bestSOverB': bestSOverB,
                    'bestPois': bestPois,
                    'bestAsimov': bestAsimov,
                }

    # write values to file
    dumpResults(values,args.analysis,'optimization_{0}'.format(args.variable))

    for mode in modes:
        for mass in masses:
            best = values[mode][mass][args.variable]
            print mode, mass, args.variable, 'sOverB', best['bestSOverB'], 'poisson', best['bestPois'], 'asimov', best['bestAsimov']

if __name__ == "__main__":
    status = main()
    sys.exit(status)
