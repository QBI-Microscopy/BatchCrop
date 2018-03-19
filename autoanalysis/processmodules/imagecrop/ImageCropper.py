class ImageCropper(object):
    """
    Abstract Interface for the cropping of an inputted image over all dimensions such that the ImageSegmentation object
    applies to each x-y plane. 
    """
    @staticmethod
    def crop_input_images(InputImage, ImageSegmentation, OutputPath):
        """
        Crops the inputted image against the given segmentation. All output files will be saved to the OutputPath
        :param InputImage: An InputImage object. 
        :param ImageSegmentation: ImageSegmentation object 
        :param OutputPath: String output path must be a directory
        :return: 
        """
        raise NotImplementedError( "Method not implemented, but is in the ImageCropper interface" )
