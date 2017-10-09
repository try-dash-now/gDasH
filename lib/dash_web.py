__author__ = 'Sean Yu'
'''created @2017/10/09'''
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import threading
import shlex
import  traceback
class dash_web(object):
    driver= None
    output_buffer = None
    output_locker = None
    function_in_dirver=None
    function_in_dash_web =None
    help_doc= None
    function_supported = None
    response =None
    def __init__(self, executable_path = './lib/', time_out= 15,):
        import os
        print os.path.abspath(executable_path)
        self.driver = webdriver.Chrome(executable_path = '{}/chromedriver.exe'.format(executable_path))
        #self.driver.maximize_window()  # full screen
        self.driver.set_page_load_timeout(time_out)
        self.output_locker = threading.Lock()
        self.output_buffer ='Web Browser opened'
        self.function_in_dirver={}
        self.help_doc= {}
        #self.function_supported = ''
        import types


        self.function_in_dash_web ={}
        ignore_function= ['__init__', 'write', 'read']
        for attribute in dir(self):
            if attribute not in ignore_function:
                if isinstance(self.__getattribute__(attribute), types.MethodType):
                    if not attribute.startswith('_'):
                        self.function_in_dash_web[attribute]= self.__getattribute__(attribute)
                        self.help_doc[attribute]= '{}:\n{}'.format(attribute, self.__getattribute__(attribute).__doc__)

        for attribute in dir(self.driver):
            #print attribute
            try:
                if isinstance(self.driver.__getattribute__(attribute), types.MethodType):
                    if not attribute.startswith('_'):
                        self.function_in_dirver[attribute] = self.driver.__getattribute__(attribute)
                        self.help_doc[attribute]= '{}\n{}'.format(attribute, self.driver.__getattribute__(attribute).__doc__)
            except Exception as e:
                pass
    def read(self):
        self.output_locker.acquire()
        data =self.output_buffer
        self.output_buffer=''
        self.output_locker.release()
        return  data

    def write(self, cmd, ctrl=False):
        try:
            lex = shlex.shlex(cmd)
            lex.quotes = '"'
            lex.whitespace_split = True
            function_and_args = list(lex)
            self.__update_output_buffer(cmd)
            if len(function_and_args)>0:
                function_name = function_and_args[0]
                args = function_and_args[1:]

                func = None
                if function_name in self.function_in_dash_web:
                    func= self.function_in_dash_web[function_name]
                elif function_name in self.function_in_dirver:
                    func= self.function_in_dirver[function_name]

                if func:
                    new_argvs=[]
                    new_kwargs={}
                    def GetFunArgs(*argvs, **kwargs):
                    #re-assign for self.argvs and self.kwargvs

                        for arg in argvs:
                            new_argvs.append(arg)
                        for k in kwargs.keys():
                            new_kwargs.update({k:kwargs[k]})

                    args_string = ','.join(['{}'.format(x) for x in args])

                    eval('GetFunArgs({args})'.format(args=args_string))
                    response = None
                    try:
                        self.response = func(*new_argvs, **new_kwargs)
                        self.__update_output_buffer( 'done - {}({})\n{}'.format(function_name, args_string, response))
                    except Exception as e:

                        response = traceback.format_exc()
                        self.__update_output_buffer( 'failed - {}({})\n{}'.format(function_name, args_string, response))
                        #raise e
                else:
                    self.__update_output_buffer('{} is not valid function name\n"help" to get all supported functions/command'.format(function_name))
        except Exception as e:
            self.__update_output_buffer(traceback.format_exc())
        return ''
    def close(self):
        self.driver.quit()

        #done: 2017-10-9, 2017-10-7 a new type of dut--shell, powershell for windows and linux shell
    def __update_output_buffer(self,data):
        self.output_locker.acquire()
        self.output_buffer+= '{}\n>\n'.format(data)
        self.output_locker.release()

    def help(self,attribute=None):
        if self.function_supported is None:
            self.function_supported =''
            for f in sorted(self.help_doc):
                self.function_supported +='{}\n'.format(f)

        if attribute is None:
            self.__update_output_buffer('\n{}\n'.format(self.function_supported))
        elif attribute in self.help_doc:
                self.__update_output_buffer(self.help_doc[attribute])
    def xfind(self, identifier, by=None ):
        '''
        xfind(self, identifier, by=None ):
        to find element by identifier, and return the element, return None if failed to find the element
        identifier: string, search the identifier in the source code
        by: string, one of  list [link_text,partial_link_text,id,name,xpath,tag_name,class_name, None]
            default is None, try order: left to right as list above
        '''
        if by is None:
            search_order =[self.driver.find_element_by_link_text,
                       self.driver.find_element_by_partial_link_text,
                       self.driver.find_element_by_id,
                       self.driver.find_element_by_name,
                       self.driver.find_element_by_xpath,
                       self.driver.find_element_by_tag_name,
                       self.driver.find_element_by_class_name]
        else:
            fun_name = 'find_element_by_{}'.format(by.strip().lower())
            if fun_name in self.function_in_dirver:
                search_order = [self.driver.__getattribute__(fun_name)]



        element =None
        for func in search_order:
            try:
                element  = func(identifier)
            except Exception as e:
                pass
            if element:
                self.__update_output_buffer('find element({})'.format(identifier))
                break
        if element is None:
            self.__update_output_buffer('failed to find element({})'.format(identifier))
        return  element

    def xclick(self, identifier,  by=None):
        '''
        xclick(self, identifier,  by=None ):
        to find element by identifier, and click it
        identifier: string, search the identifier in the source code
        by: string, one of  list [link_text,partial_link_text,id,name,xpath,tag_name,class_name, None]
            default is None, try order: left to right as list above
        '''
        element = self.xfind(identifier, by)
        element.click()
        self.__update_output_buffer('clicked element({})'.format(identifier))
    def xget_attribute(self, identifier, attribute ,by =None,):
        element =self.xfind(identifier, by)
        value =element.get_attribute(attribute)
        self.__update_output_buffer('{} of {}:\n\t{}'.format(attribute, identifier, value))
        return  value






