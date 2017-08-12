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
from lib.common import load_bench, caller_stack_info,info, get_next_in_ring_list
import re
import time
import threading
class SessionTab(wx.Panel):
    stdout=None
    stderr=None
    parent = None
    type = type
    output_window = None
    cmd_window = None
    session = None
    alive =False
    output_lock = None
    font_point = None
    history_cmd = None
    history_cmd_index = 0
    sequence_queue =None
    def on_close(self):
        self.alive = False
        self.session.close_session()
        #self.session.sleep(0.001)
        info('tab {} closed!!!'.format(self.session.name))

    def update_output(self):
        status =True
        while( status):
            try:
                status = self.alive and self.session.session_status
            except Exception as e :
                time.sleep(0.001)
                break
            #time.sleep(0.05)
            self.output_lock.acquire()
            response = self.session.read_display_buffer()
            ansi_escape = re.compile(r'\x1b[^m]*m*|'+r'\x1b(' \
             r'(\[\??\d+[hl])|' \
             r'([=<>a-kzNM78])|' \
             r'([\(\)][a-b0-2])|' \
             r'(\[\d{0,2}[ma-dgkjqi])|' \
             r'(\[\d+;\d+[hfy]?)|' \
             r'(\[;?[hf])|' \
             r'(#[3-68])|' \
             r'([01356]n)|' \
             r'(O[mlnp-z]?)|' \
             r'(/Z)|' \
             r'(\d+)|' \
             r'(\[\?\d;\d0c)|' \
             r'(\d;\dR))'
             , flags=re.IGNORECASE)
            response = ansi_escape.sub('', response)
            BACKSPACE = chr(8)
            #response = re.sub(chr(32)+BACKSPACE,'',response)

            BACKSPACE_pat = '.'+BACKSPACE#+'\[\d+[;]{0,1}\d*m'#+chr(27)+'\[0'
            if len(response)!=0:
                if False:
                    whole_text = self.output_window.GetValue()
                    last_index = len(whole_text)
                    total_BS_in_response = int(response.count(BACKSPACE))
                    start_BS = response.find(BACKSPACE)
                    end_BS = response.rfind(BACKSPACE)+1
                    start = last_index-total_BS_in_response-1
                    end = last_index
                    if total_BS_in_response:
                        self.output_window.Remove(start ,end)
                        #wx.CallAfter(self.output_window.Remove,start ,end)
                        response= response[:start_BS]+response[end_BS:]
                        #response =''

                if re.search('error|err|fail|wrong',response.lower()):
                    self.output_window.SetDefaultStyle(wx.TextAttr(wx.RED,  wx.YELLOW, font =wx.Font(self.font_point+2, family = wx.DEFAULT, style = wx.NORMAL, weight = wx.BOLD, faceName = 'Consolas')))
                    #wx.CallAfter(self.output_window.SetDefaultStyle,wx.TextAttr(wx.RED,  wx.YELLOW, font =wx.Font(self.font_point+2, family = wx.DEFAULT, style = wx.NORMAL, weight = wx.BOLD, faceName = 'Consolas')))
                else:
                    self.output_window.SetDefaultStyle(wx.TextAttr(wx.GREEN,  wx.BLACK,font =wx.Font(self.font_point, family = wx.DEFAULT, style = wx.NORMAL, weight = wx.NORMAL, faceName = 'Consolas')))
                    #wx.CallAfter(self.output_window.SetDefaultStyle,wx.TextAttr(wx.GREEN,  wx.BLACK,font =wx.Font(self.font_point, family = wx.DEFAULT, style = wx.NORMAL, weight = wx.NORMAL, faceName = 'Consolas')))
                self.output_window.AppendText( response)
                whole_text = self.output_window.GetValue()
                m = re.search('[^\b]\b',whole_text)
                while m:
                    self.output_window.Remove(m.start(), m.end())
                    whole_text = self.output_window.GetValue()
                    m = re.search('[^\b]\b',whole_text)

                #wx.CallAfter(self.output_window.AppendText, response)#wx.CallAfter make thread safe!!!!
                last = self.output_window.GetLastPosition()
                wx.CallAfter(self.output_window.SetInsertionPoint,last)
                wx.CallAfter(self.output_window.ShowPosition,last+len(response)+1)
            self.output_lock.release()
            time.sleep(0.5)


    def __init__(self, parent, name,attributes, seq_queue=None):
        #init a session, and stdout, stderr, redirected to
        wx.Panel.__init__(self, parent)
        self.history_cmd=[]
        self.history_cmd_index = 0
        self.parent = parent
        self.type = type
        self.sequence_queue= seq_queue
        self.output_lock = threading.Lock()
        #wx.stc.StyledTextCtrl #wx.richtext.RichTextCtrl
        self.output_window = wx.TextCtrl( self, -1, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_AUTO_URL|wx.VSCROLL|wx.TE_RICH|wx.TE_READONLY |wx.TE_MULTILINE&(~wx.TE_PROCESS_ENTER))#0|wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER|wx.TE_READONLY )
        self.cmd_window= wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )

        self.font_point = self.output_window.GetFont().PointSize

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.output_window, 10, wx.EXPAND)
        sizer.Add(self.cmd_window, 0, wx.EXPAND)
        self.SetSizer(sizer)
        from lib.common import create_session
        info (os.curdir)
        #self.Bind(wx.EVT_CLOSE, self.on_close)
        #parent.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSED, self.on_close, parent)
        self.cmd_window.Bind(wx.EVT_TEXT_ENTER, self.on_enter_a_command)
        self.cmd_window.Bind(wx.EVT_KEY_UP, self.on_key_up)
        self.cmd_window.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.output_window.SetBackgroundColour('Black')
        self.output_window.SetDefaultStyle(wx.TextAttr(wx.GREEN,  wx.BLACK, font =wx.Font(9, family = wx.DEFAULT, style = wx.NORMAL, weight = wx.BOLD, faceName = 'Consolas')))
        self.cmd_window.SetFocus()
        self.session  = create_session(name, attributes)
        self.alive =True
        th =threading.Thread(target=self.update_output)
        th.start()
    def on_key_up(self, event):
        keycode = event.KeyCode

        increase =False
        if keycode ==wx.WXK_UP:
                #self.history_cmd_index= self.history_cmd_index-1 if self.history_cmd_index>0 else len(self.history_cmd)-1
                #get_next_in_ring_list(self.history_cmd_index,self.history_cmd,increase=True)
                pass
        elif keycode ==wx.WXK_DOWN:
                increase =True#
                #self.history_cmd_index= self.history_cmd_index+1 if self.history_cmd_index <len(self.history_cmd)-1 else 0

        if keycode in [wx.WXK_UP, wx.WXK_DOWN]:
            self.cmd_window.Clear()
            self.history_cmd_index, new_command = get_next_in_ring_list(self.history_cmd_index,self.history_cmd,increase=increase)
            self.cmd_window.AppendText(new_command)
        if keycode in [wx.WXK_TAB]:
            pass
        else:
            event.Skip()
    def on_enter_a_command(self, event):

        ctrl = False
        cmd = self.cmd_window.GetRange(0, self.cmd_window.GetLastPosition())
        cmd= cmd.replace('\n', os.linesep)
        self.cmd_window.Clear()
        self.add_cmd_to_history(cmd)

        try:
            if self.session.session_status:
                th = threading.Thread(target=self.session.write,args=( cmd,ctrl))
                th.start()
                self.sequence_queue.put(['TC.step({}, "{}")'.format(self.session.name,cmd)])#
            else:
                self.alive= self.session.session_status
                #self.session.write(cmd,ctrl=ctrl)
        except Exception as e:
            self.on_close()
            self.session.close_session()
            error ('{} closed unexpected'.format(self.session.name))
            self.alive= False
        self.cmd_window.SetFocus()
    def add_cmd_to_history(self, cmd):
        if self.history_cmd==[]:
            self.history_cmd.append(cmd)
        elif self.history_cmd[-1]==cmd:
            pass
        else:
            self.history_cmd.append(cmd)
            self.history_cmd_index= len(self.history_cmd)
    def on_key_down(self, event):
        keycode = event.KeyCode

        if keycode ==wx.WXK_TAB:
                self.cmd_window.AppendText('\t')
                self.on_enter_a_command(event)
        elif keycode == wx.WXK_NONE and wx.GetKeyState(wx.WXK_SHIFT):
            self.cmd_window.AppendText('?')
            self.on_enter_a_command(event)
        else:
            event.Skip()
class RedirectText(object):
    font_point_size = 10
    old_stdout = None
    old_stderr = None
    write_lock = None
    def __init__(self,aWxTextCtrl):
        self.old_stderr , self.old_stdout=sys.stderr , sys.stdout
        self.out=aWxTextCtrl
        self.font_point_size = self.out.GetFont().PointSize
        self.write_lock = threading.Lock()
    def write(self,string):
        self.write_lock.acquire()
        self.old_stdout.write(string)
        #string = string.replace('\\033\[[0-9\;]+m', '')

        #self.old_stderr.write(string)
        if re.search('error|err|fail|wrong',string.lower()):
            wx.CallAfter(self.out.SetDefaultStyle,wx.TextAttr(wx.RED,  wx.YELLOW, font =wx.Font(self.font_point_size+2, family = wx.DEFAULT, style = wx.NORMAL, weight = wx.BOLD, faceName = 'Consolas')))
        else:
            wx.CallAfter(self.out.SetDefaultStyle,wx.TextAttr(wx.GREEN,  wx.BLACK,font =wx.Font(self.font_point_size, family = wx.DEFAULT, style = wx.NORMAL, weight = wx.NORMAL, faceName = 'Consolas')))
        wx.CallAfter(self.out.AppendText, string)
        self.write_lock.release()

class FileEditor(wx.Panel):
    editor =None
    font_size=10
    parent=None
    type = None
    sessions_node =None
    function_node =None
    case_suite_node =None
    def on_close(self):
        pass
        #todo: handle close tab in edit_area
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
from lib.common import get_folder_item, info,debug, warn,  error
import ConfigParser
import sys
import inspect
import Queue

#DONE: DasHFrame should handle CLOSE event when closing the app, call on_close_tab_in_edit_area for all opened sessions and files
class DasHFrame(MainFrame):#wx.Frame
    ini_setting = None
        #m_left_navigator =None
    redir = None
    edit_area=None
    tabs_in_edit_area = None
    src_path = None
    sessions_alive=None
    sequence_queue=None
    def __init__(self,parent=None, ini_file = './gDasH.ini'):
        #wx.Frame.__init__(self, None, title="DasH")
        self.tabs_in_edit_area=[]
        self.sessions_alive={}
        MainFrame.__init__(self, parent=parent)
        self.sequence_queue= Queue.Queue()
        #self.sequence_queue.put()
        self.ini_setting = ConfigParser.ConfigParser()
        self.ini_setting.read(ini_file)
        self.src_path = os.path.abspath(self.ini_setting.get('dash','src_path'))
        self.add_src_path_to_python_path(self.src_path)
        self.redir = RedirectText(self.m_log)
        sys.stdout = self.redir
        sys.stderr = self.redir
        self.m_log.SetBackgroundColour('Black')
        self.m_log.SetDefaultStyle(wx.TextAttr(wx.GREEN,  wx.BLACK, font =wx.Font(9, family = wx.DEFAULT, style = wx.NORMAL, weight = wx.BOLD, faceName = 'Consolas')))
        #self.m_editor.WriteText('welcome to dash world')
        self.m_log.WriteText('Welcome to DasH!\n')

        self.m_command_box.WriteText('functions.static_function_in_module  test_ssh 2')
        fileMenu = wx.Menu()
        open_test_suite = fileMenu.Append(wx.NewId(), "Open TestSuite", "Open a Test Suite")
        open_test_case = fileMenu.Append(wx.NewId(), "Open TestCase", "Open a Test Case")
        self.m_menubar_main.Append(fileMenu, "&Open TestSuite")

        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.m_command_box.Bind(wx.EVT_TEXT_ENTER, self.on_command_enter)
        from wx.aui import AuiNotebook




        bookStyle = wx.aui.AUI_NB_DEFAULT_STYLE &(~wx.aui.AUI_NB_CLOSE_ON_ACTIVE_TAB)
        self.navigator = AuiNotebook(self.m_left_navigator, style= bookStyle )
        self.case_suite_page    = wx.TreeCtrl(self.navigator, wx.ID_ANY, wx.DefaultPosition, wx.Size(-1, -1), wx.TR_DEFAULT_STYLE | wx.TR_EDIT_LABELS | wx.TR_EXTENDED | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.HSCROLL | wx.TAB_TRAVERSAL | wx.VSCROLL | wx.WANTS_CHARS)
        self.function_page      = wx.TreeCtrl(self.navigator, wx.ID_ANY, wx.DefaultPosition, wx.Size(-1, -1), wx.TR_DEFAULT_STYLE | wx.TR_EDIT_LABELS | wx.TR_EXTENDED | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.HSCROLL | wx.TAB_TRAVERSAL | wx.VSCROLL | wx.WANTS_CHARS)
        self.session_page       = wx.TreeCtrl(self.navigator, wx.ID_ANY, wx.DefaultPosition, wx.Size(-1, -1), wx.TR_DEFAULT_STYLE | wx.TR_EDIT_LABELS | wx.TR_EXTENDED | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.HSCROLL | wx.TAB_TRAVERSAL | wx.VSCROLL | wx.WANTS_CHARS)

        self.navigator.AddPage(self.session_page, 'SESSION')
        self.navigator.AddPage(self.function_page, 'FUNCTION')
        self.navigator.AddPage(self.case_suite_page, 'CASE')




        self.edit_area = AuiNotebook(self.m_file_editor, style = wx.aui.AUI_NB_DEFAULT_STYLE)
        self.edit_area.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.on_close_tab_in_edit_area, self.edit_area)
        if False:
            new_page = FileEditor(self.edit_area, 'a', type= type)
            self.edit_area.AddPage(new_page, 'test')
            self.tabs_in_edit_area.append(('test'))
        self.edit_area.Enable(True)
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        #right_sizer =wx.GridSizer( 3, 1, 0, 0 )


        left_sizer = wx.BoxSizer(wx.HORIZONTAL)
        left_sizer.Add(self.m_left_navigator, 1, wx.EXPAND)



        self.case_suite_page.Bind(wx.EVT_LEFT_DCLICK, self.m_case_treeOnLeftDClick)
        #self.case_suite_page.Bind(wx.EVT_MOUSEWHEEL, self.case_tree_OnMouseWheel)
        self.case_suite_page.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.m_case_treeOnTreeItemExpanding)
        self.session_page.Bind(wx.EVT_LEFT_DCLICK, self.on_LeftDClick_in_Session_tab)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        #main_sizer = wx.GridSizer( 1, 2, 0, 0 )
        nav_sizer = wx.BoxSizer()
        nav_sizer.Add(self.navigator, 1, wx.EXPAND, 1)
        self.m_left_navigator.SetSizer(nav_sizer)
        #main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        #main_sizer.Add(left_sizer,  3,  wx.EXPAND)

        main_sizer.Add(left_sizer, 3, wx.EXPAND)
        edit_sizer = wx.BoxSizer()
        edit_sizer.Add(self.edit_area, 1, wx.EXPAND, 1)
        self.m_file_editor.SetSizer(edit_sizer)
        right_sizer.Add(self.m_file_editor,     6,  wx.ALL|wx.EXPAND, 1)
        right_sizer.Add(self.m_log,         3,  wx.ALL|wx.EXPAND, 2)
        right_sizer.Add(self.m_command_box, 0,  wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(right_sizer, 7,  wx.EXPAND)
        self.SetSizer(main_sizer)
        self.build_session_tab()
        self.build_suite_tree()

        ico = wx.Icon('./gui/dash.bmp', wx.BITMAP_TYPE_ICO)
        self.SetIcon(ico)
    def on_close(self, event):
        for index in range(0,self.edit_area.GetPageCount()): #len(self.tabs_in_edit_area)):
            closing_page = self.edit_area.GetPage(index)
            closing_page.on_close()
            self.tabs_in_edit_area.pop(self.tabs_in_edit_area.index(closing_page.session.name))
        sys.stderr =self.redir.old_stderr
        sys.stdout = self.redir.old_stdout
        event.Skip()

    def on_close_tab_in_edit_area(self, event):
        #self.edit_area.GetPage(self.edit_area.GetSelection()).on_close()
        closing_page = self.edit_area.GetPage(self.edit_area.GetSelection())
        closing_page.on_close()
        self.tabs_in_edit_area.pop(self.tabs_in_edit_area.index(closing_page.session.name))


    def add_item_to_subfolder_in_tree(self,node):
        subfolder_path_name = self.case_suite_page.GetPyData(node)['path_name']
        items = get_folder_item(subfolder_path_name)
        if items is None:
            self.case_suite_page.SetItemText(node, self.m_case_tree.GetItemText(node) + ' Not Exists!!!')
            self.case_suite_page.SetItemTextColour(node, wx.Colour(255, 0, 0))
            return
        for i in items:
            path_name = '{}/{}'.format(subfolder_path_name,i)

            base_name = os.path.basename(i)
            item_info = wx.TreeItemData({'path_name':path_name})
            new_item = self.case_suite_page.InsertItem(node, node, base_name)
            self.case_suite_page.SetItemData(new_item, item_info)

            if os.path.isdir(path_name):
                self.case_suite_page.SetItemHasChildren(new_item)
                #self.m_case_tree.ItemHasChildren()
                #self.m_case_tree.InsertItem(new_item,new_item,'')

    def build_suite_tree(self):
        suite_path = os.path.abspath(self.ini_setting.get('dash','test_suite_path'))
        if not os.path.exists(suite_path):
            suite_path= os.path.abspath(os.path.curdir)
        base_name = os.path.basename(suite_path)


        root =self.case_suite_page.AddRoot(base_name)
        item_info = wx.TreeItemData({'path_name':suite_path})
        self.case_suite_page.SetItemData(root, item_info)
        self.add_item_to_subfolder_in_tree(root)
        self.case_suite_page.Expand(root)

   # def OnSelChanged(self, event):
   #     item =  event.GetItem()
   #     self.display.SetLabel(self.tree.GetItemText(item))
    #def case_tree_OnMouseWheel(self, event):

    def m_case_treeOnLeftDClick(self, event):
        ht_item =self.case_suite_page.GetSelection()
        #ht_item = self.HitTest(event.GetPosition())
        item_name = self.case_suite_page.GetItemText(ht_item)
        if self.case_suite_page.ItemHasChildren(ht_item):
            if self.case_suite_page.IsExpanded(ht_item):
                self.case_suite_page.Collapse(ht_item)
            else:
                self.case_suite_page.ExpandAllChildren(ht_item)
        else:
            type = 'grid'
            new_page = FileEditor(self.edit_area, 'a', type= type)
            self.edit_area.AddPage(new_page, item_name)
            index = self.edit_area.GetPageIndex(new_page)
            self.edit_area.SetSelection(index)

    def m_case_treeOnTreeItemExpanding(self,event):
        ht_item =self.case_suite_page.GetSelection()
        try:
            item_info = self.case_suite_page.GetPyData(ht_item)

            if 0== self.case_suite_page.GetChildrenCount(ht_item):
                if os.path.isdir(item_info['path_name']):
                    self.add_item_to_subfolder_in_tree(ht_item)
        except Exception as e:
            pass
    def build_session_tab(self):
        if self.session_page.RootItem:
            self.session_page.DeleteAllItems()

        session_path = os.path.abspath(self.ini_setting.get('dash','session_path'))
        if not os.path.exists(session_path):
            session_path= os.path.abspath(os.path.curdir)
        base_name = os.path.basename(session_path)
        sessions = {}

        root =self.session_page.AddRoot(base_name)
        item_info = wx.TreeItemData({'path_name':session_path})
        self.session_page.SetItemData(root, item_info)
        self.session_page.Expand(root)
        item_list =  get_folder_item(session_path)
        session_files=[]
        for item in item_list:
            if os.path.isfile('{}/{}'.format(session_path,item)) and '{}'.format(item).lower().strip().endswith('.csv'):
                session_files.append(item)
        for csv_file in sorted(session_files):
            try:
                ses_in_bench = load_bench(os.path.abspath('{}/{}'.format(session_path, csv_file)))
                sessions.update(ses_in_bench)
            except Exception as e:
                pass

        root =self.session_page.GetRootItem()
        for file_name in sorted(sessions.keys()):

            item_name = os.path.basename(file_name)
            item_info = wx.TreeItemData({'file_name':file_name})
            new_bench = self.session_page.InsertItem(root, root, item_name)
            self.case_suite_page.SetItemData(new_bench, item_info)

            for ses in sorted(sessions[file_name]):
                item_name = ses
                item_info = wx.TreeItemData({'attribute':sessions[file_name][ses]})
                new_item = self.session_page.InsertItem(new_bench, new_bench, item_name)
                self.case_suite_page.SetItemData(new_item, item_info)

        self.session_page.Expand(root)
        first_child = self.session_page.GetFirstChild(root)
        self.session_page.Expand(first_child[0])
    def on_LeftDClick_in_Session_tab(self, event):
        event.Skip()
        ses_name = self.session_page.GetItemText(self.session_page.GetSelection())
        self.session_page.GetItemText(self.session_page.GetSelection())
        session_attribute = self.session_page.GetItemData(self.session_page.GetSelection())
        if session_attribute.Data.has_key('attribute'):
            info(session_attribute.Data['attribute'])

            counter = 1
            original_ses_name = ses_name
            while ses_name in self.tabs_in_edit_area:
                ses_name= '{}_{}'.format(original_ses_name,counter)
                counter+=1
            new_page = SessionTab(self.edit_area, ses_name, session_attribute.Data['attribute'], self.sequence_queue)

            window_id = self.edit_area.AddPage(new_page, ses_name)

            index = self.edit_area.GetPageIndex(new_page)
            self.edit_area.SetSelection(index)
            self.tabs_in_edit_area.append(ses_name)
            self.sessions_alive.update({ses_name: new_page.session})

    def add_new_session_to_globals(self, ses):
        if globals().has_key(ses.name):
            error('{} already '.format(ses.name))
        else:
            globals().update({ses.name: ses})

    def on_command_enter(self, event):
        info('called on_command_enter')
        cmd = self.m_command_box.GetValue()

        from lib.common import parse_command_line, call_function_in_module
        module,class_name, function,args = parse_command_line(cmd)
        #args[0]=self.sessions_alive['test_ssh'].session

        instance_name, function_name, new_argvs, new_kwargs = call_function_in_module(module,class_name,function,args)

        session_name = new_argvs[0]
        if globals().has_key(session_name):
            new_argvs[0]= globals()[session_name]
        elif self.sessions_alive.has_key(session_name):
            new_argvs[0]=self.sessions_alive[session_name]
        if class_name!="":
            getattr(instance_name, function_name)(*new_argvs,**new_kwargs)
        else:
            instance_name(*new_argvs,**new_kwargs)

    def add_src_path_to_python_path(self, path):
        paths = path.split(';')
        old_path = sys.path
        for p in paths:
            if p in old_path:

                info('path {} already in sys.path'.format(p))
            else:
                abspath = os.path.abspath(p)
                if os.path.exists(abspath):
                    sys.path.insert(0,abspath)
                else:
                    warn('path {} is not existed, ignored to add it into sys.path'.format(p))



