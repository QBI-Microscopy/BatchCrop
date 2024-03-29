from __future__ import print_function

from glob import iglob
from os.path import join, exists

import tifffile as tf
import wx


class ImagePanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.magsize = -2
        sizer = wx.BoxSizer(wx.VERTICAL)

        self.m_bitmapPreview = wx.StaticBitmap(self, wx.ID_ANY, wx.NullBitmap, wx.DefaultPosition,
                                               wx.DefaultSize, 0)
        sizer.Add(self.m_bitmapPreview, 0, wx.ALL, 5)

        self.SetSizer(sizer)
        self.Fit()

        self.Layout()

    def SetMagsize(self,val):
        self.magsize = val

    def loadImage(self, img):
        # print('Load image')
        tif_file = tf.TiffFile(img)
        thumb = tif_file.pages[self.magsize]
        I = wx.Image(wx.Size(thumb.shape[1], thumb.shape[0]), thumb.asarray())
        self.m_bitmapPreview.SetBitmap(I.ConvertToBitmap())
        self.Refresh()





class ImageViewer(wx.Frame):
    def __init__(self, imglist=None):
        wx.Frame.__init__(self, None, wx.ID_ANY,
                          "ImageViewer",
                          size=(900, 700)
                          )
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        self.currentimage = 0
        self.imglist = imglist
        self.maglist = ["Small" , "Medium", "Large"]
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.plotpanel = ImagePanel(self)
        # Add toolbar with filename (may be quite long so full length)
        toolbarf = wx.BoxSizer(wx.HORIZONTAL)
        fwdBtn = wx.Button(self, label='Forward')
        fwdBtn.Bind(wx.EVT_BUTTON, self.nextImage)
        backBtn = wx.Button(self, label='Back')
        backBtn.Bind(wx.EVT_BUTTON, self.prevImage)
        self.fnameLbl = wx.StaticText( self, wx.ID_ANY, u"Filename: ", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.fnameTxt = wx.StaticText( self, wx.ID_ANY, u"Filename", wx.DefaultPosition, wx.DefaultSize, 0 )
        toolbarf.Add(self.fnameLbl, 0, wx.ALL, 5)
        toolbarf.Add(self.fnameTxt,0, wx.ALL, 5)
        sizer.Add(toolbarf, 0, wx.GROW)
        # Add toolbar with scroll buttons
        toolbar = wx.BoxSizer(wx.HORIZONTAL)
        # Add mag sizes choice
        self.choiceLbl = wx.StaticText(self, wx.ID_ANY, u"Display Size: ", wx.DefaultPosition, wx.DefaultSize, 0)
        m_choice1Choices = self.maglist
        self.m_choice1 = wx.Choice(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice1Choices, 0)
        self.m_choice1.SetSelection(1)
        self.m_choice1.Bind(wx.EVT_CHOICE, self.OnChangeMag)
        toolbar.Add(self.choiceLbl, 0, wx.ALL, 5)
        toolbar.Add(self.m_choice1, 0, wx.ALL, 5)
        toolbar.Add(backBtn, 0, wx.ALL, 5)
        toolbar.Add(fwdBtn, 0, wx.ALL, 5)
        sizer.Add(toolbar, 0, wx.GROW)
        # Load first image
        self.plotpanel.loadImage(self.imglist[self.currentimage])
        self.fnameTxt.SetLabelText(self.imglist[self.currentimage])
        sizer.Add(self.plotpanel, 1, wx.EXPAND)
        self.SetSizer(sizer)

        self.Layout()
        self.Center(wx.BOTH)
        self.Show()

    def OnChangeMag(self,event):
        """
        Allow user to change magnification of thumb - three smallest options
        :param event:
        :return:
        """
        mag = self.m_choice1.GetStringSelection()
        #print('Selected mag=', mag)
        self.plotpanel.SetMagsize(-(self.maglist.index(mag)+1))
        self.plotpanel.loadImage(self.imglist[self.currentimage])

    def nextImage(self, event):
        """
        Load next image in the list if it exists
        :param event:
        :return:
        """

        if self.currentimage < len(self.imglist)-1:
            self.currentimage += 1
            loadimg = self.imglist[self.currentimage]
            # Ensure image file is OK
            while not exists(loadimg):
                self.currentimage += 1
                if self.currentimage < len(self.imglist):
                    loadimg = self.imglist[self.currentimage]
            if exists(loadimg):
                self.plotpanel.loadImage(loadimg)
                self.fnameTxt.SetLabelText(loadimg)


    def prevImage(self, event):
        #print('Prev image')
        if self.currentimage > 0:
            self.currentimage -= 1
            loadimg = self.imglist[self.currentimage]
            while not exists(loadimg):
                self.currentimage -= 1
                if self.currentimage >= 0:
                    loadimg = self.imglist[self.currentimage]
            if exists(loadimg):
                self.plotpanel.loadImage(self.imglist[self.currentimage])
                self.fnameTxt.SetLabelText(self.imglist[self.currentimage])

    def OnExit(self, e):
        self.Destroy()



if __name__ == '__main__':
    imgapp = wx.App()
    imgdir = "Z:\\Micro Admin\\Jack\\For Rumelo from Lei\\cropped\\170818_APP_1878 UII_BF~B"
    imglist = [x for x in iglob(join(imgdir, "*.tiff"))]
    frame = ImageViewer(imglist)
    imgapp.MainLoop()