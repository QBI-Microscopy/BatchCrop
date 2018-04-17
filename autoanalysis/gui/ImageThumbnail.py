import wx
import skimage.external.tifffile as tf
import numpy as np

from autoanalysis.processmodules.imagecrop.ImarisImage import ImarisImage


class ImageThumbnail(wx.StaticBitmap):
    """
    
    Abstract class. Use concrete Image type classes below. 
    
    """
    def __init__(self, parent, filename, shape=None):
        self.thumbnail = self.get_image_data(filename)
        if self.thumbnail is None:
            return

        if shape is not None:
            if len(shape) ==2:
                np.resize(self.thumbnail, (shape[0], shape[1], self.thumbnail.shape(2)))
            else:
                np.resize(self.thumbnail, shape)

        image = wx.Image(self.thumbnail.shape[1], self.thumbnail.shape[0], self.thumbnail)
        super(ImageThumbnail, self).__init__(parent, bitmap =wx.BitmapFromImage(image))
        self.SetBitmap(wx.BitmapFromImage(image))



    def get_image_data(self, filename):
        return None


class IMSImageThumbnail(ImageThumbnail):

    def __init__(self, parent, filename, shape=None):
        super(IMSImageThumbnail, self).__init__(parent, filename, shape=shape)

    def get_image_data(self, filename):
        try:
            return ImarisImage(filename).get_low_res_image()[0, :, :]

        except Exception as e:
            return None



class MultiPageTiffImageThumbnail(ImageThumbnail):

        def __init__(self, parent, filename, shape=None):
            super(MultiPageTiffImageThumbnail, self).__init__(parent, filename, shape=shape)

        def get_image_data(self, filename):
            try:
                segment_file = tf.TiffFile(filename)

                if (len(segment_file.pages) > 0):
                    # Get smallest resolution image

                    thumbnail = segment_file.pages[-1].asarray()
                    segment_file.close()
                    return thumbnail
                else:
                    segment_file.close()
                    return None

            except Exception:
                return None