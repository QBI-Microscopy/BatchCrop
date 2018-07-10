import logging

import numpy as np
import scipy.ndimage as ndimage
from skimage.morphology import square
from skimage.exposure import adjust_gamma
from skimage.filters import threshold_minimum, threshold_otsu, threshold_triangle, threshold_mean, threshold_isodata, sobel, rank
from autoanalysis.processmodules.imagecrop.ImageSegmentation import ImageSegmentation

K_Clusters = 2
BGPCOUNT = 80  # Background Pixel Count: Pixel length of the squares to be used in the image corners to be considered
# background
SENSITIVITY_THRESHOLD = .01  # Sensitivity for K means iterating. smaller threshold means a more accurate threshold.
MAX_NOISE_AREA = 1000  # Max area (pixels) of a slice for it to be still considered noise

DELTAX, DELTAY = (0, 0)  # (20, 50) # How close in both directions a slice can be to another to be considered the same image
IMAGEX, IMAGEY = (3000, 1200)  # Size of image to use when segmenting the image.


class ImageSegmenter(object):
    """
    Static Methods to segment an 2D image with multiple channels. 
    Primary method segment_image() uses the following implementation: 
        1. Thresholding the image to find a binary image through a k means clustering on the histogram. 
        2. Morpological opening(erosion then dilation) for noise reduction
         and detail blurring (& joining relevant pixels back together) . 
        3. Detect bounding boxes for connected foreground pixels
        4. Get image bound box by reconstructing sub-boxes (those from step 3)
    """

    @staticmethod
    def segment_image(image_array, lightbg, darkbg):
        """
        Segments the image by means of mathematical morphology.
        :param image_array: a 2D image array to be cropped with an optional channel dimension Shape in form (c,y,x)
         where c >=1
        :return: an ImageSegmentation object 
        """
        # Step 1
        # binary_image = ImageSegmenter._threshold_image(misc.imresize(image_array, size=(IMAGEY, IMAGEX)), K_Clusters)

        binary_image = ImageSegmenter._threshold_image(image_array, K_Clusters, lightbg, darkbg)
        # Step 2
        opened_image = ImageSegmenter._image_dilation(binary_image)
        closed_image = ImageSegmenter._noise_reduction(opened_image)
        binary_image = ndimage.binary_fill_holes(closed_image.astype(np.int))

        #opened_image = ImageSegmenter._image_dilation(closed_image)
        # Step 3 & 4
        #closed_image = ImageSegmenter._noise_reduction(opened_image)
       # opened_image = ImageSegmenter._image_dilation(closed_image)
        segments = ImageSegmenter._apply_object_detection(binary_image)
        # NOT WORKING PROPERLY  .change_segment_bounds(border_factor)
        return segments

    @staticmethod
    def _threshold_image(image_array, k, lightbg, darkbg):
        """
        Handler to properly threshold the image_array to a binary image of
        foreground and background. Algorithm used is a k-means clustering. 
        :param image_array: 
        :return: a 2D binary image
        """
        channel_image = ImageSegmenter._optimal_thresholding_channel_image(image_array)
        #histogram = ImageSegmenter._image_histogram(channel_image)
        #cluster_vector = ImageSegmenter._k_means_iterate(histogram, k)
        #has_light_bg = sum(histogram[0:50]) < sum(histogram[205:])
        #t0_min = threshold_minimum(image_array)

        if (lightbg == 'auto' and darkbg == 'auto'):
            # filter the image slightly
            sizefoot = [2, 2]
            channel_image = ndimage.median_filter(channel_image, sizefoot)
            channel_image = adjust_gamma(channel_image, gamma=1.4, gain=1)
            histogram = ImageSegmenter._image_histogram(channel_image)
            t0_min = threshold_mean(channel_image)
            has_light_bg = sum(histogram[0:5]) < sum(histogram[250:])
        else:
            channel_image = ImageSegmenter._optimal_thresholding_channel_image(image_array)
            histogram = ImageSegmenter._image_histogram(channel_image)
            t0_min = threshold_mean(channel_image)
            has_light_bg = sum(histogram[0:5]) < sum(histogram[250:])
        return ImageSegmenter._apply_cluster_threshold(t0_min, channel_image, has_light_bg, lightbg, darkbg)  # ImageSegmenter._has_dark_objects(channel_image))

    @staticmethod
    def _has_dark_objects(image):
        """
        :return: True if the image parameter has black foreground images on a light background, false otherwise. 
        """
        mean_background_vector = ImageSegmenter._background_average_vector(image)
        return (mean_background_vector > 127)  # light background => dark foreground objects

    @staticmethod
    def _background_average_vector(image):
        """
        :return: the average background pixel intensity for the four corners of the image in each channel. 
        """
        x_dim, y_dim = image.shape[0], image.shape[1]

        background_corner_index_x_list = []
        background_corner_index_y_list = []

        # Add indices for each corner of the image
        for i in range(BGPCOUNT):
            background_corner_index_x_list.append(i)
            background_corner_index_y_list.append(i)
            background_corner_index_x_list.append(x_dim - (i + 1))
            background_corner_index_y_list.append(y_dim - (i + 1))

        if image.ndim == 3:
            background_vector = image[background_corner_index_x_list, background_corner_index_y_list, :]
            return np.mean(np.mean(background_vector, axis=1), axis=0)
        else:
            background_vector = image[background_corner_index_x_list, background_corner_index_y_list]
            return np.mean(background_vector)

    @staticmethod
    def _construct_mean_channelled_image(image):
        """
        :param image: a 2D image array to be cropped with an optional channel dimension Shape in form (c,y,x)
         where c >=1
        :return: a purely 2D image by averaging the pixel intensities across the channels. 
        """
        if image.ndim == 3:
            return np.mean(image, axis=0)
        logging.info("Image for segmenting does not contain multiple channels.")
        return image

    @staticmethod
    def _optimal_thresholding_channel_image(image):
        """
        Handles a 2Darray of multiple channels and determines the best channel to apply thresholding to. 
        :param image: 3Darray image of a 2D image with multiple channels
        :return: a 2Darray of the image from the best channel
        """
        if image.ndim == 3:
            channel_mean_vector = np.mean(np.mean(image, axis=1), axis=0)

            background_channel_mean_vector = ImageSegmenter._background_average_vector(image)

            # Choose channel for clustering based on maximum difference in background and average intensity
            max_difference_channel = np.abs(background_channel_mean_vector - channel_mean_vector)
            clustering_channel = np.argmax(max_difference_channel)
            return image[:, :, clustering_channel]
        return image.copy()

    @staticmethod
    def _image_histogram(channel_image):
        """
        Creates a histogram from a 2D channel image/ 
        :param channel_image: 2D array
        :return: a 1D array of length 256 where the index represents the pixel intensity [0,255] and the value in each
        cell is the number of pixels of that intensity from the channel_image
        """
        histogram = np.zeros((256))
        for pixel in channel_image:
            histogram[pixel] += 1
        return histogram

    @staticmethod
    def _k_means_iterate(histogram, kcluster):
        """
        K-means algorithm from a histogram based implementation. 
        :param k: number of clusters for the algorithm
        :return: a vector of size k of the clusters' pixel intensities
        """

        def closest_index(ndarray, value):
            """
            Helper Method: returns the index in ndarray of the number which is closest to value. 
            """
            return np.argmin(np.abs(ndarray - value))

        # Initiate k clusters equidistant on the domain of the channel intensity
        cluster_vector = np.linspace(0, 255, num=kcluster)
        cluster_temp_vector = cluster_vector.copy()

        while (1):

            # Find closest cluster for each pixel intensity in histogram
            index_histogram = [closest_index(cluster_vector, i) for i in range(256)]

            # for each cluster, find mean of clustered pixel intensities
            # histogram[i] is number of pixels at intensity i
            for k in range(kcluster):
                weighted_mean_sum = sum(ind * histogram[ind] for ind in range(256) if index_histogram[ind] == k)
                pixel_count = sum(histogram[ind] for ind in range(256) if index_histogram[ind] == k)
                cluster_temp_vector[k] = weighted_mean_sum / (pixel_count + 1)

            # If all clusters change less than the threshold -> finish iteration
            if (np.abs((cluster_vector - cluster_temp_vector)) <= SENSITIVITY_THRESHOLD).all():
                return cluster_temp_vector
            cluster_vector = cluster_temp_vector.copy()

    @staticmethod
    def _apply_cluster_threshold(t0_min, channel_image, darkObjects, lightbg, darkbg):
        """
        Applies the cluster_vector thresholds to the channel_image to create a binary image. 
        :param cluster_vector: 1D array of cluster pixel intensities
        :param channel_image: 2D image array
        :param darkObjects: boolean True for light bg, False for dark bg
        :param lightbg: manual override value for thresholding light bg (or 'auto')
        :param darkbg: manual override value for thresholding dark bg (or 'auto')
        :return: a binary image of the median threshold from cluster_vector
        """

        # Using 2nd index of 10 clusters for foreground (index found through testing)
        if (darkObjects):
            # logging.info("Image currently being segmented is deemed to have a light background.")
            if lightbg != 'auto' and int(lightbg) > 0 and int(lightbg) < 255:
                binary_threshold = int(lightbg)
            else:
                binary_threshold = t0_min  # cluster_vector[-1]
            msg = 'LIGHT bg: threshold=%d' % binary_threshold
            print(msg)
            logging.info(msg)
            yy = np.zeros(channel_image.shape, dtype=np.uint8)
            rtn = 255 * (yy+(channel_image < binary_threshold))

        else:
            # logging.info("Image currently being segmented is deemed to have a dark background.")
            if darkbg != 'auto' and int(darkbg) > 0 and int(darkbg) < 255:
                binary_threshold = int(darkbg)
            else:
                binary_threshold = t0_min  # cluster_vector[0] /2 #Correction for dark bg thresholding
            msg = 'DARK bg: threshold=%d' % binary_threshold
            print(msg)
            logging.info(msg)
            yy = np.zeros(channel_image.shape, dtype=np.uint8)
            rtn = 255 * (yy+(channel_image > binary_threshold))
        return rtn

    @staticmethod
    def _noise_reduction(binary_image):
        """
        Applies morphological erosion to the binary_image to reduce noise. 
        :param binary_image: image to be opened.
        :return: A new binary image that has undergone opening. 
        """
        struct_size = 2  # max(round(binary_image.size / 8000000), 2)
        structure = np.ones((struct_size, struct_size))
        #binary_image = ndimage.gaussian_filter(binary_image.astype(np.int),sigma=0.1)
        return ndimage.binary_erosion(binary_image.astype(np.int), structure=structure)


    @staticmethod
    def _image_dilation(binary_image):
        """
        Applies morphological dilation to the binary_image to increase size of the foreground objects
        :param binary_image: image to be opened.
        :return: A new binary image that has undergone opening. 
        """
        struct_size = 3  # int(min(binary_image.shape) * 0.01)
        structure = np.ones((2, 2))  # ((struct_size, struct_size))
        yy = np.zeros(binary_image.shape, dtype=np.uint8)
        return ndimage.binary_dilation((yy + binary_image), structure=structure).astype(yy.dtype)
        #return ndimage.median_filter(binary_image.astype(np.int), size=[1, 1])

    @staticmethod
    def _apply_object_detection(morphological_image):
        """
        Detects foreground objects from a binary, opened image. 
        :param morphological_image: Binary image
        :return: A ImageSegmentation object
        """
        # segmentations = ImageSegmentation(IMAGEX, IMAGEY)
        segmentations = ImageSegmentation(morphological_image.shape[0], morphological_image.shape[1])

        # Separate objects into separate labelled ints on matrix imlabelled
        imlabeled, num_features = ndimage.measurements.label(morphological_image, output=np.dtype("int"))
        labels = np.unique(imlabeled)

        # Iterate through range and make array of 0, 1, ..., len(labels)
        lab = []
        for i in range(len(labels) - 1):
            lab.append(i + 1)

        slices = ndimage.measurements.find_objects(imlabeled, max_label=len(labels))

        # filter out None values and sort the slices
        slices = filter(None, slices)
        slices = sorted(slices)

        #  apply construction of subslices to form larger sized images
        slices = ImageSegmenter._reconstruct_images_from_slices(slices)

        # add to ImageSegmenter data structure
        for box in slices:
            ImageSegmenter._add_box_from_slice(box, segmentations)

        # Remove objects that aren't big enough to be considered full images.
        totalarea = morphological_image.shape[0] * morphological_image.shape[1]
        fraction = 0.001  # segment/area 1%
        for bounding_box in segmentations.segments:
            a = segmentations.segment_area(bounding_box)
            if (a / totalarea) < fraction:
                segmentations.segments.remove(bounding_box)

        msg = "ObjectDetection: Features found: %d Segments created: %d" % (num_features, len(segmentations.segments))
        logging.info(msg)
        print(msg)
        return segmentations

    @staticmethod
    def _add_box_from_slice(box, segmentation_object):
        """
        returns an array of two points [x1, y1, x2, y2] where point 1 is the left top corner and point 2 the right
        bottom corner of a box surrounding an object. 
        :param box: a 2 value tuple of slice objects
        """
        y_slice = box[0]
        x_slice = box[1]
        segmentation_object.add_segmentation(x_slice.start, y_slice.start, x_slice.stop, y_slice.stop)

    @staticmethod
    def is_noise(s1):
        """
        Checks if the slice object should be considered as noise pixels and not constructive of a larger image. 
        :param s1: slice object tuple
        :return:  True if the area of the bounding box is less than 1000 pixels
        """
        if (s1[0].stop - s1[0].start) * (s1[1].stop - s1[1].start) < MAX_NOISE_AREA:
            return True
        return False

    @staticmethod
    def intersect(s1, s2):
        """
        :param s1, s2: 2D tuples of slice objects i.e. (Slice, Slice) for a region of an image. 
        :return: 1 if the intersection of the two regions is not empty (i.e. have common pixels) 
        """
        if (s1[0].stop < s2[0].start) | (s1[0].start > s2[0].stop):
            return False

        xx = np.zeros((max(s1[0].stop, s2[0].stop), max(s1[1].stop, s2[1].stop))).astype(np.int)
        yy = np.zeros((max(s1[0].stop, s2[0].stop), max(s1[1].stop, s2[1].stop))).astype(np.int)
        xx[s1[0].start:s1[0].stop, s1[1].start:s1[1].stop] = 1
        yy[s2[0].start:s2[0].stop, s2[1].start:s2[1].stop] = 1
        zz = xx + yy
        if zz.max() == 2:
            return True
        else:
            return False

        #elif (((s2[1].start <= s1[1].stop) and (s2[1].stop >= s1[1].start)) and ((s2[0].start <= s1[0].stop) and (s2[0].stop >= s1[0].start))):
        #    return True
        #else:
        #    return False
        #return not (s1[1].stop < s2[1].start) | (s1[1].start > s2[1].stop)

    @staticmethod
    def add(s1, s2):
        """
        :param s1, s2: 2D tuples of slice objects i.e. (Slice, Slice) for a region of an image. 
        :return: a 2D tuple of slice objects for a region of an image that contains both s1 and s2. 
        """
        x_values = [s1[0].start, s2[0].start, s1[0].stop, s2[0].stop]
        y_values = [s1[1].start, s2[1].start, s1[1].stop, s2[1].stop]
        x_slice = slice(min(x_values), max(x_values))
        y_slice = slice(min(y_values), max(y_values))
        return (x_slice, y_slice)

    @staticmethod
    def _reconstruct_images_from_slices(box_slices):
        """
        Iterative process to continuously add intersecting  
        :param box_slices: List of slice tuples considered as bounding boxes for an image. 
        :return: a new list of bounding boxes that are the reconstructed bounding boxes for the images in the photo. 
        """
        prev_len = len(box_slices)
        curr_len = len(box_slices)
        flag = True


        for rect in box_slices:
            if ImageSegmenter.is_noise(rect):
                box_slices.remove(rect)

        while flag | (prev_len != curr_len):
            flag = False

            temp_list = []
            i = 0

            #  Iterate through all slices in the list.
            while i < (len(box_slices) - 1):
                add_this_obj = True

                j = i + 1
                x1 = box_slices[i]
                x2 = box_slices[j]

                #  Since sorted, iterate through all boxes with intersecting x until box i is past box j

                #while (not (x1.stop < x2.start) | (x1.start > x2.stop)) & (j < len(box_slices)):
                while (j < len(box_slices)):
                    if ImageSegmenter.intersect(x1,x2):
                        temp_list.append(ImageSegmenter.add(box_slices.pop(j), box_slices.pop(i)))
                        add_this_obj = False
                        j = len(box_slices)
                    else:
                        j += 1
                        if j < len(box_slices):
                            x2 = box_slices[j]
                        else:
                            j = len(box_slices)

                # Only add to iterative list if it does not intersect with any of the boxes.
                if add_this_obj:
                    temp_list.append(box_slices[i])
                    i += 1

            # Correct for last object not being iterated over
            if len(box_slices) != 0:
                temp_list.append(box_slices[-1])

            # re-sort
            box_slices = sorted(temp_list.copy())
            del temp_list

            prev_len = curr_len
            curr_len = len(box_slices)
            i = 0

        #iterate over this twice to see if it helps join things that should have been joined the first time
        prev_len = len(box_slices)
        curr_len = len(box_slices)
        flag = True

        for rect in box_slices:
            if ImageSegmenter.is_noise(rect):
                box_slices.remove(rect)

        while flag | (prev_len != curr_len):
            flag = False

            temp_list = []
            i = 0

            #  Iterate through all slices in the list.
            while i < (len(box_slices) - 1):
                add_this_obj = True

                j = i + 1
                x1 = box_slices[i]
                x2 = box_slices[j]

                #  Since sorted, iterate through all boxes with intersecting x until box i is past box j

                # while (not (x1.stop < x2.start) | (x1.start > x2.stop)) & (j < len(box_slices)):
                while (j < len(box_slices)):
                    if ImageSegmenter.intersect(x1, x2):
                        temp_list.append(ImageSegmenter.add(box_slices.pop(j), box_slices.pop(i)))
                        add_this_obj = False
                        j = len(box_slices)
                    else:
                        j += 1
                        if j < len(box_slices):
                            x2 = box_slices[j]
                        else:
                            j = len(box_slices)

                # Only add to iterative list if it does not intersect with any of the boxes.
                if add_this_obj:
                    temp_list.append(box_slices[i])
                    i += 1

            # Correct for last object not being iterated over
            if len(box_slices) != 0:
                temp_list.append(box_slices[-1])

            # re-sort
            box_slices = sorted(temp_list.copy())
            del temp_list

            prev_len = curr_len
            curr_len = len(box_slices)
            i = 0
        return box_slices
