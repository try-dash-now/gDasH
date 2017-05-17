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
__author__ = 'Yu, Xiongwei(Sean Yu)'

__doc__ = '''
created 5/9/2017
class session is to create a SSH/telnet/shell/PowerShell/web_browser
an abstract layer of device
provide functions
    setup the connection, handle the login operation
    enter a command and wait for a respone
    when interacting with real device, record the steps to a json file
'''
#todo: function_step completion, add stream_buffer, search_index, to support search in buffer
#todo: function_step defines the output format:
from pprint import pprint
from traceback import format_exc
import time,datetime, re, math, datetime
import threading
from common import dut_exception_handler
import common
class dut(object):
    name=None
    session_type= None
    host=None
    port=23
    log_path=None
    new_line=None
    new_line_during_login =None
    login_steps= None
    session =None
    command_respone_json = None # a dict to record the interaction procedure
    search_buffer =None
    buffer_locker =None
    session_status = None
    login_done =False
    write_locker = None

    def __del__(self):
        if self.session:
            self.close_session()

    def __init__(self, name='session' ,type='telnet', host='127.0.0.1', port=23, login_step=None, log_path = '../log', new_line= '\n', new_line_during_login='\n'):
        #expected types are [echo, telnet, ssh, shell, web_brower]
        self.login_steps = login_step
        self.session_type = type
        self.name = name
        self.host= host
        self.port = port
        self.log_path = log_path
        self.new_line = new_line
        self.session_status = True
        self.search_buffer = ''
        self.buffer_locker=  threading.Lock()
        self.write_locker=  threading.Lock()
        th =threading.Thread(target=self.read_data)
        th.start()
        self.new_line_during_login = new_line_during_login
        if type == 'echo':
            from lib.echo import echo
            self.session = echo(host)
        if login_step==None:
            self.login_steps =[]
        else:
            self.login(login_step)


    def step(self,command, expect='.*', time_out=30, total_try =1, ctrl=False, not_want_to_find=False,no_wait = False, flags = re.I|re.M):
        error_info = None
        total_try= int(total_try)
        match, buffer = None, ''
        while total_try:
            total_try -= 1
            try:
                resp = self.write(command)
                self.add_data_to_search_buffer(resp)
                if not no_wait:
                    pass
                else:
                    self.reset_search_buffer()
                success, match, buffer = self.wait_for(expect, time_out,flags,not_want_to_find)

            except Exception as e:
                if total_try ==0:#no more chance to try again, the last chance
                    pprint(format_exc())
                    e.message='{dut_name}.step: command={cmd}, time_out={time_out}, total_try={total_try},ctrl={ctrl}, not_want_to_find={not_want}, no_wait={no_wait},flags={flags}\n{msg}'.format(
                        dut_name = self.name,
                        cmd = command,
                        time_out = time_out,
                        total_try = total_try,
                        ctrl = ctrl,
                        not_want = not_want_to_find,
                        no_wait = no_wait,
                        flags = flags,
                        msg= e.message
                    )
                    pprint( e.message)
                    raise

    def match_in_buffer(self, pattern):
        buffer = self.search_buffer
        match = re.search(pattern,buffer)
        return match, buffer
    def sleep(self, sleep_time):
        if self.session_type == 'echo':
            pass
        else:
            time.sleep(sleep_time)

    def wait_for(self, pattern='.*', time_out=30, flags=re.I|re.M, not_want_to_find=False):
        poll_interval = 0.5# default polling interval, 0.5 second
        if self.session_type == 'echo':
            time_out = 0.
        time_out=float(time_out)
        start_time = datetime.datetime.now()
        end_time = start_time + datetime.timedelta(seconds=math.ceil(time_out))
        pat =re.compile(pattern=pattern,flags=flags)
        match = None
        buffer = ''
        success= False
        while True:
            match, buffer = self.match_in_buffer(pat)
            if match:
                if not_want_to_find:
                    success = False
                else:
                    success = True
                break #quit the while
            else: #not find the pattern
                now = datetime.datetime.now()
                remain_time = end_time - now
                remain_seconds = remain_time.total_seconds()
                remain_seconds = remain_seconds if remain_seconds> 0 else 0
                self.sleep(min(remain_seconds, poll_interval))

            now = datetime.datetime.now()
            if end_time > now:
                continue
            else:
                break
        return success,match,buffer
    @dut_exception_handler
    def login(self, login_step_file=None, retry=1):
        import csv
        if login_step_file !=None:
            time.sleep(0.001)
            with open(login_step_file, 'rb') as csvfile:
                self.login_steps = csv.reader(csvfile, delimiter=',', quotechar='|')
                for row in self.login_steps:
                    cmd,expect, time_out, total_try ='', '.*',30,1
                    if len(row)==1:
                        cmd= row[0]
                    elif len(row)==2:
                        cmd, expect= row
                    elif len(row)==3:
                        cmd,expect,time_out= row
                    elif len(row) >3:
                        cmd,expect, time_out, total_try =row[:4]
                    self.step(cmd,expect, time_out,total_try)
        self.login_done =True

    def close_session(self):
        self.session_status=False
        time.sleep(0.001)
    def add_data_to_search_buffer(self,data):
        if len(data):
            self.buffer_locker.acquire()
            self.search_buffer+='{}'.format(data)
            self.buffer_locker.release()
    def reset_search_buffer(self):
        self.buffer_locker.acquire()
        self.search_buffer=''
        self.buffer_locker.release()
    def read_data(self):
        max_idle_time = 60
        last_update_time = datetime.datetime.now()
        while self.session_status:
            current_time = datetime.datetime.now()
            if common.debug:
                print('session {name} alive'.format(name =self.name))
            if (current_time-last_update_time).total_seconds()> max_idle_time:
                last_update_time = current_time
                self.write()

            self.add_data_to_search_buffer(self.read())

            time.sleep(0.001)
    def write(self, cmd=''):
        resp = ''
        if self.session:
            new_line =self.new_line
            if not self.login_done:
                new_line = self.new_line_during_login
            self.write_locker.acquire()
            resp = self.session.write('{cmd}{new_line}'.format(cmd=cmd, new_line=new_line))
            self.write_locker.release()
        return  resp
    def read(self):
        resp =''
        if self.session:
            resp =self.session.read()
        return  resp