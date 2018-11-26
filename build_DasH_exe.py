# -*- coding:  UTF-8 -*-
__author__ = 'Sean Yu'
__mail__ = 'try.dash.now@gmail.com'
'''
created 2015/11/10
'''
import os,sys,abc
import appdirs
import packaging
import packaging.version
import packaging.specifiers
import packaging.requirements
from setuptools.archive_util import unpack_archive
from lib.common import create_dir
pardir =os.path.dirname(os.path.realpath(__file__))
pardir= os.path.sep.join(pardir.split(os.path.sep)[:-1])
sys.path.append(os.path.sep.join([pardir,'lib']))
sys.path.append(os.path.sep.join([pardir,'test']))
sys.path.append(os.path.sep.join([pardir,'dut']))
print('\n'.join(sys.path))
import wx
import Tkinter
import os
import glob
from py2exe.build_exe import py2exe as build_exe
import zipfile
import sys
if len(sys.argv)<2:
    sys.argv.append('py2exe')
    sys.argv.append('-d')
    sys.argv.append('../DasH')


import paramiko
paramiko.SSHClient()
#import zeep
#C:/Python27/Lib/site-packages/paramiko-1.16.0-py2.7.egg!/paramiko/__init__.py

import shutil
target_distribute_folder = '../DasH'

for op in sys.argv:

    indexOfd = op.find('-d')
    if indexOfd !=-1:
        target_distribute_folder = sys.argv[sys.argv.index(op) + 1]
        break
target_distribute_folder =os.path.abspath(target_distribute_folder)
create_dir(target_distribute_folder)
targetDir = os.sep.join([target_distribute_folder, './tmp'])
excludedFolder =['sessions',
                 'src',
                 'lib',
                 ]
if not os.path.exists(target_distribute_folder):
    os.mkdir(target_distribute_folder)
else:
    shutil.rmtree(target_distribute_folder, ignore_errors=True)
    import time
    time.sleep(1)
    try:
        os.mkdir(target_distribute_folder)
    except:
        import traceback
        print(traceback.format_exc())

class tcltk(Tkinter.Tk):
    def __init__(self):
        Tkinter.Tk.__init__(self, None, None, 'Tk', 0)
tcltk()
from lib.dut import dut
a =dut('ssh', type='ssh',port=22, log_path='../log' ,retry_login = 0, retry_login_interval= 1)
from lib.TELNET import TELNET
try:
    wt = TELNET('a', log_path='../log')
except:
    pass
import pandas
import numpy
import matplotlib
import win32con,win32gui, win32api
pandas.DataFrame()
numpy.array([])
def numpy_dll_paths_fix():
    paths = set()
    np_path = numpy.__path__[0]
    for dirpath, _, filenames in os.walk(np_path):
        for item in filenames:
            if item.endswith('.dll'):
                paths.add(dirpath)

    sys.path.append(*list(paths))

numpy_dll_paths_fix()
# from TclInter import TclInter
# try:
#     ti = TclInter('a',{}, logpath='../test/log')
# except:
#     pass
eggdir = r'C:\Python27\Lib\site-packages\paramiko-1.16.0-py2.7.egg!\paramiko'
import pkg_resources
eggs = pkg_resources.require("paramiko")#TurboGears

for egg in eggs:
   if os.path.isdir(egg.location):
       sys.path.insert(0, egg.location)
       continue
   unpack_archive(egg.location, eggdir)
eggpacks = set()
eggspth = open("build/eggs.pth", "w")
for egg in eggs:
    print egg
    eggspth.write(os.path.basename(egg.location))
    eggspth.write("\n")
    try:
        eggpacks.update(egg.get_metadata_lines("top_level.txt"))
    except Exception as e :
        print(e)
eggspth.close()

#eggpacks.remove("pkg_resources")


def compressFile(infile,outfile):
    try:
        import zlib
        compression = zipfile.ZIP_DEFLATED
    except:
        compression = zipfile.ZIP_STORED

    modes = { zipfile.ZIP_DEFLATED: 'deflated',
              zipfile.ZIP_STORED:   'stored',
              }

    print 'creating archive'
    zf = zipfile.ZipFile(outfile, mode='w')
    try:
        zf.write(infile,outfile, compress_type=compression)
    except :
        import traceback
        print(traceback.format_exc())
        print 'closing'
        zf.close()
    return outfile
class MediaCollector(build_exe):
    def copy_extensions(self, extensions):
        build_exe.copy_extensions(self, extensions)

        # Create the media subdir where the
        # Python files are collected.

        media = 'selenium\\webdriver\\firefox'
        full = os.path.join(self.collect_dir, media)
        if not os.path.exists(full):
            self.mkpath(full)

        # Copy the media files to the collection dir.
        # Also add the copied file to the list of compiled
        # files so it will be included in zipfile.
        files = [
                '''C:\\Python27\\Lib\\site-packages\\selenium\\webdriver\\firefox\\webdriver.xpi'''
                 #   '''C:/Python27/Lib/site-packages/selenium-2.46.0-py2.7.egg/selenium/webdriver/firefox/webdriver.xpi''',
                 # '''C:\\Python27\\Lib\\site-packages\\selenium\\webdriver\\firefox\\webdriver_prefs.json'''
                 ]
        for f in files :#glob.glob('tools/'):
            name = os.path.basename(f)
            try:
                #zf = compressFile(f,'./abc.xpi')


                self.copy_file(f, os.path.join(full, name))
                self.compiled_files.append(os.path.join(media, name))
            except Exception as e:
                import traceback
                print(traceback.format_exc())

from distutils.core import setup
import py2exe
dll_excludes = [
                'libgdk-win32-2.0-0.dll',
                'libgobject-2.0-0.dll',
                #'tcl84.dll',
                #'tk84.dll',
                'MSVCP90.dll'
                 ]
py2exe_options = {
        'cmdclass': {'py2exe': MediaCollector},
        # [...] Other py2exe options here.
    }
#done 2017-10-14 2017-10-10 add webdriver for web browser
wd_base = r'C:\Python27\Lib\site-packages\selenium\webdriver'
RequiredDataFailes = [
    ('selenium/webdriver/firefox', ['%s\\firefox\\webdriver.xpi'%(wd_base), '%s\\firefox\\webdriver_prefs.json'%(wd_base)])
]
#done 2017-10-14 2017-10-11 need copy getAttribute.js and isDisplayed.js in C:\Python27\Lib\site-packages\selenium\webdriver\remote to ./selenium\webdriver\remote
#done 2017-10-14 2017-10-11 need copy all files under ./src, web.py missed
#done 2017-10-14 ./lib/ 2017-10-11 need find a better place for chromedriver.exe

def get_file_list_in_dir(dir_path, copy_py=False):
    #dir_path = 'test'
    base_dir = os.path.join('.', dir_path)
    for (dirpath, dirnames, files) in os.walk(base_dir):
        for f in files:
            print(f)
            if f.endswith('.pyc'):
                continue
            elif f.endswith('.py') and copy_py==False:
                continue
            elif f in ['.' , '..']:
                continue
            else:
                yield os.path.join(dirpath.split(os.path.sep, 1)[1], f)
try:
    dist = setup(
       # windows = ['./gDasH.py'],#'../bin/dash.py'
        windows =[{"script": "./gDasH.py", "icon_resources": [(1, "./gui/dash.bmp")] }],
        console=[
                    "./script_runner.py",
                    # "../test/cr.py",
                    # "../test/sr.py",
                    # "../test/ia.py",
                    # "../bin/ImportModule.py",#to include tcl things in the distribute package
                    "./lib/import_module.py",
                          ],

        data_files=list(matplotlib.get_py2exe_datafiles())+ [
                     './LICENSE.TXT',
                   # './gDasH.ini',
                    ( 'gui',[ './gui/dash.bmp']),
                    ('gui/html', [f for f in get_file_list_in_dir('./gui/html')]),#copy web related files to ./gui/html
                    ( 'sessions',[f for f in get_file_list_in_dir('./sessions')]),
                    ('selenium/webdriver/remote', [f for f in get_file_list_in_dir(r'C:\\Python27\Lib\site-packages\selenium\webdriver\remote', True)]),
                    ('src', [f for f in get_file_list_in_dir('./src', True)]),
                    ('lib', ['./lib/chromedriver.exe'])# copy chromedriver.exe to lib

                       #('dut', [ f for f in copy_dir('../dut')]),


                       ],
        options = {"py2exe":
                       {
                          "unbuffered": True,

                          #"compressed": 2,
                          "optimize": 0,#2,#no optimaze it, create .pyc files
                          "includes":[],# includes,
                          "excludes":[],# excludes,
                          "packages": ['numpy','pandas','win32con', 'win32api', 'win32gui'],#packages,,'numpy'
                          "dll_excludes": dll_excludes,
                          #"bundle_files": 1,
                          "dist_dir": "DasH",
                          "xref": False,
                          "skip_archive": True,
                          "ascii": False,
                          "custom_boot_script": '',

                        }
                   },
        **py2exe_options
    )
except:
    import traceback
    print(traceback.format_exc())




#fix numpy and matplotlib can be imported in py2exe distribute, it need to copy all *.dll under numpy/core/*.DLL and *.pyd ... as below listed
# copy core/*.DLL
# copy core/umath.pyd
# copy fft/*.pyd
# copy linalg/*.pyd
# copy random/*.pyd
# copy mpl-data to malplotlib
# copy backends to malplotlib
# copy C:\workspace\DasH\matplotlib/backend_managers.py

numpy_path_src = 'C:/Python27/Lib/site-packages/numpy'
numpy_path_dst = '{}/numpy'.format(target_distribute_folder)
matplotlib_path_src = 'C:/Python27/Lib/site-packages/matplotlib'
matplotlib_path_dst = '{}/matplotlib'.format(target_distribute_folder)
dirs_to_copy= [
    #source folder                                   , target folder,                                                   filter

    [r'{}/core'.format(numpy_path_src),              '{}/core'.format(numpy_path_dst),                               'DLL'],
    [r'{}/core'.format(numpy_path_src),             '{}/core'.format(numpy_path_dst),                               'pyd'],
    [r'{}/fft'.format(numpy_path_src),               '{}/fft'.format(numpy_path_dst),                                'pyd'],
    [r'{}/linalg'.format(numpy_path_src),            '{}/linalg'.format(numpy_path_dst),                             'pyd'],
    [r'{}/random'.format(numpy_path_src),           '{}/random'.format(numpy_path_dst),                             'pyd'],
    #matplotlib
    ['{}/'.format(matplotlib_path_src),             '{}/'.format(matplotlib_path_dst),                                'pyd'],
    ['{}/mpl-data'.format(matplotlib_path_src),     '{}/mpl-data'.format(matplotlib_path_dst),                      '*'],
    ['{}/'.format(matplotlib_path_src),                '{}/'.format(matplotlib_path_dst),                                'py'],
    ['{}/backends'.format(matplotlib_path_src),     '{}/backends'.format(matplotlib_path_dst),                       'py'],
    ['{}/backends'.format(matplotlib_path_src),     '{}/backends'.format(matplotlib_path_dst),                       'pyd'],
    ['{}/backends/qt_editor'.format(matplotlib_path_src),     '{}/backends/qt_editor'.format(matplotlib_path_dst),                       '*'],
    ['{}/backends/web_backend'.format(matplotlib_path_src),     '{}/backends/web_backend'.format(matplotlib_path_dst),                       '*'],
]
def copy_files_from_src_to_dest(src, dest, filter=None):
    FILTER ='.{}'.format(filter.lower())
    if FILTER in [None, '.', '.*', '']:
        #FILTER in ['.dll', '.pyd']:
        shutil.copytree(src, dest)
    else:
        print('copying {}/*.{} ->{}'.format(src, FILTER, dest))
        file_list = os.listdir(src)
        for src_path in  file_list:
            print('!!! copying {} from {}'.format(src_path, src))
            if os.path.splitext(src_path)[1].lower() in [FILTER] :
                shutil.copy2('{}/{}'.format(src,src_path), dest)




for src, dest, filter in dirs_to_copy:
    copy_files_from_src_to_dest(src, dest, filter)

import zipfile
zip_ref = zipfile.ZipFile('./build_packages/build_package.zip', 'r')
zip_ref.extractall(target_distribute_folder)
zip_ref.close()

target_distribute_folder = os.path.abspath(os.path.normpath(os.path.expanduser(target_distribute_folder)))
dash_zipfile = os.path.abspath('{}/../DasH'.format(target_distribute_folder))
shutil.make_archive(dash_zipfile, 'zip', target_distribute_folder)