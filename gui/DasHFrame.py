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

class PageOne(wx.Panel):
    editor =None
    def __init__(self, parent, title='pageOne'):
        wx.Panel.__init__(self, parent)
        #self.editor = wx.TextCtrl(self, style = wx.TE_MULTILINE|wx.TE_RICH2|wx.EXPAND|wx.ALL, size=(-1,-1))
        self.editor = wx.richtext.RichTextCtrl( self, -1, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0|wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER|wx.WANTS_CHARS )
        #self.content1 = wx.richtext.RichTextCtrl(self, size=(300, 100), style=wx.TE_MULTILINE)

        sizer = wx.BoxSizer()
        sizer.Add(self.editor, 1, wx.EXPAND)
        self.SetSizer(sizer)


        #wx.StaticText(self, -1, "THIS IS A PAGE OBJECT", (20,20))

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

            self.m_case_tree.SetItemTextColour(tmp ,wx.Colour(255-10*i,10*i,i*i))

        self.m_case_tree.ExpandAll()
        self.m_editor.WriteText('welcome to dash world')
        self.m_log.WriteText('Happy Birthday!')
        self.m_command_box.WriteText('read only,but select copy allowed')
        fileMenu = wx.Menu()
        open_test_suite = fileMenu.Append(wx.NewId(), "Open TestSuite", "Open a Test Suite")
        open_test_case = fileMenu.Append(wx.NewId(), "Open TestCase", "Open a Test Case")
        self.m_menubar_main.Append(fileMenu, "&Open TestSuite")


        p = self.m_file_editor
        nb = wx.Notebook(p)
                # create the page windows as children of the notebook
        page1 = PageOne(nb, 'a')
        page2 = PageOne(nb, 'b')
        page3 = PageOne(nb)
        page1.editor.WriteText('aaa')

        # add the pages to the notebook with the label to show on the tab
        nb.AddPage(page1, "Page 1")
        nb.AddPage(page2, "Page 2")
        nb.AddPage(page3, "Page 3")
        page1.editor.WriteText('aaa')
        page2.editor.WriteText('bbbb')
        page3.editor.WriteText('aaacccc')
        page1.editor.BeginTextColour((255,0,255))
        page1.editor.WriteText('color')
        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        self.m_file_editor.SetSizer(sizer)


    def OnSelChanged(self, event):
        item =  event.GetItem()
        self.display.SetLabel(self.tree.GetItemText(item))