#!/usr/bin/python
'''The MIT License (MIT)
Copyright (c) 2017 Yu Xiong Wei(try.dash.now@gmail.com)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.'''
__author__ = 'sean yu (Yu, Xiongwei)'
__doc__ = '''
it's GUI of DasH aka Do as Human
created 2017-05-06 by Sean Yu
'''


import wx.grid as gridlib
import wx
from gui.MainFrame import MainFrame
import os

class FileEditor(wx.Panel):
    editor =None
    font_size=10
    parent=None
    type = None
    sessions_node =None
    function_node =None
    case_suite_node =None
    def __init__(self, parent, title='pageOne', type ='grid'):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.type = type

        #self.editor = wx.TextCtrl(self, style = wx.TE_MULTILINE|wx.TE_RICH2|wx.EXPAND|wx.ALL, size=(-1,-1))
        if type in ['text']:

            self.editor = wx.richtext.RichTextCtrl( self, -1, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER|wx.WANTS_CHARS )
        else:
            self.editor= gridlib.Grid(self)
            self.editor.CreateGrid(50, 5)
            col = self.editor.GetNumberCols()
            row = self.editor.GetNumberRows()

            function_color ='black'
            arg_color = 'blue'
            for c in range(0, col):
                if c < 1 :
                    self.editor.SetColLabelValue(c, 'Function Name')
                else:
                    self.editor.SetColLabelValue(c, 'arg# {}'.format(c))
                for r in range (0, row):
                    self.editor.SetCellTextColour(r,c,function_color if c <1 else arg_color)

            for r in range (0, row):
                    self.editor.SetCellFont(r, 0, wx.Font(self.font_size,wx.SWISS, wx.NORMAL, wx.BOLD ))

        self.editor.Bind( wx.EVT_MOUSEWHEEL, self.editor_OnMouseWheel )
        sizer = wx.BoxSizer()
        sizer.Add(self.editor, 1, wx.EXPAND)
        self.SetSizer(sizer)
    def editor_OnMouseWheel(self,event):
        min_font_size = 5
        interval_step = 2
        if event.ControlDown():
            pass
        else:
            return

        if event.GetWheelRotation() < 0:
                if self.font_size>min_font_size:
                    self.font_size-=interval_step
        else:
            self.font_size+=1
        if self.type in ['text']:
            f =self.editor.GetFont()
            f.PointSize= self.font_size
            self.editor.SetFont(f)
        else:
            col = self.editor.GetNumberCols()
            row = self.editor.GetNumberRows()
            for c in range(0, col):
                for r in range (0, row):
                    f = self.editor.GetCellFont(r, c)
                    f.PointSize = self.font_size
                    self.editor.SetCellFont(r, c, f)
            self.Refresh()
        #wx.StaticText(self, -1, "THIS IS A PAGE OBJECT", (20,20))
from lib.common import get_folder_item
import ConfigParser
class DasHFrame(MainFrame):#wx.Frame
    ini_setting = None
    edit_area=None
    def __init__(self,parent=None, ini_file = './gDasH.ini'):
        #wx.Frame.__init__(self, None, title="DasH")
        MainFrame.__init__(self, parent=parent)
        self.ini_setting = ConfigParser.ConfigParser()
        self.ini_setting.read(ini_file)

        #self.m_editor.WriteText('welcome to dash world')
        self.m_log.WriteText('Happy Birthday!')
        self.m_command_box.WriteText('read only,but select copy allowed')
        fileMenu = wx.Menu()
        open_test_suite = fileMenu.Append(wx.NewId(), "Open TestSuite", "Open a Test Suite")
        open_test_case = fileMenu.Append(wx.NewId(), "Open TestCase", "Open a Test Case")
        self.m_menubar_main.Append(fileMenu, "&Open TestSuite")

        bSizerLeft = wx.BoxSizer( wx.VERTICAL )
        self.m_file_editor = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizerLeft.Add( self.m_file_editor, 1, wx.EXPAND |wx.ALL, 5 )
        p = self.m_file_editor
        from wx.aui import AuiNotebook
        nb = AuiNotebook(p)
        self.edit_area =nb

        self.m_case_tree.Hide()
        self.m_case_tree = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.m_case_tree.Show()
        case_nb = AuiNotebook(self.m_case_tree)
        self.case_suite_node =wx.TreeCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), wx.TR_DEFAULT_STYLE|wx.TR_EDIT_LABELS|wx.TR_EXTENDED|wx.TR_HAS_BUTTONS|wx.TR_HAS_VARIABLE_ROW_HEIGHT|wx.HSCROLL|wx.TAB_TRAVERSAL|wx.VSCROLL|wx.WANTS_CHARS )
        self.function_node =wx.TreeCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), wx.TR_DEFAULT_STYLE|wx.TR_EDIT_LABELS|wx.TR_EXTENDED|wx.TR_HAS_BUTTONS|wx.TR_HAS_VARIABLE_ROW_HEIGHT|wx.HSCROLL|wx.TAB_TRAVERSAL|wx.VSCROLL|wx.WANTS_CHARS )
        self.session_node =wx.TreeCtrl( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), wx.TR_DEFAULT_STYLE|wx.TR_EDIT_LABELS|wx.TR_EXTENDED|wx.TR_HAS_BUTTONS|wx.TR_HAS_VARIABLE_ROW_HEIGHT|wx.HSCROLL|wx.TAB_TRAVERSAL|wx.VSCROLL|wx.WANTS_CHARS )

        case_nb.AddPage(self.session_node, 'SESSION')
        case_nb.AddPage(self.function_node, 'FUNCTION')
        case_nb.AddPage(self.case_suite_node, 'CASE')
                # create the page windows as children of the notebook
        sizer = wx.BoxSizer()
        sizer.Add(case_nb, 1, wx.EXPAND)
        self.m_case_tree.SetSizer(sizer)
        #self.session_node.SetSizer(sizer)
        #self.case_suite_node.SetSizer(sizer)
        if False:
            page1 = FileEditor(nb, 'a', type='text')
            page2 = FileEditor(nb, 'b')
            page3 = FileEditor(nb)
            nb.AddPage(page1, "Page 1")
            nb.AddPage(page2, "Page 2")
            nb.AddPage(page3, "Page 3")

            page1.editor.WriteText('aaa')
            # add the pages to the notebook with the label to show on the tab

            page1.editor.WriteText('aaa')
            page2.editor.WriteText('bbbb')
            page3.editor.WriteText('aaacccc')
            page1.editor.BeginTextColour((255,0,255))
            page1.editor.WriteText('color')
            page1.editor.BeginFontSize( 20)
            page1.editor.BeginTextColour((0,0,255))
            page1.editor.WriteText('xcolor')

        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        self.m_file_editor.SetSizer(sizer)

        mid_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        mid_sizer.Add(self.m_file_editor, 6, wx.EXPAND)
        mid_sizer.Add(self.m_log,3 ,wx.EXPAND)
        mid_sizer.Add(self.m_command_box, 1, wx.EXPAND)

        main_sizer.Add(self.m_case_tree,3,wx.EXPAND)
        main_sizer.Add(mid_sizer,7,wx.EXPAND)
        #main_sizer.Add(self.m_case_steps,0,wx.EXPAND)


        self.SetSizer(main_sizer)
        self.build_suite_tree()
    def add_item_to_subfolder_in_tree(self,node):
        subfolder_path_name = self.case_suite_node.GetPyData(node)['path_name']
        items = get_folder_item(subfolder_path_name)
        if items is None:
            self.case_suite_node.SetItemText(node, self.m_case_tree.GetItemText(node)+' Not Exists!!!')
            self.case_suite_node.SetItemTextColour(node, wx.Colour(255,0,0))
            return
        for i in items:
            path_name = '{}/{}'.format(subfolder_path_name,i)

            base_name = os.path.basename(i)
            item_info = wx.TreeItemData({'path_name':path_name})
            new_item = self.case_suite_node.InsertItem(node, node, base_name)
            self.case_suite_node.SetItemData(new_item, item_info)

            if os.path.isdir(path_name):
                self.case_suite_node.SetItemHasChildren(new_item)
                #self.m_case_tree.ItemHasChildren()
                #self.m_case_tree.InsertItem(new_item,new_item,'')

    def build_suite_tree(self):
        suite_path = os.path.abspath(self.ini_setting.get('dash','test_suite_path'))
        if not os.path.exists(suite_path):
            suite_path= os.path.abspath(os.path.curdir)
        base_name = os.path.basename(suite_path)


        root =self.case_suite_node.AddRoot(base_name)
        item_info = wx.TreeItemData({'path_name':suite_path})
        self.case_suite_node.SetItemData(root, item_info)
        self.add_item_to_subfolder_in_tree(root)



        if False:
            for i in item_list.sort():
                base_name = os.path.basename(i)
            if os.path.isdir(i):
                sub_folder = self.m_case_tree.AppendItem(root,base_name)
                self.m_case_tree.ItemHasChildren(sub_folder)
            else:
                self.m_case_tree.AppendItem(root, base_name)


            sub_folder = self.m_case_tree.AppendItem(root,'TestSuiteName 2')
        #self.m_case_tree.InsertItem
            for i in range(10):
                tmp = self.m_case_tree.InsertItem(sub_folder, sub_folder, 'case %d'%(i+1))

                self.m_case_tree.SetItemTextColour(tmp ,wx.Colour(255-10*i,10*i,i*i))

        self.case_suite_node.Expand(root)

    def OnSelChanged(self, event):
        item =  event.GetItem()
        self.display.SetLabel(self.tree.GetItemText(item))
    #def case_tree_OnMouseWheel(self, event):

    def m_case_treeOnLeftDClick(self, event):
        ht_item =self.m_case_tree.GetSelection()
        #ht_item = self.HitTest(event.GetPosition())
        item_name = self.m_case_tree.GetItemText(ht_item)
        if self.m_case_tree.ItemHasChildren(ht_item):
            if self.m_case_tree.IsExpanded(ht_item):
                self.m_case_tree.Collapse(ht_item)
            else:
                self.m_case_tree.ExpandAllChildren(ht_item)
        else:
            type = 'grid'
            new_page = FileEditor(self.edit_area, 'a', type= type)
            self.edit_area.AddPage(new_page, item_name)

    def m_case_treeOnTreeItemExpanding(self,event):
        ht_item =self.case_suite_node.GetSelection()
        try:
            item_info = self.m_case_tree.GetPyData(ht_item)

            if 0== self.m_case_tree.GetChildrenCount(ht_item):
                if os.path.isdir(item_info['path_name']):
                    self.add_item_to_subfolder_in_tree(ht_item)
        except Exception as e:
            pass
