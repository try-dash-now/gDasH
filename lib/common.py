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
created 5/14/2017
'''
from functools import wraps
import  traceback
import os



debug = False
def dut_exception_handler(function_name):
    @wraps(function_name)
    def wrapped(*args, **kwargs):
        try:
            dut_instance=None
            if len(args):
                dut_instance= args[0]
            r = function_name(*args, **kwargs)
        except Exception as e:
            if dut_instance:
                if debug:
                    pass
                else:
                    dut_instance.close_session()
            raise
        return r
    return wrapped

def get_folder_item(path):
    abs_path = os.path.abspath(path)
    if os.path.exists(abs_path):
        folder_list = sorted(os.listdir(abs_path))
    else:
        folder_list= None
    return folder_list

import subprocess, tempfile
def runner(file_name, setting_file=None):
    exe_cmd =''
    pipe_input ,file_name =tempfile.mkstemp()
    #from setting file to get the log folder path and more setting for future
    valid_file_type =['.tc', '.ts', '.py']
    cmd={
        'tc': '',
        'ts': ''
    }
    #check file type, python file, csv file, test suite file ....
    subprocess.Popen(args = exe_cmd ,shell =True, stdin=pipe_input)
    #init sessions, create a session pool for used by test steps

    #execute
import csv
def load_bench(bench_file):
    dict_bench = {os.path.basename(bench_file):{}}
    with open(bench_file) as bench:
        reader = csv.reader(bench,delimiter=',')
        for row in reader:
            if len(row)<1:
                continue
            else:
                name = row[0]
                if dict_bench.has_key(name):
                    print('warning: duplicate session name "{}" in file "{}",overwritten!!!'.format(name, os.path.abspath(bench_file)))
                    continue
                else:
                    dict_attributes = {}
                    for attribute in row[1:]:
                        a_name,a_value = attribute.split('=')
                        dict_attributes[a_name.strip()]=a_value.strip()
                    dict_bench[os.path.basename(bench_file)][name]=dict_attributes
    return dict_bench



