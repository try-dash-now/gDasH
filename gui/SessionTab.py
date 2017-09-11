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
from datetime import datetime
class SessionTab(wx.Panel, dut):
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
    log_path =None
    name = None
    open =None
    step= None
    def on_close(self):
        self.alive = False

        if self.session:
            self.session.close_session()
        #self.session.sleep(0.001)
        info('tab {} closed!!!'.format(self.name))

    def update_output(self):
        if self.session:
            if self.open :
                pass
            else:
                self.open = self.session.open
                self.step = self.session.step
                self.sleep = self.session.sleep
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
        while( status):
            try:
                status = self.alive and self.session
            except Exception as e :
                time.sleep(0.001)
                break
            time.sleep(0.05)
            self.output_lock.acquire()
            response = self.session.read_display_buffer()
            if True:
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

                if re.search('error|\s+err\s+|fail|wrong',response.lower()):
                    #self.output_window.SetDefaultStyle( wx.TextAttr(wx.RED,  wx.YELLOW, font =wx.Font(self.font_point+2, family = wx.DEFAULT, style = wx.NORMAL, weight = wx.BOLD, faceName = 'Consolas')))
                    wx.CallAfter(self.output_window.SetDefaultStyle,wx.TextAttr(wx.RED,  wx.YELLOW, font =wx.Font(self.font_point+2, family = wx.DEFAULT, style = wx.NORMAL, weight = wx.BOLD, faceName = 'Consolas')))
                else:
                    #self.output_window.SetDefaultStyle( wx.TextAttr(wx.GREEN,  wx.BLACK,font =wx.Font(self.font_point, family = wx.DEFAULT, style = wx.NORMAL, weight = wx.NORMAL, faceName = 'Consolas')))
                    wx.CallAfter(self.output_window.SetDefaultStyle,wx.TextAttr(wx.GREEN,  wx.BLACK,font =wx.Font(self.font_point, family = wx.DEFAULT, style = wx.NORMAL, weight = wx.NORMAL, faceName = 'Consolas')))
                wx.CallAfter(self.output_window.AppendText, response)
                if False:
                    whole_text = self.output_window.GetValue()
                    m = re.search('[^\b]\b',whole_text)
                    while m:
                        self.output_window.Remove(m.start(), m.end())
                        whole_text = self.output_window.GetValue()
                        m = re.search('[^\b]\b',whole_text)

                #wx.CallAfter(self.output_window.AppendText, response)#wx.CallAfter make thread safe!!!!
                last = self.output_window.GetLastPosition()
                wx.CallAfter(self.output_window.SetInsertionPoint,last)#wx.CallAfter(
                wx.CallAfter(self.output_window.ShowPosition,last+len(response)+1)#wx.CallAfter(
            try:
                self.output_lock.release()
            except Exception as e:
                error('{}'.format(e))
            time.sleep(0.5)


    def __init__(self, parent, name,attributes, seq_queue=None, log_path = None):
        #init a session, and stdout, stderr, redirected to
        wx.Panel.__init__(self, parent)
        self.name = name
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
        #from lib.common import create_session
        info (os.curdir)
        #self.Bind(wx.EVT_CLOSE, self.on_close)
        #parent.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSED, self.on_close, parent)
        self.cmd_window.Bind(wx.EVT_TEXT_ENTER, self.on_enter_a_command)
        self.cmd_window.Bind(wx.EVT_KEY_UP, self.on_key_up)
        self.cmd_window.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.output_window.SetBackgroundColour('Black')
        self.output_window.SetDefaultStyle(wx.TextAttr(wx.GREEN,  wx.BLACK, font =wx.Font(9, family = wx.DEFAULT, style = wx.NORMAL, weight = wx.BOLD, faceName = 'Consolas')))
        self.cmd_window.SetFocus()
        def create_dut( name, **kwargs):

            self.session  = dut(name, **attributes)
            self.alive =True
            th =threading.Thread(target=self.update_output)
            th.start()
        attributes['log_path']= log_path
        th = threading.Thread(target=create_dut, args= [name], kwargs=attributes)
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


                self.sequence_queue.put(['TC.step({}, "{}")'.format(self.name,cmd),  datetime.now()])#
            else:
                self.alive= self.session#.session_status
                #self.session.write(cmd,ctrl=ctrl)
        except Exception as e:
            self.on_close()
            self.session.close_session()
            error ('{} closed unexpected'.format(self.name))
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
        elif keycode == wx.PAPER_ENV_INVITE and wx.GetKeyState(wx.WXK_SHIFT):
            self.cmd_window.AppendText('?')
            self.on_enter_a_command(event)
        else:
            event.Skip()