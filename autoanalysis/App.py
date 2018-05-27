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
import sys
import time
from os import mkdir
from os.path import join, isdir, exists

import matplotlib

# maintain this order of matplotlib
# TkAgg causes Runtime errors in Thread
matplotlib.use('Agg')
from autoanalysis.gui.ImageThumbnail import IMSImageThumbnail
from autoanalysis.gui.ImageViewer import ImageViewer
import wx
import wx.xrc
import wx.html2
import wx.dataview

from glob import iglob
from autoanalysis.controller import EVT_RESULT, Controller
from autoanalysis.utils import findResourceDir
from autoanalysis.gui.appgui import ConfigPanel, FilesPanel, WelcomePanel, ProcessPanel, dlgLogViewer

__version__ = '1.0.0'
DEBUG = 1
COLWIDTH=500 #DISPLAY COLUMNS
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
        welcome = "Welcome to the Batch Slide Cropper App (v.%s)" % __version__
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
            "Select a top level directory containing the required data files and/or use the Drag'n'Drop for individual files. Only files checked in the file list will be included in processing. A preview of each file can be displayed by selecting the filename.  If required, the file list can be saved and reloaded.")
        self.m_richText1.Newline()
        self.m_richText1.BeginBold()
        self.m_richText1.WriteText("Run Processes")
        self.m_richText1.EndBold()
        # self.m_richText1.BeginLeftIndent(20)
        self.m_richText1.Newline()
        self.m_richText1.WriteText(
            r"Select which processing modules is to run by viewing description. Each file is processed in the background as a multi-threaded process which will run in sequence as listed and once running their progress can be monitored. Any output files will be put in the output directory specified or in subfolders under a directory called 'cropped' in the input directory structure. A review panel is provided for output files. A log file is produced which can be viewed in a popup.")
        # self.m_richText1.EndLeftIndent()
        self.m_richText1.Newline()
        self.m_richText1.BeginItalic()
        self.m_richText1.AddParagraph(
            r"Copyright (2018) https://github.com/QBI-Microscopy/BatchCrop")
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
        # load config values
        rownum = 0
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
        self.controller.db.connect()
        configid = self.controller.currentconfig
        configlist = []
        data = self.m_grid1.GetTable()
        for rownum in range(0, data.GetRowsCount()):
            if not data.IsEmptyCell(rownum, 0):
                configlist.append((self.m_grid1.GetCellValue(rownum, 0), self.m_grid1.GetCellValue(rownum, 1), configid,
                                   self.m_grid1.GetCellValue(rownum, 2)))
        # print('Saved config:', configlist)
        # Save to DB
        cnt = self.controller.db.addConfig(configid, configlist)

        # reload other panels
        for fp in self.parent.Children:
            if isinstance(fp, wx.Panel) and self.__class__ != fp.__class__:
                fp.loadController()
        # notification
        #msg = "Config saved: %s" % configid
        msg = "Config updated successfully"
        self.Parent.Info(msg)
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
        fileList = [str(self.target.GetTextValue(i, 1)) for i in range(self.target.GetItemCount())]
        for fname in list(set(filenames).difference(set(fileList))):
            self.target.AppendItem([True, fname, "{:0.3f}".format(os.stat(fname).st_size / 10e8)])

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
        self.inputdir = None

    def OnFileClicked(self, event):
        row = self.m_dataViewListCtrl1.ItemToRow(event.GetItem())
        filepath = self.m_dataViewListCtrl1.GetTextValue(row, 1)
        #print('File clicked: ', filepath)

        if self.preview_thumbnail is not None:
            self.preview_thumbnail.Destroy()

        try:
            W, H = self.panel_right.GetSize()
            self.preview_thumbnail = IMSImageThumbnail(self.panel_right, filepath, max_size=(H, W))
            self.panel_right.Sizer.Add(self.preview_thumbnail, wx.CENTER)
        except Exception as e:
            msg = "Could not open file {0} as an IMS image. Error is {1}".format(filepath, str(e))
            self.Parent.Warn(msg)
            #self.preview_thumbnail = None
            # self.Layout()

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
                            swriter.writerow(
                                [self.m_dataViewListCtrl1.GetValue(i, 1), self.m_dataViewListCtrl1.GetValue(i, 2)])
                self.Parent.Info('SUCCESS: List saved')

        except Exception as e:
            self.Parent.Warn("ERROR: Save list:" + e.args[0])


    def loadFileToPanel(self, filepath):
        currentFileList = [str(self.m_dataViewListCtrl1.GetTextValue(i, 1)) for i in
                           range(self.m_dataViewListCtrl1.GetItemCount())]
        if filepath not in currentFileList:
            self.m_dataViewListCtrl1.AppendItem([True, filepath, "{:0.3f}".format(os.stat(filepath).st_size / 10e8)])

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
                # Try to resize column
                self.col_file.SetWidth(COLWIDTH)
        except Exception as e:
            #print(e.args[0])
            self.Parent.Warn("Load list error:" + e.args[0])


    def OnAutofind(self, event):
        """
        Find all matching files in top level directory
        :param event:
        :return:
        """
        self.btnAutoFind.Disable()
        if self.inputdir is not None:
            self.m_status.SetLabelText("Finding files ... please wait")
            imgtype = self.controller.db.getConfigByName(self.controller.currentconfig, 'IMAGE_TYPE')
            if imgtype is None:
                imgtype = '*.ims'
            else:
                imgtype = '*' + imgtype
            allfiles = [y for y in iglob(join(self.inputdir, '**', imgtype), recursive=True)]

            searchtext = self.m_tcSearch.GetValue()
            if (len(searchtext) > 0):
                allfiles = [f for f in allfiles if re.search(searchtext, f, flags=re.IGNORECASE)]

            #Exclude directories
            filenames = [f for f in allfiles if not isdir(f)]

            for fname in filenames:
                self.loadFileToPanel(fname)
                if DEBUG:
                    msg = 'FilePanel loaded: %s' % fname
                    print(msg)

            # Try to resize column
            self.col_file.SetWidth(COLWIDTH)
            msg = "Total Files loaded: %d" % len(filenames)
            self.m_status.SetLabelText(msg)
        else:
            self.Parent.Warn("Cannot autofind files when no directory is selected. Please select Top Level Directory.")

        self.btnAutoFind.Enable(True)

    def OnSelectall(self, event):
        for i in range(0, self.m_dataViewListCtrl1.GetItemCount()):
            self.m_dataViewListCtrl1.SetToggleValue(event.GetSelection(), i, 0)
        if DEBUG:
            print("Toggled selections to: ", event.GetSelection())

    def OnClearlist(self, event):
        if DEBUG:
            print("Clear items in list")
        self.m_dataViewListCtrl1.DeleteAllItems()


########################################################################
class ProcessRunPanel(ProcessPanel):
    def __init__(self, parent):
        super(ProcessRunPanel, self).__init__(parent)
        #self.m_panelImageOrder = ImagePanel(self)
        self.loadController()
        self.loadCaptions()

        # Bind progress update function
        EVT_RESULT(self, self.progressfunc)

        # Set timer handler
        self.start = {}

    def loadController(self):
        self.controller = self.Parent.controller

    def loadCaptions(self):
        self.controller.db.connect()
        processes = self.controller.db.getCaptions()
        self.m_checkListProcess.Clear()
        self.m_checkListProcess.AppendItems(processes)
        self.controller.db.closeconn()

    def OnShowDescription(self, event):
        """
        Pull the clicked on process description form the Database and display it in the description panel.  
        """
        self.controller.db.connect()
        ref = self.controller.db.getRef(event.String)
        desc = self.controller.db.getDescription(ref)

        self.m_stTitle.SetLabelText(event.String)
        self.m_stDescription.Clear()
        self.m_stDescription.WriteText(desc)
        self.Layout()
        self.controller.db.closeconn()

    def progressfunc(self, msg):
        """
        Update progress bars in progress table. This will be sent from the panel running a process 
        (from the controller) with a msg as a RESULTEVENT. 
        :param msg: message passed in to Proccess panel. Currently in the form
            (count, row, process, outputPath) 
        """
        (count, row, process, outputPath, update) = msg.data

        if count == 0:
            self.m_dataViewListCtrlRunning.AppendItem([process, outputPath, count, "Starting"])
            self.m_dataViewListColumnFilename.SetWidth(200)
            self.m_dataViewListColumnOutput.SetWidth(200)
            self.m_dataViewListCtrlRunning.Refresh()
            self.start[process] = time.time()

        elif count < 100:
            self.m_dataViewListCtrlRunning.SetValue(count, row=row, col=2)
            self.m_dataViewListCtrlRunning.SetValue("Running  - " + update, row=row, col=3)
            self.m_dataViewListCtrlRunning.Refresh()
            self.m_stOutputlog.SetLabelText("Running: %s for %s ...please wait" % (process, outputPath))

        elif count == 100:
            status ='Done'
            if process in self.start:
                endtime = time.time() - self.start[process]
                status = "%s (%d secs)" % ("Done", endtime)

            self.m_dataViewListCtrlRunning.SetValue(count, row=row, col=2)
            self.m_dataViewListCtrlRunning.SetValue(status, row=row, col=3)
            self.m_btnRunProcess.Enable()
            self.m_stOutputlog.SetLabelText("COMPLETED process %s " % process)

        else:
            self.m_dataViewListCtrlRunning.SetValue("ERROR in process - see log file : " + update, row=row, col=3)
            self.m_btnRunProcess.Enable()

    def OnShowResults(self, event):
        """
        Event handler for when a user clicks on a completed image in the process panel. Loads the segments and templates
        the index order for them. Users can then renumber and submit the segments to be ordered via the 
        self.CreateOrderFile function. 
        """

        # Get the file directory from the selected row.
        row = self.m_dataViewListCtrlRunning.ItemToRow(event.GetItem())
        process = self.m_dataViewListCtrlRunning.GetTextValue(row, 0)
        status = self.m_dataViewListCtrlRunning.GetTextValue(row, 3)
        if self.controller.db.getProcessFilesout(process) != 'NA' and status.startswith('Done'):
            self.segmentGridPath = self.m_dataViewListCtrlRunning.GetTextValue(row, 1)

            # Load filenames to Review Panel
            imglist = [y for y in iglob(join(self.segmentGridPath, '*.tiff'), recursive=False)]
            self.m_dataViewListCtrlReview.DeleteAllItems()
            for fname in imglist:
                self.m_dataViewListCtrlReview.AppendItem([False, fname, "{:0.3f}".format(os.stat(fname).st_size / 10e8)])

            self.m_Col_reviewFilename.SetWidth(COLWIDTH)

            # Launch Viewer in separate window
            viewerapp = wx.App()
            frame = ImageViewer(imglist)
            viewerapp.MainLoop()


    def OnDeleteImage(self, event):
        """
        Delete image from disk if marked in list
        :return:
        """
        dial = wx.MessageDialog(None, 'Are you sure you want to delete these files?', 'Question',
                                wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        ret = dial.ShowModal()
        if ret == wx.ID_YES:
            try:
                filenames = []
                for i in range(self.m_dataViewListCtrlReview.GetItemCount()):
                    fname = self.m_dataViewListCtrlReview.GetValue(i, 1)
                    if self.m_dataViewListCtrlReview.GetToggleValue(i, 0):
                        os.remove(fname)
                        msg = "PROCESSPANEL: Deleted file: %s" % fname
                        print(msg)
                    else:
                        filenames.append(fname)
                # Refresh list
                self.m_dataViewListCtrlReview.DeleteAllItems()
                for fname in filenames:
                    self.m_dataViewListCtrlReview.AppendItem([False, fname,"{:0.3f}".format(os.stat(fname).st_size / 10e8)])
                self.Refresh()
            except PermissionError as e:
                self.Parent.Warn('Windows Permission Error: file is still open so cannot delete: ', e.args[0])
            except Exception as e:
                self.Parent.Warn('Error: cannot delete selected file: ', e.args[0])


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


    def getDefaultOutputdir(self):
        """
        :return: the default output directory for the segmented images. If a problem occured, return default. 
        """
        default = "cropped"
        try:
            self.controller.db.connect()
            sdir = self.controller.db.getConfigByName(self.controller.currentconfig, 'CROPPED_IMAGE_FILES')
            if len(sdir) > 0:
                default = sdir
        except Exception as e:
            print("Error occured when getting the default output directory: {0}".format(str(e)))

        finally:
            self.controller.db.closeconn()
            return default

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
        try:
            if len(selections) <= 0:
                raise ValueError("No Processes selected. Please check at least one process then click Run.")

            # Get data from other panels
            filepanel = self.getFilePanel()
            filenames = []
            num_files = filepanel.m_dataViewListCtrl1.GetItemCount()
            outputdir = filepanel.txtOutputdir.GetValue()
            # Set output directory: if blank will use subdir in inputdir
            if len(outputdir) <= 0:
                outputdir = join(filepanel.txtInputdir.GetValue(), self.getDefaultOutputdir())
                if not exists(outputdir):
                    mkdir(outputdir)
            self.outputdir = outputdir

            if num_files > 0:
                # Get selected files and sort into groups
                for i in range(0, num_files):
                    if filepanel.m_dataViewListCtrl1.GetToggleValue(i, 0):
                        fname = filepanel.m_dataViewListCtrl1.GetValue(i, 1)
                        if not isdir(fname):
                            filenames.append(fname)
                if len(filenames) <= 0:
                    raise ValueError("No files selected in Files Panel")

                # For each process
                prow = 0
                for pcaption in selections:
                    p = self.controller.db.getRef(pcaption)
                    prow = self.controller.RunProcess(self, p, outputdir, filenames,prow)
                    prow += 1

            else:
                raise ValueError("No files selected - please go to Files Panel and add to list")
        except Exception as e:
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

    def OnStopProcessing( self, event ):
        self.controller.shutdown()
        while self.controller._stopevent.isSet():
            time.sleep(1)
            self.m_stOutputlog.SetLabelText('Called Stop processing .. please wait')
        self.m_stOutputlog.SetLabelText('Called Stop processing -complete')


########################################################################
class AppMain(wx.Listbook):
    def __init__(self, parent):
        """Constructor"""
        wx.Listbook.__init__(self, parent, wx.ID_ANY, style=wx.BK_DEFAULT)
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

        if sys.platform == 'win32':
            self.GetListView().SetColumnWidth(0, wx.LIST_AUTOSIZE)

    def Warn(self, message, caption='Warning!'):
        dlg = wx.MessageDialog(self, message, caption, wx.OK | wx.ICON_WARNING)
        dlg.ShowModal()
        dlg.Destroy()

    def Info(self, message, caption='Information'):
        dlg = wx.MessageDialog(self, message, caption, wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()




########################################################################
class AppFrame(wx.Frame):
    """
    Frame that holds all other widgets
    """

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        title = "Batch Crop Application [v %s]" % __version__
        wx.Frame.__init__(self, None, wx.ID_ANY,
                          title,
                          size=(1000, 720)
                          )

        self.Bind(wx.EVT_CLOSE, self.OnExit)
        panel = wx.Panel(self)

        notebook = AppMain(panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(notebook, 1, wx.ALL | wx.EXPAND, 5)
        panel.SetSizer(sizer)
        self.Layout()
        self.Center(wx.BOTH)
        self.Show()

    def OnExit(self, e):
        dial = wx.MessageDialog(None, 'Are you sure you want to quit?', 'Question',
                                wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

        ret = dial.ShowModal()

        if ret == wx.ID_YES:
            self.DestroyChildren()
            self.Destroy()

        else:
            e.Veto()

# ----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App()
    frame = AppFrame()
    app.MainLoop()
