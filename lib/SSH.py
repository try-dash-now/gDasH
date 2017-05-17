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
import os, sys,time , traceback
import threading
import paramiko as ssh
from dut import dut
class SSH(object):
    chan=None
    client=None

    def __init__(self, name, host='localhost', user='sean', password='0421'):
        try:


            self.lockStreamOut =threading.Lock()
            self.streamOut=''
            th =threading.Thread(target=self.ReadOutput)
            th.start()
            self.debuglevel=0

            self.login()
        except Exception as e:
            self.closeSession()
            raise e

    def ReadOutput(self):
        maxInterval = 60
        if self.timestampCmd ==None:
            self.timestampCmd= time.time()
        fail_counter = 0
        while self.SessionAlive:
            self.lockStreamOut.acquire()
            try:
                #self.info('time in ReadOutput',time.time(), 'timestampCmd', self.timestampCmd, 'max interval', maxInterval, 'delta',  time.time()-self.timestampCmd)
                if (time.time()-self.timestampCmd)>maxInterval:
                    self.write('\r\n')
                    self.timestampCmd = time.time()
                    self.info('anti-idle', fail_counter)
                if self.client and self.chan:
                    out = self.chan.recv(64)
                    if len(out):
                        self.streamOut+=out
                    if self.logfile and len(out)!=0:
                        self.logfile.write(out)
                        self.logfile.flush()
                fail_counter = 0
            except KeyboardInterrupt:
                break
            except Exception as e:
                fail_counter+=1
                if self.debuglevel:
                    print('\nReadOutput Exception %d:'%(fail_counter)+e.__str__()+'\n')
                #self.lockStreamOut.release()
                if self.autoReloginFlag and self.max_output_time_out< fail_counter:
                    import threading
                    fail_counter = 0
                    th =threading.Thread(target=self.relogin)
                    th.start()
                print("ReadOutput Exception: %s"%(str(e)))

                msg = traceback.format_exc()
                print(msg)
                self.error(msg)
            self.lockStreamOut.release()
            time.sleep(0.001)
        self.closeSession()

    def login(self):
        #self.loginDone=False
        if self.is_simulation():
            self.loginDone=True
            return
        if self.client:
                self.client.close()
                self.chan=None
                self.client=None
        self.client = ssh.SSHClient()
        ssh.util.log_to_file(self.logfile.name+'.ssh')
        self.client.set_missing_host_key_policy(ssh.WarningPolicy())
        self.client.load_system_host_keys()
        self.client.connect(self.attribute['HOST'], self.attribute['PORT'], self.attribute['USER'], self.attribute['PASSWORD'])
        self.chan = self.client.invoke_shell()
        self.loginDone=True
    def relogin(self):
        self.lockRelogin.acquire()
        try:
            if self.counterRelogin>0:
                self.lockRelogin.release()
                return
            self.counterRelogin+=1
            self.loginDone=False
            self.login()
            self.counterRelogin-=1
            self.loginDone=True
        except Exception as e:
            self.counterRelogin-=1
            self.lockRelogin.release()
            raise  e
        self.lockRelogin.release()

    def write(self, data):
        self.timestampCmd= time.time()        #super(SSH, self).write(data)
        if self.chan :
            if self.dry_run:
                self.chan.send('')
            else:
                self.chan.send(data)
