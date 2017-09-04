print('''script_runner.exe/py script_name [arg1, arg2 ...argN]
script_runner.exe/py reads src_path/lib_path/log_path from file ./gDasH.ini to set PYTHONPATH''')
if __name__ == "__main__":
    import os
    import sys
    import ConfigParser
    ini_file = './gDasH.ini'
    ini_setting = ConfigParser.ConfigParser()
    ini_setting.read(ini_file)
    src_path = os.path.abspath(ini_setting.get('dash','src_path')).replace(',',';').split(';')
    lib_path = os.path.abspath(ini_setting.get('dash','lib_path')).replace(',',';').split(';')
    log_path = os.path.abspath(ini_setting.get('dash','log_path')).replace(',',';').split(';')
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
        script_name = sys.argv[1]
        sys.argv= sys.argv[2:]
        try:
            execfile(script_name,globals(), locals() )
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            raise e


