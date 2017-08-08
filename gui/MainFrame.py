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
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"DasH", pos = wx.DefaultPosition, size = wx.Size( 1000,600 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		self.m_menubar_main = wx.MenuBar( 0 )
		self.SetMenuBar( self.m_menubar_main )
		
		gSizerMain = wx.GridSizer( 1, 2, 0, 0 )
		
		self.m_left_navigator = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		gSizerMain.Add( self.m_left_navigator, 3, wx.EXPAND |wx.ALL, 5 )
		
		sizer_right = wx.BoxSizer( wx.VERTICAL )
		
		self.m_file_editor = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		sizer_right.Add( self.m_file_editor, 6, wx.EXPAND, 5 )
		
		self.m_log = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_AUTO_URL|wx.VSCROLL|wx.TE_READONLY |wx.TE_RICH|wx.TE_MULTILINE&(~wx.TE_PROCESS_ENTER) )#richtext.RichTextCtrl |wx.WANTS_CHARS
		sizer_right.Add( self.m_log, 3, wx.ALL|wx.EXPAND, 5 )
		
		self.m_command_box = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,  wx.TE_PROCESS_ENTER)
		sizer_right.Add( self.m_command_box, 0, wx.ALL|wx.EXPAND, 1 )
		
		
		gSizerMain.Add( sizer_right, 7, wx.EXPAND|wx.ALL, 1 )
		
		
		self.SetSizer( gSizerMain )
		self.Layout()
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	

