#!/usr/bin/env python
import os
import sys
import glob
import logging
import argparse
import re
from multiprocessing import Pool
from copy import deepcopy

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True

from DevTools.Plotter.utilities import getNtupleDirectory, getTreeName
from DevTools.Plotter.Hpp3lSkimmer import Hpp3lSkimmer
from DevTools.Plotter.Hpp4lSkimmer import Hpp4lSkimmer

try:
    from DevTools.Utilities.MultiProgress import MultiProgress
    from progressbar import ProgressBar, ETA, Percentage, Bar, SimpleProgress
    hasProgress = True
except:
    hasProgress = False

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def skim(analysis,sample,**kwargs):
    inputFileList = kwargs.pop('inputFileList','')
    outputFile = kwargs.pop('outputFile','')
    shift = kwargs.pop('shift','')
    multi = kwargs.pop('multi',False)
    if hasProgress and multi:
        pbar = kwargs.pop('progressbar',ProgressBar(widgets=['{0}: '.format(sample),' ',SimpleProgress(),' events ',Percentage(),' ',Bar(),' ',ETA()]))
    else:
        pbar = None

    skimMap = {
        'Hpp3l': Hpp3lSkimmer,
        'Hpp4l': Hpp4lSkimmer,
        'DijetFakeRate': DijetFakeRateSkimmer,
        'WTauFakeRate': WTauFakeRateSkimmer,
    }
    if analysis not in skimMap:
        logging.warning('No skimmer found for analysis {0}'.format(analysis))
        return

    if outputFile:
        skimmer = skimMap[analysis](sample,inputFileList=inputFileList,outputFile=outputFile,shift=shift,progressbar=pbar)
    else:
        skimmer = skimMap[analysis](sample,inputFileList=inputFileList,shift=shift,progressbar=pbar)

    skimmer.skim()

def getSampleDirectories(analysis,sampleList):
    source = getNtupleDirectory(analysis)
    directories = []
    for s in sampleList:
        for d in glob.glob(os.path.join(source,s)):
            directories += [d]
    return directories

def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Flatten Tree')

    parser.add_argument('analysis', type=str, choices=['WZ','ZZ','DY','Charge','TauCharge','Hpp3l','Hpp4l','Electron','Muon','Tau','DijetFakeRate','WTauFakeRate','WFakeRate'], help='Analysis to process')
    parser.add_argument('shift', type=str, default='', nargs='?', help='Shift to apply to scale factors')
    parser.add_argument('--samples', nargs='+', type=str, default=['*'], help='Samples to flatten. Supports unix style wildcards.')
    parser.add_argument('-j',type=int,default=1,help='Number of cores to use')

    return parser.parse_args(argv)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = parse_command_line(argv)

    logging.info('Preparing to flatten {0}'.format(args.analysis))

    grid = False
    if 'INPUT' in os.environ and 'OUTPUT' in os.environ:
        inputFileList = os.environ['INPUT']
        outputFile = os.environ['OUTPUT']
        # figureout the sample
        with open(inputFileList,'r') as f:
            inputfiles = [x.strip() for x in f.readlines()]
            jobparams = inputfiles[0].split('/')
            sample = jobparams[-2]
        grid = True
    else:
        directories = getSampleDirectories(args.analysis,args.samples)
        logging.info('Will flatten {0} samples'.format(len(directories)))

    if grid:
        skim(args.analysis,
             sample,
             outputFile=outputFile,
             shift=args.shift,
             )
    elif args.j>1 and hasProgress:
        multi = MultiProgress(args.j)
        for directory in directories:
            sample = directory.split('/')[-1]
            if sample.endswith('.root'): sample = sample[:-5]
            multi.addJob(sample,skim,args=(args.analysis,sample,),kwargs={'shift':args.shift,'multi':True,})
        multi.retrieve()
    else:
        for directory in directories:
            sample = directory.split('/')[-1]
            if sample.endswith('.root'): sample = sample[:-5]
            skim(args.analysis,
                 sample,
                 shift=args.shift,
                 multi=False,
                 )

    logging.info('Finished')

if __name__ == "__main__":
    status = main()
    sys.exit(status)

