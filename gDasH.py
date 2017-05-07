#!/usr/bin/python
__author__ = 'sean yu'
__doc__ = '''
it's GUI of DasH aka Do as Human
created 2017-05-06 by Sean Yu
'''

from gui.DasHFrame import DasHFrame
import wx
if __name__ == "__main__":
    app = wx.App()
    dash = DasHFrame(None)
    dash.Centre()
    dash.Show()
    app.MainLoop()