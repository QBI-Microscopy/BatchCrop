from collections import deque
import wx
import os

from wx.lib.pubsub import pub as Publisher

from autoanalysis.gui.ImageThumbnail import *


class ImageSegmentOrderingPanel(wx.Panel):
    """
    Widget to display the segments of a cropped image for the user to order and produce an XML that it ultimately able
     to help stack the slices in FIJI/ImageJ
    """

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(500, 500), style=wx.TAB_TRAVERSAL)
        self.SetBackgroundColour((111, 111, 111))
        self.segmentOrderQueue = None
        Publisher.subscribe(self.updateSegmentOrderQueue, "Image_Cropped_Finished")
        self.parent = parent
        self.bSizer1 = wx.BoxSizer(wx.VERTICAL)
        self.bSizer2 = wx.BoxSizer(wx.VERTICAL)

        self.submit = wx.Button(self, wx.ID_ANY, u"Confirm", wx.DefaultPosition, wx.DefaultSize, 0)
        self.bSizer2.Add(self.submit, 0, wx.ALL, 5)
        self.submit.Bind(wx.EVT_BUTTON, self.confirmSegmentOrder)

        self.SetSizer(self.bSizer1)
        self.image_sizer = wx.BoxSizer(wx.VERTICAL)
        self.bSizer1.Add(self.image_sizer, 0, wx.ALL, 5)
        self.bSizer1.Add(self.bSizer2)
        self.Layout()

        self.images = []


    def confirmSegmentOrder(self, event):
        self.generateSegmentOrderFile()
        self.deleteSegmentImages()
        self.updatesegmentUI()

    def generateSegmentOrderFile(self):
        pass

    def deleteSegmentImages(self):
        pass


    def loadSegmentImages(self, Image):
        try:
            self.bitmaps = []
            for file in os.listdir(Image.filepath):
                    filepath = os.path.join(Image.filepath, file)
                    image = MultiPageTiffImageThumbnail(self, filepath)
                    self.bitmaps.append(image)
                    self.image_sizer.Add(image)

        except Exception as e:
            print(str(e))


    def updatesegmentUI(self):
        if self.segmentOrderQueue is None:
            return
        if len(self.segmentOrderQueue) != 0:
            next_image = self.segmentOrderQueue.pop()
            self.loadSegmentImages(next_image)


    def updateSegmentOrderQueue(self, details):
        """
        Triggered on a subscription to Image_Cropped_Finished. Updates the image ordering queue and if its the first image
        for the application will trigger the initial UI change. 
        :param details: 
        """
        if self.segmentOrderQueue is None:
            self.segmentOrderQueue = deque()
            self.segmentOrderQueue.appendleft(details)
            self.updatesegmentUI()
        else:
            self.segmentOrderQueue.appendleft(details)
