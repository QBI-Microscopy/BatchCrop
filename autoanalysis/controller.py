import importlib
import logging
import threading
import time
from logging.handlers import RotatingFileHandler
from multiprocessing import freeze_support
from os import access, R_OK, W_OK, mkdir
from os.path import join, expanduser, splitext, basename

import psutil
import wx

from autoanalysis.resources.dbquery import DBI

FORMAT = '[ %(asctime)s %(levelname)-4s ]%(threadName)-9s %(filename)s (%(funcName)s %(lineno)d) %(message)s'

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


########################################################################

lock = threading.Lock()
event = threading.Event()


####################################################################################################

class ProcessThread(threading.Thread):
    """Multi Worker Thread Class."""

    # ----------------------------------------------------------------------
    def __init__(self, wxObject, configid, processname, processmodule, processclass, outputdir, filename, row):
        """Init Worker Thread Class."""
        threading.Thread.__init__(self)
        self.configID = configid
        self.db = DBI()
        self.max_mem = float(self.db.getConfigByName(self.configID, 'MAX_MEMORY'))
        if self.max_mem is None:
            self.max_mem = 80
        self.wxObject = wxObject
        self.filename = filename
        self.output = outputdir
        # Use outputfile directory rather than filename for progress bar output
        self.outfile = join(self.output, splitext(basename(self.filename))[0])
        self.row = row
        self.processname = processname
        logger = logging.getLogger(processname)
        # Instantiate module
        module = importlib.import_module(processmodule)
        self.class_ = getattr(module, processclass)
        self.mod = self.class_(filename, outputdir)

    def configure(self):
        try:
            # Load all configurable params required for module - get list from module
            cfg = self.mod.getConfigurables()
            self.db.connect()
            for c in cfg.keys():
                cfg[c] = self.db.getConfigByName(self.configID, c)

            self.db.closeconn()
            self.mod.setConfigurables(cfg)

        except Exception as e:
            raise ValueError("Configure:", str(e))
    # ----------------------------------------------------------------------


    def run(self):
        """
        Run module in thread
        :return:
        """
        try:
            # event.set()
            # lock.acquire(True)
            q = dict()
            # Configure parameters
            self.configure()
            logging.info('Configuration set')
            # Run thread processing
            msg = 'Running: %s' % self.filename
            print(msg)
            logging.info(msg)
            if self.mod.imgfile is not None:
                q[self.filename] = self.mod.run()

            else:
                msg = "ERROR: No data loaded for process: %s file: %s" % (self.class_, self.filename)
                print(msg)
                logging.error(msg)
                q[self.filename] = None
                raise ValueError(msg)
            msg = 'Complete: %s' % self.filename
            print(msg)
            logging.info(msg)

        except Exception as e:
            print(e)
            wx.PostEvent(self.wxObject, ResultEvent((-1, self.row, self.processname, self.outfile,e.args[0])))
        finally:
            print('Finished ProcessThread')
            # self.terminate()
            # lock.release()
            # event.clear()



########################################################################

class Controller():
    def __init__(self):
        self.currentconfig = 'default'  # maybe future multiple configs possible
        # connect to db
        self.db = DBI()
        self.db.connect()
        self.logfile = None
        self.logger = self.loadLogger(self.db.userconfigdir)
        self.threadlist=[]
        self._stopevent = threading.Event()

    def loadLogger(self, outputdir=None):
        #### LoggingConfig
        logger.setLevel(logging.INFO)
        # Check dirs exist and are writable
        if outputdir is not None and access(outputdir, R_OK):
            homedir = outputdir
        else:
            userdir = expanduser("~")
            homedir = join(userdir, '.qbi_apps', 'batchcrop')
            if not access(homedir, W_OK):
                if not access(join(userdir, '.qbi_apps'), W_OK):
                    mkdir(join(userdir, '.qbi_apps'))
                mkdir(homedir)

        logdir = join(homedir, "logs")
        if not access(logdir,W_OK):
            mkdir(logdir)
        self.logfile = join(logdir, 'batchcrop.log')
        handler = RotatingFileHandler(filename=self.logfile, maxBytes=10000000, backupCount=10)
        formatter = logging.Formatter(FORMAT)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def poll(self,t,row,processname,outfile,wxObject,max_mem):
        # Poll thread to update progress bar
        ctr = 0
        increment = 5
        tcount = 90
        while t.isAlive():
            time.sleep(increment)

            # Check CPU usage
            percent = psutil.virtual_memory().percent
            msg = "Controller:RunProcess (t.alive): [%s] %s (%s)" % (
            processname, outfile, "{0}% memory".format(percent))
            print(msg)
            logger.debug(msg)
            if percent >= max_mem:
                msg = 'Low memory - stop processing: %d' % percent
                logging.warning(msg)
                print(msg)
                raise OSError(msg)

            ctr += increment
            # reset ??
            if ctr == tcount:
                ctr = increment
            # count, row, process, filename
            wx.PostEvent(wxObject, ResultEvent((ctr, row, processname, outfile, "{0}% memory".format(percent))))
            wx.YieldIfNeeded()

    # ----------------------------------------------------------------------
    def RunProcess(self, wxGui, processref, outputdir, filenames):
        """
        :param wxGui:
        :param processref:
        :param outputdir: either set by user or defaults to subdir in input dir (from App.py)
        :param filenames:
        :param row:
        :return:
        """
        self.db.connect()
        processname = self.db.getCaption(processref)
        processmodule = self.db.getProcessModule(processref)
        processclass = self.db.getProcessClass(processref)
        self.db.closeconn()
        # Check users available RAM and CPU
        msg = "CPU count: %d" % psutil.cpu_count(False)
        print(msg)
        logging.info(msg)
        max_mem = float(self.db.getConfigByName(self.currentconfig,'MAX_MEMORY'))
        if max_mem is None:
            max_mem = 80
        avail_mem = psutil.virtual_memory().available
        swap = psutil.swap_memory().free
        percent = psutil.virtual_memory().percent #used/total
        msg = "MEMORY: \n\tAvailable: %d \t Swap: %d \t Percent: %d \n" % (avail_mem,swap,percent)
        print(msg)
        logging.info(msg)

        if len(filenames) > 0:
            row = 0
            # One thread per file
            for filename in filenames:
                if not self._stopevent.isSet():
                    msg = "Load Process Threads: %s %s [row: %d]" % (processname, filename, row)
                    print(msg)
                    logger.info(msg)
                    # Outputfile directory rather than filename for progress bar output
                    outfolder = join(outputdir, splitext(basename(filename))[0])
                    # Initial entry
                    wx.PostEvent(wxGui, ResultEvent((0, row, processname, outfolder,'')))
                    wx.YieldIfNeeded()
                    t = ProcessThread(wxGui, self.currentconfig, processname, processmodule, processclass, outputdir,
                                      filename, row)

                    self.threadlist.append(t)
                    t.start()
                    self.poll(t,row,processname,outfolder,wxGui,max_mem)

                    wx.PostEvent(wxGui, ResultEvent((100, row, processname, outfolder,'')))
                    # New row
                    row += 1
                else:
                    msg ='Stop event detected - ending all processing'
                    logging.warning(msg)
                    print(msg)
                    break


        else:
            logger.error("No files to process")
            raise ValueError("No matched files to process")

    # ----------------------------------------------------------------------


    def shutdown(self):
        self._stopevent.set()
        msg="Controller: stop event set"
        logging.warning(msg)
        print(msg)
        # Loop through threads to finish?
        for t in self.threadlist:
            if t != threading.main_thread() and t.is_alive():
                msg = 'Stop processing called: closing {0}'.format(t.getName())
                logging.info(msg)
                print(msg)
                t.join(timeout=5)
