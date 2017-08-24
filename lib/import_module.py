__author__ = 'Sean Yu'
'''created @2015/7/2'''
import os,sys
pardir =os.path.dirname(os.path.realpath(__file__))
pardir= os.path.sep.join(pardir.split(os.path.sep)[:-1])
sys.path.append(os.path.sep.join([pardir,'lib']))
sys.path.append(os.path.sep.join([pardir,'src']))
sys.path.append(os.path.sep.join([pardir,'gui']))
print('\n'.join(sys.path))
import abc #, zeep

