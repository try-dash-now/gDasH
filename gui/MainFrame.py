# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Jun 17 2015)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.richtext

###########################################################################
## Class MainFrame
###########################################################################

class MainFrame ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"DasH", pos = wx.DefaultPosition, size = wx.Size( 1200,700 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		self.m_menubar_main = wx.MenuBar( 0 )
		self.SetMenuBar( self.m_menubar_main )
		
		gSizerMain = wx.GridSizer( 1, 3, 0, 0 )
		
		self.m_case_tree = wx.TreeCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), wx.TR_DEFAULT_STYLE|wx.TR_EDIT_LABELS|wx.TR_EXTENDED|wx.TR_HAS_BUTTONS|wx.TR_HAS_VARIABLE_ROW_HEIGHT|wx.HSCROLL|wx.TAB_TRAVERSAL|wx.VSCROLL|wx.WANTS_CHARS )
		gSizerMain.Add( self.m_case_tree, 0, wx.ALL|wx.EXPAND, 5 )
		
		bSizerLeft = wx.BoxSizer( wx.VERTICAL )
		
		self.m_file_editor = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		bSizerLeft.Add( self.m_file_editor, 1, wx.EXPAND |wx.ALL, 5 )
		
		self.m_log = wx.richtext.RichTextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER|wx.WANTS_CHARS )
		self.m_log.Enable( False )
		
		bSizerLeft.Add( self.m_log, 1, wx.EXPAND |wx.ALL, 5 )
		
		self.m_command_box = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE|wx.TE_READONLY )
		bSizerLeft.Add( self.m_command_box, 0, wx.ALL|wx.EXPAND, 5 )
		
		
		gSizerMain.Add( bSizerLeft, 1, wx.ALL|wx.EXPAND, 5 )
		
		
		self.SetSizer( gSizerMain )
		self.Layout()
		
		self.Centre( wx.BOTH )
		
		# Connect Events
		self.m_case_tree.Bind( wx.EVT_MOUSEWHEEL, self.case_tree_OnMouseWheel )
	
	def __del__( self ):
		pass
	
	
	# Virtual event handlers, overide them in your derived class
	def case_tree_OnMouseWheel( self, event ):
		event.Skip()
	

