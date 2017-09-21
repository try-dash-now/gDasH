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
from datetime import datetime
import wx.grid as gridlib
import traceback
import wx
from gui.MainFrame import MainFrame
import os
from lib.common import load_bench, caller_stack_info,info, get_next_in_ring_list,get_folder_item, info,debug, warn,  error, parse_command_line, call_function_in_module
import re
import time
import threading
import ConfigParser
import sys
import inspect
import Queue
from SessionTab import  SessionTab
import imp
import types
#from dut import  dut

class RedirectText(object):
    font_point_size = 10
    old_stdout = None
    old_stderr = None
    write_lock = None
    log_file    = None

    def __init__(self,aWxTextCtrl, log_path=None):
        self.old_stderr , self.old_stdout=sys.stderr , sys.stdout
        self.out=aWxTextCtrl
        self.font_point_size = self.out.GetFont().PointSize
        self.write_lock = threading.Lock()

        if log_path:
            name = '{}/dash.log'.format(log_path)
            self.log_file = open(name, 'w+')
            self.fileno = self.log_file.fileno
    def write(self,string):
        self.write_lock.acquire()
        self.old_stdout.write(string)
        #string = string.replace('\\033\[[0-9\;]+m', '')

        #self.old_stderr.write(string)
        if re.search('error|\s+err\s+|fail|wrong',string.lower()):
            self.out.SetDefaultStyle(wx.TextAttr(wx.RED,  wx.YELLOW, font =wx.Font(self.font_point_size+2, family = wx.DEFAULT, style = wx.NORMAL, weight = wx.BOLD, faceName = 'Consolas')))#wx.CallAfter(s
        else:
            self.out.SetDefaultStyle(wx.TextAttr(wx.GREEN,  wx.BLACK,font =wx.Font(self.font_point_size, family = wx.DEFAULT, style = wx.NORMAL, weight = wx.NORMAL, faceName = 'Consolas')))#wx.CallAfter(
        wx.CallAfter(self.out.AppendText, string)
        if self.log_file:
            self.log_file.write(string)
            self.log_file.flush()
        self.write_lock.release()
    def close(self):
        if self.log_file:
            self.log_file.flush()
            self.log_file.close()
class process_info(object):
    process = None
    pid=None
    full_name=None
    returncode = None
    def __init__(self,name, process):
        self.process= process
        self.pid = process.pid
        self.full_name =name
        self.returncode = process.returncode
    @property
    def returncode(self):
        return  self.process.returncode

class FileEditor(wx.Panel):
    editor =None
    font_size=10
    parent=None
    type = None
    sessions_node =None
    function_node =None
    case_suite_node =None
    full_file_name = None
    file_instance = None
    def on_close(self):
        if self.full_file_name:
            data = self.editor.GetValue()
            with open(self.full_file_name, 'w') as f:
                f.write(data)
                f.flush()

        #done 2017-9-12: handle close tab in edit_area
    def __init__(self, parent, title='pageOne', type ='grid', file_name = None):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.type = type
        self.full_file_name = file_name
        #self.editor = wx.TextCtrl(self, style = wx.TE_MULTILINE|wx.TE_RICH2|wx.EXPAND|wx.ALL, size=(-1,-1))
        if type in ['text']:

            self.editor = wx.TextCtrl( self, -1, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_AUTO_URL|wx.VSCROLL|wx.TE_RICH|wx.TE_MULTILINE&(~wx.TE_PROCESS_ENTER))
            #wx.richtext.RichTextCtrl( self, -1, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER|wx.WANTS_CHARS )
            with open(self.full_file_name, 'r') as f:
                for line in f.readlines():
                    self.editor.AppendText(line)


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
    history_cmd = []
    history_cmd_index = -1
    import_modules={'TC':'TC'}
    lib_path ='./lib'
    log_path = '../log'
    session_path = './sessions'
    suite_path = '../test_suite'

    dict_test_report= None
    alive =True
    mail_server=None
    mail_to_list=None
    mail_from=None
    mail_read_url= 'outlook.office365.com'
    mail_password = None
    mail_usre =None
    def __init__(self,parent=None, ini_file = './gDasH.ini'):
        #wx.Frame.__init__(self, None, title="DasH")
        self.dict_test_report={}

        self.tabs_in_edit_area=[]
        self.sessions_alive={}
        MainFrame.__init__(self, parent=parent)
        self.sequence_queue= Queue.Queue()
        #self.sequence_queue.put()
        self.ini_setting    = ConfigParser.ConfigParser()
        self.ini_setting.read(ini_file)
        self.src_path       = os.path.abspath(self.ini_setting.get('dash','src_path'))
        self.lib_path       = os.path.abspath(self.ini_setting.get('dash','lib_path'))
        self.log_path       = os.path.abspath(self.ini_setting.get('dash','log_path'))
        self.suite_path     = os.path.abspath(self.ini_setting.get('dash', 'test_suite_path'))
        self.mail_server    = self.ini_setting.get('dash', 'mail_server')
        self.mail_from      =self.ini_setting.get('dash', 'mail_from')
        self.mail_to_list   =self.ini_setting.get('dash', 'mail_to_list')
        self.mail_read_url  =self.ini_setting.get('dash', 'mail_read_url')
        self.mail_user      = self.ini_setting.get('dash','mail_user')
        self.mail_password  =self.ini_setting.get('dash', 'mail_password')
        from  lib.common import create_case_folder, create_dir
        sys.argv.append('-l')
        sys.argv.append('{}'.format(self.log_path))
        self.log_path = create_case_folder(self.log_path)
        self.suite_path = create_dir(self.suite_path)
        self.lib_path = create_dir(self.lib_path)
        self.src_path = create_dir(self.src_path)
        if not os.path.exists(self.log_path):
            os.mkdir(self.log_path)
        self.add_src_path_to_python_path(self.src_path)
        self.redir = RedirectText(self.m_log, self.log_path)
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
        mail_test_report = fileMenu.Append(wx.NewId(), "Mail Test Report", "Mail Test Report")
        self.m_menubar_main.Append(fileMenu, "&Open")

        self.Bind(wx.EVT_MENU,self.on_mail_test_report ,mail_test_report)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.m_command_box.Bind(wx.EVT_TEXT_ENTER, self.on_command_enter)
        self.m_command_box.Bind(wx.EVT_KEY_UP, self.on_key_up)
        self.m_command_box.Bind(wx.EVT_KEY_DOWN, self.on_key_down)

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
        self.function_page.Bind(wx.EVT_LEFT_DCLICK, self.on_LeftDClick_in_Function_tab)
        self.function_page.Bind(wx.EVT_RIGHT_DOWN, self.on_right_down_in_function_tab)
        self.case_suite_page.Bind(wx.EVT_RIGHT_DOWN, self.on_right_down_in_case_tab)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        #main_sizer = wx.GridSizer( 1, 2, 0, 0 )
        nav_sizer = wx.BoxSizer()
        nav_sizer.Add(self.navigator, 1, wx.EXPAND, 1)
        self.m_left_navigator.SetSizer(nav_sizer)
        #main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        #main_sizer.Add(left_sizer,  3,  wx.EXPAND)

        main_sizer.Add(left_sizer, 2, wx.EXPAND)
        edit_sizer = wx.BoxSizer()
        edit_sizer.Add(self.edit_area, 1, wx.EXPAND, 1)
        self.m_file_editor.SetSizer(edit_sizer)
        right_sizer.Add(self.m_file_editor,     6,  wx.ALL|wx.EXPAND, 1)
        right_sizer.Add(self.m_log,         3,  wx.ALL|wx.EXPAND, 2)
        right_sizer.Add(self.m_command_box, 0,  wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(right_sizer, 8,  wx.EXPAND)
        self.SetSizer(main_sizer)
        self.build_session_tab()
        self.build_suite_tree()
        self.build_function_tab()

        ico = wx.Icon('./gui/dash.bmp', wx.BITMAP_TYPE_ICO)
        self.SetIcon(ico)
        th= threading.Thread(target=self.polling_running_cases)
        th.start()
    def on_close(self, event):
        self.alive =False
        time.sleep(0.01)
        self.generate_code(file_name='{}/test_script.py'.format(self.suite_path))

        self.mail_test_report("DASH TEST REPORT")
        for index in range(0,self.edit_area.GetPageCount()): #len(self.tabs_in_edit_area)):
            closing_page = self.edit_area.GetPage(index)
            if isinstance(closing_page, (SessionTab)):
                if closing_page:
                    name = closing_page.name
                    self.tabs_in_edit_area.pop(self.tabs_in_edit_area.index(name))

            closing_page.on_close()


        self.redir.close()
        sys.stderr =self.redir.old_stderr
        sys.stdout = self.redir.old_stdout
        event.Skip()
    def generate_report(self, filename):
        report = '''Test Report
RESULT,\tStart_Time,\tEnd_Time,\tPID,\tDuration,\tCase_Name,\tLog\n'''
        if len(self.dict_test_report):
            with open(filename, 'a+') as f:
                f.write(report)
                for pi in sorted(self.dict_test_report, key = lambda x: self.dict_test_report[x][1]):
                    case_name, start_time, end_time, duration, return_code ,proc, log_path =self.dict_test_report[pi][:7]
                    if return_code is None:
                        result = 'IP'
                    else:
                        result = return_code # 'FAIL' if return_code else 'PASS'
                    record = '\t'.join(['{},\t'.format(x) for x in [result,start_time,end_time,pi,duration,case_name,'<{}>'.format(log_path) ]])
                    report+=record+'\n'
                    f.write(record+'\n')

        return report

    def on_close_tab_in_edit_area(self, event):
        #self.edit_area.GetPage(self.edit_area.GetSelection()).on_close()
        closing_page = self.edit_area.GetPage(self.edit_area.GetSelection())
        closing_page.on_close()
        if isinstance(closing_page, (SessionTab)):
            ses_name = closing_page.name
            self.tabs_in_edit_area.pop(self.tabs_in_edit_area.index(ses_name))
            if globals().has_key(ses_name):
                #g = dict(globals())
                #globals()[ses_name]=None
                #del g[ses_name]
                globals()[ses_name].close_session()
                del globals()[ses_name]



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
        suite_path = self.suite_path #os.path.abspath(self.ini_setting.get('dash','test_suite_path'))
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
        item_data = self.case_suite_page.GetItemData(ht_item)
        if self.case_suite_page.ItemHasChildren(ht_item):
            if self.case_suite_page.IsExpanded(ht_item):
                self.case_suite_page.Collapse(ht_item)
            else:
                self.case_suite_page.ExpandAllChildren(ht_item)
        else:
            if item_name.lower() in ['.csv', '.xlsx','.xls']:
                type = 'grid'
                file_name = item_data.Data['path_name']
            else:
                type = 'text'
                file_name = item_data.Data['path_name']
            new_page = FileEditor(self.edit_area, 'a', type= type,file_name=file_name)
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
        self.session_path= session_path
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

                for bench in ses_in_bench:
                    for ses in ses_in_bench[bench]:
                        if ses_in_bench[bench][ses].has_key('login_step') and ses_in_bench[bench][ses]['login_step'].strip() not in ['', None]:
                            ses_in_bench[bench][ses].update(
                                    {'login_step': os.path.abspath('{}/{}'.format(session_path, ses_in_bench[bench][ses]['login_step'].strip()))}
                                    )
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
            counter =1
            original_ses_name = ses_name
            while ses_name in self.tabs_in_edit_area:
                ses_name= '{}_{}'.format(original_ses_name,counter)
                counter+=1
            if globals().has_key(ses_name):
                if not globals().has_key('_{}'.format(ses_name)):
                    info("variable '{}' is existed in global, change the name to _{}".format(ses_name, ses_name))
                    ses_name='_{}'.format(ses_name)
                    self.session_page.SetItemText(self.session_page.GetSelection(), ses_name)

                else:
                    error(("variable '{}' is existed in global, please change the name".format(ses_name)))
                    return

            new_page = SessionTab(self.edit_area, ses_name, session_attribute.Data['attribute'], self.sequence_queue, log_path=self.log_path)

            window_id = self.edit_area.AddPage(new_page, ses_name)

            index = self.edit_area.GetPageIndex(new_page)
            self.edit_area.SetSelection(index)
            self.tabs_in_edit_area.append(ses_name)
            self.sessions_alive.update({ses_name: new_page.name})
            attribute = session_attribute.Data['attribute']
            log_path='a_fake_log_path_for_auto_script'
            attribute['log_path']=log_path
            self.add_new_session_to_globals(new_page, '{}'.format(attribute))
            #globals().update({ses_name: new_page.session})

    def add_new_session_to_globals(self, new_page, args_str):
        if globals().has_key(new_page.name):
            if globals()[new_page.name]==None:
                pass
            else:
                error('{} already '.format(new_page.name))
        else:
            globals().update({new_page.name: new_page})
            self.add_cmd_to_sequence_queue('{} = dut.dut(name= "{}", **{})'.format(new_page.name,new_page.name,args_str.replace("'a_fake_log_path_for_auto_script'",'log_path').replace("'not_call_open': True,", "'not_call_open': False,") ), 'dut')
            #session  = dut(name, **attributes)

    def on_command_enter(self, event):
        info('called on_command_enter')
        cmd = self.m_command_box.GetValue()
        self.m_command_box.Clear()
        if cmd.strip()=='':
            return


        module,class_name, function,args = parse_command_line(cmd)
        #args[0]=self.sessions_alive['test_ssh'].session
        if module !='' or class_name!='' or function!='':
            instance_name, function_name, new_argvs, new_kwargs, str_code = call_function_in_module(module,class_name,function,args, globals())
            call_function = None

            if class_name!="":

                call_function = getattr(instance_name, function_name)
                #(*new_argvs,**new_kwargs)
            else:
                call_function = instance_name#(*new_argvs,**new_kwargs)
            th =threading.Thread(target=call_function, args=new_argvs, kwargs=new_kwargs)
            th.start()
            self.add_cmd_to_history(cmd,  module, str_code)
        else:
            error('"{}" is NOT a valid call in format:\n\tmodule.class.function call or \n\tmodule.function'.format(cmd))
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



    def on_key_down(self, event):
        #error(event.KeyCode)
        keycode = event.KeyCode
        if keycode ==wx.WXK_TAB:
                self.m_command_box.AppendText('\t')
                self.on_command_enter(event)
        elif keycode == wx.PAPER_ENV_INVITE and wx.GetKeyState(wx.WXK_SHIFT):
            self.m_command_box.AppendText('?')
            self.on_command_enter(event)
        else:
            event.Skip()
    def on_key_up(self, event):
        keycode = event.KeyCode
        increase =False
        if keycode ==wx.WXK_UP:
                pass
        elif keycode ==wx.WXK_DOWN:
                increase =True#
        if keycode in [wx.WXK_UP, wx.WXK_DOWN]:
            self.m_command_box.Clear()
            self.history_cmd_index, new_command = get_next_in_ring_list(self.history_cmd_index,self.history_cmd,increase=increase)
            self.m_command_box.AppendText(new_command)
        if keycode in [wx.WXK_TAB]:
            pass
        else:
            event.Skip()
    def add_cmd_to_history(self, cmd, module_name, str_code):
        if self.history_cmd==[]:
            self.history_cmd.append(cmd)
        elif self.history_cmd[-1]==cmd:
            pass
        else:
            self.history_cmd.append(cmd)
        self.history_cmd_index= len(self.history_cmd)
        self.add_cmd_to_sequence_queue(str_code,module_name )
        #self.sequence_queue.put([cmd, datetime.now()])
    def build_function_tab(self):
        src_path = os.path.abspath(self.src_path)
        if not os.path.exists(src_path):
            src_path= os.path.abspath(os.path.curdir)
        base_name = os.path.basename(src_path)


        root =self.function_page.AddRoot(base_name)
        item_info = wx.TreeItemData({'name':src_path})
        self.function_page.SetItemData(root, item_info)
        modules = get_folder_item(src_path)

        if modules is None:
            self.function_page.SetItemText(root, self.function_page.GetItemText(root) + ' Not Exists!!!')
            self.function_page.SetItemTextColour(root, wx.Colour(255, 0, 0))
            return
        for module_file in modules:
            path_name = '{}'.format(os.path.abspath(self.src_path))
            module_name = os.path.basename(module_file).split('.')[0]
            new_module = self.function_page.InsertItem(root, root, module_name)
            file, path_name, description = imp.find_module(module_name)
            lmod = imp.load_module(module_name, file, path_name,description)
            for attr in sorted(dir(lmod)):
                if attr.startswith('__'):
                    continue
                attr_obj = getattr(lmod, attr)
                attr_type = type(attr_obj)

                if attr_type == types.FunctionType :
                    new_item  = self.function_page.InsertItem(new_module, new_module, '{}'.format( attr))
                    item_info = wx.TreeItemData({'name':'{}.{}'.format(module_name,attr)})
                    self.function_page.SetItemData(new_item, item_info)
                elif attr_type== types.TypeType:
                    class_obj = getattr(lmod, attr)
                    new_class  = self.function_page.InsertItem(new_module, new_module, attr)
                    item_info = wx.TreeItemData({'name':'{}.{}'.format(module_name,attr)})
                    self.function_page.SetItemData(new_item, item_info)
                    for attr_in_class in sorted(dir(class_obj)):
                        if attr_in_class.startswith('__'):
                            continue
                        attr_obj = getattr(class_obj,attr_in_class)
                        attr_type =type(attr_obj)

                        if attr_type == types.MethodType :
                            item_info = wx.TreeItemData({'name':'{}.{}.{}'.format(module_name,attr,attr_in_class)})
                            new_item  = self.function_page.InsertItem(new_class, new_class, attr_in_class)
                            self.function_page.SetItemData(new_item, item_info)
        self.function_page.Expand(root)
        first_child = self.function_page.GetFirstChild(root)
        self.function_page.Expand(first_child[0])
    def on_LeftDClick_in_Function_tab(self,event):
        event.Skip()
        select_item = self.function_page.GetSelection()
        fun_name = self.function_page.GetItemData(select_item)
        text_in_tree = self.function_page.GetItemText(select_item)
        if fun_name != None and  fun_name.Data.has_key('name'):
            cmd = fun_name.Data['name']
            info('click item in Functions tab: {}'.format(fun_name.Data['name']))
            wx.CallAfter(self.m_command_box.Clear)
            wx.CallAfter(self.m_command_box.AppendText, cmd+' ')
            wx.CallAfter(self.m_command_box.SetFocus)
            wx.CallAfter(self.m_command_box.SetInsertionPointEnd)
            wx.CallAfter(self.m_command_box.Refresh)

    def on_right_down_in_function_tab(self, event):
        menu = wx.Menu()
        item = wx.MenuItem(menu, wx.NewId(), "Refresh")
        #acc = wx.AcceleratorEntry()
        #acc.Set(wx.ACCEL_NORMAL, ord('O'), self.popupID1)
        #item.SetAccel(acc)
        menu.AppendItem(item)

        self.Bind(wx.EVT_MENU, self.on_refresh_function_page,item)
        self.PopupMenu(menu,event.GetPosition())
    def on_refresh_function_page(self, event):
        self.function_page.DeleteAllItems()
        self.build_function_tab()
        info('Refresh Function tab done!')
    def add_cmd_to_sequence_queue(self, cmd, module_name):
        if self.import_modules.has_key(module_name):

            pass
        else:
            self.import_modules.update({module_name:module_name})
        self.sequence_queue.put([cmd,datetime.now() ])
    def generate_code(self, file_name ):
        str_code ="""#created by DasH
if __name__ == "__main__":
    import sys, traceback
    sys.path.insert(0,r'{}')
    sys.path.insert(0,r'{}')
    import lib.common

    log_path= '../log/tmp'
    log_path= lib.common.create_case_folder()
    try:

""".format(self.src_path,self.lib_path )
        sessions =[]
        for module in self.import_modules:
            str_code+='        import {mod}\n'.format(mod=module)#\n    {mod}_instance = {mod}()
        no_operation = True
        while True:
            try:
                cmd, timestamp =self.sequence_queue.get(block=False)[:2]
                str_code +='        {} #{}\n'.format(cmd, timestamp.isoformat( ' '))
                if cmd.find('dut.dut(')!=-1:
                    sessions.append(cmd.split('=')[0].strip())
                no_operation=False
                #datetime.now().isoformat()
            except Exception as e:
                break
        close_session=''
        str_code+='''    except Exception as e:
        print(traceback.format_exc())\n'''
        for ses in sessions:
            str_code+='''        {}.close_session()\n'''.format(ses)
        str_code+='        sys.exit(-1)\n'#, sys.exit(-1)
        for ses in sessions:
            str_code+='''    {}.close_session()\n'''.format(ses)

        info(str_code)
        if not no_operation:
            with open(file_name, 'a+') as f:
                f.write(str_code)

    def on_right_down_in_case_tab(self, event):
        menu = wx.Menu()
        item1 = wx.MenuItem(menu, wx.NewId(), "Run Test")
        item2 = wx.MenuItem(menu, wx.NewId(), "Kill Test")
        #acc = wx.AcceleratorEntry()
        #acc.Set(wx.ACCEL_NORMAL, ord('O'), self.popupID1)
        #item.SetAccel(acc)
        menu.AppendItem(item1)
        menu.AppendItem(item2)

        self.Bind(wx.EVT_MENU, self.on_run_script,item1)
        self.Bind(wx.EVT_MENU, self.on_kill_script,item2)
        self.PopupMenu(menu,event.GetPosition())
    def on_kill_script(self,event):
        hit_item = self.case_suite_page.GetSelection()
        item_name = self.case_suite_page.GetItemText(hit_item)
        item_data = self.case_suite_page.GetItemData(hit_item).Data

        if item_data.has_key('PROCESS'):
            p = item_data['PROCESS']
            name= item_data['FULL_NAME']

            info('script:{}, returncode:{}'.format(name,p.returncode))
            if p.returncode is None:
            #if p.is_alive():
                info('Terminate alive process {}:{}'.format(item_name, p.pid))
                result ='KILL'
                self.update_case_status(p.pid, result)
                self.mail_test_report("DASH TEST REPORT-updating")
                p.terminate()
            else:
                result ='FAIL' if p.returncode else 'PASS'
                info('{}:{} completed with returncode {}'.format(item_name, p.pid, result))
                self.update_case_status(p.pid, result)
    def on_run_script(self,event):
        hit_item = self.case_suite_page.GetSelection()
        item_name = self.case_suite_page.GetItemText(hit_item)
        import shlex
        lex = shlex.shlex(item_name)
        lex.quotes = '"'
        lex.whitespace_split = True
        script_args =list(lex)[1:]
        item_data = self.case_suite_page.GetItemData(hit_item).Data
        script_name = self.case_suite_page.GetItemData(hit_item).Data['path_name']

        from lib.common import run_script
        from multiprocessing import Process, Queue
        import subprocess

        self.on_kill_script(event)
        #queue = Queue()
        from lib.common import create_case_folder
        old_sys_argv = sys.argv
        sys.argv= [script_name]+script_args
        case_log_path = self.log_path #create_case_folder()
        sys.argv= old_sys_argv


        try:
            if os.path.exists('script_runner.exe'):
                execute = 'script_runner.exe'
                cmd = [execute,script_name ]+script_args + ['-l','{}'.format(case_log_path)]
                #p=subprocess.Popen(cmd, creationflags = subprocess.CREATE_NEW_CONSOLE)
            else:
                cmd = [sys.executable,'./script_runner.py', script_name ]+script_args+ ['-l','{}'.format(case_log_path)]

            p=subprocess.Popen(cmd, creationflags = subprocess.CREATE_NEW_CONSOLE)#, stdin=pipe_input, stdout=pipe_output,stderr=pipe_output)

            self.case_suite_page.GetItemData(hit_item).Data['PROCESS']=p
            self.case_suite_page.GetItemData(hit_item).Data['FULL_NAME']= item_name
            info('start process {} :{}'.format(item_name,  p.pid))

            self.add_newe_case_to_report(p.pid,item_name,p,case_log_path)
            #p.join() # this blocks until the process terminates
            time.sleep(1)
        except Exception as e :
            error(traceback.format_exc())

        #p = Process(target=run_script, args=[script_name,  script_and_args])
        #p.start()
    def check_case_status(self):
        changed=False
        for pid in self.dict_test_report:
            case_name, start_time, end_time, duration, return_code ,proc, log_path= self.dict_test_report[pid]
            if return_code is None:
                if proc.poll() is None:
                    pass
                    debug('RUNNING', start_time, end_time, duration, return_code ,proc, log_path)
                else:
                    changed=True
                    return_code = 'FAIL' if proc.returncode else 'PASS'
                self.update_case_status(pid,return_code)
        if changed:
            #test_report = self.generate_report(filename='{}/dash_report.txt'.format(self.log_path))
            self.mail_test_report('DasH Test Report-updating')
        return  changed
    def polling_running_cases(self):
        while True:
            time.sleep(10)
            try:
                if not self.alive:
                    break
            except:
                break
            self.check_case_status()




    def add_newe_case_to_report(self, pid, case_name, proc, log_path):
        start_time=datetime.now()
        duration = 0
        end_time = None
        return_code = None

        if pid in self.dict_test_report:
            self.dict_test_report[pid].update([case_name,start_time,end_time, duration, return_code, proc,log_path])
        else:
            self.dict_test_report[pid]=[case_name, start_time, end_time, duration,return_code, proc, log_path ]

    def update_case_status(self, pid,return_code=None):
        now = datetime.now()
        case_name, start_time, end_time, duration, tmp_return_code ,proc,log_path= self.dict_test_report[pid]

        if tmp_return_code is None:
            duration = (now-start_time).total_seconds()
            self.dict_test_report[pid]=[case_name,start_time, end_time, duration, return_code, proc, log_path]
        else:
            pass# don't update one case result twice

    def mail_test_report(self, subject="DASH TEST REPORT-updating"):
        try:
            from lib.common import send_mail_smtp_without_login
            self.check_case_status()
            test_report = self.generate_report(filename='{}/dash_report.txt'.format(self.log_path))
            #TO, SUBJECT, TEXT, SERVER, FROM
            send_mail_smtp_without_login(self.mail_to_list, subject,test_report,self.mail_server,self.mail_from)
        except Exception as e:
            error(traceback.format_exc())
    def on_mail_test_report(self,event):
        self.mail_test_report('DasH Test Report-updating')
        #p.terminate()
    def on_handle_request_via_mail(self):
        import imaplib
        url, user, password = self.mail_read_url,self.mail_user, self.mail_password
        conn = imaplib.IMAP4_SSL(url,993)
        conn.login(user,password)
        conn.select('INBOX')
        results,data = conn.search(None,'(UNSEEN)') # #'ALL')
        msg_ids = data[0]
        msg_id_list = msg_ids.split()
        from email.parser import Parser
        def process_multipart_message(message):
            if isinstance(message, basestring) or isinstance(message , list):
                return message
            rtn = ''
            try:
                if message.is_multipart():
                    for m in message.get_payload():
                        rtn += process_multipart_message(m)
                else:
                    rtn += message.get_payload()
            except Exception as e:
                pass
            return rtn
        MAX_UNREAD_MAIL = 50
        for unread_mail_id in msg_id_list[::-1][:MAX_UNREAD_MAIL]:
            result,data = conn.fetch(unread_mail_id,"(RFC822)")
            raw_email = data[0][1]
            p = Parser()
            msg = p.parsestr(raw_email)
            #msg = process_multipart_message(msg )
            from1 = msg.get('From')
            if from1 in ['dash@calix.com', 'yu_silence@163.com']:
                conn.uid('STORE', unread_mail_id, '+FLAGS', '\SEEN')
                #conn.uid('STORE', '-FLAGS', '(\Seen)')
            sub = msg.get('Subject')
            pat_dash_request= re.compile('dash\s*request', flags=re.IGNORECASE)


            payload = msg.get_payload()
            print(payload)
            payload = process_multipart_message(payload )
            print(payload)
#done: 2017-08-22, 2017-08-19 save main log window to a file
#todo: 2017-08-19 add timestamps to log message
#done: 2017-08-22, 2017-08-19 mail to someone
#todo: 2017-08-19 run a script in DasH
#todo: 2017-08-19 generate test report
#todo: 2017-08-19 publish all test cases in a web page
#todo: 2017-08-19 trigger a test remote via web page
#todo: 2017-08-19 re-run failed cases
#todo: 2017-08-19 build executable packege for DasH
#todo: 2017-08-19 a popup window to get email address/password/mail_server...
#todo: 2017-08-22 output in m_log window has a lot of empty line, need remove them
#todo: 2017-08-23 in common.call_function_in_module, should end all threads which are started in previous instance
#todo: 2017-08-23 add tips for all tree item in teh left