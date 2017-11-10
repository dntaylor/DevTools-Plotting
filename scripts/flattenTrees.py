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

from DevTools.Plotter.histParams import getHistParams, getHistSelections, getProjectionParams
from DevTools.Plotter.utilities import getNtupleDirectory, getTreeName
from DevTools.Plotter.FlattenTree import FlattenTree

try:
    from DevTools.Utilities.MultiProgress import MultiProgress
    from progressbar import ProgressBar, ETA, Percentage, Bar, SimpleProgress
    hasProgress = True
except:
    hasProgress = False

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def flatten(analysis,sample,**kwargs):
    histParams = kwargs.pop('histParams',{})
    histSelections = kwargs.pop('histSelections',{})
    inputFileList = kwargs.pop('inputFileList','')
    outputFile = kwargs.pop('outputFile','')
    shift = kwargs.pop('shift','')
    countOnly = kwargs.pop('countOnly',False)
    njobs = kwargs.pop('njobs',1)
    job = kwargs.pop('job',0)
    multi = kwargs.pop('multi',False)
    useProof = kwargs.pop('useProof',False)
    if hasProgress and multi:
        pbar = kwargs.pop('progressbar',ProgressBar(widgets=['{0}: '.format(sample),' ',SimpleProgress(),' histograms ',Percentage(),' ',Bar(),' ',ETA()]))
    else:
        pbar = None

    if outputFile:
        flat = outputFile
        proj = outputFile.replace('.root','_projection.root')
        flattener = FlattenTree(analysis,sample,inputFileList=inputFileList,flat=flat,proj=proj,shift=shift,countOnly=countOnly,useProof=useProof)
    else:
        flattener = FlattenTree(analysis,sample,inputFileList=inputFileList,shift=shift,countOnly=countOnly,useProof=useProof)

    for histName, params in histParams.iteritems():
        flattener.addHistogram(histName,**params)

    for selName, sel in histSelections.iteritems():
        if sel: flattener.addSelection(selName,**sel['kwargs'])

    flattener.flattenAll(progressbar=pbar,njobs=njobs,job=job,multi=multi)

def getSampleDirectories(analysis,sampleList):
    source = getNtupleDirectory(analysis)
    directories = []
    for s in sampleList:
        for d in glob.glob(os.path.join(source,s)):
            directories += [d]
    return directories

def getSelectedHistParams(analysis,hists,sample,**kwargs):
    allHistParams = getHistParams(analysis,sample,**kwargs)
    params = {}
    params.update(allHistParams)
    if 'all' in hists: return params
    selectedHistParams = {}
    for h in hists:
        if h in allHistParams: selectedHistParams[h] = allHistParams[h]
    return selectedHistParams

def getSelectedHistSelections(analysis,sels,sample,**kwargs):
    allHistSelections = getHistSelections(analysis,sample,**kwargs)
    if 'all' in sels: return allHistSelections
    selectedHistSelections = {}
    for s in sels:
        if s in allHistSelections: selectedHistSelections[s] = allHistSelections[s]
    return selectedHistSelections

def getSelectedProjections(analysis,projs,sample,**kwargs):
    allProjections = getProjectionParams(analysis,sample,**kwargs)
    if 'all' in projs: return allProjections
    selectedProjections = {}
    for p in projs:
        if p in allProjections: selectedProjections[p] = allProjections[p]
    return allProjections

def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Flatten Tree')

    parser.add_argument('analysis', type=str, help='Analysis to process')
    parser.add_argument('shift', type=str, default='', nargs='?', help='Shift to apply to scale factors')
    parser.add_argument('countOnly', type=int, default=0, nargs='?', help='Only do counts, no distributions')
    parser.add_argument('--samples', nargs='+', type=str, default=['*'], help='Samples to flatten. Supports unix style wildcards.')
    parser.add_argument('--hists', nargs='+', type=str, default=['all'], help='Histograms to flatten.')
    parser.add_argument('--selections', nargs='+', type=str, default=['all'], help='Selections to flatten.')
    parser.add_argument('--channels', nargs='+', type=str, default=['all'], help='Channels to project.')
    parser.add_argument('--skipProjection', action='store_true', help='Skip projecting')
    #parser.add_argument('--useProof', action='store_true', help='Use PROOF')
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
            if '.root' in jobparams[-1]:
                sample = jobparams[-2]
                njobs = 1
                job = 0
            else:
                sample = jobparams[-4]
                njobs = int(jobparams[-2])
                job = int(jobparams[-1])
        grid = True
    else:
        directories = getSampleDirectories(args.analysis,args.samples)
        logging.info('Will flatten {0} samples'.format(len(directories)))

    if grid:
        histParams = getSelectedHistParams(args.analysis,args.hists,sample,shift=args.shift,countOnly=args.countOnly)
        histSelections = getSelectedHistSelections(args.analysis,args.selections,sample,shift=args.shift,countOnly=args.countOnly)
        flatten(args.analysis,
                sample,
                histParams=histParams,
                histSelections=histSelections,
                #inputFileList=inputFileList,
                outputFile=outputFile,
                shift=args.shift,
                countOnly=args.countOnly,
                njobs=njobs,
                job=job,
                )
    elif args.j>1 and hasProgress:
        multi = MultiProgress(args.j)
        for directory in directories:
            sample = directory.split('/')[-1]
            if sample.endswith('.root'): sample = sample[:-5]
            histParams = getSelectedHistParams(args.analysis,args.hists,sample,shift=args.shift,countOnly=args.countOnly)
            histSelections = getSelectedHistSelections(args.analysis,args.selections,sample,shift=args.shift,countOnly=args.countOnly)
            multi.addJob(sample,flatten,args=(args.analysis,sample,),kwargs={'histParams':histParams,'histSelections':histSelections,'shift':args.shift,'countOnly':args.countOnly,'multi':True,})
        multi.retrieve()
    else:
        for directory in directories:
            sample = directory.split('/')[-1]
            if sample.endswith('.root'): sample = sample[:-5]
            histParams = getSelectedHistParams(args.analysis,args.hists,sample,shift=args.shift,countOnly=args.countOnly)
            histSelections = getSelectedHistSelections(args.analysis,args.selections,sample,shift=args.shift,countOnly=args.countOnly)
            flatten(args.analysis,
                    sample,
                    histParams=histParams,
                    histSelections=histSelections,
                    shift=args.shift,
                    countOnly=args.countOnly,
                    multi=False,
                    #useProof=args.useProof,
                    )

    logging.info('Finished')

if __name__ == "__main__":
    status = main()
    sys.exit(status)

