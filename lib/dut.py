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
class dut(object):
    name=None
    session_type= None
    host=None
    port=23
    log_path=None
    new_line=None
    new_line_during_login =None
    alive_counter =0 # if it keeps change, the session should be alive, otherwise, end itself

    login_steps= None
    session =None
    command_respone_json = None # a dict to record the interaction procedure

    stream_in=None
    search_index = None
    def __init__(self, name='session' ,type='telnet', host='127.0.0.1', port=23, login_step=None, log_path = '../log', new_line= '\n', new_line_during_login='\n'):
        #expected types are [echo, telnet, ssh, shell, web_brower]
        self.login_steps = login_step
        self.session_type = type
        self.name = name
        self.host= host
        self.port = port
        self.log_path = log_path
        self.new_line = new_line

        self.search_index = 0
        self.stream_in = ''

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
                if no_wait:
                    self.wait_for(expect, time_out,flags,not_want_to_find)
                resp = self.session.cmd(command)

            except Exception as e:
                if total_try ==0:#no more chance to try again, the last chance
                    pprint(format_exc())
                    raise(e)

    def match_in_buffer(self, pattern, flags=re.I|re.M):
        buffer = self.stream_in[self.search_index:]
        match = re.search(pattern,buffer,flags=flags)
        return match, buffer

    def wait_for(self, pattern='.*', time_out=30, flags=re.I|re.M, not_want_to_find=False):
        poll_interval = 0.5# default polling interval, 0.5 second
        start_time = datetime.datetime.now()
        end_time = start_time + datetime.timedelta(seconds=int(time_out), microseconds=1000*(time_out-int(time_out)))
        pat =re.compile(pattern=pattern,flags=flags)
        match = None
        buffer = ''
        success= False
        while(end_time> datetime.datetime.now()):

            match, buffer = self.match_in_buffer(pat,flags)
            if match:
                if not_want_to_find:
                    success = False
                else:
                    success = True
                break #quit the while
            else: #not find the pattern
                now = datetime.datetime.now()
                remain_time = end_time - now
                time.sleep(min(remain_time.total_seconds(), poll_interval))
        return success,match,buffer

    def login(self, login_step_file=None, retry=1):
        import csv
        if login_step_file !=None:
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


