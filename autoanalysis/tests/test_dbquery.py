import unittest2 as unittest

from autoanalysis.resources.dbquery import DBI


class TestDBquery(unittest.TestCase):
    def setUp(self):
        self.dbi = DBI(test=True)
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

    def test_getCaptions(self):
        data = self.dbi.getCaptions()
        expected = 0
        print('Captions: ', data)
        self.assertIsNotNone(data)
        self.assertGreater(len(data), expected)

    def test_getRefs(self):
        data = self.dbi.getRefs()
        expected = 0
        print('Refs: ', data)
        self.assertIsNotNone(data)
        self.assertGreater(len(data), expected)

    def test_getDescription(self):
        ref = 'Crop Slide into Images'
        data = self.dbi.getDescription(ref)
        expected = 0
        print('Description: ', data)
        self.assertIsNotNone(data)
        self.assertGreater(len(data), expected)

    def test_getCaption(self):
        ref = 'crop'
        data = self.dbi.getCaption(ref)
        expected = 0
        print('Caption: ', data)
        self.assertIsNotNone(data)
        self.assertGreater(len(data), expected)

    def test_getProcessModule(self):
        ref = 'crop'
        data = self.dbi.getProcessModule(ref)
        expected = 0
        print('Module: ', data)
        self.assertIsNotNone(data)
        self.assertGreater(len(data), expected)

    def test_getProcessClass(self):
        ref = 'crop'
        data = self.dbi.getProcessClass(ref)
        expected = 0
        print('Class: ', data)
        self.assertIsNotNone(data)
        self.assertGreater(len(data), expected)
