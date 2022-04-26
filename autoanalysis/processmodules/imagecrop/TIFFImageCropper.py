import logging
import os
from os.path import basename, splitext, join, exists

import math

import psutil
from PIL import Image
from PIL.TiffImagePlugin import AppendingTiffWriter as TIFF
from skimage.filters import threshold_minimum
import tifffile

import autoanalysis.processmodules.imagecrop.ImarisImage as I
from autoanalysis.processmodules.imagecrop.ImageSegmenter import ImageSegmenter


class TIFFImageCropper(object):
    """
    Implementation of the ImageCropper interface for the cropping of an inputted image over all dimensions such that the
    ImageSegmentation object applies to each x-y plane and the output is in TIFF format. 
    """

    def __init__(self, imgfile, border_factor, output_path, memmax, lightbg, darkbg, offset, resolution, xyres):
        self.maxmemory = memmax
        self.lightbg = lightbg
        self.darkbg = darkbg
        self.border_factor = border_factor
        self.offset = offset
        self.resolution = resolution
        self.xyres = xyres
        self.imgfile = imgfile
        try:
            self.image = I.ImarisImage(self.imgfile)
            if not os.path.isdir(output_path):
                raise IOError('Invalid output directory: ', output_path)
            else:
                # create unique output directory from image filename
                filename = basename(imgfile)
                new_folder = splitext(filename)[0]
                image_folder = join(output_path, new_folder)
                if not os.path.isdir(image_folder):
                    os.makedirs(image_folder)

                self.output_folder = image_folder
            # self.thresholdImage()
            self.segmentation = self.generateSegments()
            if (len(self.segmentation.segments) > 0):
                msg = 'SlideCropperAPI: run: Image segmentation created %d segments' % len(self.segmentation.segments)
                print(msg)
                logging.info(msg)
            else:
                raise ValueError('Segmentation failed')
            #self.xyres = ...
        except Exception as e:
            raise (e)

    def thresholdImage(self):
        image = I.ImarisImage(self.imgfile).get_low_res_image()
        t0_min = threshold_minimum(image.value)
        binary_img = image.value > t0_min
        image.close_file()
        return binary_img

    def generateSegments(self):
        # if self.image is None:
        #     image = I.ImarisImage(self.imgfile)
        # else:
        # image = self.image
        segmentations = ImageSegmenter.segment_image(self.image.get_multichannel_segmentation_image(self.xyres), self.lightbg,
                                                     self.darkbg)
        # if image is not None:
        #     image.close_file()
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
        try:
            ## Iterate through each bounding box

            ## Check to see if all bounding boxes are smaller than 2Gpx and trigger reduced resolution if any >
            largesections = False
            input_image = self.image
            r_lev = 0
            dims = input_image.image_dimensions()
            for box_index in range(len(self.segmentation.segments)):
                resolution_dimensions = dims[r_lev]
                segment = self.segmentation.get_scaled_segments(resolution_dimensions[0], resolution_dimensions[1],
                                                                r_lev, len(dims), self.border_factor, self.offset,
                                                                input_image.chunks)[box_index]
                if float((segment[2] - segment[0])) * float((segment[3] - segment[1])) > 2000000000:
                    r_lev = r_lev + 1
                    largesections = True
                    msg = "Cannot crop image with size >2Gpx, decreasing resoltion by one"
                    logging.info(msg)
                    print(msg)

            new_r_lev = r_lev



            for box_index in range(len(self.segmentation.segments)):
                # done_list += self.crop_single_image(self.imgfile, self.segmentation, self.output_folder, box_index,self.maxmemory,self.border_factor,self.offset)
                done_list += self.crop_single_image(box_index,new_r_lev)
            # the program will give individual processes a ROI each: multiprocessing to use more CPU.
        except Exception as e:
            raise e
        return done_list

    def crop_single_image(self, box_index,maxrlev):
        rtn = 0
        input_image = self.image  # I.ImarisImage(input_path)

        dims = input_image.image_dimensions()
        # TODO only capture every second use:
        # for r_lev in range(input_image.get_resolution_levels(),2):

        if self.resolution == 'High':
            r_lev = maxrlev
            outputfile = join(self.output_folder, basename(input_image.get_name()) + "_" + str(box_index + 1) + ".tiff")
            if exists(outputfile):
                os.remove(outputfile)

            # for r_lev in range(input_image.get_resolution_levels())[0:1]:
            # Get appropriately scaled ROI for the given dimension.
            resolution_dimensions = dims[r_lev]
            segment = self.segmentation.get_scaled_segments(resolution_dimensions[0], resolution_dimensions[1],
                                                            r_lev, len(dims), self.border_factor, self.offset,
                                                            input_image.chunks)[box_index]
            print('Segment:', segment)

            image_width, image_height, z, c, t = input_image.resolution_dimensions(r_lev)
            msg = 'Image: w=%d,h=%d,z=%d,c=%d,t=%d  segment dims: %d x %d' % (
                image_width, image_height, z, c, t, segment[3] - segment[1], segment[2] - segment[0])
            print(msg)
            logging.info(msg)
            if float((segment[2] - segment[0])) * float((segment[3] - segment[1])) > 2000000000:
                r_lev = r_lev + 1
                msg = "Cannot crop image with size >2Gpx, decreasing resolution by one"
                logging.info(msg)
                print(msg)

            segment = self.segmentation.get_scaled_segments(resolution_dimensions[0], resolution_dimensions[1],
                                                                r_lev, len(dims), self.border_factor, self.offset,
                                                                input_image.chunks)[box_index]
            print('Segment:', segment)
            # Use all z, c & t planes of the image.
            image_width, image_height, z, c, t = input_image.resolution_dimensions(r_lev)
            msg = 'Image: w=%d,h=%d,z=%d,c=%d,t=%d  segment dims: %d x %d' % (
                image_width, image_height, z, c, t, segment[3] - segment[1], segment[2] - segment[0])
            print(msg)
            logging.info(msg)

            # image data with dimensions [c,x,y,z,t]
            #  Check if enough memory on computer to load into disk



            # IF IT IS A MULTI-Z LEVEL STACK SPLIT INTO MULTIPLE CHANNELS WITH TIFF STACK PER CHANNEL APPEND TIFF

            if z > 1:
                for channs in range(c):

                    outputfile = join(self.output_folder,
                                      basename(input_image.get_name()) + "_" + str(box_index + 1) + "Channel_" + str(channs) + ".tiff")

                    mempercent = psutil.virtual_memory().percent
                    if mempercent < self.maxmemory:

                        image_data = input_image.get_euclidean_subset_in_resolution(r=r_lev,
                                                                                    t=[0, t],
                                                                                    c=[channs,channs+1],
                                                                                    z=[0, z],
                                                                                    y=[segment[1], segment[3]],
                                                                                    x=[segment[0], segment[2]])

                        # Appended Tiff
                        msg = "CropSingleImage: Writing file: %s [level %d]" % (outputfile, r_lev)
                        logging.info(msg)
                        print(msg)
                        with TIFF(outputfile, False) as tf:

                            try:
                                for zplanes in range(z):
                                    im = Image.fromarray(image_data[:, :, zplanes, 0, 0], mode="L")
                                    im.save(tf,resolution=round(self.xyres[r_lev]), resolution_unit=3)
                                    tf.newFrame()
                                    im.close()
                                    rtn = 1

                            except Exception as e:
                                msg = 'Image error:%s  Could not create multi-page TIFF: %s' % (
                                outputfile, e.args[0])
                                print(msg)
                                logging.error(msg)

                        del image_data

                    else:
                        raise OSError('Memory insufficient to generate images')

            else:
                # image data with dimensions [c,x,y,z,t]
                #  Check if enough memory on computer to load into disk
                mempercent = psutil.virtual_memory().percent
                if mempercent < self.maxmemory:

                    image_data = input_image.get_euclidean_subset_in_resolution(r=r_lev,
                                                                                t=[0, t],
                                                                                c=[0, c],
                                                                                z=[0, z],
                                                                                y=[segment[1], segment[3]],
                                                                                x=[segment[0], segment[2]])

                    # Appended Tiff
                    msg = "CropSingleImage: Writing file: %s [level %d]" % (outputfile, r_lev)
                    logging.info(msg)
                    print(msg)
                    with TIFF(outputfile, False) as tf:
                        if c == 3:
                            if image_data.size < 2000000000:
                                try:
                                    im = Image.fromarray(image_data[:, :, 0, :, 0], mode="RGB")
                                    im.save(tf,resolution=round(self.xyres[r_lev]),resolution_unit=3)
                                    # tf.newFrame()
                                    im.close()
                                    rtn = 1

                                except Exception as e:
                                    msg = 'Image error:%s  Could not create multi-page TIFF: %s' % (
                                    outputfile, e.args[0])
                                    print(msg)
                                    logging.error(msg)

                            else:
                                try:
                                    for chan in range(c):
                                        im = Image.fromarray(image_data[:, :, 0, chan, 0], mode="L")
                                        im.save(tf,resolution=round(self.xyres[r_lev]),resolution_unit=3)
                                        tf.newFrame()
                                        im.close()
                                        rtn = 1

                                except Exception as e:
                                    msg = 'Image error:%s  Could not create multi-page TIFF: %s' % (
                                    outputfile, e.args[0])
                                    print(msg)
                                    logging.error(msg)


                        else:
                            if True:
                                try:
                                    for chan in range(c):
                                        im = Image.fromarray(image_data[:, :, 0, chan, 0], mode="L")
                                        im.save(tf,resolution=round(self.xyres[r_lev]), resolution_unit=3)
                                        tf.newFrame()
                                        im.close()
                                        rtn = 1

                                except Exception as e:
                                    msg = 'Image error:%s  Could not create multi-page TIFF: %s' % (
                                    outputfile, e.args[0])
                                    print(msg)
                                    logging.error(msg)

                    del image_data

                else:
                    raise OSError('Memory insufficient to generate images')

        elif self.resolution == 'Low':
            r_lev = 3
            outputfile = join(self.output_folder,
                              basename(input_image.get_name()) + "_" + str(box_index + 1) + "_1.tiff")
            if exists(outputfile):
                os.remove(outputfile)

            # for r_lev in range(input_image.get_resolution_levels())[0:1]:
            # Get appropriately scaled ROI for the given dimension.
            resolution_dimensions = dims[r_lev]
            segment = self.segmentation.get_scaled_segments(resolution_dimensions[0], resolution_dimensions[1],
                                                            r_lev, len(dims), self.border_factor, self.offset,
                                                            input_image.chunks)[box_index]
            print('Segment:', segment)
            # Use all z, c & t planes of the image.
            image_width, image_height, z, c, t = input_image.resolution_dimensions(r_lev)
            msg = 'Image: w=%d,h=%d,z=%d,c=%d,t=%d  segment dims: %d x %d' % (
                image_width, image_height, z, c, t, segment[3] - segment[1], segment[2] - segment[0])
            print(msg)
            logging.info(msg)
            # image data with dimensions [c,x,y,z,t]
            #  Check if enough memory on computer to load into disk
            if z > 1:
                for channs in range(c):

                    outputfile = join(self.output_folder,
                                      basename(input_image.get_name()) + "_" + str(box_index + 1) + "Channel_" + str(
                                          channs) + ".tiff")

                    mempercent = psutil.virtual_memory().percent
                    if mempercent < self.maxmemory:

                        image_data = input_image.get_euclidean_subset_in_resolution(r=r_lev,
                                                                                    t=[0, t],
                                                                                    c=[channs, channs+1],
                                                                                    z=[0, z],
                                                                                    y=[segment[1], segment[3]],
                                                                                    x=[segment[0], segment[2]])

                        # Appended Tiff
                        msg = "CropSingleImage: Writing file: %s [level %d]" % (outputfile, r_lev)
                        logging.info(msg)
                        print(msg)
                        with TIFF(outputfile, False) as tf:

                            try:
                                for zplanes in range(z):
                                    im = Image.fromarray(image_data[:, :, zplanes, 0, 0], mode="L")
                                    im.save(tf,resolution=round(self.xyres[r_lev]),resolution_unit=3)
                                    tf.newFrame()
                                    im.close()
                                    rtn = 1

                            except Exception as e:
                                msg = 'Image error:%s  Could not create multi-page TIFF: %s' % (
                                    outputfile, e.args[0])
                                print(msg)
                                logging.error(msg)

                        del image_data

                    else:
                        raise OSError('Memory insufficient to generate images')

            else:
                # image data with dimensions [c,x,y,z,t]
                #  Check if enough memory on computer to load into disk
                mempercent = psutil.virtual_memory().percent
                if mempercent < self.maxmemory:

                    image_data = input_image.get_euclidean_subset_in_resolution(r=r_lev,
                                                                                t=[0, t],
                                                                                c=[0, c],
                                                                                z=[0, z],
                                                                                y=[segment[1], segment[3]],
                                                                                x=[segment[0], segment[2]])

                    # Appended Tiff
                    msg = "CropSingleImage: Writing file: %s [level %d]" % (outputfile, r_lev)
                    logging.info(msg)
                    print(msg)
                    with TIFF(outputfile, False) as tf:
                        if c == 3:
                            if image_data.size < 2000000000:
                                try:
                                    im = Image.fromarray(image_data[:, :, 0, :, 0], mode="RGB")
                                    im.save(tf,resolution=round(self.xyres[r_lev]),resolution_unit=3)
                                    # tf.newFrame()
                                    im.close()
                                    rtn = 1
                                except Exception as e:
                                    msg = 'Image error:%s  Could not create multi-page TIFF: %s' % (
                                        outputfile, e.args[0])
                                    print(msg)
                                    logging.error(msg)

                            else:
                                try:
                                    for chan in range(c):
                                        im = Image.fromarray(image_data[:, :, 0, chan, 0], mode="L")
                                        im.save(tf,resolution=round(self.xyres[r_lev]),resolution_unit=3)
                                        tf.newFrame()
                                        im.close()
                                        rtn = 1

                                except Exception as e:
                                    msg = 'Image error:%s  Could not create multi-page TIFF: %s' % (
                                        outputfile, e.args[0])
                                    print(msg)
                                    logging.error(msg)

                        else:
                            if True:
                                try:
                                    for chan in range(c):
                                        im = Image.fromarray(image_data[:, :, 0, chan, 0], mode="L")
                                        im.save(tf,resolution=round(self.xyres[r_lev]),resolution_unit=3)
                                        tf.newFrame()
                                        im.close()
                                        rtn = 1

                                except Exception as e:
                                    msg = 'Image error:%s  Could not create multi-page TIFF: %s' % (
                                        outputfile, e.args[0])
                                    print(msg)
                                    logging.error(msg)

                    del image_data

                else:
                    raise OSError('Memory insufficient to generate images')

        elif self.resolution == 'Both':
            r_lev = maxrlev
            outputfile = join(self.output_folder, basename(input_image.get_name()) + "_" + str(box_index + 1) + ".tiff")
            if exists(outputfile):
                os.remove(outputfile)
            # for r_lev in range(input_image.get_resolution_levels())[0:1]:
            # Get appropriately scaled ROI for the given dimension.

            resolution_dimensions = dims[r_lev]
            segment = self.segmentation.get_scaled_segments(resolution_dimensions[0], resolution_dimensions[1],
                                                            r_lev, len(dims), self.border_factor, self.offset,
                                                            input_image.chunks)[box_index]
            print('Segment:', segment)
            # Use all z, c & t planes of the image.
            image_width, image_height, z, c, t = input_image.resolution_dimensions(r_lev)
            msg = 'Image: w=%d,h=%d,z=%d,c=%d,t=%d  segment dims: %d x %d' % (
                image_width, image_height, z, c, t, segment[3] - segment[1], segment[2] - segment[0])

            print(msg)
            logging.info(msg)
            if float((segment[2] - segment[0])) * float((segment[3] - segment[1])) > 2000000000:
                r_lev = r_lev + 1
                msg = "Cannot crop image with size >2Gpx, decreasing resoltion by one"
                print(msg)
                logging.info(msg)

            segment = self.segmentation.get_scaled_segments(resolution_dimensions[0], resolution_dimensions[1],
                                                            r_lev, len(dims), self.border_factor, self.offset,
                                                            input_image.chunks)[box_index]

            print('Segment:', segment)
            # Use all z, c & t planes of the image.
            image_width, image_height, z, c, t = input_image.resolution_dimensions(r_lev)
            msg = 'Image: w=%d,h=%d,z=%d,c=%d,t=%d  segment dims: %d x %d' % (
                image_width, image_height, z, c, t, segment[3] - segment[1], segment[2] - segment[0])
            print(msg)
            logging.info(msg)
            # image data with dimensions [c,x,y,z,t]
            #  Check if enough memory on computer to load into disk

                # IF IT IS A MULTI-Z LEVEL STACK SPLIT INTO MULTIPLE CHANNELS WITH TIFF STACK PER CHANNEL APPEND TIFF

            if z > 1:
                for channs in range(c):
                    outputfile = join(self.output_folder,
                                      basename(input_image.get_name()) + "_" + str(
                                          box_index + 1) + "Channel_" + str(channs) + ".tiff")

                    mempercent = psutil.virtual_memory().percent
                    if mempercent < self.maxmemory:
                        image_data = input_image.get_euclidean_subset_in_resolution(r=r_lev,
                                                                                    t=[0, t],
                                                                                    c=[channs,channs+1],
                                                                                    z=[0, z],
                                                                                    y=[segment[1], segment[3]],
                                                                                    x=[segment[0], segment[2]])

                        # Appended Tiff
                        msg: str = "CropSingleImage: Writing file: %s [level %d]" % (outputfile, r_lev)
                        logging.info(msg)
                        print(msg)
                        with TIFF(outputfile, False) as tf:
                            try:
                                for zplanes in range(z):
                                    im = Image.fromarray(image_data[:, :, zplanes, 0, 0], mode="L")
                                    im.save(tf,resolution=round(self.xyres[r_lev]),resolution_unit=3)
                                    tf.newFrame()
                                    im.close()
                                    rtn = 1

                            except Exception as e:
                                msg = 'Image error:%s  Could not create multi-page TIFF: %s' % (
                                    outputfile, e.args[0])
                                print(msg)
                                logging.error(msg)

                        del image_data

                    else:
                        raise OSError('Memory insufficient to generate images')

            else:
                mempercent = psutil.virtual_memory().percent
                if mempercent < self.maxmemory:
                    image_data = input_image.get_euclidean_subset_in_resolution(r=r_lev,
                                                                                t=[0, t],
                                                                                c=[0, c],
                                                                                z=[0, z],
                                                                                y=[segment[1], segment[3]],
                                                                                x=[segment[0], segment[2]])

                    # Appended Tiff
                    msg = "CropSingleImage: Writing file: %s [level %d]" % (outputfile, r_lev)
                    logging.info(msg)
                    print(msg)
                    with TIFF(outputfile, False) as tf:
                        if c == 3:
                            if image_data.size<2000000000:
                                try:
                                    im = Image.fromarray(image_data[:, :, 0, :, 0], mode="RGB")
                                    im.save(tf,resolution=round(self.xyres[r_lev]),resolution_unit=3)
                                    # tf.newFrame()
                                    im.close()
                                    rtn = 1

                                except Exception as e:
                                    msg = 'Image error:%s  Could not create multi-page TIFF: %s' % (outputfile, e.args[0])
                                    print(msg)
                                    logging.error(msg)

                            else:
                                try:
                                    for chan in range(c):
                                        im = Image.fromarray(image_data[:, :, 0, chan, 0], mode="L")
                                        im.save(tf,resolution=round(self.xyres[r_lev]),resolution_unit=3)
                                        tf.newFrame()
                                        im.close()
                                        rtn = 1

                                except Exception as e:
                                    msg = 'Image error:%s  Could not create multi-page TIFF: %s' % (outputfile, e.args[0])
                                    print(msg)
                                    logging.error(msg)

                    with tifffile.TiffWriter(outputfile, bigtiff=True, imagej=True) as tif:
                        if True:
                            try:
                                for chan in range(c):
                                    # im = Image.fromarray(image_data[:, :, 0, chan, 0], mode="L")
                                    tif.save(image_data[:, :, 0, chan, 0], photometric='minisblack',
                                             contiguous=True, dtype='uint8', resolution=(
                                        float(self.xyres[r_lev] / 10000), float(self.xyres[r_lev]) / 10000),
                                             metadata={'DimensionOrder': 'XYZTC',
                                                       'spacing': 10000 / self.xyres[r_lev], 'unit': 'um'})
                                    # im.close()
                                    rtn = 1
                            except Exception as e:
                                msg = 'Image error:%s  Could not create multi-page TIFF: %s' % (
                                outputfile, e.args[0])
                                print(msg)
                                logging.error(msg)

                    del image_data

                else:
                    raise OSError('Memory insufficient to generate images')

            r_lev = 3
            outputfile = join(self.output_folder,
                              basename(input_image.get_name()) + "_" + str(box_index + 1) + "_1.tiff")
            if exists(outputfile):
                os.remove(outputfile)

            # for r_lev in range(input_image.get_resolution_levels())[0:1]:
            # Get appropriately scaled ROI for the given dimension.
            resolution_dimensions = dims[r_lev]
            segment = self.segmentation.get_scaled_segments(resolution_dimensions[0], resolution_dimensions[1],
                                                            r_lev, len(dims), self.border_factor, self.offset,
                                                            input_image.chunks)[box_index]
            print('Segment:', segment)
            # Use all z, c & t planes of the image.
            image_width, image_height, z, c, t = input_image.resolution_dimensions(r_lev)
            msg = 'Image: w=%d,h=%d,z=%d,c=%d,t=%d  segment dims: %d x %d' % (
                image_width, image_height, z, c, t, segment[3] - segment[1], segment[2] - segment[0])
            print(msg)
            logging.info(msg)
            # image data with dimensions [c,x,y,z,t]
            #  Check if enough memory on computer to load into disk
            if z > 1:
                for channs in range(c):

                    outputfile = join(self.output_folder,
                                      basename(input_image.get_name()) + "_" + str(box_index + 1) + "Channel_" + str(
                                          channs) + ".tiff")

                    mempercent = psutil.virtual_memory().percent
                    if mempercent < self.maxmemory:

                        image_data = input_image.get_euclidean_subset_in_resolution(r=r_lev,
                                                                                    t=[0, t],
                                                                                    c=[channs,channs+1],
                                                                                    z=[0, z],
                                                                                    y=[segment[1], segment[3]],
                                                                                    x=[segment[0], segment[2]])

                        # Appended Tiff
                        msg = "CropSingleImage: Writing file: %s [level %d]" % (outputfile, r_lev)
                        logging.info(msg)
                        print(msg)
                        with TIFF(outputfile, False) as tf:

                            try:
                                for zplanes in range(z):
                                    im = Image.fromarray(image_data[:, :, zplanes, 0, 0], mode="L")
                                    im.save(tf,resolution=round(self.xyres[r_lev]),resolution_unit=3)
                                    tf.newFrame()
                                    im.close()
                                    rtn = 1
                            except Exception as e:
                                msg = 'Image error:%s  Could not create multi-page TIFF: %s' % (
                                    outputfile, e.args[0])
                                print(msg)
                                logging.error(msg)

                        del image_data

                    else:
                        raise OSError('Memory insufficient to generate images')

            else:
                # image data with dimensions [c,x,y,z,t]
                #  Check if enough memory on computer to load into disk
                mempercent = psutil.virtual_memory().percent
                if mempercent < self.maxmemory:

                    image_data = input_image.get_euclidean_subset_in_resolution(r=r_lev,
                                                                                t=[0, t],
                                                                                c=[0, c],
                                                                                z=[0, z],
                                                                                y=[segment[1], segment[3]],
                                                                                x=[segment[0], segment[2]])

                    # Appended Tiff
                    msg = "CropSingleImage: Writing file: %s [level %d]" % (outputfile, r_lev)
                    logging.info(msg)
                    print(msg)
                    with TIFF(outputfile, False) as tf:
                        if c == 3:
                            if image_data.size < 2000000000:
                                try:
                                    im = Image.fromarray(image_data[:, :, 0, :, 0], mode="RGB")
                                    im.save(tf,resolution=round(self.xyres[r_lev]),resolution_unit=3)
                                    # tf.newFrame()
                                    im.close()
                                    rtn = 1

                                except Exception as e:
                                    msg = 'Image error:%s  Could not create multi-page TIFF: %s' % (
                                        outputfile, e.args[0])
                                    print(msg)
                                    logging.error(msg)

                            else:
                                try:
                                    for chan in range(c):
                                        im = Image.fromarray(image_data[:, :, 0, chan, 0], mode="L")
                                        im.save(tf,resolution=round(self.xyres[r_lev]),resolution_unit=3)
                                        tf.newFrame()
                                        im.close()
                                        rtn = 1

                                except Exception as e:
                                    msg = 'Image error:%s  Could not create multi-page TIFF: %s' % (
                                        outputfile, e.args[0])
                                    print(msg)
                                    logging.error(msg)


                        else:
                            if True:
                                try:
                                    for chan in range(c):
                                        im = Image.fromarray(image_data[:, :, 0, chan, 0], mode="L")
                                        im.save(tf,resolution=round(self.xyres[r_lev]),resolution_unit=3)
                                        tf.newFrame()
                                        im.close()
                                        rtn = 1

                                except Exception as e:
                                    msg = 'Image error:%s  Could not create multi-page TIFF: %s' % (
                                        outputfile, e.args[0])
                                    print(msg)
                                    logging.error(msg)
                    del image_data

                else:
                    raise OSError('Memory insufficient to generate images')

        msg = "Finished writing image %d from %s" % (box_index + 1, self.imgfile)
        print(msg)
        logging.info(msg)
        return rtn
