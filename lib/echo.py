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
it's simulator of an equipment, it is simple to get input 'command', match to an output, and response the matched output to the caller
'''
import  time, datetime
import threading
import common
class echo (object):
    io_map = None
    search_buffer =None
    buffer_locker =None
    session_status = None
    max_heart_beat_lost_counter = 10
    name = None
    def __init__(self, io_data_file):
        self.name = io_data_file
        self.session_status = True
        self.load(io_data_file)
        self.search_buffer = ''
        self.buffer_locker=  threading.Lock()
        th =threading.Thread(target=self.read_data)
        th.start()

    def load(self, io_data_file):
        import json
        json_data = ''.join([x.strip() for x in open(io_data_file).readlines()])
        self.io_map =json.loads(json_data)
    def add_data_to_search_buffer(self,data):
        self.buffer_locker.acquire()
        self.search_buffer+='{}'.format(data)
        self.buffer_locker.release()
    def reset_search_buffer(self):
        self.buffer_locker.acquire()
        self.search_buffer=''
        self.buffer_locker.release()
    def cmd(self,input_cmd):
        response = ''
        if self.io_map.has_key(input_cmd):
            data = self.io_map[input_cmd]
            if type(data) ==type(u''):
                response = data
            elif type([]) == type(data):
                if len(data)>0:
                    response = data[0]
                    self.io_map[input_cmd].pop(0)
        self.add_data_to_search_buffer(response)
        return  '{}'.format(response)
    def close_session(self):
        self.session_status=False
        time.sleep(0.001)
    def read_data(self):
        while self.session_status:
            if common.debug:
                print('session {name} alive'.format(name =self.name))
            time.sleep(0.001)