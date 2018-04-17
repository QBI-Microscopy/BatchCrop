import numpy as np
import skimage.external.tifffile as tf
import wx
from autoanalysis.processmodules.imagecrop.ImarisImage import ImarisImage
from scipy.misc import imresize

class ImageThumbnail(wx.StaticBitmap):
    """
    
    Abstract class. Use concrete Image type classes below. 
    
    """
    def __init__(self, parent, filename, max_size=None):
        self.thumbnail = self.get_image_data(filename)
        if self.thumbnail is None:
            return

        if max_size is not None:
            # Adjust size so that the image dimensions just fit within max_size dimensions
            if self.thumbnail.shape[0]/max_size[0] > self.thumbnail.shape[1]/max_size[1]:
                self.thumbnail = imresize(self.thumbnail, max_size[0] / self.thumbnail.shape[0])
            else:
                self.thumbnail = imresize(self.thumbnail, max_size[1] / self.thumbnail.shape[1])

        image = wx.Image(wx.Size(self.thumbnail.shape[1], self.thumbnail.shape[0]), self.thumbnail)
        super(ImageThumbnail, self).__init__(parent, bitmap =wx.BitmapFromImage(image))
        self.SetBitmap(wx.BitmapFromImage(image))



    def get_image_data(self, filename):
        return None


class IMSImageThumbnail(ImageThumbnail):

    def __init__(self, parent, filename, max_size=None):
        super(IMSImageThumbnail, self).__init__(parent, filename, max_size=max_size)

    def get_image_data(self, filename):
        try:
            file = ImarisImage(filename)
            # Must get all channels of image to be compatible with wx.image
            data = [file.get_two_dim_data(file.resolutions-1, c=i) for i in range(file.get_channel_levels())]
            data = np.stack(data, axis=2)
            file.close_file()
            return data

        except Exception as e:
            import traceback
            print(traceback.format_exc())
            print("Error getting thumbnail from {0}".format(filename), str(e))
            return None



class MultiPageTiffImageThumbnail(ImageThumbnail):

        def __init__(self, parent, filename, max_size=None):
            super(MultiPageTiffImageThumbnail, self).__init__(parent, filename, max_size=max_size)

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