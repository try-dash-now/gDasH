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
import webbrowser
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
from lib.common import send_mail_smtp_without_login
from lib.common import run_script
from multiprocessing import Process
import subprocess
import shlex
#from dut import  dut
DUT={}
class RedirectText(object):
    font_point_size = 10
    old_stdout = None
    old_stderr = None
    write_lock = None
    log_file    = None
    error_pattern = None
    font_point = None
    previous_scroll_pos = 0
    previous_insert_pos = 0
    def __init__(self,aWxTextCtrl, log_path=None):
        self.old_stderr , self.old_stdout=sys.stderr , sys.stdout
        self.out=aWxTextCtrl
        self.font_point_size = self.out.GetFont().PointSize+2
        self.write_lock = threading.Lock()
        self.error_pattern = re.compile('error|\s+err\s+|fail|wrong|errno')
        self.font_point =self.out.GetFont().PointSize
        if log_path:
            name = '{}/dash.log'.format(log_path)
            self.log_file = open(name, 'w+')
            self.fileno = self.log_file.fileno
    def write(self,string):
        def __write(string):
            #self.write_lock.acquire()
            try:
                self.old_stdout.write(string)
                err_pattern = self.error_pattern#re.compile('error|\s+err\s+|fail|wrong')
                self.__freeze_main_log_window()
                current_scroll_pos = self.out.GetScrollPos(wx.VERTICAL)
                current_insert_pos = self.out.GetInsertionPoint()
                last_pos = self.out.GetLastPosition()

                v_scroll_range = self.out.GetScrollRange(wx.VERTICAL)
                char_height = self.out.GetCharHeight()
                w_client,h_client = self.out.GetClientSize()
                line_in_a_page= h_client/char_height
                max_gap=line_in_a_page

                c_col, c_line = self.out.PositionToXY(current_scroll_pos) #current_scroll_pos
                t_col, t_line = self.out.PositionToXY(last_pos) #v_scroll_range last_pos


                x, y = c_col, c_line
                real_gap = t_line- c_line
                if real_gap>max_gap:#100
                    self.previous_insert_pos = current_scroll_pos
                    #self.previous_scroll_pos = current_scroll_pos
                tmp_msg ='\n!!!!! current {}, range {}, t_line {}, c_line {}, gap {}\n'.format(current_scroll_pos, v_scroll_range, t_line, c_line, t_line -c_line)
                string+=tmp_msg
                #self.old_stdout.write()
                if True:#err_pattern.search(string.lower()):
                    last_start = 0
                    for m in err_pattern.finditer(string.lower()):
                        wx.CallAfter(self.out.SetDefaultStyle,wx.TextAttr(wx.GREEN,  wx.BLACK,font =wx.Font(self.font_point, family = wx.DEFAULT, style = wx.NORMAL, weight = wx.NORMAL, faceName = 'Consolas')))
                        wx.CallAfter(self.out.AppendText, string[last_start:m.start()])
                        wx.CallAfter(self.out.SetDefaultStyle,wx.TextAttr(wx.RED,  wx.YELLOW,font =wx.Font(self.font_point+2, family = wx.DEFAULT, style = wx.NORMAL, weight = wx.NORMAL, faceName = 'Consolas')))
                        wx.CallAfter(self.out.AppendText, string[m.start():m.end()])
                        last_start= m.end()
                    wx.CallAfter(self.out.SetDefaultStyle,wx.TextAttr(wx.GREEN,  wx.BLACK,font =wx.Font(self.font_point, family = wx.DEFAULT, style = wx.NORMAL, weight = wx.NORMAL, faceName = 'Consolas')))
                    wx.CallAfter(self.out.AppendText, string[last_start:])

                else:
                    wx.CallAfter(self.out.SetDefaultStyle,wx.TextAttr(wx.GREEN,  wx.BLACK,font =wx.Font(self.font_point, family = wx.DEFAULT, style = wx.NORMAL, weight = wx.NORMAL, faceName = 'Consolas')))
                    wx.CallAfter(self.out.AppendText, string)
                if self.log_file:
                    self.log_file.write(string)
                    self.log_file.flush()

                if real_gap>max_gap:#1000
                    #time.sleep(0.01)
                    pass
                    #self.out.SetScrollPos(wx.VERTICAL, self.previous_scroll_pos)
                    #self.previous_insert_pos = current_scroll_pos
                else:
                    self.previous_scroll_pos= self.out.GetScrollRange(wx.VERTICAL)#v_scroll_range
                    self.previous_insert_pos = last_pos+len(string)

                self.out.SetScrollPos(wx.VERTICAL, self.previous_scroll_pos)
                self.out.SetInsertionPoint( self.previous_insert_pos)                #self.out.ScrollToLine(c_line+line_in_a_page)
                    #pos =self.out.XYToPosition(xxx[0], xxx[1])
                #self.out.ShowPosition(self.previous_insert_pos)
                self.__thaw_main_log_window()

            except Exception as  e:
                self.old_stdout.write('\n'+error(traceback.format_exc()))
            #self.write_lock.release()
            #time.sleep(0.1)
        __write(string)
        #threading.Thread(target=__write, args=[string]).start()
    def close(self):
        if self.log_file:
            self.log_file.flush()
            self.log_file.close()
    def flush(self):
        if self.log_file:
            self.log_file.flush()
    def __freeze_main_log_window(self):
        #return
        if self.out.IsFrozen():
            pass
        else:
            self.output_window_last_position =self.out.GetScrollRange(wx.VERTICAL)
            self.out.Freeze()
    def __thaw_main_log_window(self):
        #self.out.SetScrollPos(wx.VERTICAL, self.previous_scroll_pos)
        if self.out.IsFrozen():
            self.out.Thaw()
        else:
            pass

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
from functools import wraps
import pprint
def gui_event_thread_handler( func):


    @wraps(func)
    def inner(func, *args, **kwargs):
        ret =None
        try:
            ret  = func(*args, **kwargs)
            #th = threading.Thread(target=func,args= args, kwargs=kwargs)
            #th.start()
        except:
            error(traceback.format_exc())
        return  ret
    return inner


class gui_event_decorator():

    def __init__(self):
        pass
    @classmethod
    def gui_even_handle(self, func):
        def inner(*args, **kwargs):
            ret =None
            try:
                #print('decorator!!!')
                #ret  = func(*args, **kwargs)
                th = threading.Thread(target=func,args= args, kwargs=kwargs)
                th.start()
                #print('decorator####')
            except:
                print(traceback.format_exc())
            return  ret
        return inner


class DasHFrame(MainFrame, gui_event_decorator):#wx.Frame
    ini_setting = None
        #m_left_navigator =None
    redir = None
    edit_area=None
    tabs_in_edit_area = None
    src_path = './src/'
    sessions_alive=None
    sequence_queue=None
    history_cmd = []
    history_cmd_index = -1
    import_modules={'TC':''}
    lib_path ='./lib'
    log_path = '../log/dash'
    session_path = './sessions'
    suite_path = '../test_suite'

    dict_test_report= ''
    alive =True
    mail_server=None
    mail_to_list=None
    mail_from=None
    mail_read_url= 'outlook.office365.com'
    mail_password = None
    mail_user ='nonexistent@dash.com'
    case_queue =None
    check_case_running_status_lock = None
    case_list=None
    #session_names={}
    web_daemon = None
    web_host = None
    web_port = 8888

    mailed_case_pids= []
    timestamp=None

    mail_failure =False
    last_time_call_on_idle= None
    ini_file=None

    dict_function_obj= {'instance':{}}
    dict_function_files = {}
    updating_function_page =False
    m_log_current_pos = None
    def __init__(self,parent=None, ini_file = './gDasH.ini'):
        #wx.Frame.__init__(self, None, title="DasH")
        gui_event_decorator.__init__(self)
        self.timestamp= datetime.now().isoformat('-').replace(':','-')
        self.case_list= []
        self.case_queue = Queue.Queue()
        self.dict_test_report={}
        self.check_case_running_status_lock = threading.Lock()
        self.tabs_in_edit_area=[]
        self.sessions_alive={}
        MainFrame.__init__(self, parent=parent)
        self.sequence_queue= Queue.Queue()
        #self.sequence_queue.put()
        self.ini_setting    = ConfigParser.ConfigParser()
        self.m_log_current_pos = 0
        if os.path.exists(ini_file):
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
            self.web_port       =int(self.ini_setting.get('dash', 'web_port'))
        else:
            with open(ini_file, 'w') as tmp_ini_file:
                tmp_ini_file.write('''[dash]
test_suite_path = ../test_suite/
log_path= {log_path}
lib_path = {lib_path}
session_path={session_path}
#the source python file folder
src_path = {src_path}
mail_server={mail_server}
mail_to_list={mail_to_list}
mail_user={mail_user}
mail_from ={mail_from}
mail_read_url={mail_read_url}
mail_password = {mail_password}
web_port={web_port}
                '''.format(
                    log_path = self.log_path,
                    lib_path = self.lib_path,
                    session_path = self.session_path,
                    src_path = self.src_path,
                    mail_server = self.mail_server,
                    mail_to_list = self.mail_to_list,
                    mail_user = self.mail_user,
                    mail_from = self.mail_from,
                    mail_read_url = self.mail_read_url,
                    mail_password = self.mail_password,
                    web_port = self.web_port))
                tmp_ini_file.flush()
        #self.ini_setting.read(ini_file)
        self.ini_file = ini_file
        from  lib.common import create_case_folder, create_dir
        sys.argv.append('-l')
        sys.argv.append('{}'.format(self.log_path))
        from lib.common import create_dir
        self.log_path = create_dir(self.log_path)
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
        #open_test_suite = fileMenu.Append(wx.NewId(), "Open TestSuite", "Open a Test Suite")
        #open_test_case = fileMenu.Append(wx.NewId(), "Open TestCase", "Open a Test Case")
        generate_test_report = fileMenu.Append(wx.NewId(), "Generate Test Report", "Generate Test Report")
        generate_code = fileMenu.Append(wx.NewId(), "Generate Python Code", "Generate Python Code")
        mail_test_report = fileMenu.Append(wx.NewId(), "Mail Test Report", "Mail Test Report")
        get_case_queue = fileMenu.Append(wx.NewId(), "Get Case Queue", "Get Case Queue") #done
        clear_case_queue = fileMenu.Append(wx.NewId(), "Clear Case Queue", "Clear Case Queue")
        kill_running_case = fileMenu.Append(wx.NewId(), "Kill Running Case(s)", "Kill Running Case(s)")
        self.m_menubar_main.Append(fileMenu, "&Operations")
        self.Bind(wx.EVT_MENU,self.on_generate_test_report ,generate_test_report)
        self.Bind(wx.EVT_MENU,self.on_generate_code ,generate_code)
        self.Bind(wx.EVT_MENU,self.on_mail_test_report ,mail_test_report)
        self.Bind(wx.EVT_MENU,self.get_case_queue ,get_case_queue)
        self.Bind(wx.EVT_MENU,self.on_clear_case_queue ,clear_case_queue)
        self.Bind(wx.EVT_MENU,self.on_kill_running_case ,kill_running_case)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.m_command_box.Bind(wx.EVT_TEXT_ENTER, self.on_command_enter)
        self.m_command_box.Bind(wx.EVT_KEY_UP, self.on_key_up)
        self.m_command_box.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.m_log.Bind(wx.EVT_TEXT, self.on_m_log_text_changed)

        from wx.aui import AuiNotebook
        bookStyle = wx.aui.AUI_NB_DEFAULT_STYLE &(~wx.aui.AUI_NB_CLOSE_ON_ACTIVE_TAB)
        self.navigator = AuiNotebook(self.m_left_navigator, style= bookStyle )
        self.case_suite_page    = wx.TreeCtrl(self.navigator, wx.ID_ANY, wx.DefaultPosition, wx.Size(-1, -1), wx.TR_DEFAULT_STYLE | wx.TR_EDIT_LABELS | wx.TR_EXTENDED | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.HSCROLL | wx.TAB_TRAVERSAL | wx.VSCROLL | wx.WANTS_CHARS)
        self.function_page      = wx.TreeCtrl(self.navigator, wx.ID_ANY, wx.DefaultPosition, wx.Size(-1, -1), wx.TR_DEFAULT_STYLE | wx.TR_EDIT_LABELS | wx.TR_EXTENDED | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.HSCROLL | wx.TAB_TRAVERSAL | wx.VSCROLL | wx.WANTS_CHARS)
        self.session_page       = wx.TreeCtrl(self.navigator, wx.ID_ANY, wx.DefaultPosition, wx.Size(-1, -1), wx.TR_DEFAULT_STYLE | wx.TR_EDIT_LABELS | wx.TR_EXTENDED | wx.TR_HAS_BUTTONS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.HSCROLL | wx.TAB_TRAVERSAL | wx.VSCROLL | wx.WANTS_CHARS)

        self.navigator.AddPage(self.session_page, 'SESSION')
        self.navigator.AddPage(self.function_page, 'FUNCTION')
        self.navigator.AddPage(self.case_suite_page, 'CASE')

        self.edit_area = AuiNotebook(self.m_file_editor, style = bookStyle)#wx.aui.AUI_NB_DEFAULT_STYLE)
        if False:
            new_page = FileEditor(self.edit_area, 'a', type= type)
            self.edit_area.AddPage(new_page, 'test')
            self.tabs_in_edit_area.append(('test'))
        self.edit_area.Enable(True)
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        #right_sizer =wx.GridSizer( 3, 1, 0, 0 )


        left_sizer = wx.BoxSizer(wx.HORIZONTAL)
        left_sizer.Add(self.m_left_navigator, 1, wx.EXPAND)
        self.edit_area.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.on_active_change_in_edit_area)
        #self.m_file_editor.Bind(wx.EVT_CLOSE, self.on_close_tab_in_edit_area)

        self.case_suite_page.Bind(wx.EVT_LEFT_DCLICK, self.m_case_treeOnLeftDClick)
        #self.case_suite_page.Bind(wx.EVT_MOUSEWHEEL, self.case_tree_OnMouseWheel)
        self.case_suite_page.Bind(wx.EVT_TREE_ITEM_EXPANDING, self.m_case_treeOnTreeItemExpanding)
        self.session_page.Bind(wx.EVT_LEFT_DCLICK, self.on_LeftDClick_in_Session_tab)
        self.function_page.Bind(wx.EVT_LEFT_DCLICK, self.on_LeftDClick_in_Function_tab)
        self.function_page.Bind(wx.EVT_RIGHT_DOWN, self.on_right_down_in_function_tab)
        self.case_suite_page.Bind(wx.EVT_RIGHT_DOWN, self.on_right_down_in_case_tab)
        self.session_page.Bind(wx.EVT_RIGHT_DOWN, self.on_right_down_in_session_tab)
        self.edit_area.Bind(wx.aui.EVT__AUINOTEBOOK_TAB_RIGHT_DOWN, self.on_right_up_over_tab_in_edit_area)
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
        right_sizer.Add(self.m_file_editor,     100,  wx.ALL|wx.EXPAND, 1)
        #right_sizer.Add(self.m_log,         2,  wx.ALL|wx.EXPAND, 2)
        right_sizer.Add(self.m_command_box,1,  wx.ALL|wx.EXPAND, 3)
        main_sizer.Add(right_sizer, 8,  wx.EXPAND)
        self.SetSizer(main_sizer)


        ico = wx.Icon('./gui/dash.bmp', wx.BITMAP_TYPE_ICO)
        self.SetIcon(ico)
        #th= threading.Thread(target=self.polling_running_cases)
        #th.start()
        #th = threading.Thread(target=self.polling_request_via_mail)
        #th.start()

        threading.Thread(target=self.web_server_start).start()

        #tooltips bind
        self.case_suite_page.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.session_page.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        self.function_page.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        #wx.html.EVT_HTML_LINK_CLICKED wx.EVT_TEXT_URL,  wx.EVT_TEXT_URL,
        self.m_log.Bind(wx.EVT_TEXT_URL, self.on_leftD_click_url_in_m_log)
        self.Bind(wx.EVT_IDLE, self.on_idle)
        self.last_time_call_on_idle = datetime.now()

        self.build_session_tab()
        self.build_suite_tree()
        self.build_function_tab()
        self.Show(True)
        self.Maximize()
        self.create_main_log_window()

    def on_close(self, event):
        try:
            self.alive =False
            sys.stderr =self.redir.old_stderr
            sys.stdout = self.redir.old_stdout
            self.redir.close()
            event.Skip()
        except Exception as e:
            error(traceback.format_exc())
        self.Show(False)
        time.sleep(0.01)
        def close():
            try:
                self.web_daemon.shutdown()
            except:
                pass

            self.generate_code(file_name='{}/test_script.py'.format(self.suite_path))
            if len(self.dict_test_report):
                self.mail_test_report("DASH TEST REPORT")
            for index in range(1,self.edit_area.GetPageCount()): #len(self.tabs_in_edit_area)):
                closing_page = self.edit_area.GetPage(index)
                if isinstance(closing_page, (SessionTab)):
                    if closing_page:
                        name = closing_page.name
                        self.tabs_in_edit_area.pop(self.tabs_in_edit_area.index(name))
                try:
                    closing_page.Disable()
                    closing_page.on_close()
                except:
                    pass
        close()
        time.sleep(0.01)
        #sys.exit(0)

    def generate_report(self, filename, report_all_cases=True):
        #fixed 2017-11-19, 2017-10-21 no need to send whole report, just the updating part

        def GetTime(duration):
            from datetime import timedelta
            sec = timedelta(seconds=int(duration))
            d = datetime(1,1,1) + sec

            #print("DAYS:HOURS:MIN:SEC")

            return "%d:%d:%d:%d" % (d.day-1, d.hour, d.minute, d.second)
        report_in_list =[['result',
                        'start_time',
                        'end_time',
                        'ProcessID',
                        'duration',
                        'duration',
                        'case_name','log']]
        report = '''Test Report
RESULT,\tStart_Time,\tEnd_Time,\tPID,\tDuration(s),\tDuration(D:H:M:S)\tCase_Name,\tLog\n'''
        with open(filename, 'w') as f:
            if len(self.dict_test_report):
                #f.write(report)
                for pi in sorted(self.dict_test_report, key = lambda x: self.dict_test_report[x][1]):
                    case_name, start_time, end_time, duration, return_code ,proc, log_path =self.dict_test_report[pi][:7]

                    if return_code is None:
                        result = 'IP'
                        result_html = '<font color="blue">IP'
                    else:
                        result = return_code # 'FAIL' if return_code else 'PASS'
                        if result.lower() in ['pass']:
                            result_html= '<font color="green">PASS'
                        else:
                            result_html= '<font color="red">FAIL'

                    one_record = ['{}'.format(x) for x in [
                        result,
                        start_time,
                        end_time,
                        pi,
                        duration,
                        GetTime(duration),
                        case_name,
                        '{html_link} {file_path}'.format(
                                file_path=log_path,
                                html_link = log_path.replace(
                                        self.log_path,
                                        'http://{}:{}/log/'.format(self.web_host,self.web_port)
                                ).replace('/\\',r'/')
                        ) ]]
                    one_record_html = ['{}'.format(x) for x in [
                        result_html,
                        start_time,
                        end_time,
                        pi,
                        duration,
                        GetTime(duration),
                        case_name,
                        '<a href={html_link}>{file_path}</a>'.format(
                                file_path=log_path,
                                html_link = log_path.replace(
                                        self.log_path,
                                        'http://{}:{}/log/'.format(self.web_host,self.web_port)
                                ).replace('/\\',r'/')
                        ) ]]
                    report_in_list.append(one_record_html)
                    record = '\t'.join(one_record)
                    if result == 'IP':
                        report+=record+'\n'
                    else:
                        if report_all_cases:
                            report+=record+'\n'
                            self.mailed_case_pids.append(pi)
                        elif  pi not in self.mailed_case_pids:
                            report+=record+'\n'
                            self.mailed_case_pids.append(pi)

                        else:
                            pass
            from lib.common import array2htmltable
            report_in_html_string = array2htmltable(report_in_list)
            f.write(report_in_html_string)
        return report

    def on_close_tab_in_edit_area(self, event):
        #self.edit_area.GetPage(self.edit_area.GetSelection()).on_close()
        if self.edit_area.GetSelection()==0:
            return

        def close_tab():
            global  gSessions
            closing_page = self.edit_area.GetPage(self.edit_area.GetSelection())
            index =self.edit_area.GetPageIndex(closing_page)
            closing_page.on_close()
            if isinstance(closing_page, (SessionTab)):
                ses_name = closing_page.name
                self.tabs_in_edit_area.pop(self.tabs_in_edit_area.index(ses_name))
                if gSessions.has_key( ses_name):
                    #    globals().has_key(ses_name):
                    #g = dict(globals())
                    #globals()[ses_name]=None
                    #del g[ses_name]
                    gSessions[ses_name].close_session()
                    del gSessions[ses_name] #del globals()[ses_name]
        threading.Thread(target=close_tab, args=[]).start()
        event.Skip()


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
            self.case_list.append(path_name)
            new_item = self.case_suite_page.InsertItem(node, node, base_name)
            self.case_suite_page.SetItemData(new_item, item_info)

            if os.path.isdir(path_name):
                self.case_suite_page.SetItemHasChildren(new_item)
                #self.m_case_tree.ItemHasChildren()
                #self.m_case_tree.InsertItem(new_item,new_item,'')
    @gui_event_decorator.gui_even_handle
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
    @gui_event_decorator.gui_even_handle
    def build_session_tab(self):
        if self.session_page.RootItem:
            self.session_pagef.DeleteAllItems()
        self.ini_setting.read(self.ini_file)
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
                error(traceback.format_exc())

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
    #@gui_event_decorator.gui_even_handle
    def create_main_log_window(self):
        ses_name ='*LOG*'
        indow_id = self.edit_area.AddPage(self.m_log, ses_name)
        index = self.edit_area.GetPageIndex(self.m_log)
        self.edit_area.SetSelection(index)
        #self.edit_area.Disable(0,False)


    def on_active_change_in_edit_area(self, event):
        if self.edit_area.GetPageText(self.edit_area.GetSelection())=="*LOG*":
            self.edit_area.SetWindowStyle(wx.aui.AUI_NB_DEFAULT_STYLE&(~wx.aui.AUI_NB_CLOSE_ON_ACTIVE_TAB))
        else:
            self.edit_area.SetWindowStyle(wx.aui.AUI_NB_DEFAULT_STYLE)

    #@gui_event_decorator.gui_even_handle
    def on_LeftDClick_in_Session_tab(self, event):
        #self.session_page.Disable()
        ses_name = self.session_page.GetItemText(self.session_page.GetSelection())
        self.session_page.GetItemText(self.session_page.GetSelection())
        session_attribute = self.session_page.GetItemData(self.session_page.GetSelection())
        if session_attribute.Data.has_key('attribute'):
            info(session_attribute.Data['attribute'])
            counter =1
            original_ses_name = ses_name
            tmp_tabs =[]
            for index in range(1,self.edit_area.GetPageCount()): #len(self.tabs_in_edit_area)):
                tab_page = self.edit_area.GetPage(index)
                #tab_page.name
                tmp_tabs.append(tab_page.name)
            self.tabs_in_edit_area = tmp_tabs
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

            new_page = SessionTab(self.edit_area, ses_name, session_attribute.Data['attribute'], self.sequence_queue, log_path=self.log_path+'/session_log')

            window_id = self.edit_area.AddPage(new_page, ses_name)

            index = self.edit_area.GetPageIndex(new_page)
            self.edit_area.SetSelection(index)
            self.tabs_in_edit_area.append(ses_name)
            self.sessions_alive.update({ses_name: new_page.name})
            attribute = session_attribute.Data['attribute']
            log_path='a_fake_log_path_for_auto_script'
            attribute['log_path']=log_path
            self.add_new_session_to_globals(new_page, '{}'.format(attribute))

            #time.sleep(0.1)
            event.Skip()
        time.sleep(0.5)
        #self.session_page.Enable()
    def add_new_session_to_globals(self, new_page, args_str):
        name = new_page.name
        global  DUT
        #FIX ISSUE
            #  INFO	common.py:161	call_function_in_module:
            # 	module_name: 	xdsl
            # 	class_name: 	xdsl
            # 	function_name: 	get_eut
            # 	args:[wxPython wrapper for DELETED SessionTab object! (The C++ object no longer exists.)]
            # 	kwargs: {}
            # Exception in thread Thread-40:
            # Traceback (most recent call last):
            #   File "C:\Python27\Lib\threading.py", line 801, in __bootstrap_inner
            #     self.run()
            #   File "C:\Python27\Lib\threading.py", line 754, in run
            #     self.__target(*self.__args, **self.__kwargs)
            #   File "C:\workspace\gDasH\src\xdsl.py", line 36, in get_eut
            #     ses.write(cmd)
            #   File "C:\Python27\lib\site-packages\wx-3.0-msw\wx\_core.py", line 16711, in __getattr__
            #     raise PyDeadObjectError(self.attrStr % self._name)
        if  name in DUT:
            try:
                DUT[name].name
                del DUT[name]
            except :
                DUT[name]= new_page
        else:
            DUT[name]= new_page
            self.add_cmd_to_sequence_queue('DUT["{}"] = dut.dut(name= "{}", **{})'.format(new_page.name,new_page.name,args_str.replace("'a_fake_log_path_for_auto_script'",'log_path').replace("'not_call_open': True,", "'not_call_open': False,") ), 'dut')
            #session  = dut(name, **attributes)
    @gui_event_decorator.gui_even_handle
    def on_command_enter(self, event):

        info('called on_command_enter')
        self.redir.previous_scroll_pos=self.m_log.GetScrollRange(wx.VERTICAL)
        self.redir.provious_insert_pos = self.m_log.GetLastPosition()+1
        self.redir.out.SetInsertionPoint(self.redir.previous_insert_pos)
        self.redir.out.SetScrollPos(wx.VERTICAL,self.redir.previous_scroll_pos)

        cmd = self.m_command_box.GetValue()
        self.m_command_box.Clear()

        cmd = cmd.strip()
        cmds = cmd.replace('\r\n', '\n').split('\n')
        def handle_one_cmd(cmd):
            if cmd.strip()=='':
                return
            cmd_string = cmd.strip()
            lex = shlex.shlex(cmd_string)
            lex.quotes = '"'
            lex.whitespace_split = True
            cmd_list=list(lex)
            function_obj_name = cmd_list[0]
            if self.dict_function_obj.has_key(function_obj_name):
                call_function = self.dict_function_obj[function_obj_name]
            else:
                return
            module,class_name, function,args = parse_command_line(cmd)

            self.add_cmd_to_history(cmd,  module, None, class_name)
            #args[0]=self.sessions_alive['test_ssh'].session
            if module !='' or class_name!='' or function!='':
                after_sub_args=[]
                for i in range(len(args)):
                    a = args[i]
                    if a in globals():
                        after_sub_args.append(a)
                    elif a in DUT:
                        after_sub_args.append('DUT["{}"]'.format(a))
                    else:
                        after_sub_args.append(a)
                function_name, new_argvs, new_kwargs, str_code = call_function_in_module(module,class_name,function,after_sub_args, globals())
                #call_function = None

                # if class_name!="":
                #
                #     call_function = getattr(instance_name, function_name)
                #     #(*new_argvs,**new_kwargs)
                # else:
                #     call_function = instance_name#(*new_argvs,**new_kwargs)
                th =threading.Thread(target=call_function, args=new_argvs, kwargs=new_kwargs)
                th.start()

                #self.m_command_box.ShowPosition(len(self.m_command_box.GetString())+1)
                self.add_cmd_to_history(cmd,  module, str_code, class_name)

            else:
                error('"{}" is NOT a valid call in format:\n\tmodule.class.function call or \n\tmodule.function'.format(cmd))

        for cmd in cmds:
            try:
                handle_one_cmd(cmd)
            except:
                error(traceback.format_exc())
        self.redir.previous_scroll_pos=self.m_log.GetScrollRange(wx.VERTICAL)
        self.redir.provious_insert_pos = self.m_log.GetLastPosition()+1
        self.redir.out.SetInsertionPoint(self.redir.previous_insert_pos)
        self.redir.out.SetScrollPos(wx.VERTICAL,self.redir.previous_scroll_pos)

        event.Skip()
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
        elif keycode in [wx.WXK_RETURN]:
            #cmd = self.m_command_box.GetValue()
            self.m_command_box.SetInsertionPointEnd()
            #self.m_command_box.SetValue(cmd)
            event.Skip()
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
    def add_cmd_to_history(self, cmd, module_name, str_code, class_name=""):
        if str_code is None:
            if self.history_cmd==[]:
                self.history_cmd.append(cmd)
            elif self.history_cmd[-1]==cmd:
                pass
            else:
                self.history_cmd.append(cmd)
            self.history_cmd_index= len(self.history_cmd)
        else:# str_code is not None:
            self.add_cmd_to_sequence_queue(str_code,module_name, class_name )
        #self.sequence_queue.put([cmd, datetime.now()])
    def get_description_of_function(self, function_obj):
        import inspect
        fundefstr=''
        try:
            try:
                fundef = inspect.getsource(function_obj) # recreate function define for binary distribute
                fundefstr = fundef[:fundef.find(':')]
            except Exception as e:
                (args, varargs, keywords, defaults) =inspect.getargspec(function_obj)
                argstring = ''
                largs=len(args)
                ldefaults= len(defaults)
                gaplen = largs-ldefaults
                index =0

                for  arg in args:
                    if index <gaplen:
                        argstring+='%s, '%arg
                    else:
                        defvalue = defaults[index-gaplen]
                        if type('')==type(defvalue):
                            defvalue = '"%s"'%defvalue
                        argstring+='%s = %s, '%(arg,str(defvalue))
                    index+=1


                fundefstr ='%s( %s )'%(function_obj.func_name, argstring)
                fundef =fundefstr
            listoffun =fundef.split('\n')
            ret = function_obj.__doc__
            if ret:
                fundefstr = fundefstr +'\n    '+'\n    '.join(ret.split('\n'))

        except Exception as e:
            pass
        return fundefstr

    @gui_event_decorator.gui_even_handle
    def check_whether_function_file_is_updated(self):
        for module_file in self.dict_function_files.keys():
            old_modify_time = self.dict_function_files[module_file]
            current_modify_time = os.path.getmtime(module_file)
            if current_modify_time ==old_modify_time:
                continue
            else:
                if self.updating_function_page is False:
                    self.build_function_tab()
    @gui_event_decorator.gui_even_handle
    def build_function_tab(self):
        self.updating_function_page=True
        try:
            instances = self.dict_function_obj['instance'].keys()
            for inst_name in instances:
                inst = self.dict_function_obj['instance'][inst_name]
                #print ('instance ref count',inst_name, sys.getrefcount(inst))
                if 'close' in dir(inst):
                    inst.close()
                del inst
            fun_list = self.dict_function_obj.keys()
            for fun_name in fun_list:
                inst = self.dict_function_obj[fun_name]
                #print ('instance ref count',fun_name, sys.getrefcount(inst))
                del inst
            time.sleep(1)
            #import gc
            #gc.collect()

            self.dict_function_obj={'instance':{}}
            self.dict_function_files= {}
            src_path = os.path.abspath(self.src_path)
            if not os.path.exists(src_path):
                src_path= os.path.abspath(os.path.curdir)
            base_name = os.path.basename(src_path)
            #FIX ISSUE BELOW, rebuild function tree
            # Traceback (most recent call last):
            # File "gui\DasHFrame.pyc", line 995, in build_function_tab
            # File "wx\_controls.pyc", line 5428, in AddRoot
            # PyAssertionError: C++ assertion "parent.IsOk() || !(HTREEITEM)::SendMessageW((((HWND)GetHWND())), (0x1100 + 10), (WPARAM)(0x0000), (LPARAM)(HTREEITEM)(0))" failed at ..\..\src\msw\treectrl.cpp(1472) in wxTreeCtrl::DoInsertAfter(): can't have more than one root in the tree

            self.function_page.DeleteAllItems()
            root =self.function_page.AddRoot(base_name)
            item_info = wx.TreeItemData({'name':src_path})
            self.function_page.SetItemData(root, item_info)
            modules = get_folder_item(src_path)

            if modules is None:
                self.function_page.SetItemText(root, self.function_page.GetItemText(root) + ' Not Exists!!!')
                self.function_page.SetItemTextColour(root, wx.Colour(255, 0, 0))
                return
            for module_file in modules:
                if module_file.endswith('.pyc'):
                    if  module_file[:-1] in modules:
                        continue
                if  module_file.startswith('__'):
                    continue
                path_name = '{}'.format(os.path.abspath(self.src_path))
                module_name = os.path.basename(module_file).split('.')[0]
                extension = os.path.basename(module_file).split('.')[-1]
                full_name = '{}/{}'.format(path_name,module_file)
                if extension.lower() in ['py', 'pyc']:
                    try:
                        new_module = self.function_page.InsertItem(root, root, module_name)
                        module_file, path_name, description = imp.find_module(module_name)
                        lmod = imp.load_module(module_name, module_file, path_name,description)
                        self.dict_function_files[full_name] = os.path.getmtime(full_name)
                        for attr in sorted(dir(lmod)):
                            if attr.startswith('__'):
                                continue
                            attr_obj = getattr(lmod, attr)
                            attr_type = type(attr_obj)

                            if attr_type == types.FunctionType :
                                new_item  = self.function_page.InsertItem(new_module, new_module, '{}'.format( attr))
                                fun_str = '{}.{}'.format(module_name,attr)
                                item_info = wx.TreeItemData({'name':fun_str,
                                                             'tip':self.get_description_of_function(attr_obj),

                                                             })
                                self.dict_function_obj[fun_str] = attr_obj
                                self.function_page.SetItemData(new_item, item_info)
                            elif attr_type== types.TypeType:
                                #class_obj = getattr(lmod, attr)
                                instance = getattr(lmod, attr)()
                                self.dict_function_obj['instance'][attr]=instance

                                new_class  = self.function_page.InsertItem(new_module, new_module, attr)
                                item_info = wx.TreeItemData({'name':'{}.{}'.format(module_name,attr)})
                                self.function_page.SetItemData(new_class, item_info)
                                for attr_in_class in sorted(dir(instance)):
                                    if attr_in_class.startswith('__'):
                                        continue
                                    attr_obj = getattr(instance,attr_in_class)
                                    attr_type =type(attr_obj)

                                    if attr_type == types.MethodType :
                                        fun_str = '{}.{}.{}'.format(module_name,attr,attr_in_class)
                                        item_info = wx.TreeItemData({'name':fun_str,
                                                                     'tip':self.get_description_of_function(attr_obj)})
                                        new_item  = self.function_page.InsertItem(new_class, new_class, attr_in_class)
                                        self.dict_function_obj[fun_str] = getattr(instance, attr_in_class)#attr_obj
                                        self.function_page.SetItemData(new_item, item_info)
                    except :
                        pass
            self.function_page.Expand(root)
            first_child = self.function_page.GetFirstChild(root)
            self.function_page.Expand(first_child[0])
        except Exception as e:
            print(traceback.format_exc())
        self.updating_function_page=False

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

    def on_refresh_case_page(self, event):
        self.case_suite_page.DeleteAllItems()
        self.build_suite_tree()
        info('Refresh Case tab done!')
    def on_right_down_in_session_tab(self, event):
        menu = wx.Menu()
        item = wx.MenuItem(menu, wx.NewId(), "Refresh")
        #acc = wx.AcceleratorEntry()
        #acc.Set(wx.ACCEL_NORMAL, ord('O'), self.popupID1)
        #item.SetAccel(acc)
        menu.AppendItem(item)

        self.Bind(wx.EVT_MENU, self.on_refresh_session_page,item)
        self.PopupMenu(menu,event.GetPosition())
    def on_refresh_session_page(self, event):
        self.session_page.DeleteAllItems()
        self.build_session_tab()
        info('Refresh Session tab done!')
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
    def add_cmd_to_sequence_queue(self, cmd, module_name, class_name=""):
        if self.import_modules.has_key(module_name):
            pass
        else:
            self.import_modules.update({module_name:class_name})
        self.sequence_queue.put([cmd,datetime.now() ])
    def generate_code(self, file_name ):
        #todo 2017-10-21 no code need, when no command entered at all
        str_code ="""#created by DasH {}
if __name__ == "__main__":
    import sys, traceback
    sys.path.insert(0,r'{}')
    sys.path.insert(0,r'{}')
    import common

    log_path= '../log/tmp'
    log_path= common.create_case_folder()
    DUT={}
    try:

""".format(datetime.now().isoformat('-'), self.src_path,self.lib_path , "{}")
        sessions =[]
        for module in self.import_modules:
            str_code+='        import {mod}\n'.format(mod=module)#\n    {mod}_instance = {mod}()
        for module in self.import_modules:
            class_name = self.import_modules[module]
            if class_name!="":
                str_code+='        {mod}_instance = {mod}.{class_name}()\n'.format(mod=module, class_name=class_name)#\
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
            no_operation=False
        str_code+='        sys.exit(-1)\n'#, sys.exit(-1)
        for ses in sessions:
            str_code+='''    {}.close_session()\n'''.format(ses)
        info('code saved to file: ',file_name)
        info(str_code)
        info('code saved to file: ',file_name)
        if not no_operation:
            with open(file_name, 'a+') as f:
                f.write(str_code)
        else:
            info('No code will be saved to file, due to no operation was performed ',file_name)

    def on_right_down_in_case_tab(self, event):
        menu = wx.Menu()
        item1 = wx.MenuItem(menu, wx.NewId(), "Run Test")
        item2 = wx.MenuItem(menu, wx.NewId(), "Kill Test")
        item3 = wx.MenuItem(menu, wx.NewId(), "Refresh")

        #acc = wx.AcceleratorEntry()
        #acc.Set(wx.ACCEL_NORMAL, ord('O'), self.popupID1)
        #item.SetAccel(acc)
        menu.AppendItem(item1)
        menu.AppendItem(item2)
        menu.AppendItem(item3)
        self.Bind(wx.EVT_MENU, self.on_run_script,item1)
        self.Bind(wx.EVT_MENU, self.on_kill_script,item2)
        self.Bind(wx.EVT_MENU, self.on_refresh_case_page,item3)
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
    def run_script(self, script_name):

        old_script_name = script_name
        lex = shlex.shlex(script_name)
        lex.quotes = '"'
        lex.whitespace_split = True
        script_name_and_args = list(lex)

        script_args = script_name_and_args[1:]
        script_name = script_name_and_args[0]
        if script_name.find(os.path.sep)!=-1:
            pass
        else:
            script_name= '{}/{}'.format(self.suite_path,script_name)
        from lib.common import create_case_folder
        old_sys_argv = sys.argv
        sys.argv= [script_name]+script_args
        case_log_path = create_case_folder(self.log_path )#self.log_path #create_case_folder()
        sys.argv= old_sys_argv
        try:
            if os.path.exists('script_runner.exe'):
                execute = 'script_runner.exe'
                cmd = [execute,script_name ]+script_args + ['-l','{}'.format(case_log_path)]
                #p=subprocess.Popen(cmd, creationflags = subprocess.CREATE_NEW_CONSOLE)
            else:
                cmd = [sys.executable,'./script_runner.py', script_name ]+script_args+ ['-l','{}'.format(case_log_path)]

            p=subprocess.Popen(cmd, creationflags = subprocess.CREATE_NEW_CONSOLE)#, stdin=pipe_input, stdout=pipe_output,stderr=pipe_output)
            self.add_new_case_to_report(p.pid, old_script_name, p, case_log_path)
        except:
            error(traceback.format_exc())

        return p, case_log_path
    def on_run_script(self,event):
        hit_item = self.case_suite_page.GetSelection()
        item_name = self.case_suite_page.GetItemText(hit_item)

        item_data = self.case_suite_page.GetItemData(hit_item).Data
        script_name = self.case_suite_page.GetItemData(hit_item).Data['path_name']
        if script_name.lower().split('.')[-1] in ['txt','csv']:#test suite file, not a single script
            self.run_a_test_suite(script_name)
        else:#a single test case

            self.on_kill_script(event)
            try:
                p, case_log_path = self.run_script('{} {}'.format(script_name, item_name.replace(os.path.basename(script_name), '')))
                self.case_suite_page.GetItemData(hit_item).Data['PROCESS']=p
                self.case_suite_page.GetItemData(hit_item).Data['FULL_NAME']= item_name
                info('start process {} :{}'.format(item_name,  p.pid))
                #p.join() # this blocks until the process terminates
                time.sleep(1)
            except Exception as e :
                error(traceback.format_exc())

        #p = Process(target=run_script, args=[script_name,  script_and_args])
        #p.start()
    def check_case_status(self):
        self.check_case_running_status_lock.acquire()
        changed=False
        running_case = 0

        for pid in self.dict_test_report.keys():
            case_name, start_time, end_time, duration, return_code ,proc, log_path= self.dict_test_report[pid]
            if return_code is None:
                if proc.poll() is None:
                    running_case+=1
                    debug('RUNNING', start_time, end_time, duration, return_code ,proc, log_path)
                else:
                    changed=True
                    return_code = 'FAIL' if proc.returncode else 'PASS'
                self.update_case_status(pid,return_code)
        if running_case:
            pass
        elif not self.case_queue.empty():#self.case_queue.qsize():
                case_name_with_args = self.case_queue.get()
                p, case_log_path = self.run_script(case_name_with_args)
        self.check_case_running_status_lock.release()
        if changed:
            #test_report = self.generate_report(filename='{}/dash_report.txt'.format(self.log_path))
            self.mail_test_report('DasH Test Report-updating')

        return changed
    def polling_running_cases(self):
        try:
            while self.alive:
                time.sleep(10)
                try:
                    self.check_case_status()
                except:
                    if self.alive:
                        error(traceback.format_exc())
        except:
            pass
        print('end polling_running_cases')
        time.sleep(0.01)
                    #sys.exit(0) #break can't exit the app immediately, so change it to exit
                #self.check_case_running_status_lock.acquire()

            #self.check_case_running_status_lock.release()



    def add_new_case_to_report(self, pid, case_name, proc, log_path):
        start_time=datetime.now()
        duration = 0
        end_time = None
        return_code = None
        #self.check_case_running_status_lock.acquire()
        if pid in self.dict_test_report:
            self.dict_test_report[pid].update([case_name, start_time, end_time, duration, return_code, proc, log_path])
        else:
            self.dict_test_report[pid]=       [case_name, start_time, end_time, duration, return_code, proc, log_path ]
        #self.check_case_running_status_lock.release()
    def update_case_status(self, pid,return_code=None):
        now = datetime.now()
        case_name, start_time, end_time, duration, tmp_return_code ,proc,log_path= self.dict_test_report[pid]

        if tmp_return_code is None:
            duration = (now-start_time).total_seconds()
            if return_code is not None:
                end_time=now
            self.dict_test_report[pid]=[case_name,start_time, end_time, duration, return_code, proc, log_path]

        else:
            pass# don't update one case result twice


    def mail_test_report(self, subject="DASH TEST REPORT-updating"):
        try:

            #self.check_case_status()
            report_all_cases=True
            if subject.find('updating')!=-1:
                report_all_cases=False
            test_report = self.generate_report(filename='{}/dash_report_{}.html'.format(self.log_path, self.timestamp),report_all_cases= report_all_cases)
            #TO, SUBJECT, TEXT, SERVER, FROM
            send_mail_smtp_without_login(self.mail_to_list, subject,test_report,self.mail_server,self.mail_from)
        except Exception as e:
            error(traceback.format_exc())
    def on_mail_test_report(self,event):
        self.mail_test_report('DasH Test Report-requested')
        #p.terminate()
    def on_handle_request_via_mail(self):
        import imaplib
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
        url, user, password = self.mail_read_url,self.mail_user, self.mail_password
        if self.mail_user in ['nonexistent@dash.com']:
            return
        conn = imaplib.IMAP4_SSL(url,993)
        #conn.logout()
        #conn.authenticate('')
        conn.debug = 0#10
        def plain_callback(response):
            return "{}\x00{}\x00{}".format(user.lower(),user.lower(),password)
        try:
            conn.authenticate('PLAIN',plain_callback)
        except:
            conn.login(user,password)
        self.mail_failure = False
        conn.select('INBOX')#, readonly=True)

        try:

            authorized_mail_address = self.mail_to_list.replace(',',';').split(';')
        except Exception as e:
            return

        for mail_address  in authorized_mail_address:
            results,data = conn.search(None,'(UNSEEN)', '(FROM "{}")'.format(mail_address)) # #'ALL')
            msg_ids = data[0]
            msg_id_list = msg_ids.split()

            MAX_UNREAD_MAIL = 50
            for unread_mail_id in msg_id_list[::-1][:MAX_UNREAD_MAIL]:
                result,data = conn.fetch(unread_mail_id,'(BODY.PEEK[HEADER])')#"(RFC822)")#
                raw_email = data[0][1]
                p = Parser()
                msg = p.parsestr(raw_email)
                #msg = process_multipart_message(msg )
                from1 = msg.get('From')
                sub = '{}'.format(msg.get('Subject'))
                sub = sub.strip().lower()
                support_list='''
    ###############################
    mail subject below is supported:
        dash-request-case-queue    : request the cases in queue which to be executed
        dash-request-case          : request cases which are under suite_path
        dash-request-report        : request a test report by now
        dash-request-kill-running  : to kill all running test cases
        dash-request-clear-queue   : to clear/remove all cases which are in case queue
        dash-request-run           : to run script(s), each line is a script with arguments if it has
    --------------------------------
    ***non-case-sensitive***
    ###############################
                    '''
                handled =False
                if sub in ['dash']:
                    send_mail_smtp_without_login(self.mail_to_list, 'DONE-DasH Support List',support_list,self.mail_server,self.mail_from)
                    handled = True
                    #conn.uid('STORE', unread_mail_id, '+FLAGS', '\SEEN')
                elif sub in ['dash-request-case-queue']:
                    case_in_queue =self.get_case_queue(None)
                    send_mail_smtp_without_login(self.mail_to_list, 'DONE-DasH:Case In Queue',case_in_queue+support_list,self.mail_server,self.mail_from)
                    #conn.uid('STORE', unread_mail_id, '+FLAGS', '\SEEN')
                    handled = True
                elif sub in ['dash-request-case']:
                    cases_string = '\n\t'.join(self.case_list)
                    send_mail_smtp_without_login(self.mail_to_list, 'DONE-DasH:Case List',cases_string+support_list,self.mail_server,self.mail_from)
                    handled = True
                    #conn.uid('STORE', unread_mail_id, '+FLAGS', '\SEEN')
                elif sub in ['dash-request-report']:
                    self.mail_test_report('DasH Test Report-requested')
                    #conn.uid('STORE', unread_mail_id, '+FLAGS', '\SEEN')
                    handled = True
                elif sub in ['dash-request-kill-running']:
                    killed= self.on_kill_running_case()
                    send_mail_smtp_without_login(self.mail_to_list, 'DONE-[DasH]:Killed Running Case(s)',killed+support_list,self.mail_server,self.mail_from)
                    handled = True
                    #conn.uid('STORE', unread_mail_id, '+FLAGS', '\SEEN')
                elif sub in ['dash-request-clear-queue']:
                    case_in_queue = self.on_clear_case_queue()
                    send_mail_smtp_without_login(self.mail_to_list, 'DONE-DasH:Clear Case Queue',case_in_queue+support_list,self.mail_server,self.mail_from)
                    handled = True
                    #conn.uid('STORE', unread_mail_id, '+FLAGS', '\SEEN')
                elif sub in ['dash-request-run']:
                    #if from1 in [ 'yu_silence@163.com',self.mail_to_list]:
                    conn.uid('STORE', unread_mail_id, '+FLAGS', r'(\SEEN)')
                    handled = True

                    #conn.uid('STORE', '-FLAGS', '(\Seen)')
                    payload = msg.get_payload()
                    payload = process_multipart_message(payload )
                    from lib.html2text import html2text
                    txt = html2text(payload)
                    cases = txt.replace('\r\n','\n').split('\n')
                    for line in cases:
                        line = line.strip()
                        if line.strip().startswith('#') or len(line)==0:
                            pass
                        else:
                            #done: replace lines below with a function
                            self.add_line_to_case_queue(line)
                    result,data = conn.fetch(unread_mail_id,'(RFC822)')#"(RFC822)")#
                else:

                    conn.uid('STORE', unread_mail_id, '-FLAGS', r"(\SEEN)")
                    #fixed : 2017-09-25 failed to set unmatched mail to unread, to fetch it again with RFC822
                if handled:
                    result,data = conn.fetch(unread_mail_id,'(RFC822)')#"(RFC822)")#
    def check_case_type(self, str_line):
        lex = shlex.shlex(str_line)
        lex.quotes = '"'
        lex.whitespace_split = True
        script_name_and_args = list(lex)
        script_name = script_name_and_args[0]
        return script_name.lower().split('.')[-1],script_name_and_args[0] ,script_name_and_args[1:]

    def polling_request_via_mail(self):
        try:
            while self.alive:
                time.sleep(5)
                try:
                    self.on_handle_request_via_mail()
                    self.mail_failure =False
                except Exception as e:
                    self.mail_failure =True
        except :
            pass
        print('end polling_request_via_mail!!!')
        time.sleep(0.01)

    def get_case_queue(self, item=None):
        case_in_queue = list(self.case_queue.queue)
        number_in_queue= len(case_in_queue)
        if number_in_queue:
            str_case_in_queue='\ntotal {} case(s) in Queue\n'.format(number_in_queue)+'\n'.join('{}'.format(x) for x in case_in_queue)
        else:
            str_case_in_queue='\nNo Case in Queue'
        info('Case(s) in Queue', str_case_in_queue)

        return str_case_in_queue



    def on_clear_case_queue(self, event=None):
        case_in_queue = self.get_case_queue(None)
        self.case_queue.queue.clear()
        self.get_case_queue(None)
        return  case_in_queue
    def on_kill_running_case(self,event=None):
        killed_case= ''
        for case in self.dict_test_report:
            case_name,start_time, end_time, duration, return_code, proc, log_path = self.dict_test_report[:7]
            if return_code is None:
                if proc.poll() is None:
                    killed_case+='{}:{}\n'.format(case_name, proc.pid)
                    info('Terminate alive process {}:{}'.format(case_name, proc.pid))
                    result ='KILL'
                    self.update_case_status(proc.pid, result)
                    proc.terminate()
        info('Killed All Running cases', killed_case)
        return killed_case
    def run_a_test_suite(self, csv_file_name, clear_queue=False, kill_running =False):
        try:
            case_type, suite_file_name, args =self.check_case_type(csv_file_name)
            if clear_queue:
                self.on_clear_case_queue()
            if kill_running:
                self.on_kill_running_case()
            import csv
            if suite_file_name.find(os.path.sep)!=-1:
                pass
            else:
                suite_file_name= '{}/{}'.format(self.suite_path,suite_file_name)
            with open(suite_file_name) as bench:
                reader = csv.reader(bench,delimiter=',')
                for row in reader:
                    if len(row)<1:
                        continue
                    else:
                        name = row[0]
                        args.insert(0,0)
                        for index in range(1,len(args)):
                            name =name.replace('{{index}}'.format(index =index), '{}'.format(args[index]))
                        self.case_queue.put(name)
                        info('adding case to queue: {}'.format(name))
        except Exception as e:
            error(traceback.format_exc())

    def web_server_start(self):
        from SocketServer import ThreadingMixIn
        from BaseHTTPServer import HTTPServer,BaseHTTPRequestHandler
        import  cgi , urllib#StringIO
        class HttpHandler(BaseHTTPRequestHandler):
            runner_proc =self.add_line_to_case_queue
            root = os.path.dirname(__file__)+ '/html/'
            home = root
            suite_path = self.suite_path
            log_path = self.log_path
            session_path = self.session_path

            def __del__(self):
                #self.hdrlog.close()
                #print('end http server')
                pass

            def list_dir(self, path, related_path, pattern=['']):
                """Helper to produce a directory listing (absent index.html).

                Return value is either a file object, or None (indicating an
                error).  In either case, the headers are sent, making the
                interface the same as for send_head().

                """
                content =""
                try:
                    list = os.listdir(path)
                except os.error:
                    self.send_error(404, "No permission to list directory")
                    return ""
                list.sort(key=lambda a: a.lower())
                #f = StringIO()
                displaypath = cgi.escape(urllib.unquote(self.path))
                content='<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">'
                content+="<html>\n<title>Directory listing for %s</title>\n" % displaypath
                content+="<body>\n<h2>Directory listing for %s</h2>\n" % displaypath
                content+="<hr>\n<ul>\n"
                content+='''<SCRIPT>
function post( id, script, dest )
{
element = document.getElementById(id);
value = element.value
params = 'script='+encodeURI(script)+'&arg='+encodeURI(value)
var xmlhttp;

if (window.XMLHttpRequest)
{// code for IE7+, Firefox, Chrome, Opera, Safari
xmlhttp=new XMLHttpRequest();
}
else
{// code for IE6, IE5
xmlhttp=new ActiveXObject('Microsoft.XMLHTTP');
}

xmlhttp.onreadystatechange=function()
{
if (xmlhttp.readyState==4 && xmlhttp.status==200)
{
alert(xmlhttp.responseText);
newHTML( xmlhttp.responseText);
setTimeout("window.close()",3000);
}
}
xmlhttp.open("POST",dest,true);
xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
xmlhttp.send( params );
}
function newHTML(HTMLstring) {
//var checkitem = mygetCheckedItem();
//HTMLstring=post( 'manualtest','/cgi-bin/onSUTLIST.py', 'bedname='+encodeURI(checkitem) );
var newwindow=window.open();
var newdocument=newwindow.document;
newdocument.write(HTMLstring);
newdocument.close();
}
</SCRIPT>
<table>'''

                for name in list:
                    extension = os.path.basename(name).split('.')[-1]
                    if pattern in ['', '*', '*.*']:
                        pass
                    elif extension in pattern:
                        pass
                    else:
                        continue
                    fullname = os.path.join(path, name)
                    displayname = linkname = name
                    # Append / for directories or @ for symbolic links
                    if os.path.isdir(fullname):
                        displayname = name + "/"
                        linkname = name + "/"
                    if os.path.islink(fullname):
                        displayname = name + "@"
                        # Note: a link to a directory displays with @ and links with /
                    input_button =""
                    filename = urllib.quote(linkname)
                    if not related_path.endswith('/'):
                        related_path+='/'
                    fullfilename =related_path+urllib.quote(linkname)
                    if related_path.startswith('/case') and os.path.isfile(fullname):
                        input_button = """<input id=%s name="ARGS" style="width:200"  type="text" value="" rows="1"   autocomplete="on"/>
<input name="go" value="Run" type="button" onclick="post('%s','%s', 'RunCase');return false";/>"""%(filename,filename,fullfilename)
                    elif related_path.startswith('/suite') and os.path.isfile(fullname):
                        input_button = """<input id=%s name="ARGS" style="width:200"  type="text" value="" rows="1"   autocomplete="on"/>
<input name="go" value="Run" type="button" onclick="post('%s','%s', 'RunSuite');return false";/>
</td></tr>\n"""%(filename,filename,fullfilename)
                    content+='<tr><td><a href="%s">%s</a></td><td>'% (related_path+urllib.quote(linkname), cgi.escape(displayname))+input_button
                content+="</table></ul>\n<hr>\n</body>\n</html>\n"

                return content
            def array2htmltable(self,Array):
                content = "<table   border='1' align='left' width=autofit  >"

                for index , sublist in enumerate( Array):
                    content += '  <tr><td>\n%d</td><td>'%(index+1)
                    content += '    </td><td>'.join([x if x!='' else '&nbsp;' for x in sublist ])
                    content += '  \n</td></tr>\n'
                content += ' \n </table><br>'
                return  content
            def show_content_by_path(self, path, type='csv'):
                header = '''
<table   border="0" align='center' width="100%"  >
<tr>    <td align=center valign=middle><a href="/">Back to DasH</a></td>		</tr>
</table>'''
                footer = header
                if  os.path.isfile(path):

                    indexpage= open(path)
                    encoded=indexpage.read()
                    html = []
                    for line in encoded.split('\n'):
                        html.append('<p>%s</p>'%line.replace('\r', '').replace('\n',''))
                    encoded= ''.join(html)
                    if type in ['csv']:
                        ar =[]
                        for line in html:
                            row = line.split(',')
                            ar.append(row)
                        encoded = self.array2htmltable(ar)
                    # elif type in ['py']:
                    #     ar =[]
                    #     for line in html:
                    #         row = line.split(',')
                    #         ar.append(row)
                    #     encoded = self.array2htmltable(ar)
                else:
                    encoded =self.list_dir(path, self.path, type)
                #encoded = "<html>{}</html>".format(cgi.escape(encoded))
                encoded =header+encoded.replace('\t', '&nbsp;    ').replace('    ', '&nbsp;    ') + footer
                return  encoded
            def do_GET(self):

                root = self.root
                home = self.home
                suite_path = self.suite_path
                log_path = self.log_path

                response = 200
                type = 'text/html'
                if self.path=='/':
                    indexpage= open(home+ 'index.html', 'r')
                    encoded=indexpage.read()
                    encoded = encoded.encode(encoding='utf_8')
                elif self.path =='/favicon.ico':
                    indexpage= open(home+'dash.bmp', 'r')
                    encoded=indexpage.read()
                    type =  "application/x-ico"
                elif self.path=='/home':
                    path = os.path.abspath(self.suite_path)
                    encoded =self.list_dir(path, './')
                elif self.path.startswith('/sessions'):
                    path = os.path.abspath(self.session_path)
                    path = path+ self.path[9:]#replace('/log/','/')
                    encoded = self.show_content_by_path(path)
                elif self.path.startswith('/case'):
                    path = os.path.abspath(self.suite_path)
                    path = path+ self.path[5:]#replace('/log/','/')
                    encoded = self.show_content_by_path(path, 'py')
                elif self.path.startswith('/suite'):
                    path = os.path.abspath(self.suite_path)
                    path = path+ self.path[6:]#replace('/log/','/')
                    encoded = self.show_content_by_path(path, 'csv')
                elif self.path.startswith('/log'):
                    path = os.path.abspath(self.log_path)
                    print(path)
                    path = path+ self.path[4:]#replace('/log/','/')
                    encoded = self.show_content_by_path(path, '*')
                elif self.path.startswith('/report'):
                    path = os.path.abspath(self.log_path)
                    print(path)
                    path = path+ self.path[7:]#replace('/report/','/')
                    encoded = self.show_content_by_path(path, 'html')
                else:
                    path = os.path.abspath(root)
                    path = path+ self.path.replace('//','/')
                    if  os.path.isfile(path):
                        from lib.common import csvfile2array
                        arrary = csvfile2array(path)
                        encoded = self.array2htmltable(arrary)
                    else:
                        encoded =self.list_dir(path, self.path)


                self.send_response(200)
                self.send_header("Content-type", type)
                self.end_headers()
                self.wfile.write(encoded)
            def LoadHTMLPage(self, filename, replace=[], Pattern4ESCAPE1='#NOTEXISTPATTERN_HERE_FOR_STRING_FORMAT1#',Pattern4ESCAPE2='#NOTEXISTPATTERN_HERE_FOR_STRING_FORMAT2#'):

                indexpage= open(filename, 'r')
                encoded=indexpage.read()
                encoded =encoded.replace('%s',Pattern4ESCAPE1 )
                encoded =encoded.replace('%',Pattern4ESCAPE2 )
                encoded =encoded.replace(Pattern4ESCAPE1,'%s' )

                for item in replace:
                    encoded =encoded.replace('%s', item, 1)
                encoded =encoded.replace(Pattern4ESCAPE2, '%' )

                return encoded

            def RunScript(self, script, args=None):
                    if not args:
                        args =''
                    exe_cmd = '%s %s'%(script,args)
                    print('Run Script:'+exe_cmd)
                    encoded = self.runner_proc(exe_cmd)
                    #encoded ='run{}'.format(exe_cmd)
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")#; charset=%s" % enc)
                    self.end_headers()
                    self.wfile.write(encoded)


            def ParseFormData(self, s):
                import re
                reP = re.compile('^(-+[\d\w]+)\r\n(.+)-+[\d\w]+-*', re.M|re.DOTALL)
                #s = '''-----------------------------186134213815046583202125303385\r\nContent-Disposition: form-data; name="fileToUpload"; filename="case1.csv"\r\nContent-Type: text/csv\r\n\r\n,ACTION,EXPECT,TIMEOUT,CASE OR COMMENTS\n[case1],,,,\n#var,\ncmd,${5}\ncmd2,${cmd2}\n#setup,,,,\ntel,pwd,],10\ntel,ls,],10,\n,ls,],10,\ntel,${cmd},],10,\n,${cmd2},],10,\n#!---,,,,\n\n\r\n-----------------------------186134213815046583202125303385--\r\n'''
                #rs = re.escape(s)
                rs =s
                m = re.match(reP, rs)
                print(rs)
                if m:
                    print('match!')
                    boundary = m.group(1)
                    print(m.group(2))
                    c = m.group(2)
                    index =c.find(boundary)
                    if index ==-1:
                        pass
                    else:
                        c = c[:index]
                    l = c.split('\r\n')
                    print(l)
                    attribute=l[0].split('; ')
                    da={}
                    la =attribute[0].split(':')
                    da.update({la[0]:la[1]})
                    for a in attribute[1:]:
                        la=a.split('=')
                        da.update({la[0]:la[1].replace('"','').replace('\'','')})
                    data = '\r\n'.join(l[3:-1])
                    filename = da['filename']
                    if filename.find('\\')!=-1:
                        filename=filename[filename.rfind('\\')+1:]
                    else:
                        filename=filename[filename.rfind('/')+1:]
                    return (da['name'],filename,data)
                else:
                    print('not match')
                    return None
            def do_POST(self):
                content_len = int(self.headers['Content-Length'])
                #self.queryString
                self.path
                s = self.rfile.read(content_len)
                encoded=''
                try:
                    s=str(s)
                    import urlparse
                    req = urlparse.parse_qs(urlparse.unquote(s))
                    strip_char_length = 6 #for case
                    if self.path.startswith('/RunSuite'):
                        strip_char_length = 7
                    elif self.path.startswith('/RunCase'):
                        strip_char_length = 6
                    script = '{}/{}'.format(self.suite_path, req['script'][0][strip_char_length:])#remove the starting string /case/ or /suite/
                    if req.has_key('arg'):
                        arg= req['arg'][0]
                    else:
                        arg = ''

                    executefile =''
                    cmd_line = script+ ' '+ arg

                    encoded=self.runner_proc(cmd_line)
                    #print(encoded)
                    encoded = encoded.encode(encoding='utf_8').replace('\t', '    ').replace('\n','')
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")#; charset=%s" % enc)
                    self.end_headers()
                    self.wfile.write(encoded)

                except Exception as e:
                    import traceback
                    print(traceback.format_exc())
                    response = self.ParseFormData(s)
                    if response:
                        type, filename, data =response
                        encoded = self.onUploadFile(type, filename, data)
                    else:
                        encoded ='ERROR: %s, Can\'t parse Form data: %s'%(str(e),s)
                        encoded= encoded.encode(encoding='utf_8')
                    try:
                        requestline = self.requestline
                        import re
                        reScript=re.compile('POST\s+(.+)\s+HTTP.*', re.DOTALL)
                        m= re.match(reScript, requestline)
                        if m:
                            returncode =self.RunScript(m.group(1),[])
                            encoded ='script %s completed with return code %d!'%(m.group(1), returncode)
                    except Exception as e:
                        encoded ='can\'t run script!'
                        encoded = encoded.encode(encoding='utf_8', errors='strict')

                # self.send_response(200)
                # self.send_header("Content-type", "text/html")#; charset=%s" % enc)
                # self.end_headers()
                # self.wfile.write(encoded)

        port =self.web_port
        home = __file__ #sys.argv[0]
        if os.path.exists(home):
            home = os.path.dirname(home)
            root = home
            home = home +'/html/'
            #done move runWebserver to DasH, and launch it at dash initialization

        class ThreadingHttpServer(ThreadingMixIn, HTTPServer):
            pass
        httpd=ThreadingHttpServer(('',port), HttpHandler)

        from socket import socket, AF_INET, SOCK_DGRAM, gethostname,SOL_SOCKET, SO_REUSEADDR, getfqdn#*


        try:
            hostip=''
            s = socket(AF_INET, SOCK_DGRAM)
            s.bind(("", 1234))
            #sq = socket(AF_INET, SOCK_DGRAM)
            s.connect(("10.0.0.4", 1234))

            domain = getfqdn()
            hostip = s.getsockname()[0]
            self.web_host = hostip
            self.SetTitle('DasH-{}:{}'.format(self.web_host, self.web_port))
            s.close()
        except Exception as e:
            import traceback
            msg = traceback.format_exc()
            print(msg)
        hostname =gethostname()

        info("Server started on %s (%s),port %d....."%(hostname,hostip,port))
        #print('Process ID:%d'%os.geteuid())
        self.web_daemon= httpd
        on=1
        self.web_daemon.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, on)
        httpd.serve_forever()

        try:
            s.close()
        except:
            pass
    def add_line_to_case_queue(self,line):
        type_case, case_name, args = self.check_case_type(line)
        if type_case in ['txt','csv']:
            self.run_a_test_suite(line)
        else:
            self.case_queue.put(line)
        return info('adding case to queue: {}'.format(line))

    def OnMouseMotion(self, evt):
        try:
            active_page = self.navigator.GetCurrentPage()
            pos = self.case_suite_page.ScreenToClient(wx.GetMousePosition())
            item_index, flag = active_page.HitTest(pos)
            item_data = active_page.GetItemData(item_index)
            tip = active_page.GetToolTip()
            if item_data :
                if item_data.Data.has_key('tip'):
                    active_page.SetToolTipString(item_data.Data['tip'])
                else:
                    from pprint import pformat
                    tip_string = pformat(item_data.Data)
                    active_page.SetToolTipString(tip_string)
            if False:
                if flag == wx.LIST_HITTEST_ONITEMLABEL:
                    active_page.SetToolTipString('Some information about ' + self.case_suite_page.GetItemText(item_index))
                else:
                    active_page.SetToolTipString('')
        except Exception as e:
            pass

        evt.Skip()
    def on_keyboard_key_down(self,event):

        event.Skip()
    @gui_event_decorator.gui_even_handle
    def on_generate_code(self, event):
        self.generate_code('{}/test_code_{}.py'.format(self.suite_path, datetime.now().isoformat().replace(':','-').replace('.','-')))
    def on_right_up_over_tab_in_edit_area(self, event):
        if self.edit_area.GetPageText(self.edit_area.GetSelection())=="*LOG*":
            return
        x = event.GetEventObject()
        tabID = x.GetId()
        tab = x.FindWindowById(tabID)
        #session.session.open(retry, interval)
        #tab.open(3,15)
        th =threading.Thread(target=self.edit_area.GetCurrentPage().open, args=[1, 5])
        #index = self.edit_area.GetCurrentPage().open(1, 60)
        th.start()
        event.Skip()
        #self.edit_area.SetSelection(index)
    def idle_process(self):
        try:
            self.on_handle_request_via_mail()
            self.mail_failure =False
        except Exception as e:
            self.mail_failure =True
        try:
            self.check_case_status()
        except:
            pass
        #print('{} i\'m idle !!!!!!!!!!!!!!!!!!'.format(datetime.now().isoformat()))
    def on_idle(self,event):
       # print('helllo!{}, {}\n'.format(                self.m_log.PositionToXY(                        self.m_log.GetScrollPos(wx.VERTICAL)                )[1],                self.m_log.PositionToXY(                        self.m_log.GetScrollRange(wx.VERTICAL))[1]        )        )
        #self.freeze_thaw_main_log_window()
        #self.m_log_current_pos-=1
        #self.m_log.SetScrollPos(wx.VERTICAL, self.m_log_current_pos)
        if True:
            self.out = self.redir.out
            current_pos = self.out.GetScrollPos(wx.VERTICAL)
            v_scroll_range = self.out.GetScrollRange(wx.VERTICAL)
            char_height = self.out.GetCharHeight()
            w_client,h_client = self.out.GetClientSize()
            max_gap=h_client*2/char_height/3
            c_col, c_line = self.out.PositionToXY(current_pos)
            t_col, t_line = self.out.PositionToXY(v_scroll_range)
            current_insert = self.out.GetInsertionPoint()
            tmp_msg ='\n insert {}, current_pos {} current first visible line {} column {} last line {}, colum {}\n'.format(current_insert, current_pos,  c_line, c_col, t_line, t_col)
            self.redir.old_stdout.write(tmp_msg)
        #self.redir.old_stdout.write('current {}, range {}, t_line {}, c_line {}, gap {}\n'.format(current_pos, v_scroll_range, t_line, c_line, t_line -c_line))

        now = datetime.now()
        max_idle=3
        if (now-self.last_time_call_on_idle).total_seconds()>max_idle:
            self.last_time_call_on_idle=now
            th=threading.Thread(target=self.idle_process, args=[])
            th.start()
        if self.updating_function_page is False:
            threading.Thread(target=self.check_whether_function_file_is_updated, args=[]).start()
    def on_m_log_text_changed(self, event):
        event.Skip()
        #self.freeze_thaw_main_log_window()

    def freeze_thaw_main_log_window(self):
            c_col, c_line = self.m_log.GetPosition()

            #print('cline', c_line)
            v_scroll_range = self.m_log.GetLastPosition()#wx.VERTICAL
            char_height = self.m_log.GetCharHeight()
            w_client,h_client = self.m_log.GetClientSize()
            max_gap=h_client/char_height/3
            current_pos = self.m_log.GetScrollPos(wx.VERTICAL)#self.m_log.XYToPosition(c_col, c_line)
            c_col, c_line = self.m_log.PositionToXY(current_pos)
            t_col, t_line = self.m_log.PositionToXY(v_scroll_range)

            #string = "{}\ncurrent {}\t total {},max_gap {}, gap {}, range {}\n".format(string, c_line, t_line, max_gap,t_line-c_line, self.out.GetScrollRange(wx.VERTICAL))
            #todo: when mulit-threads(up-to 7~9 SessionTab opened) are writting to DasHFrame.m_log, the log window was frozen, can't be thawed, if disable .freeze_main_log_window, there is no 'no response' issue
            #so suspect it's freeze issue
            frozen = self.m_log.IsFrozen()
            if t_line - c_line>max_gap:
                if not frozen:
                    self.m_log.SetInsertionPoint(self.m_log_current_pos)
                    self.m_log.SetScrollPos(wx.VERTICAL, self.m_log_current_pos)
                    self.m_log.Freeze()
                    #self.m_log_current_pos = current_pos#self.m_log.GetScrollPos(wx.VERTICAL)#current_pos
                    self.m_log.SetInsertionPoint(self.m_log_current_pos)
                    self.m_log.SetScrollPos(wx.VERTICAL, self.m_log_current_pos)
                    frozen=True

            else:
                self.m_log_current_pos= self.m_log.GetScrollRange(wx.VERTICAL)
                #self.m_log.SetScrollPos(wx.VERTICAL, )

            if frozen:
                self.m_log.SetInsertionPoint(self.m_log_current_pos)
                self.m_log.SetScrollPos(wx.VERTICAL, self.m_log_current_pos)

                self.m_log.Thaw()
                #time.sleep(0.1)




    @gui_event_decorator.gui_even_handle
    def on_generate_test_report(self,event):
        file_name='{}/dash_report_{}.html'.format(self.log_path, self.timestamp)
        report = self.generate_report(filename=file_name)#'{}/dash_report_{}.html'.format(self.log_path, self.timestamp))
        report = 'http://{}:{}/log/{}\n{}'.format(self.web_host, self.web_port, file_name.replace(self.log_path, ''),report)
        print(report)
    @gui_event_decorator.gui_even_handle
    def on_leftD_click_url_in_m_log(self, event):

        #print(urlString)
        mouseEvent = event.GetMouseEvent()
        if mouseEvent.LeftDClick():
            urlString = self.m_log.GetRange(event.GetURLStart(),event.GetURLEnd())
            webbrowser.open(urlString)
        event.Skip()



#done: 2017-08-22, 2017-08-19 save main log window to a file
#done: 2017-08-19 add timestamps to log message
#done: 2017-08-22, 2017-08-19 mail to someone
#done: 2017-08-19 run a script in DasH
#done: 2017-08-19 generate test report
#done: 2017-10-7 2017-08-19 publish all test cases in a web page
#done: 2017-10-7 2017-08-19 trigger a test remote via web page
#todo: 2017-08-19 re-run failed cases
#done: 2017-08-19 build executable packege for DasH
#todo: 2017-08-19 a popup window to get email address/password/mail_server...
#done: 2017-08-22 output in m_log window has a lot of empty line, need remove them
#todo: 2017-08-23 in common.call_function_in_module, should end all threads which are started in previous instance
#done: 2017-10-7  2017-08-23 add tips for all tree item in teh left
#done: 2017-10-7  2017-09-30 failed to send command to a session whose name start with numbers e.g. 1_session
    # Traceback (most recent call last):
    #   File "C:/workspace/gDasH\gui\DasHFrame.py", line 588, in on_command_enter
    #     instance_name, function_name, new_argvs, new_kwargs, str_code = call_function_in_module(module,class_name,function,args, globals())
    #   File "C:/workspace/gDasH\lib\common.py", line 153, in call_function_in_module
    #     eval('GetFunArgs({args})'.format(args=args_string))
    #   File "<string>", line 1
    #     GetFunArgs(35b)
    #                  ^
    # SyntaxError: invalid syntax
#todo: start thread for all gui event handlers with decoration, catch all exceptions
#done: mark red for all strings who match error patterns in "*LOG*", m_log
