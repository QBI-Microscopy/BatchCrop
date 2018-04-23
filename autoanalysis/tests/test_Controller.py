import importlib
from os.path import join

import unittest2 as unittest

from autoanalysis.controller import Controller, TestThread
from autoanalysis.resources.dbquery import DBI


class TestController(unittest.TestCase): #TODO: REWRITE FOR SLIDE CROPPER
    def setUp(self):
        self.resourcesdir = join('..','resources')
        self.processfile = join(self.resourcesdir, 'processes_test.yaml')
        self.configfile = join(self.resourcesdir, 'autoconfig_test.db')
        self.dbi = DBI(self.configfile)
        self.dbi.getconn()
        self.currentconfig = 'test'
        self.controller = Controller(self.configfile, self.currentconfig, self.processfile)
        # TEST DATA
        self.datafile = "D:\\Data\\Csv\\input\\control\\Brain10_Image.csv"
        self.outputdir = "D:\\Data\\Csv\\output"
        self.testcolumn = 'Count_ColocalizedGAD_DAPI_Objects'

    def tearDown(self):
        self.dbi.closeconn()

    def test_ProcessInfo(self):
        self.assertNotEqual(self.controller,None)
        for p in self.controller.processes:
            print("Process: ", p, ":", self.controller.processes[p]['caption'])
        self.assertEqual('1. Filter Data',self.controller.processes['process1']['caption'])

    def test_Modules(self):
        self.assertNotEqual(self.controller, None)
        for p in self.controller.cmodules.keys():
            print(p)
            print("Module:",self.controller.cmodules[p][0])
            print("Class:", self.controller.cmodules[p][1])
        self.assertEqual('AutoFilter', self.controller.processes['process1']['classname'])

    def test_ModuleClass(self):
        testprocess = 'process1'
        module_name = self.controller.processes[testprocess]['modulename']
        class_name = self.controller.processes[testprocess]['classname']
        module = importlib.import_module(module_name)
        class_ = getattr(module, class_name)
        mod = class_(self.datafile,self.outputdir)
        self.assertTrue(isinstance(mod, class_)) #class instantiated
        self.assertGreater(len(mod.data),0) #data loaded

    def test_RunModuleClass_Simple(self):
        testprocess = 'process1'
        module_name = self.controller.processes[testprocess]['modulename']
        class_name = self.controller.processes[testprocess]['classname']
        module = importlib.import_module(module_name)
        class_ = getattr(module, class_name)
        #Instantiate FilterClass
        mod = class_(self.datafile,self.outputdir, sheet=0,
                     skiprows=0,
                     headers=0)
        # set vars manually
        mod.column = self.testcolumn
        mod.outputallcolumns = True
        mod.minlimit = 20
        mod.maxlimit = 80
        #Run process
        mod.run()


    def test_RunModuleClass_Complex(self):
        testprocess = 'process1'
        module_name = self.controller.processes[testprocess]['modulename']
        class_name = self.controller.processes[testprocess]['classname']
        module = importlib.import_module(module_name)
        class_ = getattr(module, class_name)
        #Instantiate FilterClass
        mod = class_(self.datafile,self.outputdir)
        cfg = mod.getConfigurables()
        for c in cfg.keys():
            print("config: ",c)
            cfg[c] = self.dbi.getConfigByName(self.currentconfig,c)
            print("config set: ", cfg[c])
        mod.setConfigurables(cfg)
        self.assertEqual(mod.column,self.testcolumn)
        mod.run()

    def test_runProcessThread(self):
        testprocess = 'process1'
        type = self.controller.processes[testprocess]['href']
        self.assertEqual(type,'filter')
        output= self.controller.processes[testprocess]['output']
        processname = self.controller.processes[testprocess]['caption']
        module_name = self.controller.processes[testprocess]['modulename']
        class_name = self.controller.processes[testprocess]['classname']
        config = self.controller.db.getConfig(self.currentconfig)
        # Run Thread
        t = TestThread(self.controller, self.datafile,self.outputdir,output, processname, module_name,class_name,config)
        t.start()
        print("Running Thread - loaded: ", type)
