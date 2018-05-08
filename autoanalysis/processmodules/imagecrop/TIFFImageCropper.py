import logging
import os
from multiprocessing import Process
from os.path import basename, splitext, join

from PIL import Image
from PIL.TiffImagePlugin import AppendingTiffWriter as TIFF

import autoanalysis.processmodules.imagecrop.ImarisImage as I


#DEFAULT_LOGGING_FILEPATH = "SlideCropperLog.txt"

class TIFFImageCropper(object):
    """
    Implementation of the ImageCropper interface for the cropping of an inputted image over all dimensions such that the
    ImageSegmentation object applies to each x-y plane and the output is in TIFF format. 
    """

    @staticmethod
    def crop_input_images(input_path, image_segmentation, output_path):
        """
        Crops the inputted image against the given segmentation. All output files will be saved to the OutputPath
        :param input_image: An InputImage object. 
        :param image_segmentation: ImageSegmentation object with already added segments
        :param output_path: String output path must be a directory
        :return: 
        """
        if not os.path.isdir(output_path):
            return None
        else:
            filename = basename(input_path) #(input_path.split("/")[-1]).split(".")[0]
            new_folder = splitext(filename)[0]
            image_folder = join(output_path, new_folder)
            if not os.path.isdir(image_folder):
                os.makedirs(image_folder)

        pid_list = []

        ## Iterate through each bounding box
        for box_index in range(len(image_segmentation.segments)):
            crop_process = Process(target=TIFFImageCropper.crop_single_image,
                                   args=(input_path, image_segmentation, image_folder, box_index))
            pid_list.append(crop_process)
            crop_process.start()
            crop_process.join()  # Uncomment these two lines to allow single processing of ROIs. When commented
        return           # the program will give individual processes a ROI each: multiprocessing to use more CPU.


    @staticmethod
    def crop_single_image(input_path, image_segmentation, output_path, box_index):

        input_image = I.ImarisImage(input_path)
        for r_lev in range(input_image.get_resolution_levels()):
            # Get appropriately scaled ROI for the given dimension.
            resolution_dimensions = input_image.image_dimensions()[r_lev]
            segment = image_segmentation.get_scaled_segments(resolution_dimensions[1], resolution_dimensions[0])[
                box_index]

            # Use all z, c & t planes of the image.
            image_width, image_height, z, c, t = input_image.resolution_dimensions(r_lev)

            # image data with dimensions [c,x,y,z,t]
            #  TODO: check if enough memory on computer to load into disk
            image_data = input_image.get_euclidean_subset_in_resolution(r=r_lev,
                                                                        t=[0, t],
                                                                        c=[0, c],
                                                                        z=[0, z],
                                                                        y=[segment[1], segment[3]],
                                                                        x=[segment[0], segment[2]])

            # Only Save as AppendedTiff
            # TODO Provide option to save back to inputdir? if so,
            outputfile = join(output_path, basename(input_image.get_name()) + "_" + str(box_index) + "_full.tiff")
            print("Generating file: ", outputfile)
            with TIFF(outputfile, False) as tf:
                try:
                    im = Image.fromarray(image_data[:, :, 0, :, 0], mode="RGB")
                    im.save(tf)
                    tf.newFrame()
                    im.close()
                except Exception as e:
                    logging.error("Could not create multi-page TIFF. Couldn't compile file: {}".format(str(e)))
            del image_data
        logging.info("Finished saving image %d from %s.", box_index, input_path)

