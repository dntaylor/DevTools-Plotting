#!/usr/bin/env python
'''
Script to copy flat histograms and projections from output of farmout.
'''
import argparse
import glob
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(asctime)s.%(msecs)03d %(levelname)s %(name)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def parse_command_line(argv):
    parser = argparse.ArgumentParser(description='Copy flat histograms from directory.')

    parser.add_argument('input',type=str,help='Input top-level directory to copy, each subdirectory must have two files, the flat and projection.')
    parser.add_argument('flat',type=str,help='Destination directory to copy flat files into.')
    parser.add_argument('projection',type=str,help='Destination directory to copy projection files into.')

    args = parser.parse_args(argv)

    return args


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = parse_command_line(argv)

    os.system('mkdir -p {0}'.format(args.flat))
    os.system('mkdir -p {0}'.format(args.projection))

    alldirs = sorted(glob.glob('{0}/*'.format(args.input)))

    for i,directory in enumerate(alldirs):
        if not os.path.isdir(directory): continue
        destname = os.path.basename(os.path.normpath(directory))
        logging.info('Copying sample {0} of {1}: {2}'.format(i+1,len(alldirs),destname))
        files = glob.glob('{0}/*.root'.format(directory))
        flats = [x for x in files if '_projection.root' not in x]
        projs = [x for x in files if '_projection.root' in x]
        if flats:
            flatsource = flats[0]
            flatfile = '{0}/{1}.root'.format(args.flat,destname)
            command = 'cp {0} {1}'.format(flatsource,flatfile)
            os.system(command)
        if projs:
            projsource = projs[0]
            projfile = '{0}/{1}.root'.format(args.projection,destname)
            command = 'cp {0} {1}'.format(projsource,projfile)
            os.system(command)


if __name__ == "__main__":
    status = main()
    sys.exit(status)

