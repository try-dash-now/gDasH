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
__author__ = 'sean yu (Yu, Xiongwei)'
__doc__ = '''
it's GUI of DasH aka Do as Human
created 2017-05-06 by Sean Yu
'''
import wx
from gui.MainFrame import MainFrame
class DasHFrame(MainFrame):#wx.Frame
    def __init__(self,parent=None):
        #wx.Frame.__init__(self, None, title="DasH")
        MainFrame.__init__(self, parent=parent)

        root =self.m_case_tree.AddRoot('TestSuiteName 1')

        for i in range(10):
            self.m_case_tree.AppendItem(root, 'case %d'%(i+1))
        sub_folder = self.m_case_tree.AppendItem(root,'TestSuiteName 2')
        self.m_case_tree.ItemHasChildren(sub_folder)
        #self.m_case_tree.InsertItem
        for i in range(10):
            tmp = self.m_case_tree.InsertItem(sub_folder, sub_folder, 'case %d'%(i+1))

        self.m_case_tree.ExpandAll()
        self.m_editor.WriteText('welcome to dash world')
        self.m_log.WriteText('Happy Birthday!')
        self.m_command_box.WriteText('read only,but select copy allowed')



    def OnSelChanged(self, event):
        item =  event.GetItem()
        self.display.SetLabel(self.tree.GetItemText(item))