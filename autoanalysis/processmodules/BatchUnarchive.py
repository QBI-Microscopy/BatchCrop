# -*- coding: utf-8 -*-
"""
AutoBatch class
1. Reads in list of files from INPUTDIR
2. Matches files in list to searchtext (filenames)
3. Combines data from columns into single batch file with unique ids generated from files
4. Outputs to output directory as BATCH_filename_searchtext.csv or excel

Created on 19 Feb 2018

@author: Liz Cooper-Williams, QBI
"""

import logging
import re
from glob import iglob
from os import R_OK, access
from os.path import join, isdir, commonpath, commonprefix,sep, basename, splitext

from configobj import ConfigObj
from numpy import unique
import argparse
import pandas as pd
from plotly import offline
from plotly.graph_objs import Layout, Scatter
from collections import OrderedDict
DEBUG = 1

class FileUnarchiver():
    def __init__(self, inputfiles):
        """

        :param inputfiles: Assumes these are correct files - already filtered
        :param outputdir:
        :param showplots:
        """
        self.inputfiles = inputfiles


    def getConfigurables(self):
        '''
        List of configurable parameters in order with defaults
        :return:
        '''
        cfg = OrderedDict()

        return cfg

    def setConfigurables(self,cfg):
       pass



    def run(self):
        """
        Combine data from columns specified into batch output file
        Include basic plot if showplots is flagged
        :param colname:
        :return: outputfilename
        """

        for fname in self.inputfiles:
            print('Unarchiving file: ',fname)
            fh = open(fname, 'r')
            fh.close()


################################################################################
def create_parser():
    import sys

    parser = argparse.ArgumentParser(prog=sys.argv[0],
                                     description='''\
                Combines data from datafiles to output file

                 ''')
    parser.add_argument('--inputdir', action='store', help='Input directory',
                        default="D:\\Data\\Csv\\input")

    return parser

###############################################################################
if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    inputdir = args.inputdir
    showplots = True
    # inputfiles, outputdir, datafile_searchtext,showplots=False)
    allfiles = [y for y in iglob(join(inputdir, '**','*.ims'), recursive=True)]
    batch = FileUnarchiver(allfiles)
    rtn = batch.run()
    print("Done: ", rtn)