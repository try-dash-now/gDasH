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


    def __init__(self, name='session' ,type='telnet', host='127.0.0.1', port=23, login_step=None, log_path = '../log', new_line= '\n', new_line_during_login='\n'):
        #expected types are [echo, telnet, ssh, shell, web_brower]
        self.login_steps = login_step
        self.session_type = type
        self.name = name
        self.host= host
        self.port = port
        self.log_path = log_path
        self.new_line = new_line

        self.new_line_during_login = new_line_during_login
        if type == 'echo':
            from lib.echo import echo
            self.session = echo(host)
        if login_step==None:
            self.login_steps =[]
        else:
            self.login(login_step)

    def step(self,command, expect='.*', time_out=30, total_try =1, ctrl=False, no=False,no_wait = False):
        error_info = None
        total_try= int(total_try)
        while total_try:
            total_try -= 1
            try:
                resp = self.session.cmd(command)
            except Exception as e:
                if total_try ==0:#no more chance to try again, the last chance
                    pprint(format_exc())
                    raise(e)


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


