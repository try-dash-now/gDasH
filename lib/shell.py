__author__ = 'Sean Yu'
'''created @2015/10/12''' 
import unittest
import os
import sys
import time
import subprocess, signal
if os.name =='nt':
    pass#import win32api
def handler_ctrl_c(sig, func=None):
    return True
def signal_handler(signal, frame):
  time.sleep(1)
  print 'Ctrl+C received in wrapper.py'

#signal.signal(signal.SIGINT, signal_handler)
class shell(object):
    shell= None
    max_buffer =512
    def close_session(self):
        if self.shell:
            self.shell.kill()
            self.shell=None
            #os.killpg(self.shell.pid, signal.SIGTERM)
            #self.shell.send_signal(signal.SIGTERM)
            #self.shell=None
    def __init__(self):
        if os.name=='nt':
            exe_cmd=['powershell']#, '-noprofile', '-command', 'set-location /; $pwd']#['powershell.exe']##['cmd.exe']#cmd.exe
        else:
            exe_cmd=['bash']#cmd.exe
        CREATE_NEW_PROCESS_GROUP=512
        import win32con

        os.environ['FOR_DISABLE_CONSOLE_CTRL_HANDLER'] = '1'

        if os.name == 'nt':
            #win32api.SetConsoleCtrlHandler(handler_ctrl_c, 1)
            creationflags= win32con.CREATE_NEW_PROCESS_GROUP#.CREATE_NEW_PROCESS_GROUP#win32con.CREATE_NEW_CONSOLE#|win32con.CREATE_NEW_PROCESS_GROUP
        else:
            creationflags =512
        self.shell = subprocess.Popen(args = exe_cmd ,
                                      universal_newlines=True,
                                      shell= True,
                                      stdout=subprocess.PIPE,
                                      stdin=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      creationflags=creationflags,#CREATE_NEW_PROCESS_GROUP
                                      )#,shell =True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)

    def read(self):
        #self.shell.stdout.write('\n')
        data =self.shell.stdout.readline()#read(1024)#.readline()
        if data in ['', '\n']:
            data=''
        return  data

    def write(self, cmd, ctrl=False):
        stdin = self.shell.stdin
        if ctrl:
            if cmd[0] in ['c', 'C']:
                import signal
                s=None
                if os.name =='nt':
                    pgroupid = self.shell.pid
                    for s in [ signal.CTRL_C_EVENT, signal.CTRL_BREAK_EVENT, signal.SIGINT]:
                        s = signal.CTRL_BREAK_EVENT#CTRL_C_EVENT
                        self.shell.send_signal(s)
                        os.kill(self.shell.pid, s)
                    #todo 2017-10-10 can't stop "ping localhost -t" with ctrl+c, it's disabled by windows for non-console process
            else:
                ascii = ord(cmd[0]) & 0x1f
                ch = chr(ascii)
                stdin.write(ch)
        else:
            pad_len= (self.max_buffer-1-len(cmd))/2
            pad = ' '*pad_len+'\b'*pad_len+'\n'
            stdin.write(cmd+pad)
        return ''

        #done: 2017-10-9, 2017-10-7 a new type of dut--shell, powershell for windows and linux shell
        #todo 2017-10-10 missed win32con in distribute package


