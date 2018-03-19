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

class AutoBatch:
    def __init__(self, inputfiles, outputdir, showplots=False):
        """

        :param inputfiles: Assumes these are correct files - already filtered
        :param outputdir:
        :param showplots:
        """
        self.inputfiles = inputfiles
        self.base = commonpath(inputfiles)
        if len(outputdir) <=0:
            self.outputdir = self.base
        else:
            self.outputdir = outputdir
        self.showplots = showplots
        self.n = 1  # generating id
        self.prefix =''

    def getConfigurables(self):
        '''
        List of configurable parameters in order with defaults
        :return:
        '''
        cfg = OrderedDict()
        cfg['BATCH_COLUMN_NAMES']=[]
        cfg['BATCH_FILENAME']="BATCH.csv"
        return cfg

    def setConfigurables(self,cfg):
        if 'BATCH_COLUMN_NAMES' in cfg.keys() and cfg['BATCH_COLUMN_NAMES'] is not None:
            self.colnames = cfg['BATCH_COLUMN_NAMES'].split(',')
        else:
            self.colnames =[]
        if 'BATCH_FILENAME' in cfg.keys() and cfg['BATCH_FILENAME'] is not None:
            self.suffix = cfg['BATCH_FILENAME']
            if self.suffix.startswith('*'):
                self.suffix = self.suffix[1:]
        else:
            self.suffix ="BATCH.csv"


    def generateID(self, f,usefilenames=True):
        """
        Generate a unique ID for each file
        :param f: full path filename
        :param usefilenames: use base of filename
        :return: unique ID
        """
        # Generate unique cell ID
        (filename,ext) = splitext(basename(f))
        if len(self.prefix) > 0:
            prefix = self.prefix + "_"
        else:
            prefix = ''
        if usefilenames:
            cell = prefix + filename
        else:
            cell = prefix + 'c{0:03d}'.format(self.n)
            self.n += 1
        if DEBUG:
            print("Cellid=", cell)
        return cell

    def validHeader(self,colnames,df):
        """
        Check column names are in data files
        :param colname: array of colname/s
        :param df: data file as dataframe
        :return: true if present, false if not (all columns)
        """
        matches = []
        for col in colnames:
            matches.append(col in df.columns)
        if sum(matches)== len(colnames):
            rtn = True
        else:
            rtn = False
        return rtn

    def generatePlots(self,df, pfilename):
        if len(df)==1:
            df.plot()
        else:
            xi = [str(x) for x in range(len(df) + 1)]
            data = []
            title = 'Batch plots'
            for col in df.columns:
                data.append(Scatter(y=df[col], x=xi,name=col,mode='markers'))

            # Create plotly plot
            offline.plot({"data": data,
                          "layout": Layout(title=title,
                                           xaxis={'title': self.colnames},
                                           yaxis={'title': ''})},
                         filename=pfilename)

        return pfilename


    def run(self):
        """
        Combine data from columns specified into batch output file
        Include basic plot if showplots is flagged
        :param colname:
        :return: outputfilename
        """
        df = None
        if self.colnames is None:
            raise ValueError('No columns specified for data extraction')
        batchout = {}
        for f in self.inputfiles:
            bname = basename(f)
            if bname.endswith('.csv'):
                fid = self.generateID(bname)
                df = pd.read_csv(f)
                if self.validHeader(self.colnames, df):
                    data = [x[0] for x in df[self.colnames].get_values()]
                    batchout[fid] = data
        if len(batchout) > 0:
            df = pd.DataFrame.from_dict(batchout,orient='index').T.fillna('')
            #save to file
            fparts = [self.base.split(sep)[-1], self.suffix]
            if len(self.prefix) > 0:
                fparts = [self.prefix] + fparts
            outputfilename = join(self.outputdir, "_".join(fparts))
            df.to_csv(outputfilename,index=False)
            if self.showplots:
                plotfilename = outputfilename.replace('.csv','.html')
                self.generatePlots(df,plotfilename)
        return outputfilename

################################################################################
def create_parser():
    import sys

    parser = argparse.ArgumentParser(prog=sys.argv[0],
                                     description='''\
                Combines data from datafiles to output file

                 ''')
    parser.add_argument('--search', action='store', help='Search text of filename',
                        default='*Filtered.csv')
    parser.add_argument('--outputdir', action='store', help='Output directory (must exist)',default="D:\\Data\\Csv\\output")
    parser.add_argument('--inputdir', action='store', help='Input directory',
                        default="D:\\Data\\Csv\\input")
    parser.add_argument('--column', action='store', help='Column header/s to be combined',
                        default="Count_ColocalizedGAD_DAPI_Objects")
    parser.add_argument('--showplots', action='store_true', help='Display popup plots', default=True)

    return parser

###############################################################################
if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    datafile_searchtext = args.search
    outputdir = args.outputdir
    inputdir = args.inputdir
    showplots = True
    # inputfiles, outputdir, datafile_searchtext,showplots=False)
    allfiles = [y for y in iglob(join(inputdir, '**',datafile_searchtext), recursive=True)]

    for group in ['control','treatment1']:
        inputfiles = [f for f in allfiles if re.search(group, f, flags=re.IGNORECASE)]
        batch = AutoBatch(inputfiles, outputdir, showplots)
        batch.prefix = group
        cfg = batch.getConfigurables()
        cfg['BATCH_COLUMN_NAMES'] = args.column
        for c in cfg.keys():
            print("config set: ", c, "=", cfg[c])
        batch.setConfigurables(cfg)
        #Generate output file
        outputfilename = batch.run()
        print("Output: ", outputfilename)