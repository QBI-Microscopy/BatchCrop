import importlib
import logging
import threading
from glob import iglob
from logging.handlers import RotatingFileHandler
from multiprocessing import freeze_support
from os import access, R_OK, mkdir
from os.path import join, dirname, exists, split, expanduser

import wx
import yaml

from autoanalysis.db.dbquery import DBI
FORMAT = '|%(thread)d |%(filename)s |%(funcName)s |%(lineno)d ||%(message)s||'
# Required for dist
freeze_support()
# Define notification event for thread completion
EVT_RESULT_ID = wx.NewId()
EVT_DATA_ID = wx.NewId()
# global logger
logger = logging.getLogger()


def EVT_RESULT(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_RESULT_ID, func)


def EVT_DATA(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_DATA_ID, func)


class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""

    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data


class DataEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""

    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_DATA_ID)
        self.data = data


def CheckFilenames(filenames, configfiles):
    """
    Check that filenames are appropriate for the script required
    :param filenames: list of full path filenames
    :param configfiles: matching filename for script as in config
    :return: filtered list
    """
    newfiles = {k: [] for k in filenames.keys()}
    for conf in configfiles:
        # if conf.startswith('_'):
        #     conf = conf[1:]
        for group in filenames.keys():
            for f in filenames[group]:
                parts = split(f)
                if conf in parts[1] or conf[1:] in parts[1]:
                    newfiles[group].append(f)
                elif conf.startswith('_'):
                    c = conf[1:]
                    newfiles[group] = newfiles[group] + [y for y in
                                                         iglob(join(parts[0], '**', '*' + c), recursive=True)]
                else:
                    # extract directory and seek files
                    newfiles[group] = newfiles[group] + [y for y in iglob(join(parts[0], '**', conf), recursive=True)]

    # if self.filesIn is not None:
    #     checkedfilenames = CheckFilenames(self.filenames, self.filesIn)
    #     files = [f for f in checkedfilenames if self.controller.datafile in f]
    # else:
    #     files = self.filenames
    return newfiles


########################################################################

lock = threading.Lock()
event = threading.Event()
hevent = threading.Event()


####################################################################################################
class TestThread(threading.Thread):
    def __init__(self, controller, filenames, outputdir, output, processname, module, classname, config):
        """Init Worker Thread Class."""
        threading.Thread.__init__(self)
        self.controller = controller
        self.filenames = filenames
        self.output = output
        self.processname = processname
        self.module_name = module
        self.class_name = classname
        self.outputdir = outputdir
        self.config = config

    def run(self):
        i = 0
        try:
            event.set()
            lock.acquire(True)
            # Do work
            q = dict()
            files = self.filenames
            total_files = len(files)

            # Loop through each
            for i in range(total_files):
                tcount = ((i + 1) * 100) / total_files
                msg = "%s run: tcount=%d of %d (%d\%)" % (self.processname, i, total_files, tcount)
                print(msg)
                self.processData(files[i], q)

        except Exception as e:
            print(e)
        finally:
            print('Finished TestThread')
            # self.terminate()
            lock.release()
            event.clear()

    def processData(self, filename, q):
        """
        Activate filter process - multithreaded
        :param datafile:
        :param q:
        :return:
        """
        print("Process Data for file: ", filename)

        # create local subdir for output
        if self.output == 'individual':
            outputdir = join(dirname(filename), 'cropped')
            if not exists(outputdir):
                mkdir(outputdir)
        else:
            outputdir = self.outputdir
        # Instantiate module
        module = importlib.import_module(self.module_name)
        class_ = getattr(module, self.class_name)
        print('Filename: ', filename)
        mod = class_(filename, outputdir, sheet=self.config['SHEET'],
                     skiprows=self.config['SKIPROWS'],
                     headers=self.config['HEADERS'])
        print('Module instantiated: ', self.class_name)
        cfg = mod.getConfigurables()
        for c in cfg.keys():
            cfg[c] = self.controller.db.getConfigByName(self.controller.currentconfig, c)
            print("config set: ", cfg[c])
        mod.setConfigurables(cfg)
        if mod.data is not None:
            print("running mod ..")
            q[filename] = mod.run()
        else:
            q[filename] = None


####################################################################################################

class ProcessThread(threading.Thread):
    """Multi Worker Thread Class."""

    # ----------------------------------------------------------------------
    def __init__(self, controller, wxObject, modules, outputdir, filenames, row, processname, showplots):
        """Init Worker Thread Class."""
        threading.Thread.__init__(self)
        self.controller = controller
        self.config = self.controller.db.getConfig(self.controller.currentconfig)
        self.db = DBI(self.controller.configfile)
        self.wxObject = wxObject
        self.filenames = filenames
        self.output = outputdir
        self.row = row
        self.showplots = showplots
        self.processname = processname
        (self.module_name, self.class_name) = modules
        logger = logging.getLogger(processname)
        # self.start()  # start the thread

    # ----------------------------------------------------------------------
    def run(self):
        i = 0
        total_files = 0
        try:
            event.set()
            lock.acquire(True)
            q = dict()
            # connect to db
            self.db.getconn()
            if isinstance(self.filenames, dict):
                batch = True
                total_files = len(self.filenames) - 1
                i = 0
                for group in self.filenames.keys():
                    if group == 'all' or len(self.filenames[group]) <= 0:
                        continue
                    tcount = (i + 1 / total_files) * 100
                    msg = "PROCESS THREAD (batch):%s run: tcount=%d of %d (%d percent)" % (
                    self.processname, i + 1, total_files, tcount)
                    print(msg)
                    logger.info(msg)
                    # TODO fix this
                    wx.PostEvent(self.wxObject, ResultEvent((tcount, self.row, i + 1, total_files, self.processname)))
                    self.processBatch(self.filenames[group], q, group)
                    i += 1

            else:
                batch = False
                files = self.filenames
                total_files = len(files)
                for i in range(total_files):
                    tcount = (i + 1 / total_files) * 100
                    msg = "PROCESS THREAD: %s run: tcount=%d of %d (%d percent)" % (
                    self.processname, i + 1, total_files, tcount)
                    print(msg)
                    logger.info(msg)
                    wx.PostEvent(self.wxObject, ResultEvent((tcount, self.row, i + 1, total_files, self.processname)))
                    self.processData(files[i], q)

            wx.PostEvent(self.wxObject, ResultEvent((100, self.row, total_files, total_files, self.processname)))
        except Exception as e:
            wx.PostEvent(self.wxObject, ResultEvent((-1, self.row, i + 1, total_files, self.processname)))
            logging.error(e)
        finally:
            logger.info('Finished ProcessThread')
            # self.terminate()
            lock.release()
            event.clear()
            # connect to db
            self.db.closeconn()

    # ----------------------------------------------------------------------
    def processData(self, filename, q):
        """
        Run module here - can modify according to class if needed
        :param filename: data file to process
        :param q: queue for results
        :return:
        """
        logger.info("Process Data with file: %s", filename)
        # create local subdir for output
        if self.output == 'individual':
            inputdir = dirname(filename)
            if 'cropped' in inputdir:
                outputdir = inputdir
            else:
                outputdir = join(inputdir, 'cropped')
            if not exists(outputdir):
                mkdir(outputdir)
        else:
            outputdir = self.output
        # Instantiate module
        module = importlib.import_module(self.module_name)
        class_ = getattr(module, self.class_name)
        mod = class_(filename, outputdir, showplots=self.showplots)
        # Load all params required for module - get list from module
        cfg = mod.getConfigurables()
        for c in cfg.keys():
            cfg[c] = self.db.getConfigByName(self.controller.currentconfig, c)
            msg = "Process Data: config set: %s=%s" % (c, str(cfg[c]))
            print(msg)
            logger.debug(msg)
        mod.setConfigurables(cfg)
        if mod.data is not None:
            q[filename] = mod.run()
        else:
            q[filename] = None

    def processBatch(self, filelist, q, group=None):
        """
        Run module here - can modify according to class if needed
        :param filelist: data file to process
        :param q: queue for results
        :return:
        """
        logger.info("Process Batch with filelist: %d", len(filelist))
        outputdir = self.output

        # Instantiate module
        module = importlib.import_module(self.module_name)
        class_ = getattr(module, self.class_name)
        mod = class_(filelist, outputdir, showplots=self.showplots)
        # Load all params required for module - get list from module
        cfg = mod.getConfigurables()
        for c in cfg.keys():
            cfg[c] = self.db.getConfigByName(self.controller.currentconfig, c)
            msg = "Process Batch: config set: %s=%s" % (c, str(cfg[c]))
            logger.debug(msg)
        mod.setConfigurables(cfg)
        if group is not None:
            mod.prefix = group
            q[group] = mod.run()
        else:
            q[mod.base] = mod.run()

    # ----------------------------------------------------------------------
    def terminate(self):
        logger.info("Terminating Filter Thread")
        self.terminate()


########################################################################

class Controller():
    def __init__(self, configfile, configID, processfile):
        self.logger = self.loadLogger()
        self.processfile = processfile
        self.cmodules = self.loadProcesses()
        self.configfile = configfile
        self.currentconfig = configID  # multiple configs possible
        # connect to db
        self.db = DBI(configfile)
        self.db.getconn()

    def loadProcesses(self):
        pf = None
        try:
            pf = open(self.processfile, 'rb')
            self.processes = yaml.load(pf)
            cmodules = {}
            for p in self.processes:
                msg = "Controller:LoadProcessors: loading %s=%s" % (p, self.processes[p]['caption'])
                logging.debug(msg)
                module_name = self.processes[p]['modulename']
                class_name = self.processes[p]['classname']
                cmodules[p] = (module_name, class_name)
            return cmodules
        except Exception as e:
            raise e
        finally:
            if pf is not None:
                pf.close()

    FORMAT = '[ %(asctime)s %(levelname)-4s ]|%(threadName)-9s |%(filename)s |%(funcName)s |%(lineno)d ||%(message)s||'
    #FORMAT_0 ='[ %(asctime)s %(levelname)-4s ] (%(threadName)-9s) %(message)s'
    def loadLogger(self, outputdir=None, expt=''):
        #### LoggingConfig
        logger.setLevel(logging.INFO)
        homedir = expanduser("~")
        if outputdir is not None and access(outputdir, R_OK):
            homedir = outputdir
        if len(expt) > 0:
            expt = expt + "_"
        if not access(join(homedir, "logs"), R_OK):
            mkdir(join(homedir, "logs"))
        self.logfile = join(homedir, "logs", expt + 'slidecrop.log')
        handler = RotatingFileHandler(filename=self.logfile, maxBytes=10000000, backupCount=10)
        formatter = logging.Formatter(FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    # ----------------------------------------------------------------------
    # def loadConfig(self, config=None):
    #     """
    #     Load from config file or config object
    #     :param config:
    #     :return:
    #     """
    #     try:
    #         if config is not None and isinstance(config, ConfigObj):
    #             logger.info("Loading config obj:%s", config.filename)
    #         elif isinstance(config, str) and access(config, R_OK):
    #             logger.info("Loading config from file:%s", config)
    #             config = ConfigObj(config)
    #         else:
    #             logger.warning('No config file found')
    #             config = ConfigObj()
    #
    #     except IOError as e:
    #         logging.error(e)
    #     except ValueError as e:
    #         logging.error(e)
    #
    #     return config

    # ----------------------------------------------------------------------
    def RunCompare(self, wxGui, indirs, outputdir, prefixes, searchtext):
        """
        Comparison of groups
        :param wxGui:
        :param indirs:
        :param outputdir:
        :param prefixes:
        :param searchtext:
        :return:
        """
        pass

    # ----------------------------------------------------------------------
    def RunProcess(self, wxGui, process, outputdir, filenames, row, showplots=False):
        """
        Instantiate Thread with type for Process
        :param wxGui:
        :param filenames:
        :param type:
        :param row:
        :return:
        """

        type = self.processes[process]['href']
        processname = self.processes[process]['caption']
        filesIn = []
        for f in self.processes[process]['filesin'].split(", "):
            fin = self.db.getConfigByName(self.currentconfig, f)
            if fin is not None:
                filesIn.append(fin)
            else:
                filesIn.append(f)
        filenames = CheckFilenames(filenames, filesIn)
        # filesout = self.processes[process]['filesout'] #TODO link up with module config?
        # suffix = self.db.getConfigByName(self.currentconfig,filesout)
        if self.processes[process]['output'] == 'individual':
            outputdir = self.processes[process]['output']
            filenames = filenames['all']

        if len(filenames) > 0:
            logger.info("Load Process Threads: %s [row: %d]", type, row)
            wx.PostEvent(wxGui, ResultEvent((0, row, 0, len(filenames), processname)))
            t = ProcessThread(self, wxGui, self.cmodules[process], outputdir, filenames, row, processname, showplots)
            t.start()
            logger.info("Running Thread: %s", type)
        else:
            logger.error("No files to process")
            raise ValueError("No matched files to process")

    # ----------------------------------------------------------------------


    def shutdown(self):
        logger.info('Close extra thread')
        t = threading.current_thread()
        # print("Thread tcounter:", threading.main_thread())
        if t != threading.main_thread() and t.is_alive():
            logger.info('Shutdown: closing %s', t.getName())
            t.terminate()
