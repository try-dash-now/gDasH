print('''script_runner.exe/py script_name [arg1, arg2 ...argN]
script_runner.exe/py reads src_path/lib_path/log_path from file ./gDasH.ini to set PYTHONPATH''')
if __name__ == "__main__":
    import os
    import sys
    import ConfigParser
    ini_file = './gDasH.ini'
    ini_setting = ConfigParser.ConfigParser()
    ini_setting.read(ini_file)
    src_path = os.path.abspath(ini_setting.get('dash','src_path'))
    lib_path = os.path.abspath(ini_setting.get('dash','lib_path'))
    log_path = os.path.abspath(ini_setting.get('dash','log_path'))
    paths_of_libs = [log_path, src_path,lib_path]
    for p in paths_of_libs:
        path = os.path.abspath(p)
        if os.path.exists(path):
            print('path added to SYSTEM PATH: {}'.format(path))
            sys.path.insert(0,path)
        else:
            Exception("path is not exist, can't be added to SYSTEM PATH(PYTHON PATH\n\t{}".format(path))
    import subprocess
    DEBUG = True
    if DEBUG:
        sys.argv.append('run_ut.py')
    if len(sys.argv)<2:
        print('ERROR: please input the script name to be executed!')
    else:
        script_name = sys.argv[1]
        argvs = sys.argv[1:]
        cmd_line = ' '.join(sys.argv[1:])
        pp = subprocess.Popen(args = cmd_line ,  shell =True)
        import time
        ChildRuning = True
        while ChildRuning:
            if pp.poll() is None:
                interval = 1
                time.sleep(interval)
                print('{} is running'.format(cmd_line))
            else:
                ChildRuning = False
        print('{} is completed with returncode ={}'.format(cmd_line, pp.returncode))

        returncode = pp.returncode
        exit(returncode)