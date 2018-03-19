from os.path import join

import unittest2 as unittest

from autoanalysis.db.dbquery import DBI


class TestDBquery(unittest.TestCase):
    def setUp(self):
        configdb = join('..','resources', 'autoconfig_test.db')
        self.dbi = DBI(configdb)
        self.dbi.getconn()

    def tearDown(self):
        self.dbi.conn.close()

    def test_getConfig(self):
        configid = 'test'
        data = self.dbi.getConfig(configid)
        expected = 0
        self.assertGreater(len(data),expected)

    def test_getConfigALL(self):
        configid = 'test'
        data = self.dbi.getConfigALL(configid)
        expected = 0
        self.assertGreater(len(data),expected)

    def test_getConfigByName(self):
        group = 'test'
        test = 'BINWIDTH'
        expected = 20
        data = self.dbi.getConfigByName(group,test)
        self.assertEqual(int(data),expected)

    def test_getConfigByName_None(self):
        group = 'test'
        test = 'BINW'
        expected = None
        data = self.dbi.getConfigByName(group,test)
        self.assertEqual(data,expected)

    def test_getConfigIds(self):
        data = self.dbi.getConfigIds()
        print('IDS:', data)
        self.assertGreater(len(data),0)

    def test_updateConfig(self):
        configid='test'
        configlist = [('BINWIDTH',10,'test',"Bin width for histograms"),
                      ('COLUMN','TestData','test',"Column name for histograms"),
                      ('MINRANGE',0,'test',"Minimum range of histograms bins"),
                      ('MAXRANGE',100,'test',"Maximum range of histograms bins")]
        cnt = self.dbi.addConfig(configid,configlist)
        expected = len(configlist)
        self.assertEqual(expected,cnt)

    def test_updateConfig_Secondset(self):
        configid = 'test'
        configlist = [('BINWIDTH', 10, configid,"Bin width for histograms"),
                      ('COLUMN', 'TestData', configid,"Column name for histograms"),
                      ('MINRANGE', 0, configid,"Minimum range of histograms bins"),
                      ('MAXRANGE', 100, configid,"Maximum range of histograms bins")]
        cnt = self.dbi.addConfig(configid, configlist)
        expected = len(configlist)
        self.assertEqual(expected, cnt)

    def test_updateConfig_duplicate(self):
        configid='test'
        configlist = [('BINWIDTH', 20, 'test', "Bin width for histograms"),
                      ('COLUMN', 'TestData2', 'test', "Column name for histograms"),
                      ('MINRANGE', 5, 'test', "Minimum range of histograms bins"),
                      ('MAXRANGE', 50, 'test', "Maximum range of histograms bins")]
        cnt = self.dbi.addConfig(configid,configlist)
        expected = len(configlist)
        self.assertEqual(expected,cnt)