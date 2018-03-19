# import images
# import logging
import csv
import re
import time
from glob import iglob
from os.path import join, expanduser, isdir, sep
from autoanalysis.db.dbquery import DBI
# maintain this order of matplotlib
# TkAgg causes Runtime errors in Thread
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.style.use('seaborn-paper')
import wx
import wx.html2
from os.path import abspath, dirname, commonpath
from os import access,R_OK, mkdir
from glob import iglob
import shutil
from autoanalysis.controller import EVT_RESULT, Controller
from autoanalysis.gui.appgui import ConfigPanel, FilesPanel, WelcomePanel, ProcessPanel,dlgLogViewer

__version__ = '1.0.0'


##### Global functions
def findResourceDir():
    allfiles = [y for y in iglob(join('.', '**', "resources"), recursive=True)]
    files = [f for f in allfiles if not 'build' in f]
    resource_dir = commonpath(files)
    if len(resource_dir) > 0:
        print("Resource directory located to: ", resource_dir)
    else:
        resource_dir =join('autoanalysis','resources')

    return abspath(resource_dir)


########################################################################
class HomePanel(WelcomePanel):
    """
    This will be the first notebook tab
    """

    # ----------------------------------------------------------------------
    def __init__(self, parent):
        super(HomePanel, self).__init__(parent)
        img = wx.Bitmap(1, 1)
        img.LoadFile(join(findResourceDir(), 'loadimage.bmp'), wx.BITMAP_TYPE_BMP)

        self.m_richText1.BeginFontSize(14)
        welcome = "Welcome to the Slide Cropper App (v.%s)" % __version__
        self.m_richText1.WriteText(welcome)
        self.m_richText1.EndFontSize()
        self.m_richText1.Newline()
        # self.m_richText1.BeginLeftIndent(20)
        self.m_richText1.BeginItalic()
        self.m_richText1.WriteText("developed by QBI Software, The University of Queensland")
        self.m_richText1.EndItalic()
        # self.m_richText1.EndLeftIndent()
        self.m_richText1.Newline()
        self.m_richText1.WriteImage(img)
        self.m_richText1.Newline()
        self.m_richText1.WriteText(
            r'''This is a multi-threaded application to crop a serial sections into individual images.''')
        self.m_richText1.Newline()
        # self.m_richText1.BeginNumberedBullet(1, 0.2, 0.2, wx.TEXT_ATTR_BULLET_STYLE)
        self.m_richText1.BeginBold()
        self.m_richText1.WriteText("Configure")
        self.m_richText1.EndBold()
        self.m_richText1.Newline()
        # self.m_richText1.BeginLeftIndent(20)
        self.m_richText1.WriteText(
            'All options can be specifically configured and multiple configurations saved and reloaded.')
        self.m_richText1.Newline()
        self.m_richText1.BeginBold()
        self.m_richText1.WriteText("Select Files")
        self.m_richText1.EndBold()
        # self.m_richText1.BeginLeftIndent(20)
        self.m_richText1.Newline()
        self.m_richText1.WriteText(
            "Select a top level directory containing the required data files and/or use the Drag'n'Drop for individual files. Only files checked in the file list will be included. Output files will be put in a subfolders under matching filenames either in a directory called 'cropped' in the input directory structure or specified output directory. A prefix and group can be used for all output files.")
        self.m_richText1.Newline()
        self.m_richText1.BeginBold()
        self.m_richText1.WriteText("Run Processes")
        self.m_richText1.EndBold()
        # self.m_richText1.BeginLeftIndent(20)
        self.m_richText1.Newline()
        self.m_richText1.WriteText(
            r"Each process is described with the required input files (which need to be available in the input directory structure) and the output files which it produces. These are multi-threaded processes which will run in sequence as listed and once running their progress can be monitored. A log file is produced which can be viewed in a popup. ")
        # self.m_richText1.EndLeftIndent()
        self.m_richText1.Newline()
        self.m_richText1.BeginItalic()
        self.m_richText1.AddParagraph(
            r"Copyright (2018) https://github.com/QBI-Microscopy/SlideCrop")
        self.m_richText1.EndItalic()

    def loadController(self):
        pass


########################################################################
class Config(ConfigPanel):
    def __init__(self, parent):
        super(Config, self).__init__(parent)
        self.parent = parent
        self.configdb = self.parent.configfile
        self.dbi = DBI(self.configdb)
        self.loadController()

    def loadController(self):
        self.controller = self.parent.controller
        self.currentconfig = self.parent.controller.currentconfig
        self.OnLoadData()

    def OnLoadData(self):
        self.dbi.getconn()
        #load config values
        cids = self.dbi.getConfigIds()
        if len(cids)>0:
            self.cboConfigid.Set(cids)
            #configid = self.cboConfigid.GetStringSelection()
            rownum =0
            if self.currentconfig in cids:
                selection = self.cboConfigid.FindString(self.currentconfig)
                self.cboConfigid.SetSelection(selection)
                conf = self.dbi.getConfigALL(self.currentconfig)
            else:
                selection = self.cboConfigid.FindString(cids[0])
                self.cboConfigid.SetSelection(selection)
                conf = self.dbi.getConfigALL(cids[0])
            if conf is not None:
                for k in conf.keys():
                    self.m_grid1.SetCellValue(rownum, 0, k)
                    self.m_grid1.SetCellValue(rownum, 1, conf[k][0])
                    if conf[k][1] is not None:
                        self.m_grid1.SetCellValue(rownum, 2, conf[k][1])
                    rownum += 1
                self.m_grid1.AutoSizeColumns()
                self.m_grid1.AutoSize()
        self.dbi.closeconn()

    def OnLoadConfig(self,event):
        self.dbi.getconn()
        #load config values
        configid = self.cboConfigid.GetValue()
        try:
            rownum =0
            conf = self.dbi.getConfigALL(configid)
            if conf is not None:
                self.m_grid1.ClearGrid()
                for k in conf.keys():
                    self.m_grid1.SetCellValue(rownum, 0, k)
                    self.m_grid1.SetCellValue(rownum, 1, conf[k][0])
                    if conf[k][1] is not None:
                        self.m_grid1.SetCellValue(rownum, 2, conf[k][1])
                    rownum += 1
                self.m_grid1.AutoSizeColumns()
                self.m_grid1.AutoSize()
            #Notify other controllers
            self.parent.controller.currentconfig = configid
            # reload other panels
            for fp in self.parent.Children:
                if isinstance(fp, wx.Panel) and self.__class__ != fp.__class__:
                    fp.loadController()
            # notification
            msg = "Config loaded: %s" % configid
            self.Parent.Warn(msg)
        except Exception as e:
            self.Parent.Warn(e.args[0])
        finally:
            self.dbi.closeconn()


    def OnSaveConfig(self, event):
        self.dbi.getconn()
        configid = self.cboConfigid.GetValue()
        configlist=[]
        data = self.m_grid1.GetTable()
        for rownum in range(0, data.GetRowsCount()):
            if not data.IsEmptyCell(rownum, 0):
                configlist.append((self.m_grid1.GetCellValue(rownum, 0),self.m_grid1.GetCellValue(rownum, 1),configid,self.m_grid1.GetCellValue(rownum, 2)))
        #print('Saved config:', configlist)
        # Save to DB
        cnt = self.dbi.addConfig(configid,configlist)
        # Load as options
        cids = self.dbi.getConfigIds()
        if len(cids) > 0:
            self.cboConfigid.Set(cids)
            selection = self.cboConfigid.FindString(configid)
            self.cboConfigid.SetSelection(selection)
        # Load controller
        self.parent.controller.currentconfig = configid
        #reload other panels
        for fp in self.parent.Children:
            if isinstance(fp, wx.Panel) and self.__class__ != fp.__class__:
                fp.loadController()
        #notification
        msg = "Config saved: %s" % configid
        self.Parent.Warn(msg)
        self.dbi.closeconn()

    def OnAddRow(self, event):
        self.m_grid1.AppendRows(1, True)

########################################################################
class MyFileDropTarget(wx.FileDropTarget):
    def __init__(self, target):
        super(MyFileDropTarget, self).__init__()
        self.target = target

    def OnDropFiles(self, x, y, filenames):
        group = ''
        for fname in filenames:
            self.target.AppendItem([True, group, fname])
        # Update status bar
        status = 'Total files loaded: %s' % self.target.Parent.m_dataViewListCtrl1.GetItemCount()
        self.target.Parent.m_status.SetLabelText(status)
        return len(filenames)


########################################################################
class FileSelectPanel(FilesPanel):
    def __init__(self, parent):
        super(FileSelectPanel, self).__init__(parent)
        self.col_file.SetMinWidth(200)
        self.loadController()
        self.filedrop = MyFileDropTarget(self.m_dataViewListCtrl1)
        self.m_tcDragdrop.SetDropTarget(self.filedrop)
        # self.col_file.SetSortable(True)
        # self.col_group.SetSortable(True)

    def OnColClick(self, event):
        print("header clicked: ", event.GetColumn())
        # colidx = event.GetColumn()
        # self.m_dataViewListCtrl1.GetModel().Resort()

    def loadController(self):
        self.controller = self.Parent.controller
        datagroups = []
        config = self.controller.db.getConfig(self.controller.currentconfig)
        for c in config.keys():
            if c.startswith('GROUP'):
                datagroups.append(config[c])
        self.m_cbGroups.SetItems(datagroups)


    def OnInputdir(self, e):
        """ Open a file"""
        dlg = wx.DirDialog(self, "Choose a directory containing input files")
        if dlg.ShowModal() == wx.ID_OK:
            self.inputdir = str(dlg.GetPath())
            self.txtInputdir.SetValue(self.inputdir)
        dlg.Destroy()

    def OnOutputdir(self, e):
        """ Open a file"""
        dlg = wx.DirDialog(self, "Choose a directory for output files")
        if dlg.ShowModal() == wx.ID_OK:
            self.outputdir = str(dlg.GetPath())
            self.txtOutputdir.SetValue(self.outputdir)

        dlg.Destroy()

    def OnAssignGroup(self, event):
        """
        Allow user to assign groups to selected files
        :param event:
        :return:
        """
        num_files = self.m_dataViewListCtrl1.GetItemCount()
        group = self.m_cbGroups.GetStringSelection()
        for i in range(0, num_files):
            if self.m_dataViewListCtrl1.GetToggleValue(i, 0):
                self.m_dataViewListCtrl1.SetValue(group, i, 1)
                print('Setting %s with group %s', self.m_dataViewListCtrl1.GetValue(i, 2), group)

    def OnSaveList(self, event):
        """
        Save selected files to csv
        :param event:
        :return:
        """
        num_files = self.m_dataViewListCtrl1.GetItemCount()
        try:
            openFileDialog = wx.FileDialog(self, "Save file list", "", "", "CSV files (*.csv)|*",
                                           wx.FD_SAVE | wx.FD_CHANGE_DIR)
            if openFileDialog.ShowModal() == wx.ID_OK:
                savefile = str(openFileDialog.GetPath())
                with open(savefile, 'w') as csvfile:
                    swriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

                    for i in range(0, num_files):
                        if self.m_dataViewListCtrl1.GetToggleValue(i, 0):
                            swriter.writerow(
                                [self.m_dataViewListCtrl1.GetValue(i, 1), self.m_dataViewListCtrl1.GetValue(i, 2)])
        except Exception as e:
            self.Parent.Warn("Save list error:" + e.args[0])
        finally:
            print('Save list complete')

    def OnLoadList(self, event):
        """
        Load saved list
        :param event:
        :return:
        """
        try:
            openFileDialog = wx.FileDialog(self, "Open file list", "", "", "CSV files (*.csv)|*",
                                           wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_CHANGE_DIR)

            if openFileDialog.ShowModal() == wx.ID_OK:
                savefile = str(openFileDialog.GetPath())
                with open(savefile, 'r') as csvfile:
                    sreader = csv.reader(csvfile, delimiter=',', quotechar='"')
                    self.m_dataViewListCtrl1.DeleteAllItems()
                    for row in sreader:
                        if len(row) > 0:
                            self.m_dataViewListCtrl1.AppendItem([True, row[0], row[1]])
                msg = "Total Files loaded: %d" % self.m_dataViewListCtrl1.GetItemCount()
                self.m_status.SetLabelText(msg)
        except Exception as e:
            print(e.args[0])
            self.Parent.Warn("Load list error:" + e.args[0])
        finally:
            print("Load list complete")

    def OnAutofind(self, event):
        """
        Find all matching files in top level directory
        :param event:
        :return:
        """
        self.btnAutoFind.Disable()
        self.m_status.SetLabelText("Finding files ... please wait")
        allfiles = [y for y in iglob(join(self.inputdir, '**'), recursive=True)]
        searchtext = self.m_tcSearch.GetValue()
        if (len(searchtext) > 0):
            filenames = [f for f in allfiles if re.search(searchtext, f, flags=re.IGNORECASE)]
        else:
            filenames = [f for f in allfiles if not isdir(f)]
        #Assign files to group based on filenames
        groups = self.m_cbGroups.GetItems()
        for fname in filenames:
            group = ''
            # group if available
            for g in groups:
                group = ''
                if g.upper() in fname.upper().split(sep):
                    group = g
                    break
            self.m_dataViewListCtrl1.AppendItem([True, group, fname])

        self.col_file.SetMinWidth(wx.LIST_AUTOSIZE)
        msg = "Total Files loaded: %d" % self.m_dataViewListCtrl1.GetItemCount()
        self.m_status.SetLabelText(msg)
        self.btnAutoFind.Enable(True)

    def OnSelectall(self, event):
        for i in range(0, self.m_dataViewListCtrl1.GetItemCount()):
            self.m_dataViewListCtrl1.SetToggleValue(event.GetSelection(), i, 0)
        print("Toggled selections to: ", event.GetSelection())

    def OnClearlist(self, event):
        print("Clear items in list")
        self.m_dataViewListCtrl1.DeleteAllItems()



########################################################################
class ProcessRunPanel(ProcessPanel):
    def __init__(self, parent):
        super(ProcessRunPanel, self).__init__(parent)
        self.loadController()
        self.db = DBI(self.controller.configfile)
        self.db.getconn()
        # self.controller = parent.controller
        # Bind timer event
        # self.Bind(wx.EVT_TIMER, self.progressfunc, self.controller.timer)
        # processes = [p['caption'] for p in self.controller.processes]
        # self.m_checkListProcess.AppendItems(processes)
        # Set up event handler for any worker thread results
        EVT_RESULT(self, self.progressfunc)
        # EVT_CANCEL(self, self.stopfunc)
        # Set timer handler
        self.start = {}

    def loadController(self):
        self.controller = self.Parent.controller
        processes = [self.controller.processes[p]['caption'] for p in self.controller.processes]
        self.m_checkListProcess.Clear()
        self.m_checkListProcess.AppendItems(processes)

    def OnShowDescription(self, event):
        print(event.String)

        desc = [self.controller.processes[p]['description'] for p in self.controller.processes if
                self.controller.processes[p]['caption'] == event.String]
        filesIn = [self.controller.processes[p]['filesin'] for p in self.controller.processes if
                   self.controller.processes[p]['caption'] == event.String]
        filesOut = [self.controller.processes[p]['filesout'] for p in self.controller.processes if
                    self.controller.processes[p]['caption'] == event.String]
        # Load from Config
        filesIn = [self.controller.db.getConfigByName(self.controller.currentconfig,f) for f in filesIn[0].split(", ")]
        filesOut = [self.controller.db.getConfigByName(self.controller.currentconfig,f) for f in filesOut[0].split(", ")]
        # Load to GUI
        self.m_stTitle.SetLabelText(event.String)
        self.m_stDescription.Clear()
        self.m_stDescription.WriteText(desc[0])
        self.m_stFilesin.SetLabelText(", ".join(filesIn))
        self.m_stFilesout.SetLabelText(", ".join(filesOut))
        self.Layout()

    def progressfunc(self, msg):
        """
        Update progress bars in table - multithreaded
        :param count:
        :param row:
        :param col:
        :return:
        """
        (count, row, i, total, process) = msg.data
        status = "%d of %d files " % (i, total)
        msg = "\nProgress updated: %s count=%d status=%s" % (time.ctime(), count, status)
        print(msg)
        if count == 0:
            self.m_dataViewListCtrlRunning.AppendItem([process, count, "Pending"])
            self.start[process] = time.time()
        elif count < 0:
            self.m_dataViewListCtrlRunning.SetValue("ERROR in process - see log file", row=row, col=2)
            self.m_btnRunProcess.Enable()
        elif count < 100:
            self.m_dataViewListCtrlRunning.SetValue(count, row=row, col=1)
            self.m_dataViewListCtrlRunning.SetValue("Running " + status, row=row, col=2)
            self.m_stOutputlog.SetLabelText("Running: %s ...please wait" % process)
        else:
            if process in self.start:
                endtime = time.time() - self.start[process]
                status = "%s (%d secs)" % (status, endtime)
            print(status)
            self.m_dataViewListCtrlRunning.SetValue(count, row=row, col=1)
            self.m_dataViewListCtrlRunning.SetValue("Done " + status, row=row, col=2)
            self.m_btnRunProcess.Enable()
            self.m_stOutputlog.SetLabelText("Completed process %s" % process)

    def getFilePanel(self):
        """
        Get access to filepanel
        :return:
        """
        filepanel = None

        for fp in self.Parent.Children:
            if isinstance(fp, FileSelectPanel):
                filepanel = fp
                break
        return filepanel

    def OnCancelScripts(self, event):
        """
        Find a way to stop processes
        :param event:
        :return:
        """
        self.controller.shutdown()
        print("Cancel multiprocessor")
        event.Skip()

    def OnRunScripts(self, event):
        """
        Run selected scripts sequentially - updating progress bars
        :param e:
        :return:
        """
        # Clear processing window
        self.m_dataViewListCtrlRunning.DeleteAllItems()
        # Disable Run button
        # self.m_btnRunProcess.Disable()
        btn = event.GetEventObject()
        btn.Disable()
        # Get selected processes
        selections = self.m_checkListProcess.GetCheckedStrings()
        print("Processes selected: ", len(selections))
        showplots = self.m_cbShowplots.GetValue()
        # Get data from other panels
        filepanel = self.getFilePanel()
        filenames = {'all': []}
        groups = filepanel.m_cbGroups.GetItems()
        for g in groups:
            filenames[g]=[]

        num_files = filepanel.m_dataViewListCtrl1.GetItemCount()
        outputdir = filepanel.txtOutputdir.GetValue()  # for batch processes
        print('All Files:', num_files)
        try:
            self.db.getconn()
            if len(selections) > 0 and num_files > 0:
                # Get selected files and sort into groups
                for i in range(0, num_files):
                    if filepanel.m_dataViewListCtrl1.GetToggleValue(i, 0):
                        fname = filepanel.m_dataViewListCtrl1.GetValue(i, 2)
                        group = filepanel.m_dataViewListCtrl1.GetValue(i, 1)
                        if not isdir(fname):
                            filenames['all'].append(fname)
                            if len(group) > 0:
                                filenames[group].append(fname)
                print('Selected Files:', len(filenames['all']))
                if len(filenames) <= 0:
                    raise ValueError("No files selected in Files Panel")

                row = 0
                # For each process
                for pcaption in selections:
                    for p in self.controller.processes.keys():
                        if self.controller.processes[p]['caption']==pcaption:
                            break
                    print("processname =", p)
                    self.controller.RunProcess(self, p, outputdir,filenames, row, showplots)
                    row = row + 1

            else:
                if len(selections) <= 0:
                    raise ValueError("No processes selected")
                else:
                    raise ValueError("No files selected - please go to Files Panel and add to list")
        except ValueError as e:
            self.Parent.Warn(e.args[0])
            # Enable Run button
            self.m_btnRunProcess.Enable()
        finally:
            if self.db is not None:
                self.db.closeconn()

    def OnShowLog(self, event):
        """
        Load logfile into viewer
        :param event:
        :return:
        """
        dlg = dlgLogViewer(self)
        logfile = self.controller.logfile
        dlg.tcLog.LoadFile(logfile)
        dlg.ShowModal()
        dlg.Destroy()

    def OnClearWindow(self, event):
        self.m_dataViewListCtrlRunning.DeleteAllItems()

########################################################################
class AppMain(wx.Listbook):
    def __init__(self, parent):
        """Constructor"""
        wx.Listbook.__init__(self, parent, wx.ID_ANY, style=wx.BK_DEFAULT)
        self.resourcesdir = findResourceDir()
        self.processfile = join(self.resourcesdir, 'processes.yaml')
        self.configfile = self.getConfigdb()
        self.currentconfig = 'original'
        self.controller = Controller(self.configfile, self.currentconfig, self.processfile)

        self.InitUI()
        self.Centre(wx.BOTH)
        self.Show()

    def getConfigdb(self):
        # Save config db to user's home dir or else will be overwritten with updates
        self.userconfigdir = join(expanduser('~'), '.qbi_autoanalysis')
        dbname = 'autoconfig.db'
        if not access(self.userconfigdir, R_OK):
            mkdir(self.userconfigdir)
        configdb = join(self.userconfigdir,dbname)
        if not access(configdb, R_OK):
            defaultdb = join(self.resourcesdir, dbname)
            shutil.copy(defaultdb,configdb)

        return configdb


    def InitUI(self):

        # make an image list using the LBXX images
        il = wx.ImageList(32, 32)
        bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_HOME, wx.ART_FRAME_ICON, (32, 32))
        il.Add(bmp)
        bmp = wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_FRAME_ICON, (32, 32))
        il.Add(bmp)
        bmp = wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_FRAME_ICON, (32, 32))
        il.Add(bmp)
        bmp = wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD, wx.ART_FRAME_ICON, (32, 32))
        il.Add(bmp)
        # bmp = wx.ArtProvider.GetBitmap(wx.ART_REPORT_VIEW, wx.ART_FRAME_ICON, (32, 32))
        # il.Add(bmp)

        self.AssignImageList(il)

        pages = [(HomePanel(self), "Welcome"),
                 (Config(self), "Configure"),
                 (FileSelectPanel(self), "Select Files"),
                 (ProcessRunPanel(self), "Run Processes")]
        imID = 0
        for page, label in pages:
            self.AddPage(page, label, imageId=imID)
            # self.AddPage(page, label)
            imID += 1

        self.GetListView().SetColumnWidth(0, wx.LIST_AUTOSIZE)

        self.Bind(wx.EVT_LISTBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_LISTBOOK_PAGE_CHANGING, self.OnPageChanging)

    # ----------------------------------------------------------------------
    def OnPageChanged(self, event):
        # old = event.GetOldSelection()
        # new = event.GetSelection()
        # sel = self.GetSelection()
        # msg = 'OnPageChanged,  old:%d, new:%d, sel:%d\n' % (old, new, sel)
        # print(msg)
        event.Skip()

    # ----------------------------------------------------------------------
    def OnPageChanging(self, event):
        # old = event.GetOldSelection()
        # new = event.GetSelection()
        # sel = self.GetSelection()
        # msg = 'OnPageChanging, old:%d, new:%d, sel:%d\n' % (old, new, sel)
        # print(msg)
        event.Skip()

    def Warn(self, message, caption='Warning!'):
        dlg = wx.MessageDialog(self, message, caption, wx.OK | wx.ICON_WARNING)
        dlg.ShowModal()
        dlg.Destroy()

    def OnQuit(self, e):
        if self.controller.db is not None:
            self.controller.db.conn.close()
        self.Close()

    def OnCloseWindow(self, e):

        dial = wx.MessageDialog(None, 'Are you sure you want to quit?', 'Question',
                                wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

        ret = dial.ShowModal()

        if ret == wx.ID_YES:
            self.Destroy()
        else:
            e.Veto()


########################################################################
class AppFrame(wx.Frame):
    """
    Frame that holds all other widgets
    """

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, wx.ID_ANY,
                          "Auto Analysis Application",
                          size=(900, 700)
                          )

        # self.timer = wx.Timer(self)
        # self.Bind(wx.EVT_TIMER, self.update, self.timer)
        panel = wx.Panel(self)

        notebook = AppMain(panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(notebook, 1, wx.ALL | wx.EXPAND, 5)
        panel.SetSizer(sizer)
        self.Layout()
        self.Center(wx.BOTH)
        self.Show()


# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App()
    frame = AppFrame()
    app.MainLoop()
