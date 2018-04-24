import importlib
import logging
import threading
import time
from logging.handlers import RotatingFileHandler
from multiprocessing import freeze_support
from os import access, R_OK, W_OK, mkdir
from os.path import join, expanduser, splitext, basename, split

import wx

from autoanalysis.resources.dbquery import DBI
from autoanalysis.utils import findResourceDir
from wx.lib.pubsub import pub as Publisher

#FORMAT = '|%(thread)d |%(filename)s |%(funcName)s |%(lineno)d ||%(message)s||'
FORMAT = '[ %(asctime)s %(levelname)-4s ]|%(threadName)-9s |%(filename)s |%(funcName)s |%(lineno)d ||%(message)s||'
    #FORMAT_0 ='[ %(asctime)s %(levelname)-4s ] (%(threadName)-9s) %(message)s'
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

###################################################################
class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""

    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data


class ImageCropFinishData(object):
    """ Simple encapsulation of data to be sent to the main GUI thread after an image has been cropped. """

    def __init__(self, filepath):
        """
        Constructor. 
        :param filepath: Filepath to folder with cropped outputs.  
        """
        self.filepath = filepath

    def __str__(self):
        return str(self.filepath)


class DataEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""

    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_DATA_ID)
        self.data = data


########################################################################

lock = threading.Lock()
event = threading.Event()
hevent = threading.Event()


####################################################################################################

class ProcessThread(threading.Thread):
    """Multi Worker Thread Class."""

    # ----------------------------------------------------------------------
    def __init__(self, wxObject, configid,processname,processmodule,processclass, outputdir, filename, row):
        """Init Worker Thread Class."""
        threading.Thread.__init__(self)
        # self.controller = controller
        self.configID = configid
        self.db = DBI()
        self.wxObject = wxObject
        self.filename = filename
        self.output = outputdir
        self.row = row
        #self.showplots = showplots
        self.processname = processname
        #self.module_name = processmodule
        #self.class_name = processclass
        logger = logging.getLogger(processname)
        # Instantiate module
        module = importlib.import_module(processmodule)
        self.class_ = getattr(module, processclass)
        # This is a slidecropperAPI class show plots is whether to show boxes
        self.mod = self.class_(filename, outputdir)



    # ----------------------------------------------------------------------
    def run(self):
        i = 0
        total_files = 0
        try:
            event.set()
            lock.acquire(True)
            q = dict()
            self.processData(self.filename, q)

            tcount = 150 #secs per file?use filesize
            ctr = 5

            while self.mod.isRunning():
                time.sleep(5)
                progress = 100 *(ctr/tcount)
                msg = "PROCESS THREAD: %s (%s) (%d percent)" % (self.processname, self.filename, progress)
                print(msg)
                logger.info(msg)
                #count, row, process, filename
                wx.PostEvent(self.wxObject, ResultEvent((progress, self.row, self.processname, self.filename)))
                ctr += 5
                #reset ??
                if ctr == tcount:
                    ctr = 5

            wx.PostEvent(self.wxObject, ResultEvent((100, self.row, self.processname, self.filename)))
        except Exception as e:
            wx.PostEvent(self.wxObject, ResultEvent((-1, self.row, self.processname, self.filename)))
        finally:

            logger.info('Finished ProcessThread')
            # self.terminate()
            lock.release()
            event.clear()


    # ----------------------------------------------------------------------
    def processData(self, filename, q):
        """
        Run module here - can modify according to class if needed
        :param filename: data file to process
        :param q: queue for results
        :return:
        """
        try:
            logger.info("PROCESSTHREAD:Process Data with file: %s", filename)

            # Load all configurable params required for module - get list from module
            cfg = self.mod.getConfigurables()
            self.db.connect()
            for c in cfg.keys():
                cfg[c] = self.db.getConfigByName(self.configID,c)
                msg = "PROCESSTHREAD:Process Data: config set: %s=%s" % (c, str(cfg[c]))
                print(msg)
                logger.debug(msg)
            self.db.closeconn()
            self.mod.setConfigurables(cfg)

            # run cropping process
            if self.mod.data is not None:
                print('PROCESSTHREAD: Module running')
                q[self.mod.data] =self.mod.run()
                # if self.showplots:
                #     newOutputDir= join(split(self.filenames[0])[0], mod.outputdir, basename(splitext(filename)[0]))
                #     print(newOutputDir)
                #     wx.PostEvent(self.wxObject, DataEvent((newOutputDir)))
                #     #Publisher.sendMessage("Image_Cropped_Finished", details = ImageCropFinishData(newOutputDir))
            else:
                print("no mod.data ERROR")
                q[self.mod.data] = None
        except Exception as e:
            print("ERROR in cropping", str(e))

    # def processBatch(self, filelist, q, group=None):
    #     """
    #     Run module here - can modify according to class if needed
    #     :param filelist: data file to process
    #     :param q: queue for results
    #     :return:
    #     """
    #     logger.info("Process Batch with filelist: %d", len(filelist))
    #     outputdir = self.output
    #
    #     # Instantiate module
    #     module = importlib.import_module(self.module_name)
    #     class_ = getattr(module, self.class_name)
    #     mod = class_(filelist, outputdir, showplots=self.showplots)
    #     # Load all params required for module - get list from module
    #     cfg = mod.getConfigurables()
    #     for c in cfg.keys():
    #         cfg[c] = self.db.getConfigByName(self.controller.currentconfig, c)
    #         msg = "Process Batch: config set: %s=%s" % (c, str(cfg[c]))
    #         logger.debug(msg)
    #     mod.setConfigurables(cfg)
    #     if group is not None:
    #         mod.prefix = group
    #         q[group] = mod.run()
    #         if mod.getConfigurables['SEND_TO_CROP_PANEL']:
    #             Publisher.sendMessage("Image_Cropped_Finished", ImageCropFinishData(mod.data))
    #             print("Publisher.sendMessage('Image_Cropped_Finished', ImageCropFinishData(mod.data))")
    #     else:
    #         q[mod.base] = mod.run()

    # ----------------------------------------------------------------------
    def terminate(self):
        logger.info("Terminating Filter Thread")
        self.terminate()


########################################################################

class Controller():
    def __init__(self):
        self.logfile = None
        self.logger = self.loadLogger()
        self.currentconfig = 'default'  # maybe future multiple configs possible
        # connect to db
        self.db = DBI()
        self.db.connect()



    def loadLogger(self, outputdir=None):
        #### LoggingConfig
        logger.setLevel(logging.INFO)
        homedir = expanduser("~")
        if outputdir is not None and access(outputdir, R_OK):
            homedir = outputdir

        logdir = join(homedir, '.qbi_apps','batchcrop',"logs")
        if not access(logdir, R_OK):
            if not access(join(homedir, '.qbi_apps'),W_OK):
                mkdir(join(homedir, '.qbi_apps'))
            if not access(join(homedir, '.qbi_apps','batchcrop'),W_OK):
                mkdir(join(homedir, '.qbi_apps','batchcrop'))
            mkdir(logdir)
        self.logfile = join(logdir, 'batchcrop.log')
        handler = RotatingFileHandler(filename=self.logfile, maxBytes=10000000, backupCount=10)
        formatter = logging.Formatter(FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    # ----------------------------------------------------------------------
    def RunProcess(self, wxGui, processref, outputdir, filenames):
        """

        :param wxGui:
        :param processref:
        :param outputdir:
        :param filenames:
        :param row:
        :return:
        """
        self.db.connect()
        processname = self.db.getCaption(processref)
        processmodule = self.db.getProcessModule(processref)
        processclass = self.db.getProcessClass(processref)
        self.db.closeconn()

        if len(filenames) > 0:
            row = 0
            #One thread per file
            for filename in filenames:
                msg = "Load Process Threads: %s %s [row: %d]" % (processname, filename, row)
                print(msg)
                #TODO use outputfile directory rather than filename for progress bar output
                wx.PostEvent(wxGui, ResultEvent((0, row, processname, filename)))
                t = ProcessThread(wxGui, self.currentconfig, processname, processmodule,processclass, outputdir, filename, row)
                t.start()
                row += 1
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
