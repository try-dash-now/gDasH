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
#done: dut.add_data_to_search_buffer --function_step completion, add stream_buffer, search_index, to support search in buffer check
#todo: function_step defines the output format:
#done: 2017-09-02, build_DasH_exe.py to do that option for this script is '--verbose py2exe -d ../dist'.  build executable(exe) file for windows user, allow to distribute it without python installation
#fixed: if dut is not reachable, it will hang the gDasH gui
from pprint import pprint
from traceback import format_exc
import time,datetime, re, math, datetime
import threading
from common import dut_exception_handler, info, debug, error,warn, TRACE_LEVEL,TRACE_LEVEL_NAME
import os
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
    display_buffer =None

    display_buffer_locker =None
    session_status = None
    login_done =False
    write_locker = None
    read_locker = None
    log_path = None
    log_file =None
    last_cmd_time_stamp= None
    new_line_during_login =None
    init_file_name =None
    type =None
    first_login = True
    retry_login= 10
    retry_login_interval = 60
    def __del__(self):
        if self.session:
            self.close_session()

    def __init__(self, name='session' ,type='telnet', host='127.0.0.1', port=23, user_name=None, password=None,login_step=None, log_path = '../log', new_line= os.linesep, new_line_during_login='\n', init_file_name=None, retry_login= 10, retry_login_interval=60):
        #expected types are [echo, telnet, ssh, shell, web_brower]
        self.type = type
        if login_step in [None, '']:
            login_step = None
        if isinstance(login_step, (basestring)) and os.path.exists(login_step):
            pass
        else:
            login_step =None
        self.retry_login = retry_login
        self.retry_login_interval = retry_login_interval
        self.login_steps = login_step
        self.session_type = type
        self.name = name
        self.host= host
        self.port = port
        self.user = user_name
        self.password = password
        self.log_path = log_path
        self.new_line = new_line
        self.session_status = True
        self.search_buffer = ''
        self.display_buffer = ''
        self.new_line_during_login = new_line_during_login
        self.init_file_name = init_file_name
        th = threading.Thread(target=self.open, kwargs={'retry': self.retry_login, 'interval': 60})
        th.start()
        #self.open(retry= self.retry_login, interval=60)
    def open(self, retry =10, interval= 60):
        if self.session:
            #self.session_status=False
            del self.session
            self.session=None
            if self.read_locker.locked():
                self.read_locker.release()
            if self.write_locker.locked():
                self.write_locker.release()
            self.sleep(0.1)

        self.session_status = True
        try:
            log_path = self.log_path
            if log_path:
                self.log_path = os.path.abspath(log_path)
            else:
                self.log_path = os.path.abspath('../log')
            self.open_log_file()

            self.write_locker=  threading.Lock()
            self.read_locker=  threading.Lock()
            self.display_buffer_locker = threading.Lock()
            th =threading.Thread(target=self.read_data)

            new_line_during_login = self.new_line_during_login
            self.new_line_during_login = new_line_during_login
            init_file_name = self.init_file_name
            login_step = self.login_steps
            self.login_done=False
            name = self.name
            type = self.type
            counter = 0
            while counter<retry:
                counter+=1
                try:
                    if type == 'echo' or init_file_name !=None:
                        from lib.echo import echo
                        self.session = echo(name, init_file_name)
                    elif type.lower() =='ssh':
                        from lib.SSH import SSH
                        self.session = SSH(host = self.host, port =self.port, user = self.user, password = self.password)
                    elif type.lower() in ['telnet']:
                        from lib.TELNET import  TELNET
                        self.session = TELNET(host = self.host, port =self.port, login_step=login_step)
                    if isinstance(login_step,(list, tuple)):
                        pass
                    elif login_step is None :#login_step.strip().lower() in ['none',None, "''", '""']:
                        self.login_steps =[]
                    elif  isinstance(login_step, basestring):
                        if login_step.strip().lower() in ['none',None, "''", '""']:
                            self.login_steps=[]
                    th.start()
                    self.sleep(0.5)
                    self.login(login_step)
                    #to make sure the connection is stable, not broken
                    if not self.first_login:
                        self.sleep(interval/2)
                        self.step('','.+')
                        self.first_login = False

                    break
                except Exception as e :
                    if counter< retry:
                        info('failed to login {}'.format(self.name), retry= retry, counter = counter, interval = interval)
                        self.sleep(interval)
                    else:
                        raise e

        except Exception as e:
            import traceback
            error_msg =traceback.format_exc(e)
            error('failed to open {}'.format(self.name), e, error_msg)
            self.session_status =False


    def step(self,command, expect='.*', time_out=30, total_try =3, ctrl=False, not_want_to_find=False,no_wait = False, flags = re.I|re.M):
        error_info = None
        init_total_try = total_try
        total_try= int(total_try)
        success ,match, buffer = False, None, ''
        error_message="""
    {dut_name}.step:
    command =>{cmd},
    expect  =>{exp},
    time_out         : {time_out},
    total_try        : {total_try},
    ctrl             : {ctrl},
    not_want_to_find : {not_want},
    no_wait          : {no_wait},
    flags            :{flags}
buffer:
{buffer}
    """.format(
                        dut_name = self.name,
                        cmd = command,
                        exp = expect,
                        time_out = time_out,
                        total_try = init_total_try,
                        ctrl = ctrl,
                        not_want = not_want_to_find,
                        no_wait = no_wait,
                        flags = flags,
                        buffer = buffer
                    )
        while total_try:
            total_try -= 1
            try:
                resp = self.write(command, ctrl)
                time.sleep(0.001)
                #self.add_data_to_search_buffer(resp)
                if no_wait:
                    pass
                else:
                    self.reset_search_buffer()
                success, match, buffer = self.wait_for(expect, time_out,flags,not_want_to_find)
                if len(buffer)>256:
                    brief_buffer =buffer[:128]+'\n...\n'+buffer[-128:]
                else:
                    brief_buffer = buffer
                display_str = info(cmd = command, success = success, expect=expect, not_want_to_find = not_want_to_find, buffer = brief_buffer, total_try=total_try)
                if success:
                    break
                elif total_try>0:
                    if not_want_to_find:
                        continue
                    else:
                        success=False
                        #raise Exception(error_message)
                else:
                    if not_want_to_find:
                        success=True
                        break
                if not success:
                    raise Exception('failed in dut.step: {}'.format(display_str))
            except Exception as e:
                if total_try ==0:#no more chance to try again, the last chance
                    import traceback
                    error_msg = "{}\n{}".format(traceback.format_exc(),error_message)
                    error(error_msg)
                    e.message=e.message+'\n'+error_message
                    #error(pprint( e.message))


                    raise Exception(traceback.format_exc())
        return  success, match, buffer
    def match_in_buffer(self, pattern):
        buffer = self.search_buffer
        match = re.search(pattern,buffer)
        return match, buffer
    def sleep(self, sleep_time):
        #done: change condition of sleep, calculate end-time, compare current time to end-time
        #info('{} sleeping {}:'.format(self.name, sleep_time))
        if self.session_type == 'echo':
            time.sleep(0.001)
        elif sleep_time>1.0:
            start_time = datetime.datetime.now()
            now = datetime.datetime.now()
            delta_seconds = (now -start_time).total_seconds()
            counter = 0
            while delta_seconds <= sleep_time and self.session_status:
                delta_seconds = (datetime.datetime.now()-start_time).total_seconds()
                counter+=1
                if counter%10==0:
                    info('{} sleep {:02.1f}% {:.1f}/{} '.format(self.name , 100*delta_seconds/sleep_time,delta_seconds,sleep_time))
                time.sleep(1)
        else:
            time.sleep(sleep_time)

    def wait_for(self, pattern='.*', time_out=30, flags=re.I|re.M, not_want_to_find=False):
        poll_interval = 0.5# default polling interval, 0.5 second
        if self.session_type == 'echo':
            time_out = 0.01
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
        if success:
            if not_want_to_find:
                success = False
        else:
            if not_want_to_find:
                success = True
        return success,match,buffer

    @dut_exception_handler
    def login(self, login_step_file=None, retry=1):
        login_steps =[]
        if type(self.login_steps)==type([]):
            login_steps = self.login_steps #login_steps = self.login_steps
        elif login_step_file !=None :
            time.sleep(0.001)
            import csv
            with open(login_step_file, 'rb') as csvfile:
                self.login_steps = csv.reader(csvfile, delimiter=',', quotechar='|')
                for row in self.login_steps:
                    login_steps.append(row)
        for row in login_steps:
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

        self.login_steps= []
        for row in login_steps:
            self.login_steps.append(row)
        #self.login_steps=login_steps
        self.login_done =True

    def close_session(self):
        self.write_locker.acquire()
        if self.session_status: #try to avoid to call this function twice
            info('session {}:close_session called Closing!!!'.format(self.name))

            #fix issue
            # Traceback (most recent call last):
            # File "C:\Python27\Lib\threading.py", line 801, in __bootstrap_inner
            # self.run()
            # File "C:\Python27\Lib\threading.py", line 754, in run
            # self.__target(*self.__args, **self.__kwargs)
            # File "C:/workspace/gDasH\gui\DasHFrame.py", line 57, in update_output
            # while( self.alive ):#and self.session.session_status
            # File "C:\Python27\lib\site-packages\wx-3.0-msw\wx\_core.py", line 16711, in __getattr__
            # raise PyDeadObjectError(self.attrStr % self._name)
            # PyDeadObjectError: The C++ part of the SessionTab object has been deleted, attribute access no longer allowed.
            try:
                if self.session_type in ['ssh']:
                    #self.write('exit')
                    self.session.write('exit\r\n')
                if self.session_type in 'telnet':
                    #self.session.write('exit')
                    self.session.write('exit\r\n')
                    #self.write('exit')
            except Exception as e:
                error(e)
                self.session=None
                self.session_status = False
                self.read_locker.release()
            try:
                if self.log_file:
                    self.log_file.close()
                    self.log_file=None
            except:
                pass
            self.session_status=False

        self.write_locker.release()
        time.sleep(0.001)

    def add_data_to_search_buffer(self, data):

        #self.search_buffer_locker.acquire()
        #self.display_buffer_locker.acquire()
        #self.read_locker.acquire()
        #data = self.read()
        if len(data):
            self.search_buffer+='{}'.format(data)
            self.display_buffer+='{}'.format(data)
        #self.read_locker.release()
        #self.search_buffer_locker.release()
        #self.display_buffer_locker.release()

    def reset_search_buffer(self):
        #if not self.read_locker.locked():
        #    self.read_locker.acquire()
        self.search_buffer=''
        debug('{}:reset search buffer'.format(self.name))
        #if self.read_locker.locked():
           # self.read_locker.acquire()

        #   self.read_locker.release()
    def read_display_buffer(self, clear=True):
        self.display_buffer_locker.acquire()
        response = self.display_buffer
        if clear :
            self.display_buffer=''
        debug('{}:reset display buffer'.format(self.name))
        self.display_buffer_locker.release()
        return response
    def read_data(self):
        max_idle_time = 60
        last_update_time = datetime.datetime.now()
        self.last_cmd_time_stamp = last_update_time

        while self.session_status and self.session:
            try:
                current_time = datetime.datetime.now()
                if TRACE_LEVEL:
                    pass
                last_update_time = self.last_cmd_time_stamp        #self.log('session {name} alive'.format(name =self.name))
                if (current_time-last_update_time).total_seconds()> max_idle_time:
                    last_update_time = current_time
                    self.last_cmd_time_stamp = current_time
                    self.write("\r\n")
                data = self.read()
                time.sleep(0.1)
            except  Exception as e:
                if str(e) in ['error: Socket is closed']:
                    self.session_status =False
        if self.session_type in ['ssh']:
            if self.session:
                try:
                    if self.session.client:
                        self.session.client.close()
                        self.session.client=None
                except Exception as e:
                    error(e)
            self.session=None
        info('session {}: Closed!!!'.format(self.name))
    def write(self, cmd='', ctrl=False):
        resp = ''
        if self.session_status:
            new_line =self.new_line
            if not self.login_done:
                new_line = self.new_line_during_login
            self.write_locker.acquire()
            if ctrl:
                ascii = ord(cmd[0]) & 0x1f
                cmd = chr(ascii)
                resp = self.session.write(cmd, ctrl=ctrl)
                resp +=self.session.write(new_line)
            else:
                try:
                    resp = self.session.write('{cmd}{new_line}'.format(cmd=cmd, new_line= new_line), ctrl=ctrl)
                except Exception as e :
                    self.session_status =False
            #self.add_data_to_search_buffer('{cmd}{new_line}'.format(cmd=cmd, new_line=new_line))
            self.last_cmd_time_stamp = datetime.datetime.now()
            self.write_locker.release()
        return  resp
    def read(self):
        resp =''
        if self.session_status and self.session:
            self.read_locker.acquire()
            debug('read::read_locker acquired')
            try:
                debug('read::session reading')
                resp =self.session.read()
                debug('read::session read complete')
                self.add_data_to_search_buffer(resp)
                debug('read::added to search_buffer')
                try:
                    if self.log_file:
                        self.log_file.write(resp)
                        self.log_file.flush()
                except Exception as e:
                    error('dut {}:{}'.format(self.name, e))
                    self.log_file.flush()
                    self.log_file.close()
                    self.log_file=None
            except Exception as e:
                error('session {}'.format(self.name))
                error(pprint(format_exc()))
            if self.read_locker.locked():
                self.read_locker.release()
            debug('read::read_locker released')
            if len(resp.strip()):
                debug('-'*20+'read start'+'-'*20+'\n')
                debug('{}'.format(resp)+os.linesep)
                debug(''+'-'*20+'read   end'+'-'*20+'\n')
        return  resp

        #print('{}:{}.{}:{}'.format(log_type_name[log_type_index],self.name, caller, string))
    def open_log_file(self):
        if not os.path.exists(self.log_path):
            try:
                os.mkdir(self.log_path)
            except Exception as e:
                error('dut{}:{}'.format(self.name, e))

        file_name = '{}/{}-{}.log'.format(self.log_path,self.name, datetime.datetime.now().isoformat('-').split('.')[0].replace(':','-'))[0:256]
        self.log_file = open(file_name, r"w+")
    def save_data_to_csv(self, data, file_name_prefix= ''):
        data_file_name = '{}/{}_{}_{}.csv'.format(self.log_path, file_name_prefix, self.name, datetime.datetime.now().isoformat('-').split('.')[0].replace(':','-'))[:256]
        with open(data_file_name, 'a+') as data_file:
            for record in data:
                data_file.write(','.join(['{}'.format(x) for x in record]))
                data_file.write('\n')
                data_file.flush()
