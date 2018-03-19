import unittest2 as unittest
import argparse
from os.path import join
from os import access,R_OK
from autoanalysis.processmodules.Batch import AutoBatch, create_parser
from glob import iglob
import re

class TestBatch(unittest.TestCase):
    def setUp(self):
        parser = create_parser()
        self.args = parser.parse_args()
        allfiles = [y for y in iglob(join(self.args.inputdir, '**', self.args.search), recursive=True)]
        group = 'control'
        inputfiles = [f for f in allfiles if re.search(group, f, flags=re.IGNORECASE)]
        self.batch = AutoBatch(inputfiles, self.args.outputdir, self.args.showplots)
        self.batch.prefix = group

    def test_configurables(self):
        cfg = self.batch.getConfigurables()
        cfg['BATCH_COLUMN_NAMES'] = self.args.column
        for c in cfg.keys():
            print("config set: ", c, "=", cfg[c])
        self.batch.setConfigurables(cfg)
        expected = [self.args.column]
        self.assertEqual(expected,self.batch.colnames)


    def test_generateid(self):
        f = self.batch.inputfiles[0]
        expected = 'control_c001'
        data = self.batch.generateID(f, usefilenames=False)
        self.assertEqual(expected, data)

    def test_combinedata(self):
        cfg = self.batch.getConfigurables()
        cfg['BATCH_COLUMN_NAMES'] = self.args.column
        self.batch.setConfigurables(cfg)
        outputfile = self.batch.run()
        expected = 'BATCH'
        self.assertTrue(expected in outputfile)
