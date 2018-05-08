import importlib
import logging
import threading
import time
from logging.handlers import RotatingFileHandler
from multiprocessing import freeze_support
from os import access, R_OK, W_OK, mkdir
from os.path import join, expanduser, splitext, basename, split, abspath, dirname

import wx

from autoanalysis.resources.dbquery import DBI
from autoanalysis.utils import findResourceDir
from wx.lib.pubsub import pub as Publisher

#FORMAT = '|%(thread)d |%(filename)s |%(funcName)s |%(lineno)d ||%(message)s||'
FORMAT = '[ %(asctime)s %(levelname)-4s ]|%(threadName)-9s |%(filename)s |%(funcName)s |%(lineno)d ||%(message)s||'
    #FORMAT_0 ='[ %(asctime)s %(levelname)-4s ] (%(threadName)-9s) %(message)s'
# global logger
logger = logging.getLogger()

# Required for dist
freeze_support()
###################################################################
# Define notification event for thread completion
EVT_RESULT_ID = wx.NewId()

def EVT_RESULT(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_RESULT_ID, func)

class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""

    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data


# class ImageCropFinishData(object):
#     """ Simple encapsulation of data to be sent to the main GUI thread after an image has been cropped. """
#
#     def __init__(self, filepath):
#         """
#         Constructor.
#         :param filepath: Filepath to folder with cropped outputs.
#         """
#         self.filepath = filepath
#
#     def __str__(self):
#         return str(self.filepath)



########################################################################

lock = threading.Lock()
event = threading.Event()

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
        # Use outputfile directory rather than filename for progress bar output
        self.outfile = join(self.output, splitext(basename(self.filename))[0])
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

        # Need to make sure outputdir is relative to input file directory
        # not to where the code is running (hence the join)
        self.fullOutputPath = join(dirname(abspath(filename)), outputdir)
        self.mod = self.class_(filename, self.fullOutputPath)

    # ----------------------------------------------------------------------
    def run(self):
        i = 0
        total_files = 0
        try:
            # event.set()
            #lock.acquire(True)
            q = dict()
            # Configure mod
            self.configure()
            self.processData(self.filename, q)

        except Exception as e:
            print(e)
            wx.PostEvent(self.wxObject, ResultEvent((-1, self.row, self.processname, self.outfile)))
        finally:
            print('Finished ProcessThread')
            # self.terminate()
            #lock.release()
            #event.clear()

    def configure(self):
        try:
            msg = "PROCESSTHREAD:configuration set"
            print(msg)
            #logger.debug(msg)
            # Load all configurable params required for module - get list from module
            cfg = self.mod.getConfigurables()
            self.db.connect()
            for c in cfg.keys():
                cfg[c] = self.db.getConfigByName(self.configID, c)

            self.db.closeconn()
            self.mod.setConfigurables(cfg)
            self.mod.outputdir = self.fullOutputPath
        except Exception as e:
            print("PROCESSTHREAD:ERROR in configuration", str(e))


    # ----------------------------------------------------------------------
    def processData(self, filename, q):
        """
        Run module here - can modify according to class if needed
        :param filename: data file to process
        :param q: queue for results
        :return:
        """
        try:
            # run cropping process
            if self.mod.data is not None:
                print('PROCESSTHREAD: Module running')
                #fake loop
                t=0
                c = 100
                while t < c:
                    time.sleep(5)
                    t += 50
                # q[filename] =self.mod.run()
            else:
                print("no mod.data ERROR")
                #q[filename] = None
        except Exception as e:
            print("ERROR in cropping", str(e))


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
                # Outputfile directory rather than filename for progress bar output
                outfile = join(outputdir,splitext(basename(filename))[0])
                outfolder = join(dirname(abspath(filename)), "cropped", splitext(basename(filename))[0])

                # Initial entry
                wx.PostEvent(wxGui, ResultEvent((0, row, processname, outfolder)))
                wx.YieldIfNeeded()
                t = ProcessThread(wxGui, self.currentconfig, processname, processmodule,processclass, outputdir, filename, row)
                t.start()
                print('Thread started')
                ctr = 0
                tcount = 90
                while t.isAlive():
                    time.sleep(5)
                    msg = "Controller:RunProcess (t.alive): %s (%s) (%d percent)" % (processname, outfile, ctr)
                    print(msg)
                    #logger.info(msg)

                    ctr += 5
                    # reset ??
                    if ctr == tcount:
                        ctr = 5
                    # count, row, process, filename
                    print("OUTFOLDER", outfolder)
                    wx.PostEvent(wxGui, ResultEvent((ctr, row, processname, outfolder)))
                    wx.YieldIfNeeded()
                # End processing
                wx.PostEvent(wxGui, ResultEvent((100, row, processname, outfolder)))
                # New row
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
            logger.info('Shutdown: closing {0}'.format(t.getName()))
            t.terminate()
