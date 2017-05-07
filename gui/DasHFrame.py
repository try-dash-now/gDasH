#!/usr/bin/python
__author__ = 'sean yu'
__doc__ = '''
it's GUI of DasH aka Do as Human
created 2017-05-06 by Sean Yu
'''
import wx
from gui.MainFrame import MainFrame



# Some classes to use for the notebook pages.  Obviously you would
# want to use something more meaningful for your application, these
# are just for illustration.

class PageOne(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        t = wx.StaticText(self, -1, "This is a PageOne object", (20,20))


class PageTwo(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        t = wx.StaticText(self, -1, "This is a PageTwo object", (40,40))

class PageThree(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        t = wx.StaticText(self, -1, "This is a PageThree object", (60,60))


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


    def OnSelChanged(self, event):
        item =  event.GetItem()
        self.display.SetLabel(self.tree.GetItemText(item))