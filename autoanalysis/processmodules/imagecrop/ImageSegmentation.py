import numpy as np
import logging

X1, Y1, X2, Y2 = range(4)


class ImageSegmentation(object):
    """
    Data Structure to hold box segments for images. Box segments are defined by two points: 
    upper-left & bottom-right.  
    """

    def __init__(self, width, height):
        self.height = height
        self.width = width
        self.segments = []

    def add_segmentation(self, x1, y1, x2, y2):
        """
        Adds a segmentation array to the ImageSegmentation object
        :param x1, y1: upper-left point of the segment box
        :param x2, y2: bottom-right point of the segment box
        :return: null
        """
        if (any(value < 0 for value in [x1, y1, x2, y2]) | any(x > self.width for x in [x1, x2]) |
                any(y > self.height for y in [y1, y2]) | (x1 > x2) | (y1 > y2)):
            logging.error("Invalid image segment: %s of image sized %s", (x1, y1, x2, y2), (self.width, self.height))
            raise InvalidSegmentError()
        else:
            if [x1, y1, x2, y2] not in self.segments:
                self.segments.append([x1, y1, x2, y2])

    def get_scaled_segments(self, width, height):
        """
        :param width: pixel width of image to be scaled to.
        :param height: pixel height of image to be scaled to. 
        :return: An array of segment boxes scaled to the dimensions width x height
        """

        # make into 2d Array
        matrix = np.array(self.segments)[:]

        # column multiplication of columns 0 & 2 by width/self.width
        matrix[:, [X1, X2]] = np.multiply(matrix[:, [X1, X2]], (width / self.width))

        # same for y axis columns 1 & 3. Multiply by height/self.height
        matrix[:, [Y1, Y2]] = np.multiply(matrix[:, [Y1, Y2]], (height / self.height))
        return matrix

    def get_relative_segments(self):
        """
        :return: An array of segment boxes without scaling.  x1<= x, y <=1. 
        """
        return self.get_scaled_segments(1, 1)

    def get_max_segment(self):
        """
        :return: Returns the segment [x1, y1, x2, y2] with the largest area
        """
        max_segment = self.segments[0]
        max_area = self.segment_area(max_segment)

        for segment in self.segments:
            segment_area = self.segment_area(segment)
            if segment_area > max_area:
                max_segment = segment
                max_area = segment_area

        return max_segment

    def segment_area(self, segment):
        """
        :param segment: Bounding box of form [x1, y1, x2, y2] 
        :return: area of bounding box
        """
        return (segment[X2] - segment[X1]) * (segment[Y2] - segment[Y1])

    def handle_shift_factor(self, height, width):
        new_image_segmentation = ImageSegmentation(self.width, self.height)
        for bounding_box in self.segments:
            y = 1 - (self.height / height) / 100
            x = 1 - (self.width / width) / 100

            new_image_segmentation.add_segmentation(min(int(bounding_box[X1] * x),self.width), min(int(bounding_box[Y1] * y), self.height),
                                                    min(int(bounding_box[X2] * x), self.width), min(int(bounding_box[Y2] * y), self.height))

        return new_image_segmentation

    def change_segment_bounds(self, factor):
        """
        :param factor: a float value dictating the change in bounding box size. Factor > 1 increases the ROI
        :return: an ImageSegmentation object with bounding boxes increased/decreased by the given factor
        """
        logging.info("Segments are being increase by a factor of {}.".format(factor))
        new_image_segmentation = ImageSegmentation(self.width, self.height)
        for bounding_box in self.segments:
            centre_point = [(bounding_box[X1] + bounding_box[X2]) / 2, (bounding_box[Y1] + bounding_box[Y2]) / 2]
            half_dimensions = [(bounding_box[X2] - bounding_box[X1]) / 2, (bounding_box[Y2] - bounding_box[Y1]) / 2]
            x1 = max(int(centre_point[0] - factor * half_dimensions[0]), 0)
            y1 = max(int(centre_point[1] - factor * half_dimensions[1]), 0)
            x2 = min(int(centre_point[0] + factor * half_dimensions[0]), self.width)
            y2 = min(int(centre_point[1] + factor * half_dimensions[1]), self.height)
            new_image_segmentation.add_segmentation(x1, y1, x2, y2)
        return new_image_segmentation


class InvalidSegmentError(Exception):
    pass
