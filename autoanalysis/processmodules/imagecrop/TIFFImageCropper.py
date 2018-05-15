import logging
import os
from multiprocessing import Process
from os.path import basename, splitext, join
from skimage.filters import threshold_minimum
from PIL import Image
from PIL.TiffImagePlugin import AppendingTiffWriter as TIFF
import matplotlib
import matplotlib.pyplot as plt
import autoanalysis.processmodules.imagecrop.ImarisImage as I
from autoanalysis.processmodules.imagecrop.ImageSegmenter import ImageSegmenter

class TIFFImageCropper(object):
    """
    Implementation of the ImageCropper interface for the cropping of an inputted image over all dimensions such that the
    ImageSegmentation object applies to each x-y plane and the output is in TIFF format. 
    """

    def __init__(self,imgfile, border_factor, output_path, mem):
        self.maxmemoryavail = mem
        self.border_factor = border_factor
        self.imgfile = imgfile
        if not os.path.isdir(output_path):
            raise IOError('Invalid output directory: ', output_path)
        else:
            #create unique output directory from image filename
            filename = basename(imgfile)
            new_folder = splitext(filename)[0]
            image_folder = join(output_path, new_folder)
            if not os.path.isdir(image_folder):
                os.makedirs(image_folder)
            self.output_folder = image_folder
        #self.thresholdImage()
        self.segmentation = self.generateSegments()
        if (len(self.segmentation.segments) > 0):
            msg = 'SlideCropperAPI: run: Image segmentation created %d segments' % len(self.segmentation.segments)
            print(msg)
            logging.info(msg)
        else:
            raise ValueError('Segmentation failed')

    def thresholdImage(self):
        image = I.ImarisImage(self.imgfile).get_low_res_image()
        t0_min = threshold_minimum(image.value)
        bin_img = image.value > t0_min

        image.close_file()

    def generateSegments(self):
        image = I.ImarisImage(self.imgfile)
        segmentations = ImageSegmenter.segment_image(self.border_factor, image.get_multichannel_segmentation_image())
        image.close_file()
        return segmentations

    def crop_input_images(self):
        """
        Crops the inputted image against the given segmentation. All output files will be saved to the OutputPath
        :param input_image: An InputImage object. 
        :param image_segmentation: ImageSegmentation object with already added segments
        :param output_path: String output path must be a directory
        :return: 
        """
        done_list = 0

        ## Iterate through each bounding box
        for box_index in range(len(self.segmentation.segments)):
            done_list += TIFFImageCropper.crop_single_image(self.imgfile, self.segmentation, self.output_folder, box_index)
            # crop_process = Process(target=TIFFImageCropper.crop_single_image,
            #                        args=(self.imgfile, self.segmentation, self.output_folder, box_index))
            # pid_list.append(crop_process)
            # crop_process.start()
            # crop_process.join()  # Uncomment these two lines to allow single processing of ROIs. When commented
        # the program will give individual processes a ROI each: multiprocessing to use more CPU.
        return done_list

    @staticmethod
    def crop_single_image(input_path, image_segmentation, output_path, box_index):
        rtn = 0
        input_image = I.ImarisImage(input_path)
        for r_lev in range(input_image.get_resolution_levels()):
            # Get appropriately scaled ROI for the given dimension.
            resolution_dimensions = input_image.image_dimensions()[r_lev]
            segment = image_segmentation.get_scaled_segments(resolution_dimensions[1], resolution_dimensions[0])[box_index]

            # Use all z, c & t planes of the image.
            image_width, image_height, z, c, t = input_image.resolution_dimensions(r_lev)

            # image data with dimensions [c,x,y,z,t]
            #  TODO: check if enough memory on computer to load into disk self.maxmemoryavail
            image_data = input_image.get_euclidean_subset_in_resolution(r=r_lev,
                                                                        t=[0, t],
                                                                        c=[0, c],
                                                                        z=[0, z],
                                                                        y=[segment[1], segment[3]],
                                                                        x=[segment[0], segment[2]])

            # Only Save as AppendedTiff
            outputfile = join(output_path, basename(input_image.get_name()) + "_" + str(box_index + 1) + ".tiff")
            msg = "CropSingleImage: Generating cropped file: %s" % outputfile
            logging.debug(msg)
            print(msg)
            with TIFF(outputfile, False) as tf:
                try:
                    im = Image.fromarray(image_data[:, :, 0, :, 0], mode="RGB")
                    im.save(tf)
                    tf.newFrame()
                    im.close()
                    rtn = 1
                except Exception as e:
                    msg ='Image error:%s  Could not create multi-page TIFF: %s' % (outputfile, e.args[0])
                    print(msg)
                    logging.error(msg)
            del image_data
        msg = "Finished writing image %d to %s" % (box_index + 1, input_path)
        print(msg)
        logging.info(msg)
        return rtn

