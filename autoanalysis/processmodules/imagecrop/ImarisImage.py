import logging

import h5py
import numpy as np

SEGMENTATION_DIMENSION_MAX = 50000000

class ImarisImage(object):
    """
    Implementation of the InputImage interface for Imaris Bitplane files.
    IMARIS 5.5 File Format Description (IMS)
    http://open.bitplane.com/Default.aspx?tabid=268
    Typical chunk sizes are 128x128x64 or 256x256x16
    """

    # noinspection PyMissingConstructor
    def __init__(self, filename):
        """
        Constructor method
        :param filename: String path to the given image file. 
        """
        self.filename = filename

        try:
            self.file = h5py.File(self.filename, "r")
            self.resolutions = self.get_resolution_levels()
            self.info = self.get_info()
            self.chunks = self.get_chunks()
            # self.thumbnail = self.file['/Thumbnail/Data'] #('Data', <HDF5 dataset "Data": shape (256, 1024), type "|u1">)
            # resolution level to be used for segmentation
            self.segment_resolution = self.resolutions - 1  # self.resolutions -self._set_segmentation_res()
            msg = 'ImarisImage: H5 loaded: %s \n\t Resolution levels: %s (selected: %d)\n' % (
            self.filename, str(self.resolutions), self.segment_resolution)
            logging.info(msg)
            print(msg)

        except Exception as e:
            raise IOError(e)

    def get_info(self):
        info = self.file['/DataSetInfo']
        for item in info.items():
            print(item)
        return info

    def get_chunks(self):
        # Find if has chunks - for offsets
        dataset = self.file['/DataSet/ResolutionLevel 0/TimePoint 0/Channel 1/Data']
        if hasattr(dataset, 'chunks'):
            chunks = dataset.chunks
        else:
            chunks = None
        print('Chunks: ', chunks)
        return chunks

    def get_filename(self):
        """
        :return: the string filename of the image.  
        """
        return self.filename

    def get_name(self):
        """
        :return: the image name excluding the filepath associated with it. 
        """
        path = self.filename.split("/")
        return path[-1][:-4]

    # noinspection PyIncorrectDocstring
    def get_two_dim_data(self, r, z=0, c=0, t=0, region=None):
        """
        :param region: array of the form [x1, y1, x2, y2] for the 2D subregion desired. 0 implies the whole of 2D. 
        :return: ndarray of the given subset of the image as specified by the param. 
        """
        if ((r < self.resolutions) & (r >= 0) &
                (c < self.get_channel_levels()) & (c >= 0) &
                (t < self.get_time_size()) & (t >= 0)):
            dataset = self.file['/DataSet/ResolutionLevel {0}/TimePoint {1}/Channel {2}/Data'
                .format(r, t, c)]

            if region is not None and len(region) > 0:
                return dataset[z, region[0]:region[2], region[1]: region[3]]
            return dataset[z, :, :]


    def get_euclidean_subset_in_resolution(self, r, t, c, z, y, x):
        ### Note: xyczt is image_j format
        """
        :param r: Resolution Level integer 
        :param c: [c1, c2] of channel range indexing. c2>=c1 
        :param x: [x1, x2] of x dimension indexing. x2>=x1
        :param y: [y1, y2] of y dimension indexing.  y2>=y1
        :param z: [z1, z2] of z dimension indexing. z2>=z1
        :param t: [t1, t2] of t dimension indexing. t2>=t1
        :return: ndarray of up to 5 dimensions for the image data of a given resolution in shape [t,c,z,x,y]
        """
        time_subspace = None
        subspace = None
        for tPoint in range(t[0], t[1]):
            for cLevel in range(c[0], c[1]):

                path = "/DataSet/ResolutionLevel {0}/TimePoint {1}/Channel {2}/Data".format(r, tPoint, cLevel)
                # extract ROI from original image
                dataset = self.file[path][z[0]:z[1], y[0]:y[1], x[0]:x[1]]
                #print('File ROI: ', dataset.shape, 'y=', y, 'x=', x)
                dataset = np.expand_dims(dataset, axis=-1)
                if time_subspace is not None:  # 'time_subspace' in locals():
                    time_subspace = np.concatenate((time_subspace, dataset), axis=-1)

                else:
                    time_subspace = dataset

            time_subspace = np.expand_dims(time_subspace, axis=-1)
            #print('Tspace: ', time_subspace.shape)
            if subspace is not None:  # "subspace" in locals():
                subspace = np.concatenate((subspace, time_subspace), axis=-1)
            else:
                subspace = time_subspace
            #print('space: ', subspace.shape)
        return np.swapaxes(subspace, 0, 2)

    def get_low_res_image(self):
        """
        :return: A 2D image with the lowest resolutions at t=0, z=0, c=0
        """
        if (self.resolutions != 0) & (self.get_channel_levels() != 0):
            return self.file['/DataSet/ResolutionLevel {0}/TimePoint 0/Channel 0/Data'
                .format(self.resolutions - 1)]
        # Else return empty Array of shape (0,0)
        return [[]]

    def get_segment_res_image(self):
        """
        The default segment resolution is the resolution level less than the default size,SEGMENTATION_DIMENSION_MAX. 
        :return: a 2D image array at the file's segmentation resolution. 
        """
        if (self.resolutions != 0) & (self.get_channel_levels() != 0):
            return self.file['/DataSet/ResolutionLevel {0}/TimePoint 0/Channel 0/Data'
                .format(self.segment_resolution)]
        # Else return empty Array of shape (0,0)
        return [[]]

    def get_resolution_levels(self):
        """
        :return: the number of resolution levels of the image 
        """
        resolutions = len(self.file['/DataSet'])
        return resolutions if resolutions is not None else 0

    def get_channel_levels(self):
        """
        :return: the number of channels the image has. 
        """
        channels = len(self.file['/DataSet/ResolutionLevel 0/TimePoint 0/'])
        return channels if channels is not None else 0

    def get_time_size(self):
        times = len(self.file["/DataSet/ResolutionLevel 0"])
        return times if times is not None else 0

    def change_segment_res(self, r):
        """
        Changes the resolution level used during segmentation. 
        :return: null
        """
        if r >= 0 & r < self.resolutions:
            self.segment_resolution = r

    def _set_segmentation_res(self):
        image_dimensions = self.image_dimensions()
        resolution_level = 0
        while resolution_level < self.resolutions:
            shape = image_dimensions[resolution_level]
            if (shape[0] * shape[1]) <= SEGMENTATION_DIMENSION_MAX:
                break
            resolution_level += 1
        return resolution_level

    def resolution_dimensions(self, r):
        """
        Returns the size of each dimension for a given channel. Generally z,c,t will not change amongst resolutions. 
        :return: An array of the form [x, y, z, c, t]
        """
        base = "/DataSet/ResolutionLevel {0}/".format(r)

        t = len(self.file[base])
        c = len(self.file[base + "TimePoint 0/"])

        shape = self.file[base + "TimePoint 0/Channel 0/Data"].shape
        z = shape[0]
        y = shape[1]
        x = shape[2]
        return [x, y, z, c, t]

    def image_dimensions(self):
        """
        :return: a nested array of (x,y) sizes for all resolution levels by ascending resolution level number (0 first).
        """
        dimensions_stack = []
        lowest_path = '/DataSet/ResolutionLevel {0}/TimePoint 0/Channel 0/Data'.format(self.resolutions - 1)
        # if self.file[lowest_path].ndim == 3:
        #     y_index = 1
        #     x_index = 2
        # else:
        #     y_index = 0
        #     x_index = 1

        i = 0
        while i < self.resolutions:
            path = '/DataSet/ResolutionLevel {0}/TimePoint 0/Channel 0/Data'.format(i)
            dataset = self.file[path]
            y = dataset.shape[-2]  # self.file[path].shape[y_index]
            x = dataset.shape[-1]  # self.file[path].shape[x_index]
            dimensions_stack.append((y, x))
            i += 1
        return dimensions_stack

    def metadata_json(self):
        """
        :return: A JSON formatted structure of all the metadata for the image file. 
        """
        pass

    def metadata_from_path(self, path):
        """
        :param path: String representation of the nested path the the metadata. e.g. "metadata/timestamps/image_one" 
        :return: the value (singular or nested) from the metadata path specified. 
        """
        pass

    def close_file(self):
        """
        Closes the associated file of the image. Good memory practice before removing this object or reference. 
        :return: null
        """
        self.file.close()

    def get_multichannel_segmentation_image(self, xyres):
        """
        :return: A 2D image used for segmentation with separate channels as the first dimension on the stack (c,y,x)  
        """
        image_array = None
        if (self.resolutions != 0) & (self.get_channel_levels() != 0):
            for i in range(self.get_channel_levels()):
                if image_array is None:  # not 'image_array' in locals():
                    image_array = self.get_two_dim_data(self.segment_resolution, c=i)
                else:
                    #np.concatenate((image_array, self.get_two_dim_data(self.segment_resolution, c=i)), axis=0)
                    image_array = np.dstack((image_array, self.get_two_dim_data(self.segment_resolution, c=i)))
        seg_img_dims = tuple(round((xyres[self.segment_resolution] / xyres[0]) * x) for x in self.image_dimensions()[0])
        image_array = image_array[0:seg_img_dims[0],0:seg_img_dims[1],:]
        return image_array
