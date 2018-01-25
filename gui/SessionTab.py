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
created 2017-08-12 by Sean Yu
'''


import wx.grid as gridlib
import wx
from gui.MainFrame import MainFrame
import os
from lib.common import load_bench, caller_stack_info, get_next_in_ring_list, get_folder_item, info,debug, warn,  error
import re
import time
import threading
from lib.dut import dut
import ConfigParser
import sys
import inspect
import Queue
import webbrowser
from datetime import datetime
import traceback
class SessionTab(wx.Panel, dut):
    stdout=None
    stderr=None
    parent = None
    type = type
    output_window = None
    cmd_window = None
    #session = None
    alive =False
    output_lock = None
    font_point = None
    cmd_window_font_size = 19
    history_cmd = None
    history_cmd_index = 0
    sequence_queue =None
    log_path =None
    name = None
    error_pattern =None
    last_json_file_saving_time=None
    def __del__(self):
        self.on_close()
    def on_close(self):
        self.alive = False
        self.close_session()
        self.sleep(0.001)
        info('tab {} closed!!!'.format(self.name))
    def __freeze_output_window(self):
        if self.output_window.IsFrozen():
            pass
        else:
            self.output_window_last_position =self.output_window.GetScrollRange(wx.VERTICAL)
            self.output_window.Freeze()
    def __thaw_output_window(self):
        self.output_window.SetScrollPos(wx.VERTICAL, self.output_window.GetScrollRange(wx.VERTICAL))
        if self.output_window.IsFrozen():
            self.output_window.Thaw()
        else:
            pass

    def update_output(self):
        last = self.output_window.GetLastPosition()
        status =True
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
        BACKSPACE_pat =re.compile('(\s*\b+\n*\s*)+')
        while( self.alive):
            try:
                status = self.alive #and self.session

                time.sleep(0.001)
                response=''
                #print('scroll pos', self.output_window.GetScrollPos(wx.VERTICAL), self.output_window.GetScrollRange(wx.VERTICAL))
                if self.alive:
                    self.output_lock.acquire()
                    response = self.read_display_buffer()
                    if True:
                        response = ansi_escape.sub('', response)
                        response = BACKSPACE_pat.sub('\n', response)
                        #response = re.sub().replace('\b', '')
                    BACKSPACE = chr(8)
                    #response = re.sub(chr(32)+BACKSPACE,'',response)

                    #BACKSPACE_pat = '.'+BACKSPACE#+'\[\d+[;]{0,1}\d*m'#+chr(27)+'\[0'
                if len(response)!=0:

                    current_pos = self.output_window.GetScrollPos(wx.VERTICAL)
                    v_scroll_range = self.output_window.GetScrollRange(wx.VERTICAL)
                    char_height = self.output_window.GetCharHeight()
                    w_client,h_client = self.output_window.GetClientSize()
                    max_gap=h_client*2/char_height/3
                    c_col, c_line = self.output_window.PositionToXY(current_pos)
                    t_col, t_line = self.output_window.PositionToXY(v_scroll_range)

                    if t_line- c_line>max_gap:#1000
                        self.__freeze_output_window()
                    else:
                        self.__thaw_output_window()
                    err_pattern = self.error_pattern#re.compile('error|\s+err\s+|fail|wrong')
                    wx.CallAfter(self.output_window.SetDefaultStyle,wx.TextAttr(wx.GREEN,  wx.BLACK,font =wx.Font(self.font_point, family = wx.DEFAULT, style = wx.NORMAL, weight = wx.NORMAL, faceName = 'Consolas')))

                    #if re.search('error|\s+err\s+|fail|wrong',response.lower()):
                    last_start = 0

                    for m in err_pattern.finditer(response.lower()):
                        #print(m.start(), m.end(), m.group())

                        wx.CallAfter(self.output_window.SetDefaultStyle,wx.TextAttr(wx.GREEN,  wx.BLACK,font =wx.Font(self.font_point, family = wx.DEFAULT, style = wx.NORMAL, weight = wx.NORMAL, faceName = 'Consolas')))
                        wx.CallAfter(self.output_window.AppendText, response[last_start:m.start()])
                        wx.CallAfter(self.output_window.SetDefaultStyle,wx.TextAttr(wx.YELLOW, wx.RED,  font =wx.Font(self.font_point+2, family = wx.DEFAULT, style = wx.NORMAL, weight = wx.NORMAL, faceName = 'Consolas')))
                        wx.CallAfter(self.output_window.AppendText, response[m.start():m.end()])
                        last_start= m.end()

                    wx.CallAfter(self.output_window.SetDefaultStyle,wx.TextAttr(wx.GREEN,  wx.BLACK,font =wx.Font(self.font_point, family = wx.DEFAULT, style = wx.NORMAL, weight = wx.NORMAL, faceName = 'Consolas')))
                    wx.CallAfter(self.output_window.AppendText, response[last_start:])


                    # else:
                    #     #self.output_window.SetDefaultStyle( wx.TextAttr(wx.GREEN,  wx.BLACK,font =wx.Font(self.font_point, family = wx.DEFAULT, style = wx.NORMAL, weight = wx.NORMAL, faceName = 'Consolas')))
                    #     wx.CallAfter(self.output_window.SetDefaultStyle,wx.TextAttr(wx.GREEN,  wx.BLACK,font =wx.Font(self.font_point, family = wx.DEFAULT, style = wx.NORMAL, weight = wx.NORMAL, faceName = 'Consolas')))
                    #     wx.CallAfter(self.output_window.AppendText, response)
                    if False:
                        whole_text = self.output_window.GetValue()
                        m = re.search('[^\b]\b',whole_text)
                        while m:
                            self.output_window.Remove(m.start(), m.end())
                            whole_text = self.output_window.GetValue()
                            m = re.search('[^\b]\b',whole_text)
                    if t_line -c_line>max_gap:
                        pass
                    else:
                        self.output_window.SetScrollPos(wx.VERTICAL, self.output_window.GetScrollRange(wx.VERTICAL))#SetInsertionPoint(self.output_window.GetLastPosition())
                    self.__thaw_output_window()

            except Exception as e :
                time.sleep(0.001)
                error(traceback.format_exc())
                break
            try:
                if self.output_lock.locked():
                    self.output_lock.release()
            except Exception as e:
                error('{}'.format(e))
            time.sleep(0.5)


    def __init__(self, parent, name,attributes, seq_queue=None, log_path = '../log'):
        #init a session, and stdout, stderr, redirected to
        wx.Panel.__init__(self, parent)
        attributes['log_path']= log_path
        attributes['not_call_open']=True
        dut.__init__(self, name, **attributes)
        self.name = name
        self.history_cmd=[]
        self.history_cmd_index = 0
        self.parent = parent
        #self.type = attributes['type']
        self.sequence_queue= seq_queue
        self.output_lock = threading.Lock()
        #wx.stc.StyledTextCtrl #wx.richtext.RichTextCtrl
        self.output_window = wx.TextCtrl( self, -1, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_AUTO_URL|wx.VSCROLL|wx.TE_RICH|wx.TE_READONLY |wx.TE_MULTILINE&(~wx.TE_PROCESS_ENTER))#0|wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER|wx.TE_READONLY )
        self.cmd_window= wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER|wx.TE_MULTILINE|wx.VSCROLL )

        self.font_point = self.output_window.GetFont().PointSize+2
        self.error_pattern = re.compile('error|\s+err\s+|fail|wrong|errno')
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.output_window,   9, wx.EXPAND)
        sizer.Add(self.cmd_window,      0,  wx.EXPAND)
        self.SetSizer(sizer)
        #from lib.common import create_session
        info (os.curdir)
        #self.Bind(wx.EVT_CLOSE, self.on_close)
        #parent.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSED, self.on_close, parent)
        #self.cmd_window.Bind(wx.EVT_TEXT_ENTER, self.on_enter_a_command)
        #self.output_window.Bind(wx.EVT_SCROLLWIN  , self.on_scroll_changed)
        self.cmd_window.Bind(wx.EVT_KEY_UP, self.on_key_up)
        self.cmd_window.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.cmd_window.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel_cmd_window)
        self.cmd_window.Bind(wx.EVT_CHAR, self.on_press_enter)
        self.output_window.SetBackgroundColour('Black')
        self.output_window.SetDefaultStyle(wx.TextAttr(wx.GREEN,  wx.BLACK, font =wx.Font(9, family = wx.DEFAULT, style = wx.NORMAL, weight = wx.NORMAL, faceName = 'Consolas')))
        self.cmd_window.SetDefaultStyle(wx.TextAttr(font =wx.Font(19, family = wx.DEFAULT, style = wx.NORMAL, weight = wx.NORMAL, faceName = 'Consolas')))
        self.cmd_window.SetFocus()
        self.output_window.Bind(wx.EVT_TEXT_URL,self.on_leftD_click_url_in_output)
        self.Bind(wx.EVT_IDLE, self.on_idle)
        f =self.cmd_window.GetFont()
        f.PointSize= self.cmd_window_font_size
        self.cmd_window.SetFont(f)
        #self.session  = self
        self.alive =True
        th =threading.Thread(target=self.update_output)
        th.start()
        #self.sleep(0.1)
        th = threading.Thread(target=self.open, args= [self.retry_login,60])#, kwargs=attributes)
        th.start()
        self.last_json_file_saving_time=datetime.now()



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
            self.cmd_window.AppendText(new_command.encode(errors='ignore'))
        if keycode in [wx.WXK_TAB]:
            pass
        else:
            event.Skip()
    def on_enter_a_command(self, event):
        self.__thaw_output_window()
        ctrl = False
        cmd = self.cmd_window.GetRange(0, self.cmd_window.GetLastPosition())
        cmd= cmd.replace('\n', os.linesep)
        self.cmd_window.Clear()
        cmd = cmd.encode(errors= 'ignore')
        cmds = cmd.split(os.linesep)
        for cmd in cmds:
            self.add_cmd_to_history(cmd)
            self.history_cmd_index= len(self.history_cmd)
            try:
                if self.session_status:
                    add_newline =True
                    if len(cmd)>0:
                        if cmd[-1] in ['?', "\t"]:
                            add_newline =False
                            lcmd =len(cmd)-1
                            cmd  ='\b'*lcmd*4 +cmd + '\b'*lcmd*4
                    th = threading.Thread(target=self.write,args=( cmd,ctrl, add_newline))
                    th.start()
                    self.sequence_queue.put(["TC.step(DUT['{}'], '{}')".format(self.name,cmd.encode(errors= 'ignore')),  datetime.now()])#
                else:
                    th =threading.Thread(target=self.open, args=[1,60]) #self.alive= self.session#.session_status
                    th.start()
                    #self.write(cmd,ctrl=ctrl)
            except Exception as e:
                error_msg = traceback.format_exc()
                #self.on_close()
                #self.close_session()
                error ('{} closed unexpected\n{}'.format(self.name, error_msg))
            #self.alive= False
        #event.Skip()
        self.cmd_window.Clear()
        self.cmd_window.SetValue('')
        self.cmd_window.ShowPosition(100)
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
        try:
            keycode = event.KeyCode
            if keycode ==wx.WXK_TAB:
                #deliver 2017-10-21 when hitted key_tab or ?, need don't need clear cmd_window--or re-enter the command again
                    cmd_string = self.cmd_window.GetValue()
                    self.cmd_window.AppendText('\t')
                    self.on_enter_a_command(event)
                    self.cmd_window.AppendText(cmd_string)
            elif  keycode in [wx.WXK_RETURN]:
                self.cmd_window.SetInsertionPointEnd()
                event.Skip()
            elif keycode == wx.PAPER_ENV_INVITE and wx.GetKeyState(wx.WXK_SHIFT):
                cmd_string = self.cmd_window.GetValue()
                self.cmd_window.AppendText('?')
                self.on_enter_a_command(event)
                self.cmd_window.AppendText(cmd_string)
            elif keycode >= ord('a') and keycode <= ord('Z') and event.controlDown:#keycode == ord('C')  and
                data = self.cmd_window.GetStringSelection()
                if len(data)==0:
                    self.sequence_queue.put(["TC.step(DUT['{}'], '{}', ctrl=True)".format(self.name,chr(keycode).encode(errors= 'ignore')),  datetime.now()])#
                    self.write(chr(keycode), ctrl=True, add_newline = False)


            elif keycode == ord('V')  and event.controlDown:
                #self.sequence_queue.put(["TC.step(DUT['{}'], '{}', ctrl=True)".format(self.name,chr(keycode).encode(errors= 'ignore')),  datetime.now()])#
                #self.write(chr(keycode), ctrl=True)
                if not wx.TheClipboard.IsOpened():  # may crash, otherwise
                    do = wx.TextDataObject()
                    wx.TheClipboard.Open()
                    success = wx.TheClipboard.GetData(do)
                    wx.TheClipboard.Close()
                    if success:
                        cmds = do.GetText()
                        cmd = cmds.encode(errors= 'ignore')
                        if '\n' not in cmds:
                            self.cmd_window.AppendText(cmd)
                        else:
                            for cmd in cmds.split('\n'):
                                ctrl = False
                                add_newline = True
                                self.add_cmd_to_history(cmd)
                                try:
                                    if self.session_status:
                                        th = threading.Thread(target=self.write,args=( cmd,ctrl, add_newline))
                                        th.start()
                                        self.sequence_queue.put(["TC.step(DUT['{}'], '{}')".format(self.name,cmd.encode(errors= 'ignore')),  datetime.now()])#
                                        th.join()
                                    else:
                                        pass #self.alive= self.session#.session_status
                                        #self.write(cmd,ctrl=ctrl)

                                except Exception as e:
                                    error_msg = traceback.format_exc()
                                    error ('{} closed unexpected\n{}'.format(self.name, error_msg))
                                self.cmd_window.Clear()#append cmd to cmd_window
                                self.cmd_window.SetFocus()
                    else:
                        event.Skip()

            elif keycode >= ord('A')  and keycode <= ord('Z') and event.controlDown:
                info('ctrl+{}'.format(chr(keycode)))
                #done 2017-10-13 2017-10-12 if selected is not empty, ctrl+c should be copy, not send control code to session
                #done 2017-10-13 2017-10-12 if clipboard is not empty, ctrl+v should be paste not send control code to session
                self.sequence_queue.put(["TC.step(DUT['{}'], '{}', ctrl=True)".format(self.name,chr(keycode).encode(errors= 'ignore')),  datetime.now()])#
                self.write(chr(keycode), ctrl=True)
                event.Skip()
            else:
                event.Skip()
        except Exception as e:
            error(traceback.format_exc())
            event.Skip()
    def OnMouseWheel_cmd_window(self,event):
        min_font_size = 5
        interval_step = 2
        if event.ControlDown():
            pass
        else:
            return

        if event.GetWheelRotation() < 0:
                if self.cmd_window_font_size>min_font_size:
                    self.cmd_window_font_size-=interval_step
        else:
            self.cmd_window_font_size+=1

        f =self.cmd_window.GetFont()
        f.PointSize= self.cmd_window_font_size
        self.cmd_window.SetFont(f)

        self.Refresh()
    def on_leftD_click_url_in_output(self, event):
        mouseEvent = event.GetMouseEvent()
        if mouseEvent.LeftDClick():
            urlString = self.output_window.GetRange(event.GetURLStart(),event.GetURLEnd())
            webbrowser.open(urlString)
        event.Skip()

    def on_press_enter(self, event):
        if event.GetKeyCode() == 13:
            self.on_enter_a_command(event)
        else:
            event.Skip()
#todo EVT_TEXT_CUT   =  wx.PyEventBinder( wxEVT_COMMAND_TEXT_CUT )
#todo EVT_TEXT_COPY  =  wx.PyEventBinder( wxEVT_COMMAND_TEXT_COPY )
#todo EVT_TEXT_PASTE =  wx.PyEventBinder( wxEVT_COMMAND_TEXT_PASTE )

    def on_idle(self, event):
        try:
            #self.last_cmd_time_stamp
            max_idle_time = 60
            now = datetime.now()
            if (now-self.last_json_file_saving_time).total_seconds()> max_idle_time:
                self.save_dry_run_json()
                self.last_json_file_saving_time=now
        except Exception as e:
            error(e)
        event.Skip()