import os
from collections import deque

from autoanalysis.gui.ImageThumbnail import *


# from wx.lib.pubsub import pub as Publisher


class ImageSegmentOrderingPanel(wx.Panel):
    """
     Widget to display the segments of a cropped image for the user to order and produce an XML that it ultimately able
     to help stack the slices in FIJI/ImageJ
    """

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition)
        #self.SetBackgroundColour((111, 111, 111))
        self.segmentOrderQueue = deque()
        #Publisher.subscribe(self.updateSegmentOrderQueue, "Image_Cropped_Finished")
        self.parent = parent
        self.bitmaps = {}

    def OnShowResults(self,event,filedir):
        print('ImageSegmentPanel: processing panel results')


    def confirmSegmentOrder(self, event):
        ignore = [print(bit) for bit in self.bitmaps]
        self.generateSegmentOrderFile()
        self.deleteSegmentImages()
        self.updatesegmentUI()

    def generateSegmentOrderFile(self):
        pass

    def deleteSegmentImages(self):
        print("deleting segment images")
        if len(self.bitmaps) > 0:
            for bitmap in self.bitmaps:
                bitmap.Destroy()
        self.bitmaps = []

    def loadSegmentImages(self, Image):
        try:
            print("load segment images {0}".format(Image.filepath))
            self.bitmaps = []
            for file in os.listdir(Image.filepath):
                    filepath = os.path.join(Image.filepath, file)
                    image = MultiPageTiffImageThumbnail(self, filepath)
                    self.bitmaps.append(image)
                    # self.AddChild(image)
                    # self.image_sizer.Add(image)
            # self.image_sizer.AddMany(self.bitmaps)

        except Exception as e:
            print(str(e))


    def updatesegmentUI(self):
        if self.segmentOrderQueue is None:
            print("update segment Queue UI is None")

        elif len(self.segmentOrderQueue) != 0:
            next_image = self.segmentOrderQueue.pop()
            print(next_image.filepath)
            self.loadSegmentImages(next_image)
        else:
            print("length of queue is 0")

    def updateSegmentOrderQueue(self, details):
        """
        Triggered on a subscription to Image_Cropped_Finished. Updates the image ordering queue and if its the first image
        for the application will trigger the initial UI change. 
        :param details: 
        """
        self.segmentOrderQueue.appendleft(details)
        if len(self.segmentOrderQueue) > 0 and len(self.bitmaps) == 0:
            print("DETAILS", details)
            self.updatesegmentUI()
