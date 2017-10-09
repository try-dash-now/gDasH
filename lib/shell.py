__author__ = 'Sean Yu'
'''created @2015/10/12''' 
import unittest
import os
import sys
import time
import subprocess
class shell(object):
    shell= None
    def __init__(self):
        if os.name=='nt':
            exe_cmd=['powershell.exe']#cmd.exe
            #self.shell = subprocess.Popen(args = exe_cmd )#,shell =True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            #import threading
            #self.lockStreamOut =threading.Lock()
            #self.streamOut=''
            #th =threading.Thread(target=self.ReadOutput)
            #th.start()
            #self.debuglevel=0

        else:
            exe_cmd=['bash']#cmd.exe
        self.shell = subprocess.Popen(args = exe_cmd , shell= True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)#,shell =True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)

    def read(self):
        data =self.shell.stdout.readline()
        return  data

    def write(self, cmd, ctrl=False):
        stdin = self.shell.stdin
        if ctrl:
            ascii = ord(cmd[0]) & 0x1f
            ch = chr(ascii)
            stdin.write(ch)

        else:
            stdin.write(cmd)
        return ''

        #done: 2017-10-9, 2017-10-7 a new type of dut--shell, powershell for windows and linux shell

