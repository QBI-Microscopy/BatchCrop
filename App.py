'''
    QBI Batch Crop APP: Batch cropping of high resolution microscopy images

    QBI Software Team
    *******************************************************************************
    Copyright (C) 2018  QBI Software, The University of Queensland

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
'''

import csv
import os
import re
import time
from os.path import join, isdir, sep

# maintain this order of matplotlib
# TkAgg causes Runtime errors in Thread
import matplotlib

from autoanalysis.gui.ImageSegmentOrderingPanel import ImageSegmentOrderingPanel
from autoanalysis.gui.ImageThumbnail import IMSImageThumbnail
from autoanalysis.resources.dbquery import DBI

matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.style.use('seaborn-paper')
import wx
import wx.html2
from glob import iglob
from autoanalysis.controller import EVT_RESULT, EVT_DATA, Controller
from autoanalysis.utils import findResourceDir
from autoanalysis.gui.appgui import ConfigPanel, FilesPanel, WelcomePanel, ProcessPanel,dlgLogViewer

__version__ = '1.0.0alpha'


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
        self.loadController()

    def loadController(self):
        self.controller = self.parent.controller
        self.OnLoadData()

    def OnLoadData(self):
        self.controller.db.connect()
        #load config values
        rownum =0
        conf = self.controller.db.getConfigALL(self.controller.currentconfig)
        if conf is not None:
            for k in conf.keys():
                self.m_grid1.SetCellValue(rownum, 0, k)
                self.m_grid1.SetCellValue(rownum, 1, conf[k][0])
                if conf[k][1] is not None:
                    self.m_grid1.SetCellValue(rownum, 2, conf[k][1])
                rownum += 1
            self.m_grid1.AutoSizeColumns()
            self.m_grid1.AutoSize()
        self.controller.db.closeconn()


    def OnSaveConfig(self, event):
        self.controller.db.getconn()
        configid = self.controller.currentconfig
        configlist=[]
        data = self.m_grid1.GetTable()
        for rownum in range(0, data.GetRowsCount()):
            if not data.IsEmptyCell(rownum, 0):
                configlist.append((self.m_grid1.GetCellValue(rownum, 0),self.m_grid1.GetCellValue(rownum, 1),configid,self.m_grid1.GetCellValue(rownum, 2)))
        #print('Saved config:', configlist)
        # Save to DB
        cnt = self.controller.db.addConfig(configid,configlist)

        #reload other panels
        for fp in self.parent.Children:
            if isinstance(fp, wx.Panel) and self.__class__ != fp.__class__:
                fp.loadController()
        #notification
        msg = "Config saved: %s" % configid
        self.Parent.Warn(msg)
        self.controller.db.closeconn()

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
            print(os.stat(fname))
            self.target.AppendItem([True, fname])

        # Update status bar
        status = 'Total files loaded: %s' % self.target.Parent.m_dataViewListCtrl1.GetItemCount()
        self.target.Parent.m_status.SetLabelText(status)
        return len(filenames)

########################################################################
class FileSelectPanel(FilesPanel):
    def __init__(self, parent):
        super(FileSelectPanel, self).__init__(parent)
        self.loadController()
        self.filedrop = MyFileDropTarget(self.m_dataViewListCtrl1)
        self.m_tcDragdrop.SetDropTarget(self.filedrop)

        #TODO - Move to template - Done
        #self.panel_right = wx.Panel(self, size=wx.Size(580,650))
        # self.panel_right.SetBackgroundColour(wx.Colour(255, 255, 255))
        #self.sizer.Add(self.panel_right)
        self.inputdir = None

    #
    # @property
    # def inputdir(self):
    #     return self._inputdir
    #
    # @inputdir.setter
    # def inputdir(self, input):
    #     print(input)
    #     self._inputdir = input

    def OnFileClicked(self, event):
        row = self.m_dataViewListCtrl1.ItemToRow(event.GetItem())
        filepath = self.m_dataViewListCtrl1.GetTextValue(row, 1)
        print('File clicked: ', filepath)

        if self.preview_thumbnail is not None:
            self.preview_thumbnail.Destroy()

        try:
            W,H = self.panel_right.GetSize()
            self.preview_thumbnail = IMSImageThumbnail(self.panel_right, filepath, max_size=(H, W))
            self.panel_right.Sizer.Add(self.preview_thumbnail, wx.CENTER)
        except Exception as e :
            print("Could not open file {0} as an IMS image. Error is {1}".format(filepath, str(e)))
            self.preview_thumbnail = None
        #self.Layout()


    def OnColClick(self, event):
        print("header clicked: ", event.GetColumn())
        # colidx = event.GetColumn()
        # self.m_dataViewListCtrl1.GetModel().Resort()

    def loadController(self):
        self.controller = self.Parent.controller



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
                            swriter.writerow([self.m_dataViewListCtrl1.GetValue(i, 1)])
        except Exception as e:
            self.Parent.Warn("Save list error:" + e.args[0])
        finally:
            print('Save list complete')

    def loadFileToPanel(self, filepath):
        self.m_dataViewListCtrl1.AppendItem([True, filepath])
        print(os.stat(filepath))

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
                            self.loadFileToPanel(row[0])
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
        if self.inputdir is not None:
            self.m_status.SetLabelText("Finding files ... please wait")
            allfiles = [y for y in iglob(join(self.inputdir, '**'), recursive=True)]
            searchtext = self.m_tcSearch.GetValue()
            if (len(searchtext) > 0):
                filenames = [f for f in allfiles if re.search(searchtext, f, flags=re.IGNORECASE)]
            else:
                filenames = [f for f in allfiles if not isdir(f)]

            for fname in filenames:
                self.loadFileToPanel(fname)

            #self.col_file.SetMinWidth(wx.LIST_AUTOSIZE)
            msg = "Total Files loaded: %d" % len(fname)
            self.m_status.SetLabelText(msg)
        else:
            print("Cannot autofind files when no directory is selected. Please select Top Level Directory.")

        self.btnAutoFind.Enable(True)
        #TODO Start generating thumbnails for display (bg thread)

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
        self.loadCaptions()
        #
        # bSizer22 = wx.BoxSizer(wx.HORIZONTAL)
        # self.bSizer19.Add(bSizer22, 2, wx.EXPAND, 10)
        #TODO Add to template
        self.m_panelImageOrder = ImageSegmentOrderingPanel(self)
        #self.bSizer18.Add(self.ImageOrderingPanel)
        # bSizer22.Add(self.ImageOrderingPanel)
        # self.controller = parent.controller
        # Bind timer event
        # self.Bind(wx.EVT_TIMER, self.progressfunc, self.controller.timer)
        # processes = [p['caption'] for p in self.controller.processes]
        # self.m_checkListProcess.AppendItems(processes)
        # Set up event handler for any worker thread results
        EVT_RESULT(self, self.progressfunc)
        EVT_DATA(self,self.showresults)
        # EVT_CANCEL(self, self.stopfunc)
        # Set timer handler
        self.start = {}

    def loadController(self):
        self.controller = self.Parent.controller

    def loadCaptions(self):
        self.controller.db.connect()
        processes = self.controller.db.getCaptions() #[self.controller.processes[p]['caption'] for p in self.controller.processes]
        self.m_checkListProcess.Clear()
        self.m_checkListProcess.AppendItems(processes)
        self.controller.db.closeconn()

    def OnShowDescription(self, event):
        ref = self.controller.db.getRef(event.String)
        desc = self.controller.db.getDescription(ref)

        self.m_stTitle.SetLabelText(event.String)
        self.m_stDescription.Clear()
        self.m_stDescription.WriteText(desc)

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

    def showresults(self,filename):
        #TODO link to Image Ordering Panel
        self.m_stOutputlog.SetLabelText("Processed %s" % filename)


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

    def getDefaultOutputdir(self):
        subdir = 'cropped'
        sdir = ''
        if self.controller is not None and self.controller.db is not None:
            sdir = self.controller.db.getConfigByName(self.controller.currentconfig, 'CROPPED_IMAGE_FILES')
        if len(sdir) > 0:
            subdir = sdir
        return subdir

    def OnRunScripts(self, event):
        """
        Run selected scripts sequentially - updating progress bars
        :param e:
        :return:
        """
        # Clear processing window
        self.m_dataViewListCtrlRunning.DeleteAllItems()
        # Disable Run button
        btn = event.GetEventObject()
        btn.Disable()
        # Get selected processes
        selections = self.m_checkListProcess.GetCheckedStrings()
        print("Processes selected: ", len(selections))
        showplots = self.m_cbShowplots.GetValue()
        # Get data from other panels
        filepanel = self.getFilePanel()
        filenames =[]
        num_files = filepanel.m_dataViewListCtrl1.GetItemCount()
        outputdir = filepanel.txtOutputdir.GetValue()
        # if blank will use subdir in inputdir
        if len(outputdir) <=0:
            #TODO: change first argument to string not TextCtrl
            outputdir = join(filepanel.txtInputdir.GetLineText(0),self.getDefaultOutputdir())
        print('PROCESSPANEL: All Files:', num_files)
        try:
            if len(selections) > 0 and num_files > 0:
                # Get selected files and sort into groups
                for i in range(0, num_files):
                    if filepanel.m_dataViewListCtrl1.GetToggleValue(i, 0):
                        fname = filepanel.m_dataViewListCtrl1.GetValue(i, 1)
                        if not isdir(fname):
                            filenames.append(fname)
                print('PROCESSPANEL: Selected Files:', len(filenames))
                if len(filenames) <= 0:
                    raise ValueError("No files selected in Files Panel")

                row = 0
                # For each process
                for pcaption in selections:
                    p = self.controller.db.getRef(pcaption)
                    print("PROCESSPANEL: Running processname =", p)
                    self.controller.RunProcess(self, p, outputdir, filenames, row, showplots)
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
            if self.controller.db is not None:
                self.controller.db.closeconn()

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
        #self.resourcesdir = findResourceDir()
        # self.processfile = join(self.resourcesdir, 'processes.yaml')
        # self.configfile = self.getConfigdb()
        #self.currentconfig = 'default'
        self.controller = Controller()

        self.InitUI()
        self.Centre(wx.BOTH)
        self.Show()

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
                          "Batch Crop Application",
                          size=(1300, 720)
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
    # TODO: Run DB setup if not already done
    app = wx.App()
    frame = AppFrame()
    app.MainLoop()
