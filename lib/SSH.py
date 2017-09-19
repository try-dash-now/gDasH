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
created 5/17/2017
'''

#fixed:2017-08-25 2017-08-25 can't find paramiko in executable version
#solved by copy unzip packages to distribute folder
# No module named paramiko,Traceback (most recent call last):
# 	  File "lib\dut.pyo", line 126, in open
# 	  File "lib\SSH.pyo", line 29, in <module>
# 	ImportError: No module named paramiko
#

import os, sys,time , traceback
import threading
#import ssh
import paramiko as ssh
#from dut import dut
class SSH(object):
    chan=None
    client=None

    def __init__(self, host='localhost', port=22,user='sean', password='0421'):
        if self.client:
                self.client.close()
                self.chan=None
                self.client=None
        self.client = ssh.SSHClient()
        #ssh.util.log_to_file(self.logfile.name+'.ssh')
        self.client.set_missing_host_key_policy(ssh.WarningPolicy())
        self.client.load_system_host_keys()
        self.client.connect(host, int(port), user, password)
        self.chan = self.client.invoke_shell()
    def read(self):
        resp = self.chan.recv(64)
        if resp ==None:
            resp =''
        return resp
    def write(self, data,ctrl=False):
        self.chan.send('{}'.format(data))
        #self.chan.send(os.linesep)
        return  ''
