SEGMENTATION_DIMENSION_MAX = 2000

class InputImage(object):
    """
    Abstract Interface for accessing multidimensional image files and their associated metadata. This interface supports 
    usage for image formats with at most five dimensions [x,y,z,c,t] and/or multiple pre-stored resolutions. The
    following params & definitions are the default throughout the interface for all methods unless otherwise specified:
        -c = channel/s (at least one) 
        -r = resolution levels (at least one)
        -x = x plane of the images
        -y = y plane of the images
        -z = z plane of the images
        -t = time plane of the images
        -region = refers to the subsets of the 2D euclidean space previously refined by z, c & t. 
    
    """


    def __init__(self, filename):
        """
        Constructor method
        :param filename: String path to the given image file. 
        """
        raise NotImplementedError( "Method not implemented, but is in the InputImage interface" )

    def get_filename(self):
        """
        :return: the string filename of the image.  
        """
        raise NotImplementedError( "Method not implemented, but is in the InputImage interface" )

    @staticmethod
    def get_extension(file_path):
        """
        :return: The extension of the inputted file. 
        """
        from os.path import splitext
        path_split = splitext(file_path)
        #path_split = file_path.split(".")
        return path_split[1]

    def get_two_dim_data(self, r, z=0, c=0, t=0, region=-1):
        """
        :param region: array of the form [x1, y1, x2, y2] for the 2D subregion desired. -1 implies the whole of 2D. 
        :return: ndarray of the given subset of the image as specified by the param. 
        """
        raise NotImplementedError( "Method not implemented, but is in the InputImage interface" )

    def get_euclidean_subset_in_resolution(self, r, c, x, y, z, t):
        """
        :param r: Resolution Level integer 
        :param c: [c1, c2] of channel ranges. c2>=c1 
        :param x: [x1, x2] of x dimension. x2>=x1
        :param y: [y1, y2] of y dimension. y2>=y1
        :param z: [z1, z2] of z dimension. z2>=z1
        :param t: [t1, t2] of t dimension. t2>=t1
        :return: ndarray of up to 5 dimensions for the image data of a given resolution
        """
        raise NotImplementedError( "Method not implemented, but is in the InputImage interface" )

    def get_low_res_image(self):
        """
        :return: A 2D image with the lowest resolutions at t=0, z=0, c=0
        """
        raise NotImplementedError( "Method not implemented, but is in the InputImage interface" )

    def get_segment_res_image(self):
        """
        The default segment resolution is the resolution level less than the default,SEGMENTATION_DIMENSION_MAX. 
        :return: a 2D array of the image at the segmentation resolution. 
        """
        raise NotImplementedError( "Method not implemented, but is in the InputImage interface" )

    def get_resolution_levels(self):
        """
        :return: the number of resolution levels of the image 
        """
        raise NotImplementedError( "Method not implemented, but is in the InputImage interface" )

    def get_channel_levels(self):
        """
        :return: the number of channels the image has. 
        """
        raise NotImplementedError( "Method not implemented, but is in the InputImage interface" )


    def change_segment_res(self, r):
        """
        Changes the resolution level used during segmentation. 
        :return: null
        """
        raise NotImplementedError( "Method not implemented, but is in the InputImage interface" )

    def resolution_dimensions(self, r):
        """
        Returns the size of each dimension for a given channel. Generally z,c,t will not change amongst resolutions. 
        :return: An array of the form [x, y, z, c, t]
        """
        raise NotImplementedError( "Method not implemented, but is in the InputImage interface" )

    def image_dimensions(self):
        """
        :return: a nested array of (x,y) sizes for all resolution levels by ascending resolution level number (0 first).
        """
        raise NotImplementedError( "Method not implemented, but is in the InputImage interface" )

    def metadata_json(self):
        """
        :return: A JSON formatted structure of all the metadata for the image file. 
        """
        raise NotImplementedError( "Method not implemented, but is in the InputImage interface" )

    def metadata_from_path(self, path):
        """
        :param path: String representation of the nested path the the metadata. e.g. "metadata/timestamps/image_one" 
        :return: the value (singular or nested) from the metadata path specified. 
        """
        raise NotImplementedError( "Method not implemented, but is in the InputImage interface" )

    def close_file(self):
        """
        Closes the associated file of the image.
        :return: null
        """
        raise NotImplementedError( "Method not implemented, but is in the InputImage interface" )
