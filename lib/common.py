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
import inspect
import imp

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


def create_session(name, attribute):
    # if attribute.has_key('init_file_name'):
    #     #this is a echo session
    #     ses = echo(name, attribute['init_file_name'])
    # elif attribute.has_key('type'):
    #if attribute['type'].lower()=='ssh':

    from dut import dut
    ses = dut(name, **attribute )

    return  ses

def parse_command_line(cmd_string):
    import shlex
    lex = shlex.shlex(cmd_string)
    lex.quotes = '"'
    lex.whitespace_split = True
    cmd_list=list(lex)
    if cmd_list.__len__()>1:
        mod_funct=cmd_list[0].split('.')
        if mod_funct.__len__() ==1:
            module_name =''
            class_name = ''
            function_name = mod_funct[0]
        elif mod_funct.__len__()==2:
            class_name=''
            module_name,function_name = mod_funct[:2]
        elif mod_funct.__len__()>2:
            module_name,class_name,function_name=mod_funct[:3]
        args = cmd_list[1:]
        return  module_name,class_name,function_name,args

def call_function_in_module(module_name, class_name, function_name, args):
    import inspect
    new_argvs=[]
    new_kwargs={}
    def GetFunArgs(*argvs, **kwargs):
    #re-assign for self.argvs and self.kwargvs
        for arg in argvs:
            new_argvs.append(arg)
        for k in kwargs.keys():
            new_kwargs.update({k:kwargs[k]})


    eval('GetFunArgs({args})'.format(args=','.join(['{}'.format(x) for x in args])))
    print('module_name: \t{mn}\nclass_name: \t{cn}\nfunction_name: \t{fn}\nargs:{args}\nkwargs: {kwargs}'.format(mn=module_name,cn = class_name,fn=function_name,args=new_argvs, kwargs=new_kwargs))
    instance_name = '{}_inst'.format(module_name)
    try:
        file, path_name, description = imp.find_module(module_name)
        lmod = imp.load_module(module_name, file, path_name,description)
        instance_name = getattr(lmod, class_name)()
        getattr(instance_name, function_name)(*new_argvs,**new_kwargs)
    except Exception as e:
        msg = "failed to load module {}:{}".format(module_name, e)
        error(msg )




log_type_name = ['INFO','WARN','ERRO','DEBUG']
log_level = 4
def caller_stack_info(level=log_level, depth = 2):
    curframe = inspect.currentframe()
    calframe = inspect.getouterframes(curframe, 2)
    calframe = inspect.getouterframes(calframe[1][0],2)
    if depth==3:
        calframe = inspect.getouterframes(calframe[1][0],2)
    class_name = '{}'.format(type(calframe[2][0].f_locals['self']))
    class_name=''
    name = calframe[2][0].f_locals['self'].ses_name+'.' if  'ses_name' in inspect.getmembers(calframe[2][0].f_locals['self']) else ''
    file_name, line_no, caller_name,code_list, = calframe[2][1:5]
    msg= '{level}\t{fn}:{line_no}\t{caller}'.format(level = log_type_name[level],fn=os.path.basename(file_name), line_no = line_no,caller = caller_name)
    if level==0:
        msg = '{level}\t{line_no}\t{caller}'.format(level = log_type_name[level],line_no = line_no,caller = caller_name)
    elif level==1:
        msg = ''

    return msg

def log(string, info_type_index=3, depth = 2):
    info = caller_stack_info(info_type_index, depth)
    str = '{}:\t{}'.format(info,string)
    if log_level>=info_type_index:
        print(str)
    return  str
def error(string):
    log(string,2,3)
def debug(string):
    log(string, 3, 3)
def warn(string):
    log(string,1,3)

def reload_module(instance, function_name):
    parents = type.mro(type(instance))[:-1]
    parents.insert(0, instance)
    class_name = 0

    target_module_name =None
    target_module = None
    for p in parents:
        if p.__dict__.has_key(function_name):
            target_module_name= p.__module__
            break


    for p in parents:#[::-1]:
        mn = p.__module__
        if target_module_name==mn:
            module_info =imp.find_module(mn )# imp.new_module(modulename)
            module_dyn = imp.load_module(mn ,*module_info)
            reload(module_dyn)
            target_module= module_dyn


