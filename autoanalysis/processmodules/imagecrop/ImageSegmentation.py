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
        # if (any(value < 0 for value in [x1, y1, x2, y2]) | any(x > self.width for x in [x1, x2]) |
        #         any(y > self.height for y in [y1, y2]) | (x1 > x2) | (y1 > y2)):
        #     logging.error("Invalid image segment: %s of image sized %s", (x1, y1, x2, y2), (self.width, self.height))
        #     raise InvalidSegmentError()
        # else:
        if [x1, y1, x2, y2] not in self.segments:
            self.segments.append([x1, y1, x2, y2])

    def get_scaled_segments(self, height,width):
        """
        :param width: pixel width of image to be scaled to.
        :param height: pixel height of image to be scaled to. 
        :return: An array of segment boxes scaled to the dimensions width x height
        """

        # make into 2d Array
        matrix = np.array(self.segments)[:]

        # column multiplication of columns 0 & 2 by width/self.width
        matrix[:, [X1, X2]] = np.multiply(matrix[:, [X1, X2]], round(width / self.width))

        # same for y axis columns 1 & 3. Multiply by height/self.height
        matrix[:, [Y1, Y2]] = np.multiply(matrix[:, [Y1, Y2]], round(height / self.height))
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

    # def handle_shift_factor(self, height, width):
    #     new_image_segmentation = ImageSegmentation(self.width, self.height)
    #     for bounding_box in self.segments:
    #         y = 1 - (self.height / height) / 100
    #         x = 1 - (self.width / width) / 100
    #
    #         new_image_segmentation.add_segmentation(min(int(bounding_box[X1] * x),self.width), min(int(bounding_box[Y1] * y), self.height),
    #                                                 min(int(bounding_box[X2] * x), self.width), min(int(bounding_box[Y2] * y), self.height))
    #
    #     return new_image_segmentation

    def change_segment_bounds(self, factor):
        """
        TODO: Fix for border - currently crashing with 'argument out of range' error
        :param factor: percent of pixels to include as border eg 5
        :return: an ImageSegmentation object with bounding boxes increased/decreased by the given factor or nothing
        """

        if factor > 0 and factor < 100:
            border = int((factor / 100) * np.sqrt(self.width * self.height))
            msg ="Applying border of {} px".format(border)
            logging.info(msg)
            print(msg)
            new_image_segmentation = ImageSegmentation(self.width, self.height)
            for bounding_box in self.segments:
                pos_x1 = max(0,round(bounding_box[0] - border))
                pos_y1 = max(0,round(bounding_box[1] - border))
                pos_x2 = min(self.width, round(bounding_box[2] + border))
                pos_y2 = min(self.height, round(bounding_box[3] + border))
                new_image_segmentation.add_segmentation(pos_x1,pos_y1, pos_x2,pos_y2)
                #new_image_segmentation.add_segmentation(bounding_box[0],bounding_box[1],bounding_box[2],bounding_box[3])
            return new_image_segmentation
        else:
            return self

class InvalidSegmentError(Exception):
    pass
