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
created 5/13/2017
'''
import unittest
from unittest import TestSuite
def load_tests(loader, tests, pattern):
    ''' Discover and load all unit tests in all files named ``ut_*.py`` in ``./``
    '''

    suite = TestSuite()
    for all_test_suite in unittest.defaultTestLoader.discover('./', pattern='ut_*.py'):
        for test_suite in all_test_suite:
            suite.addTests(test_suite)
    return suite

if __name__ == '__main__':
    loader = unittest.TestLoader()
    tests = unittest.suite.TestSuite([])
    suite = load_tests(loader, tests, pattern='ut_*.py')
    result = unittest.TestResult()
    suite.run(result)
    from pprint import pprint
    pprint(result)
    for fail in result.errors:
        pprint(fail[0])
        for line in fail[1].split('\n')[1:]:
            print('\t\t{}'.format(line))
       # pprint('{},\n\t{}'.format(fail[0], fail[1]))

    pprint(result)
