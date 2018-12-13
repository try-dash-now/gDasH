print('''script_runner.exe/py script_name [arg1, arg2 ...argN]
script_runner.exe/py reads src_path/lib_path/log_path from file ./gDasH.ini to set PYTHONPATH''')
if __name__ == "__main__":
    import os
    import sys
    import ConfigParser
    import traceback
    import  time
    ini_file = './gDasH.ini'
    ini_setting = ConfigParser.ConfigParser()
    ini_setting.read(ini_file)
    src_path = os.path.abspath(ini_setting.get('dash','src_path')).replace(',',';').split(';')
    lib_path = os.path.abspath(ini_setting.get('dash','lib_path')).replace(',',';').split(';')
    log_path = os.path.abspath(ini_setting.get('dash','log_path')).replace(',',';').split(';')
    if ini_setting.has_option('dash','tcl_exe_path'):
        tcl_exe_path = ini_setting.get('dash','tcl_exe_path')
    else:
        tcl_exe_path = r'C:\Tcl\bin\tclsh.exe'
    paths_of_libs = log_path+src_path+lib_path

    for p in paths_of_libs:
        path = os.path.abspath(p)
        if os.path.exists(path):
            print('path added to SYSTEM PATH: {}'.format(path))
            sys.path.insert(0,path)
        else:
            Exception("path is not exist, can't be added to SYSTEM PATH(PYTHON PATH\n\t{}".format(path))
    import subprocess
    DEBUG = False
    if DEBUG:
        sys.argv.append('run_ut.py')
    if len(sys.argv)<2:
        print('ERROR: please input the script name to be executed!')
    else:
        old_sys_argv = sys.argv
        script_name = sys.argv[1]
        sys.argv= sys.argv[1:]
        try:
            #from lib.common import create_case_folder
            #case_log_path = create_case_folder()

            case_log_path = '../log/'
            log_option = '-l'
            if log_option in sys.argv:
                log_index = sys.argv.index(log_option)
                if len(sys.argv)> log_index+1:
                    case_log_path = sys.argv[log_index+1] #=case_log_path
                else:
                    sys.argv.append(case_log_path)
            else:
                sys.argv.append('-l')
                sys.argv.append(case_log_path)
            import tempfile
            #pipe_input ,file_name_in =tempfile.mkstemp(prefix='stdin_', suffix='.log',dir=case_log_path)
            #pipe_output ,file_name_out =tempfile.SpooledTemporaryFile(prefix='stdout_',suffix='.log' ,dir=case_log_path)
            #pipe_input ,file_name_in =tempfile.mkstemp(prefix='stdin_', suffix='.log',dir=case_log_path)
            pipe_output ,file_name_out =tempfile.mkstemp(prefix='stdout_',suffix='.log' ,dir=case_log_path)
            #pipe_input  =tempfile.SpooledTemporaryFile(prefix='stdin_', suffix='.log',dir=case_log_path)
            #pipe_output  =tempfile.SpooledTemporaryFile(prefix='stdout_',suffix='.log' ,dir=case_log_path)

            class redir(object):
                old_stdout= None
                file_obj =None
                #fileno =None
                def __init__(self, file_obj, old_stdout):
                    self.old_stdout=old_stdout
                    self.file_obj=file_obj
                    #self.fileno = file_obj
                def fileno(self):
                    return  self.file_obj
                def write(self, data):
                    try:
                        os.write(self.file_obj,data)
                        self.old_stdout.write(data)
                    except Exception as e:
                        print(traceback.format_exc())
            stdout = redir(pipe_output, sys.stdout)
            stderr = redir(pipe_output, sys.stderr)
            sys.stdout= stdout
            sys.stderr= stderr
            if script_name.endswith('.tcl'):# it is a tcl script
                cmd = [tcl_exe_path, script_name ]+sys.argv[1:]
                #print(stdout.old_stdout.fileno)
                proc=subprocess.Popen(cmd, stdout=stdout)#, creationflags = subprocess.CREATE_NEW_CONSOLE
                while 1:
                    if proc.poll() is None:
                        #print('{} is running'.format(cmd))

                        time.sleep(1)
                    else:
                        return_code = 'FAIL' if proc.returncode else 'PASS'
                        #print('{} is {}'.format(cmd, return_code))
                        if proc.returncode:
                            raise Exception('"{}" is {}'.format(' '.join(cmd), return_code))
                        break
            elif script_name.endswith('.py'):
                execfile(script_name,globals(), locals() )
        except Exception as e:
            print(traceback.format_exc())
            raise e


