#!/usr/bin/env python
'''
Script to merge split jobs from farmout for flat and projections.
'''
import argparse
import glob
import os
import sys
import logging
from DevTools.Utilities.utilities import runCommand

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Copy flat histograms from directory.')

    parser.add_argument('inputFiles',type=str,nargs='*',default=[],help='List of root files.')
    parser.add_argument('--flat',type=str,default='flat.root',help='Destination flat file.')
    parser.add_argument('--projection',type=str,default='projection.root',help='Destination projection file.')

    args = parser.parse_args(argv)

    return args


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = parse_command_line(argv)

    if 'INPUT' in os.environ and 'OUTPUT' in os.environ:
        inputFileList = os.environ['INPUT']
        outputFile = os.environ['OUTPUT']
        with open(inputFileList,'r') as f:
            args.inputFiles = [x.strip() for x in f.readlines()]
        args.flat = outputFile
        args.projection = outputFile[:-5] + '_projection.root'

    if not args.inputFiles:
        return 0


    flats = [x for x in args.inputFiles if '_projection.root' not in x]
    projs = [x for x in args.inputFiles if '_projection.root' in x]
    if flats:
        command = 'hadd -f {0} {1}'.format(args.flat,' '.join(flats))
        os.system(command)
        #runCommand(command)
    if projs:
        command = 'hadd -f {0} {1}'.format(args.projection,' '.join(projs))
        os.system(command)
        #runCommand(command)


if __name__ == "__main__":
    status = main()
    sys.exit(status)

