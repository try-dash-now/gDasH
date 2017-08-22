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
            self.log_file = open(name, 'a+')
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
        if self.log_file:
            self.log_file.write(string)
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
        self.lib_path = os.path.abspath(self.ini_setting.get('dash','lib_path'))
        self.log_path = os.path.abspath(self.ini_setting.get('dash','log_path'))
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
        self.m_menubar_main.Append(fileMenu, "&Open")

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
    def on_close(self, event):
        self.generate_code(file_name='{}/test_script.py'.format(self.ini_setting.get('dash', 'log_path')))

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
        ses_name = closing_page.session.name
        self.tabs_in_edit_area.pop(self.tabs_in_edit_area.index(ses_name))
        if globals().has_key(ses_name):
            #g = dict(globals())
            globals()[ses_name]=None
            #del g[ses_name]
            #del globals()[ses_name]


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
            self.sessions_alive.update({ses_name: new_page.session})
            self.add_new_session_to_globals(new_page.session, '{}'.format(session_attribute.Data['attribute']))
            #globals().update({ses_name: new_page.session})

    def add_new_session_to_globals(self, ses, args_str):
        if globals().has_key(ses.name):
            if globals()[ses.name]==None:
                pass
            else:
                error('{} already '.format(ses.name))
        else:
            globals().update({ses.name: ses})
            self.add_cmd_to_sequence_queue('{} = dut.dut(name= "{}", **{})'.format(ses.name,ses.name,args_str ), 'dut')
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
    import sys
    sys.path.insert(0,r'{}')
    sys.path.insert(0,r'{}')

""".format(self.src_path,self.lib_path )
        sessions =[]
        for module in self.import_modules:
            str_code+='    import {mod}\n    {mod}_instance = {mod}()'.format(mod=module)
        no_operation = True
        while True:
            try:
                cmd, timestamp =self.sequence_queue.get(block=False)[:2]
                str_code +='    {} #{}\n'.format(cmd, timestamp.isoformat( ' '))
                if cmd.find('dut.dut(')!=-1:
                    sessions.append(cmd.split('=')[0].strip())
                no_operation=False
                #datetime.now().isoformat()
            except Exception as e:
                break
        close_session=''
        for ses in sessions:
            str_code+='    {}.close_session()\n'.format(ses)
        info(str_code)
        if not no_operation:
            with open(file_name, 'a+') as f:
                f.write(str_code)

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