import numpy as np
import skimage.external.tifffile as tf
import wx
from autoanalysis.processmodules.imagecrop.ImarisImage import ImarisImage
#from scipy.misc import resize
from skimage.transform import resize

class ImageThumbnail(wx.StaticBitmap):
    """
    
    Abstract class. Use concrete Image type classes below. 
    
    """
    def __init__(self, parent, filename, max_size=None):
        self.thumbnail = self.get_image_data(filename)
        self.filename = filename
        if self.thumbnail is None:
            return

        if max_size is not None:
            # Adjust size so that the image dimensions just fit within max_size dimensions
            if self.thumbnail.shape[0]/max_size[0] > self.thumbnail.shape[1]/max_size[1]:
                self.thumbnail = resize(self.thumbnail, max_size[0] / self.thumbnail.shape[0])
            else:
                self.thumbnail = resize(self.thumbnail, max_size[1] / self.thumbnail.shape[1])

        image = wx.Image(wx.Size(self.thumbnail.shape[1], self.thumbnail.shape[0]), self.thumbnail)
        super(ImageThumbnail, self).__init__(parent, bitmap=image.ConvertToBitmap())
        #self.SetBitmap(wx.BitmapFromImage(image))

    def get_image_data(self, filename):
        return None


    @staticmethod
    def resize_thumbnail(image_data, max_size):
        # Adjust size so that the image dimensions just fit within max_size dimensions
        if image_data.shape[0] / max_size[0] > image_data.shape[1] / max_size[1]:
            image_data = resize(image_data, max_size[0] / image_data.shape[0])
        else:
            image_data = resize(image_data, max_size[1] / image_data.shape[1])

        return image_data

    @staticmethod
    def get_tiff_bitmap(filename, max_size=None):
        try:
            segment_file = tf.TiffFile(filename)

            if (len(segment_file.pages) > 0):
                # Get smallest resolution image

                data = segment_file.pages[-1].asarray()
                segment_file.close()

                if max_size is not None:
                    data = ImageThumbnail.resize_thumbnail(data, max_size)

                return wx.BitmapFromImage(wx.Image(wx.Size(data.shape[1], data.shape[0]), data))

            else:
                segment_file.close()
                return None
        except Exception:
            return None


    @staticmethod
    def get_ims_bitmap(filename, max_size=None):
        try:
            file = ImarisImage(filename)
            # Must get all channels of image to be compatible with wx.image
            data = [file.get_two_dim_data(file.resolutions-1, c=i) for i in range(file.get_channel_levels())]
            data = np.stack(data, axis=2)
            file.close_file()
            if max_size is not None:
                data = ImageThumbnail.resize_thumbnail(data, max_size)

            return wx.BitmapFromImage(wx.Image(wx.Size(data.shape[1], data.shape[0]), data))

        except Exception as e:
            import traceback
            print(traceback.format_exc())
            print("Error getting thumbnail from {0}".format(filename), str(e))
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