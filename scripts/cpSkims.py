#!/usr/bin/env python
'''
Script to copy flat histograms and projections from output of farmout.
'''
import argparse
import glob
import os
import sys
import logging
from DevTools.Utilities.utilities import runCommand, python_mkdir

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Copy skims from directory.')

    parser.add_argument('analysis',type=str,help='Analysis of skims')
    parser.add_argument('input',type=str,help='Input top-level directory to copy, each subdirectory must have two files, the flat and projection.')

    args = parser.parse_args(argv)

    return args


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = parse_command_line(argv)

    jdir = 'jsons/{0}/skims'.format(args.analysis)
    pdir = 'pickles/{0}/skims'.format(args.analysis)
    python_mkdir(jdir)
    python_mkdir(pdir)


    alldirs = sorted(glob.glob('{0}/*'.format(args.input)))

    for i,directory in enumerate(alldirs):
        if not os.path.isdir(directory): continue
        destname = os.path.basename(os.path.normpath(directory))
        logging.info('Copying sample {0} of {1}: {2}'.format(i+1,len(alldirs),destname))
        files = glob.glob('{0}/*.root'.format(directory))
        jsons = [x for x in files if '.json' in x]
        pickles = [x for x in files if '.pkl' in x]
        if jsons:
            jsonfile = '{0}/{1}.json'.format(jdir,destname)
            command = 'cp {0} {1}'.format(jsons[0],jsonfile)
            runCommand(command)
        if pickles:
            pklfile = '{0}/{1}.pkl'.format(pdir,destname)
            command = 'cp {0} {1}'.format(pickles[0],pklfile)
            runCommand(command)


if __name__ == "__main__":
    status = main()
    sys.exit(status)

