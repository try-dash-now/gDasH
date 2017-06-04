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
unit test of lib/echo.py
'''
from lib.echo import echo
import unittest
init_file_name = 'ut_echo.json'
class ut_echo(unittest.TestCase):
    def setUp(self):
        self.echo = echo(init_file_name)
    def tearDown(self):
        pass
    def test_init(self):
        #print(self.echo)
        io_data = ''.join([x.strip() for x in open(init_file_name).readlines()])
        import json
        io_json = json.loads(io_data)
        for k in io_json.keys():
            self.assertEquals(self.echo.io_map, io_json )
        #import pprint
        #pprint.pprint(io_json, indent=4)

    def test_single_line_respone(self):
        self.echo.write('cmd1')
        self.assertEquals(self.echo.read().split('\n')[-1],'result1')

    def test_repeat_same_command(self):
        self.echo.write('cmd2')
        self.assertEquals(self.echo.read().split('\n')[-1],'result2')
        self.echo.write('cmd2')
        self.assertEquals(self.echo.read().split('\n')[-1],'result3')
        self.echo.write('cmd2')
        self.assertEquals(self.echo.read().split('\n')[-1],'')
        #self.assertEquals(self.echo.cmd('cmd2'),'None')

def suite():
    suite = unittest.TestSuite()
    suite.addTest(ut_echo.test_init())
    suite.addTest(ut_echo.test_single_line_respone())
    suite.addTest(ut_echo.test_repeat_same_command())

    return suite

if __name__ == '__main__':

    unittest.main()