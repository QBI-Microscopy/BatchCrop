import numpy as np
import tifffile as tf
import wx
import traceback
from autoanalysis.processmodules.imagecrop.ImarisImage import ImarisImage
from skimage.transform import resize

class ImageThumbnail(wx.StaticBitmap):
    """
    
    Abstract class. Use concrete Image type classes below. 
    
    """
    def __init__(self, parent, filename, max_size=None):
        self.filename = filename
        self.thumbnail = self.get_thumbnail(filename)

        if max_size is not None:
            ratio_h = max_size[0]/self.thumbnail.shape[0]
            thumb_w = max_size[0]
            thumb_h = int(self.thumbnail.shape[1] * ratio_h)
            img = resize(self.thumbnail,(thumb_w,thumb_h), preserve_range=True)
            self.thumbnail = img.astype(np.uint8)
        image = wx.Image(wx.Size(self.thumbnail.shape[1], self.thumbnail.shape[0]), self.thumbnail)
        super(ImageThumbnail, self).__init__(parent, bitmap=image.ConvertToBitmap())

    def get_thumbnail(self, filename):
        try:
            file = ImarisImage(filename)
            # Must get all channels of image to be compatible with wx.image
            c_range = [0]
            if file.get_channel_levels()==1:
                c_range = [0,0,0]
            elif file.get_channel_levels()==2:
                c_range = [0, 1, 0]
            elif file.get_channel_levels()==3:
                c_range = [0, 1, 2]
            elif file.get_channel_levels()>3:
                c_range = [0, 1, 2]

            thumbnail = [file.get_two_dim_data(file.resolutions-1, c=i) for i in c_range]

            thumbnail = np.stack(thumbnail, axis=2)

            file.close_file()
            return thumbnail

        except Exception as e:
            print(traceback.format_exc())
            print("Error: Thumbnail from {0}".format(filename), str(e))
            return None


    def resize_thumbnail(self,image_data, max_size):
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


# class IMSImageThumbnail(ImageThumbnail):
#
#     def __init__(self, parent, filename, max_size=None):
#         super(IMSImageThumbnail, self).__init__(parent, filename, max_size=max_size)
#
#     def get_image_data(self, filename):
#         try:
#             file = ImarisImage(filename)
#             if self.thumbnail is None:
#                 thumbnail = self.file['/Thumbnail']
#             else:
#                 thumbnail = self.thumbnail
#             # Must get all channels of image to be compatible with wx.image
#             # data = [file.get_two_dim_data(file.resolutions-1, c=i) for i in range(file.get_channel_levels())]
#             # data = np.stack(data, axis=2)
#             file.close_file()
#             return thumbnail
#
#         except Exception as e:
#             import traceback
#             print(traceback.format_exc())
#             print("Error getting thumbnail from {0}".format(filename), str(e))
#             return None



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