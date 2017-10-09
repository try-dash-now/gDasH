__author__ = 'Sean Yu'
'''created @2015/10/12''' 
import unittest
import os
import sys
import time
import subprocess, signal
if os.name =='nt':
    import win32api
def handler_ctrl_c(sig, func=None):
    return True
def signal_handler(signal, frame):
  time.sleep(1)
  print 'Ctrl+C received in wrapper.py'

signal.signal(signal.SIGINT, signal_handler)
class shell(object):
    shell= None
    def __init__(self):
        if os.name=='nt':
            exe_cmd=['powershell.exe']##['cmd.exe']#cmd.exe
        else:
            exe_cmd=['bash']#cmd.exe
        CREATE_NEW_PROCESS_GROUP=512
        import win32con

        os.environ['FOR_DISABLE_CONSOLE_CTRL_HANDLER'] = '1'

        if os.name == 'nt':
            win32api.SetConsoleCtrlHandler(handler_ctrl_c, 1)
            creationflags= win32con.CREATE_NEW_PROCESS_GROUP#win32con.CREATE_NEW_CONSOLE#|win32con.CREATE_NEW_PROCESS_GROUP
        else:
            creationflags =0
        self.shell = subprocess.Popen(args = exe_cmd ,
                                      universal_newlines=True,
                                      shell= True,
                                      stdout=subprocess.PIPE,
                                      stdin=subprocess.PIPE,
                                      creationflags=creationflags,#CREATE_NEW_PROCESS_GROUP
                                      )#,shell =True, stdout=subprocess.PIPE, stdin=subprocess.PIPE)

    def read(self):
        data =self.shell.stdout.readline()
        return  data

    def write(self, cmd, ctrl=False):
        stdin = self.shell.stdin
        if ctrl:
            if cmd[0] in ['c', 'C']:
                import signal
                s=None
                if os.name =='nt':
                    #os.kill(self.shell.pid, signal.CTRL_BREAK_EVENT)
                    #
# SIGABRT = 22
# SIGBREAK = 21
# SIGFPE = 8
# SIGILL = 4
# SIGINT = 2
# SIGSEGV = 11
# SIGTERM = 15
#
# SIG_DFL = 0
# SIG_IGN = 1
                    import win32gui,win32con
                    #win32con
#                    tid =win32gui.FindWindowEx('shell')
 #                   win32gui.PostMessage(tid, win32con.CTRL_BREAK_EVENT)
                    import win32api
                    #os.getpgid()
                    pgroupid = self.shell.pid

                        #os.getpgid(self.shell.pid)
                    win32api.GenerateConsoleCtrlEvent(signal.CTRL_C_EVENT, pgroupid)
                    win32api.GenerateConsoleCtrlEvent(signal.CTRL_BREAK_EVENT, pgroupid)
                    #os.kill(pgroupid, signal.CTRL_C_EVENT)
                    s = signal.CTRL_BREAK_EVENT#CTRL_C_EVENT
                    self.shell.send_signal(s)
                    os.kill(self.shell.pid, s)
                    s = signal.CTRL_C_EVENT
                    self.shell.send_signal(s)
                    os.kill(self.shell.pid, s)


            else:
                ascii = ord(cmd[0]) & 0x1f
                ch = chr(ascii)
                stdin.write(ch)


        else:
            stdin.write(cmd)
        return ''

        #done: 2017-10-9, 2017-10-7 a new type of dut--shell, powershell for windows and linux shell

