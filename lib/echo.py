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
import Queue
class echo (object):
    io_map = None
    name = None
    last_command = None
    def __init__(self, io_data_file):
        self.name = io_data_file
        self.last_command = Queue.Queue()
        self.load(io_data_file)
    def load(self, io_data_file):
        import json
        json_data = ''.join([x.strip() for x in open(io_data_file).readlines()])
        self.io_map =json.loads(json_data)

    def write(self,input_cmd):
        self.last_command.put(input_cmd)
        return ''
    def read(self):
        response = ''
        input_cmd = self.last_command.get()
        pure_cmd = input_cmd.strip()
        cmd = pure_cmd
        if self.io_map.has_key(input_cmd):
            cmd = input_cmd
        elif self.io_map.has_key(pure_cmd):
            pass

        if self.io_map.has_key(cmd):
            data = self.io_map[cmd]
            if type(data) ==type(u''):
                response = data
            elif type([]) == type(data):
                if len(data)>0:
                    response = data[0]
                    self.io_map[cmd].pop(0)

        return  '{}'.format(response)


