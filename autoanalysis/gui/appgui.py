# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Jun 17 2015)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.grid
import wx.dataview
import wx.richtext

###########################################################################
## Class ConfigPanel
###########################################################################

class ConfigPanel ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 710,886 ), style = wx.TAB_TRAVERSAL )
		
		bSizer17 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_staticText66 = wx.StaticText( self, wx.ID_ANY, u"Configuration Parameters", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText66.Wrap( -1 )
		self.m_staticText66.SetFont( wx.Font( 14, 70, 90, 90, False, wx.EmptyString ) )
		
		bSizer17.Add( self.m_staticText66, 0, wx.ALL, 5 )
		
		self.m_staticline14 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer17.Add( self.m_staticline14, 0, wx.EXPAND |wx.ALL, 5 )
		
		self.m_status = wx.StaticText( self, wx.ID_ANY, u"These variables are required by the processing modules (change only the value not the name).  Enter new values and click Save Changes.", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_status.Wrap( 600 )
		self.m_status.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 71, 93, 90, False, wx.EmptyString ) )
		
		bSizer17.Add( self.m_status, 0, wx.ALL, 5 )
		
		bSizer14 = wx.BoxSizer( wx.HORIZONTAL )
		
		
		bSizer17.Add( bSizer14, 1, wx.ALL|wx.EXPAND, 5 )
		
		self.m_grid1 = wx.grid.Grid( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		
		# Grid
		self.m_grid1.CreateGrid( 20, 3 )
		self.m_grid1.EnableEditing( True )
		self.m_grid1.EnableGridLines( True )
		self.m_grid1.EnableDragGridSize( True )
		self.m_grid1.SetMargins( 0, 0 )
		
		# Columns
		self.m_grid1.EnableDragColMove( False )
		self.m_grid1.EnableDragColSize( True )
		self.m_grid1.SetColLabelSize( 50 )
		self.m_grid1.SetColLabelValue( 0, u"Name" )
		self.m_grid1.SetColLabelValue( 1, u"Value" )
		self.m_grid1.SetColLabelValue( 2, u"Description" )
		self.m_grid1.SetColLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
		
		# Rows
		self.m_grid1.EnableDragRowSize( True )
		self.m_grid1.SetRowLabelSize( 80 )
		self.m_grid1.SetRowLabelAlignment( wx.ALIGN_CENTRE, wx.ALIGN_CENTRE )
		
		# Label Appearance
		
		# Cell Defaults
		self.m_grid1.SetDefaultCellAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )
		bSizer17.Add( self.m_grid1, 0, wx.ALIGN_TOP|wx.EXPAND, 5 )
		
		bSizer21 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.btnSave = wx.Button( self, wx.ID_ANY, u"Save Changes", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.btnSave.SetDefault() 
		self.btnSave.SetForegroundColour( wx.Colour( 255, 255, 0 ) )
		self.btnSave.SetBackgroundColour( wx.Colour( 0, 128, 0 ) )
		
		bSizer21.Add( self.btnSave, 0, wx.ALL, 5 )
		
		self.m_button13 = wx.Button( self, wx.ID_ANY, u"Add", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer21.Add( self.m_button13, 0, wx.ALL, 5 )
		
		
		bSizer17.Add( bSizer21, 1, wx.ALL, 5 )
		
		
		self.SetSizer( bSizer17 )
		self.Layout()
		
		# Connect Events
		self.btnSave.Bind( wx.EVT_BUTTON, self.OnSaveConfig )
		self.m_button13.Bind( wx.EVT_BUTTON, self.OnAddRow )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnSaveConfig( self, event ):
		event.Skip()
	
	def OnAddRow( self, event ):
		event.Skip()
	

###########################################################################
## Class ProcessPanel
###########################################################################

class ProcessPanel ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 1277,941 ), style = wx.TAB_TRAVERSAL )
		
		panelMainSizer = wx.BoxSizer( wx.VERTICAL )
		
		self.m_staticText85 = wx.StaticText( self, wx.ID_ANY, u"Run Selected Processes", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText85.Wrap( -1 )
		self.m_staticText85.SetFont( wx.Font( 14, 74, 90, 90, False, "Arial" ) )
		
		panelMainSizer.Add( self.m_staticText85, 0, wx.ALL, 5 )
		
		self.m_staticline7 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		panelMainSizer.Add( self.m_staticline7, 0, wx.EXPAND |wx.ALL, 5 )
		
		bSizer19 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_panelImageOrder = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.m_panelImageOrder.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWTEXT ) )
		
		bSizer201 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_imageViewer = wx.dataview.DataViewListCtrl( self.m_panelImageOrder, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_imageViewer.SetMinSize( wx.Size( 600,800 ) )
		
		self.m_colOrder = self.m_imageViewer.AppendTextColumn( u"Order" )
		self.m_colThumb = self.m_imageViewer.AppendIconTextColumn( u"Thumbnail" )
		bSizer201.Add( self.m_imageViewer, 0, wx.ALL, 5 )
		
		
		self.m_panelImageOrder.SetSizer( bSizer201 )
		self.m_panelImageOrder.Layout()
		bSizer201.Fit( self.m_panelImageOrder )
		bSizer19.Add( self.m_panelImageOrder, 1, wx.EXPAND |wx.ALL, 5 )
		
		bSizer20 = wx.BoxSizer( wx.VERTICAL )
		
		m_checkListProcessChoices = []
		self.m_checkListProcess = wx.CheckListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_checkListProcessChoices, wx.LB_MULTIPLE )
		bSizer20.Add( self.m_checkListProcess, 0, wx.ALL, 5 )
		
		self.m_stTitle = wx.StaticText( self, wx.ID_ANY, u"TITLE", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_stTitle.Wrap( -1 )
		self.m_stTitle.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 71, 90, 92, False, wx.EmptyString ) )
		
		bSizer20.Add( self.m_stTitle, 0, wx.ALL, 5 )
		
		self.m_stDescription = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER|wx.WANTS_CHARS )
		self.m_stDescription.SetMaxSize( wx.Size( -1,150 ) )
		
		bSizer20.Add( self.m_stDescription, 1, wx.EXPAND |wx.ALL, 5 )
		
		bSizer16 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_btnRunProcess = wx.Button( self, wx.ID_ANY, u"Run", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_btnRunProcess.SetForegroundColour( wx.Colour( 255, 255, 0 ) )
		self.m_btnRunProcess.SetBackgroundColour( wx.Colour( 0, 128, 0 ) )
		
		bSizer16.Add( self.m_btnRunProcess, 0, wx.ALL, 5 )
		
		self.btnLog = wx.Button( self, wx.ID_ANY, u"Show Log", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer16.Add( self.btnLog, 0, wx.ALL, 5 )
		
		self.m_button15 = wx.Button( self, wx.ID_ANY, u"Clear Results", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer16.Add( self.m_button15, 0, wx.ALL, 5 )
		
		self.m_btnSaveOrder = wx.Button( self, wx.ID_ANY, u"Save Order", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer16.Add( self.m_btnSaveOrder, 0, wx.ALL, 5 )
		
		
		bSizer20.Add( bSizer16, 1, wx.ALL, 5 )
		
		self.m_dataViewListCtrlRunning = wx.dataview.DataViewListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.dataview.DV_ROW_LINES|wx.FULL_REPAINT_ON_RESIZE|wx.VSCROLL )
		self.m_dataViewListCtrlRunning.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 90, 90, False, wx.EmptyString ) )
		self.m_dataViewListCtrlRunning.SetMinSize( wx.Size( -1,200 ) )
		
		self.m_dataViewListColumnProcess = self.m_dataViewListCtrlRunning.AppendTextColumn( u"Process" )
		self.m_dataViewListColumnFilename = self.m_dataViewListCtrlRunning.AppendTextColumn( u"Filename" )
		self.m_dataViewListColumnStatus = self.m_dataViewListCtrlRunning.AppendProgressColumn( u"Status" )
		self.m_dataViewListColumnOutput = self.m_dataViewListCtrlRunning.AppendTextColumn( u"Output" )
		bSizer20.Add( self.m_dataViewListCtrlRunning, 0, wx.ALL|wx.EXPAND, 5 )
		
		self.m_stOutputlog = wx.StaticText( self, wx.ID_ANY, u"Processing status", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_stOutputlog.Wrap( -1 )
		bSizer20.Add( self.m_stOutputlog, 0, wx.ALL, 5 )
		
		
		bSizer19.Add( bSizer20, 1, wx.EXPAND, 5 )
		
		bSizer21 = wx.BoxSizer( wx.VERTICAL )
		
		
		bSizer19.Add( bSizer21, 1, wx.EXPAND, 5 )
		
		
		panelMainSizer.Add( bSizer19, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( panelMainSizer )
		self.Layout()
		
		# Connect Events
		self.m_checkListProcess.Bind( wx.EVT_LISTBOX, self.OnShowDescription )
		self.m_checkListProcess.Bind( wx.EVT_CHECKLISTBOX, self.OnShowDescription )
		self.m_btnRunProcess.Bind( wx.EVT_BUTTON, self.OnRunScripts )
		self.btnLog.Bind( wx.EVT_BUTTON, self.OnShowLog )
		self.m_button15.Bind( wx.EVT_BUTTON, self.OnClearWindow )
		self.m_btnSaveOrder.Bind( wx.EVT_BUTTON, self.OnSaveOrder )
		self.Bind( wx.dataview.EVT_DATAVIEW_ITEM_ACTIVATED, self.OnShowResults, id = wx.ID_ANY )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnShowDescription( self, event ):
		event.Skip()
	
	
	def OnRunScripts( self, event ):
		event.Skip()
	
	def OnShowLog( self, event ):
		event.Skip()
	
	def OnClearWindow( self, event ):
		event.Skip()
	
	def OnSaveOrder( self, event ):
		event.Skip()
	
	def OnShowResults( self, event ):
		event.Skip()
	

###########################################################################
## Class ComparePanel
###########################################################################

class ComparePanel ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 781,1025 ), style = wx.SIMPLE_BORDER|wx.TAB_TRAVERSAL )
		
		bSizer1 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_staticText18 = wx.StaticText( self, wx.ID_ANY, u"Comparison of Group Statistics", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText18.Wrap( -1 )
		self.m_staticText18.SetFont( wx.Font( 14, 74, 90, 90, False, "Arial" ) )
		
		bSizer1.Add( self.m_staticText18, 0, wx.ALIGN_LEFT|wx.ALL, 5 )
		
		self.m_staticline1 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer1.Add( self.m_staticline1, 0, wx.EXPAND, 5 )
		
		self.m_staticText62 = wx.StaticText( self, wx.ID_ANY, u"Statistical comparison of two datasets", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText62.Wrap( -1 )
		bSizer1.Add( self.m_staticText62, 0, wx.ALL, 5 )
		
		fgSizer2 = wx.FlexGridSizer( 3, 4, 0, 0 )
		fgSizer2.SetFlexibleDirection( wx.HORIZONTAL )
		fgSizer2.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_NONE )
		
		self.m_staticText19 = wx.StaticText( self, wx.ID_ANY, u"Group 1", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText19.Wrap( -1 )
		fgSizer2.Add( self.m_staticText19, 0, wx.ALL, 5 )
		
		self.m_tcGp1 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 200,-1 ), 0 )
		fgSizer2.Add( self.m_tcGp1, 0, wx.ALL, 5 )
		
		self.m_tcGp1Files = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 256,-1 ), 0 )
		fgSizer2.Add( self.m_tcGp1Files, 0, wx.ALL, 5 )
		
		self.m_btnGp1 = wx.Button( self, wx.ID_ANY, u"Browse", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer2.Add( self.m_btnGp1, 0, wx.ALL, 5 )
		
		self.m_staticText20 = wx.StaticText( self, wx.ID_ANY, u"Group 2", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText20.Wrap( -1 )
		fgSizer2.Add( self.m_staticText20, 0, wx.ALL, 5 )
		
		self.m_tcGp2 = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 200,-1 ), 0 )
		fgSizer2.Add( self.m_tcGp2, 0, wx.ALL, 5 )
		
		self.m_tcGp2Files = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 256,-1 ), 0 )
		fgSizer2.Add( self.m_tcGp2Files, 0, wx.ALL, 5 )
		
		self.m_btnGp2 = wx.Button( self, wx.ID_ANY, u"Browse", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer2.Add( self.m_btnGp2, 0, wx.ALL, 5 )
		
		self.m_btnCompareRun = wx.Button( self, wx.ID_ANY, u"Run", wx.DefaultPosition, wx.Size( -1,-1 ), 0 )
		self.m_btnCompareRun.SetForegroundColour( wx.Colour( 255, 255, 0 ) )
		self.m_btnCompareRun.SetBackgroundColour( wx.Colour( 0, 128, 64 ) )
		
		fgSizer2.Add( self.m_btnCompareRun, 0, wx.ALL, 5 )
		
		
		bSizer1.Add( fgSizer2, 1, wx.ALL, 5 )
		
		bSizer18 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_tcResults = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 500,350 ), wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_WORDWRAP|wx.SIMPLE_BORDER|wx.VSCROLL )
		bSizer18.Add( self.m_tcResults, 0, wx.EXPAND, 5 )
		
		
		bSizer1.Add( bSizer18, 1, wx.ALIGN_TOP|wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer1 )
		self.Layout()
		
		# Connect Events
		self.m_btnGp1.Bind( wx.EVT_BUTTON, self.OnBrowseGp1 )
		self.m_btnGp2.Bind( wx.EVT_BUTTON, self.OnBrowseGp2 )
		self.m_btnCompareRun.Bind( wx.EVT_BUTTON, self.OnCompareRun )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnBrowseGp1( self, event ):
		event.Skip()
	
	def OnBrowseGp2( self, event ):
		event.Skip()
	
	def OnCompareRun( self, event ):
		event.Skip()
	

###########################################################################
## Class WelcomePanel
###########################################################################

class WelcomePanel ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 783,888 ), style = wx.TAB_TRAVERSAL )
		
		bSizer18 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_staticText23 = wx.StaticText( self, wx.ID_ANY, u"Automated Analysis Application", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText23.Wrap( -1 )
		self.m_staticText23.SetFont( wx.Font( 14, 71, 90, 90, False, wx.EmptyString ) )
		
		bSizer18.Add( self.m_staticText23, 0, wx.ALL, 5 )
		
		self.m_staticline2 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer18.Add( self.m_staticline2, 0, wx.EXPAND |wx.ALL, 5 )
		
		self.m_richText1 = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_READONLY|wx.NO_BORDER|wx.VSCROLL|wx.WANTS_CHARS, wx.DefaultValidator, u"welcome" )
		bSizer18.Add( self.m_richText1, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer18 )
		self.Layout()
	
	def __del__( self ):
		pass
	

###########################################################################
## Class FilesPanel
###########################################################################

class FilesPanel ( wx.Panel ):
	
	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size( 1348,782 ), style = wx.TAB_TRAVERSAL )
		
		bSizer5 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_staticText23 = wx.StaticText( self, wx.ID_ANY, u"Select Images for processing", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText23.Wrap( -1 )
		self.m_staticText23.SetFont( wx.Font( 14, 71, 90, 90, False, wx.EmptyString ) )
		
		bSizer5.Add( self.m_staticText23, 0, wx.ALL, 5 )
		
		self.m_staticText25 = wx.StaticText( self, wx.ID_ANY, u"Browse to top level directory then AutoFind and/or manually add initial data files with Drag N Drop. ", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText25.Wrap( -1 )
		self.m_staticText25.SetFont( wx.Font( wx.NORMAL_FONT.GetPointSize(), 70, 93, 90, False, wx.EmptyString ) )
		
		bSizer5.Add( self.m_staticText25, 0, wx.ALL, 5 )
		
		self.m_staticline2 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
		bSizer5.Add( self.m_staticline2, 0, wx.EXPAND |wx.ALL, 5 )
		
		bSizer16 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.panel_right = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), 0 )
		self.panel_right.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWTEXT ) )
		self.panel_right.SetMaxSize( wx.Size( 400,-1 ) )
		
		bSizerThumb = wx.BoxSizer( wx.VERTICAL )
		
		self.preview_thumbnail = wx.StaticBitmap( self.panel_right, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizerThumb.Add( self.preview_thumbnail, 0, wx.ALL, 5 )
		
		
		self.panel_right.SetSizer( bSizerThumb )
		self.panel_right.Layout()
		bSizerThumb.Fit( self.panel_right )
		bSizer16.Add( self.panel_right, 1, wx.EXPAND |wx.ALL, 5 )
		
		bSizer18 = wx.BoxSizer( wx.VERTICAL )
		
		fgSizer4 = wx.FlexGridSizer( 0, 3, 0, 0 )
		fgSizer4.SetFlexibleDirection( wx.BOTH )
		fgSizer4.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_NONE )
		
		self.m_staticText26 = wx.StaticText( self, wx.ID_ANY, u"Top level directory", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText26.Wrap( -1 )
		fgSizer4.Add( self.m_staticText26, 0, wx.ALL, 5 )
		
		self.txtInputdir = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 300,-1 ), 0 )
		fgSizer4.Add( self.txtInputdir, 0, wx.ALL, 5 )
		
		self.m_button18 = wx.Button( self, wx.ID_ANY, u"Browse", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer4.Add( self.m_button18, 0, wx.ALL, 5 )
		
		self.m_staticText67 = wx.StaticText( self, wx.ID_ANY, u"Output directory", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText67.Wrap( -1 )
		self.m_staticText67.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_WINDOWTEXT ) )
		
		fgSizer4.Add( self.m_staticText67, 0, wx.ALL, 5 )
		
		self.txtOutputdir = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 300,-1 ), 0 )
		fgSizer4.Add( self.txtOutputdir, 0, wx.ALL, 5 )
		
		self.m_button19 = wx.Button( self, wx.ID_ANY, u"Browse", wx.DefaultPosition, wx.DefaultSize, 0 )
		fgSizer4.Add( self.m_button19, 0, wx.ALL, 5 )
		
		self.m_staticText27 = wx.StaticText( self, wx.ID_ANY, u"Filename search text", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText27.Wrap( -1 )
		self.m_staticText27.SetToolTipString( u"Select files with this search text (eg experiment code).  This is used as the prefix for batch compiled files." )
		
		fgSizer4.Add( self.m_staticText27, 0, wx.ALL, 5 )
		
		self.m_tcSearch = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 300,-1 ), 0 )
		fgSizer4.Add( self.m_tcSearch, 0, wx.ALL, 5 )
		
		self.btnAutoFind = wx.Button( self, wx.ID_ANY, u"AutoFind", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.btnAutoFind.SetForegroundColour( wx.Colour( 255, 255, 0 ) )
		self.btnAutoFind.SetBackgroundColour( wx.Colour( 0, 128, 64 ) )
		
		fgSizer4.Add( self.btnAutoFind, 0, wx.ALL, 5 )
		
		self.m_staticText251 = wx.StaticText( self, wx.ID_ANY, u"Add Files Manually", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText251.Wrap( -1 )
		fgSizer4.Add( self.m_staticText251, 0, wx.ALL, 5 )
		
		self.m_tcDragdrop = wx.TextCtrl( self, wx.ID_ANY, u"Drag data files here", wx.DefaultPosition, wx.Size( 300,100 ), wx.TE_READONLY|wx.TE_WORDWRAP )
		self.m_tcDragdrop.SetBackgroundColour( wx.Colour( 191, 191, 255 ) )
		
		fgSizer4.Add( self.m_tcDragdrop, 0, 0, 5 )
		
		self.m_cbSelectall = wx.CheckBox( self, wx.ID_ANY, u"Select All", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_cbSelectall.SetValue(True) 
		fgSizer4.Add( self.m_cbSelectall, 0, wx.ALL, 5 )
		
		self.m_staticText64 = wx.StaticText( self, wx.ID_ANY, u"Store Selected File List", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText64.Wrap( -1 )
		fgSizer4.Add( self.m_staticText64, 0, wx.ALL, 5 )
		
		bSizer17 = wx.BoxSizer( wx.HORIZONTAL )
		
		self.m_button21 = wx.Button( self, wx.ID_ANY, u"Load list", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer17.Add( self.m_button21, 0, wx.ALL, 5 )
		
		self.m_button20 = wx.Button( self, wx.ID_ANY, u"Save list", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer17.Add( self.m_button20, 0, wx.ALL, 5 )
		
		self.btnClearlist = wx.Button( self, wx.ID_ANY, u"Clear list", wx.DefaultPosition, wx.DefaultSize, 0 )
		bSizer17.Add( self.btnClearlist, 0, wx.ALIGN_CENTER|wx.ALL, 5 )
		
		
		fgSizer4.Add( bSizer17, 1, wx.EXPAND, 5 )
		
		
		bSizer18.Add( fgSizer4, 1, wx.ALIGN_TOP|wx.EXPAND, 5 )
		
		self.m_staticText252 = wx.StaticText( self, wx.ID_ANY, u"Click on filename to view thumbnail (may be delay if file is on archived storage)", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_staticText252.Wrap( -1 )
		bSizer18.Add( self.m_staticText252, 0, wx.ALL, 5 )
		
		self.m_dataViewListCtrl1 = wx.dataview.DataViewListCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), wx.dataview.DV_MULTIPLE|wx.HSCROLL|wx.VSCROLL )
		self.m_dataViewListCtrl1.SetMinSize( wx.Size( -1,300 ) )
		
		self.col_selected = self.m_dataViewListCtrl1.AppendToggleColumn( u"Select" )
		self.col_file = self.m_dataViewListCtrl1.AppendTextColumn( u"File" )
		self.col_size = self.m_dataViewListCtrl1.AppendTextColumn( u"size (GB)" )
		bSizer18.Add( self.m_dataViewListCtrl1, 0, wx.ALIGN_TOP|wx.ALL|wx.EXPAND, 5 )
		
		self.m_status = wx.StaticText( self, wx.ID_ANY, u"Select required files then go to Run Processes", wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_status.Wrap( -1 )
		bSizer18.Add( self.m_status, 0, wx.ALL, 5 )
		
		
		bSizer16.Add( bSizer18, 1, wx.ALIGN_TOP|wx.EXPAND, 5 )
		
		
		bSizer5.Add( bSizer16, 1, wx.EXPAND, 5 )
		
		
		self.SetSizer( bSizer5 )
		self.Layout()
		
		# Connect Events
		self.m_button18.Bind( wx.EVT_BUTTON, self.OnInputdir )
		self.m_button19.Bind( wx.EVT_BUTTON, self.OnOutputdir )
		self.btnAutoFind.Bind( wx.EVT_BUTTON, self.OnAutofind )
		self.m_cbSelectall.Bind( wx.EVT_CHECKBOX, self.OnSelectall )
		self.m_button21.Bind( wx.EVT_BUTTON, self.OnLoadList )
		self.m_button20.Bind( wx.EVT_BUTTON, self.OnSaveList )
		self.btnClearlist.Bind( wx.EVT_BUTTON, self.OnClearlist )
		self.Bind( wx.dataview.EVT_DATAVIEW_COLUMN_HEADER_CLICK, self.OnColClick, id = wx.ID_ANY )
		self.Bind( wx.dataview.EVT_DATAVIEW_SELECTION_CHANGED, self.OnFileClicked, id = wx.ID_ANY )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def OnInputdir( self, event ):
		event.Skip()
	
	def OnOutputdir( self, event ):
		event.Skip()
	
	def OnAutofind( self, event ):
		event.Skip()
	
	def OnSelectall( self, event ):
		event.Skip()
	
	def OnLoadList( self, event ):
		event.Skip()
	
	def OnSaveList( self, event ):
		event.Skip()
	
	def OnClearlist( self, event ):
		event.Skip()
	
	def OnColClick( self, event ):
		event.Skip()
	
	def OnFileClicked( self, event ):
		event.Skip()
	

###########################################################################
## Class dlgLogViewer
###########################################################################

class dlgLogViewer ( wx.Dialog ):
	
	def __init__( self, parent ):
		wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Log Viewer", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		bSizer15 = wx.BoxSizer( wx.VERTICAL )
		
		self.tcLog = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_WORDWRAP )
		self.tcLog.SetMinSize( wx.Size( 400,700 ) )
		
		bSizer15.Add( self.tcLog, 0, wx.ALL, 5 )
		
		
		self.SetSizer( bSizer15 )
		self.Layout()
		bSizer15.Fit( self )
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	

