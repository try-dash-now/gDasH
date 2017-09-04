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
created 5/9/2017
'''
import sys
print sys.argv

from lib.dut import dut
import lib.common
import unittest
init_file_name = 'ut_echo.json'
class ut_dut(unittest.TestCase):
    def setUp(self):
        self.my_dut = dut('test_dut', type='echo', host= './ut_dut.json', login_step='./ut_session_login_step.csv')
    def tearDown(self):
        self.my_dut.close_session()
    def test_step(self):
        lib.common.debug=True
        self.my_dut.login()
        self.my_dut.step('','')
        self.my_dut.step('step_cmd_pattern','test_wait_for: pattern_found')
        self.my_dut.step('step_cmd_no_pattern','test_wait_for: No_this_pattern',not_want_to_find=True)
        self.my_dut.step('c','control \^C',ctrl=True)
    def test_wait_for(self):
    #     #no wait, search in buffer, find the expected pattern
    #     self.my_dut = dut('test_dut', type='echo', host= './ut_dut.json', login_step='./ut_session_login_step.csv')
    #     self.my_dut.login()
        self.my_dut.write('sean')
        success,match, buffer = self.my_dut.wait_for('pattern_found',1)
    #     #print('buffer: {}'.format(buffer))
        self.assertEquals(success, True)
    #
    #     #no wait, search in buffer, expect pattern not being found
    #     success,match, buffer = self.my_dut.wait_for('abc', 1,not_want_to_find=True)
    #     self.assertEquals(success, True)
    #     self.my_dut.close_session()




def suite():
    suite = unittest.TestSuite()
    suite.addTest(ut_dut.test_login())
    return suite

if __name__ == '__main__':

    unittest.main()