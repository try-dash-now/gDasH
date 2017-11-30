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

    def close_session(self):
        if self.shell:
            pass#self.shell.kill()
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
        data =self.shell.stdout.read(1024*4)#.readline()
        #data +='\r\n'+self.shell.stderr.readline()
        #print('read', data)
        return  data

    def write(self, cmd, ctrl=False):
        stdin = self.shell.stdin
        if ctrl:
            if cmd[0] in ['c', 'C']:
                import signal
                s=None
                if os.name =='nt':
                    #import win32gui,win32con
                    #win32con
#                    tid =win32gui.FindWindowEx('shell')
 #                   win32gui.PostMessage(tid, win32con.CTRL_BREAK_EVENT)
                    #import win32api
                    #os.getpgid()
                    pgroupid = self.shell.pid

                        ##os.getpgid(self.shell.pid)

                    #if True:
                        #win32api.GenerateConsoleCtrlEvent(signal.CTRL_C_EVENT, pgroupid)
                        #win32api.GenerateConsoleCtrlEvent(signal.CTRL_BREAK_EVENT, pgroupid)
                        #C= ord('C')
                        # win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_EXTENDEDKEY, 0);
                        # win32api.keybd_event(C, 0, win32con.KEYEVENTF_EXTENDEDKEY, 0);
                        # win32api.keybd_event(win32con.VK_PAUSE, 0, win32con.KEYEVENTF_EXTENDEDKEY, 0);
                        # win32api.keybd_event(win32con.VK_PAUSE, 0, win32con.KEYEVENTF_KEYUP, 0);
                        # win32api.keybd_event(C, 0, win32con.KEYEVENTF_KEYUP, 0);
                        # win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0);
                        #import ctypes
                        #ctypes.windll.user32.keybd_event(0x11, 0, 0, 0)#
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
            stdin.write(cmd+'\r\n')
        return ''

        #done: 2017-10-9, 2017-10-7 a new type of dut--shell, powershell for windows and linux shell
        #todo 2017-10-10 missed win32con in distribute package


