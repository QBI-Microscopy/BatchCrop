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

import argparse
from collections import OrderedDict
from glob import iglob
from os.path import join

DEBUG = 1

class FileUnarchiver():
    def __init__(self, inputfile, outputdir):
        """

        :param inputfiles: Assumes these are correct files - already filtered
        :param outputdir: not used - required for template module
        :param showplots:
        """
        self.data = inputfile
        print('FileUnarchiver: data=', self.data)


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
        try:
            print('Unarchiving file: ',self.data)
            fh = open(self.data, 'r')
            fh.close()
        except Exception as e:
            raise e


################################################################################
def create_parser():
    import sys

    parser = argparse.ArgumentParser(prog=sys.argv[0],
                                     description='''\
                Combines data from datafiles to output file

                 ''')
    parser.add_argument('--inputdir', action='store', help='Input directory',
                        default="D:\\Data\\MicroscopyData")

    return parser

###############################################################################
if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()
    inputdir = args.inputdir
    outputdir = inputdir
    # Get file list
    allfiles = [y for y in iglob(join(inputdir, '**','*.ims'), recursive=True)]
    for f in allfiles:
        batch = FileUnarchiver(f, outputdir)
        batch.run()
        print("Done")