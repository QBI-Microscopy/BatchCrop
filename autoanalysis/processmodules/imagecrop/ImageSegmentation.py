import logging

import numpy as np

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

        # if (any(value < 0 for value in [x1, y1, x2, y2]) | any(x > self.height for x in [x1, x2]) |
        #         any(y > self.width for y in [y1, y2]) | (x1 > x2) | (y1 > y2)):
        #     logging.error("Invalid image segment: %s of image sized %s", (x1, y1, x2, y2), (self.width, self.height))
        #     raise InvalidSegmentError()
        # else:
        if [x1, y1, x2, y2] not in self.segments:
            self.segments.append([x1, y1, x2, y2])

    def get_scaled_segments(self, width, height, r, maxr, border=0, offset=1, chunks=None):
        """
        :param width: pixel width of image to be scaled to.
        :param height: pixel height of image to be scaled to.
        :param r: resolution level that is being scaled to.
        :param maxr: total number of resolution levels.
        :return: An array of segment boxes scaled to the dimensions width x height
        https://stackoverflow.com/questions/42000601/resize-an-image-with-offset-in-python
        """
        scalefactor = int(np.sqrt((width * height) / (self.width * self.height)))

        #Because of data chunking, height and width of resolution[-1] is padded to be a multiple of 128.
        #This means instead of being eg. 593 wide it is 640 wide, meaning scaling relative to this value is incorrect.
        #It appears to be exponential scaling with each resolution level though so I will try this instead.

        exp_scalefactor = [1,2,4,8,16,32,64,128,256]

        #scale_width = (width / self.width)
        #scale_height = (height / self.height)
        #if scale_width == 1 or scale_height == 1:
        #    scale_width = scalefactor
        #    scale_height = scalefactor

        scale_width = exp_scalefactor[(maxr -1 - r)]
        scale_height = exp_scalefactor[(maxr - 1 - r)]

        msg = 'Scalefactors: wx%d hx%d [%d x %d] with border=%d to initial [%d x %d] offset=%s' % (
        scale_width, scale_height, width, height, border, self.width, self.height, offset)
        print(msg)
        logging.info(msg)
        # make into 2d Array
        matrix = np.array(self.segments)[:]
        msg = 'Orig xy: {}'.format(matrix)
        print(msg)
        logging.debug(msg)
        # Total segment boundary
        total_seg_h = matrix[-1][X2] - matrix[0][X1]
        total_seg_w = matrix[-1][Y2] - matrix[0][Y1]
        msg = 'Segmented area: %d x %d [%0.4f %0.4f]' % (
        total_seg_w, total_seg_h, (total_seg_h / self.height), (total_seg_w / self.width))
        print(msg)
        logging.info(msg)
        if border:
            border_factor = int((border / 100) * np.sqrt(self.width * self.height))
            matrix[:, [X1, Y1]] = np.subtract(matrix[:, [X1, Y1]], border_factor)
            matrix[:, [X2, Y2]] = np.add(matrix[:, [X2, Y2]], border_factor)
        msg = 'Border xy:{}'.format(matrix)
        print(msg)
        logging.debug(msg)
        # Apply scaling
        #this was the original - but I think the width/height scaling was accidentally reversed
        #matrix[:, [X1, X2]] = np.multiply(matrix[:, [X1, X2]], scale_width)
        #matrix[:, [Y1, Y2]] = np.multiply(matrix[:, [Y1, Y2]], scale_height)
        matrix[:, [X1, X2]] = np.multiply(matrix[:, [X1, X2]], scale_height)
        matrix[:, [Y1, Y2]] = np.multiply(matrix[:, [Y1, Y2]], scale_width)
        msg = 'Scaled xy:{}'.format(matrix)
        print(msg)
        logging.debug(msg)
        # replace with boundaries
        matrix[matrix < 0] = 0

        # TODO Large images in IMS are chunked so need to adjust offset for large images only
        # chunks = 128x128x16 (this may change with diff image acquisition)
        # https://www.oreilly.com/library/view/python-and-hdf5/9781491944981/ch04.html
        if chunks is not None and width/chunks[-1] > 50:
            # allow user to add an offset between 0-2, 0 will not apply ANY correction
            if offset >= 0:
                for i in range(len(matrix)):
                    numchunks = matrix[i][Y1] / chunks[-1]
                    bytefactor = (numchunks + 1 ) * 8 # UINT8 bits per px
                    offsetfactor = int(bytefactor * offset)
                    msg ='Offset factor: [%d] %d' % (i, offsetfactor)
                    logging.info(msg)
                    print(msg)

                    matrix[i][Y1] = np.add(matrix[i][Y1], offsetfactor)
                    matrix[i][Y2] = np.add(matrix[i][Y2], offsetfactor)
                    matrix[i][X1] = np.add(matrix[i][X1], offsetfactor)
                    matrix[i][X2] = np.add(matrix[i][X2], offsetfactor)
                msg = 'Offset xy: {}'.format(matrix)
                print(msg)
                logging.info(msg)
        # check width not greater than max width
        mw = matrix[:, [X2]] - matrix[:, [X1]]
        mw[mw > width] = width
        matrix[:, [X1]] = matrix[:, [X2]] - mw
        # max height
        mw = matrix[:, [Y2]] - matrix[:, [Y1]]
        mw[mw > height] = height
        matrix[:, [Y1]] = matrix[:, [Y2]] - mw

        # Total segment boundary after
        total_seg_w = matrix[-1][X2] - matrix[0][X1]
        total_seg_h = matrix[-1][Y2] - matrix[0][Y1]
        msg = 'Segmented area: %d x %d [%0.4f %0.4f]' % (total_seg_w, total_seg_h, (total_seg_w / height), (total_seg_h / width))
        print(msg)
        logging.info(msg)
        return matrix.astype(int)

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


    def change_segment_bounds(self, factor):
        """
        TODO: Fix for border - currently crashing with 'argument out of range' error
        :param factor: percent of pixels to include as border eg 5
        :return: an ImageSegmentation object with bounding boxes increased/decreased by the given factor or nothing
        """

        if factor > 0 and factor < 100:
            border = int((factor / 100) * np.sqrt(self.width * self.height))
            msg = "Applying border of {} px".format(border)
            logging.info(msg)
            print(msg)
            new_image_segmentation = ImageSegmentation(self.width, self.height)
            for bounding_box in self.segments:
                pos_x1 = max(0, round(bounding_box[0] - border))
                pos_y1 = max(0, round(bounding_box[1] - border))
                pos_x2 = min(self.width, round(bounding_box[2] + border))
                pos_y2 = min(self.height, round(bounding_box[3] + border))
                new_image_segmentation.add_segmentation(pos_x1, pos_y1, pos_x2, pos_y2)
                # new_image_segmentation.add_segmentation(bounding_box[0],bounding_box[1],bounding_box[2],bounding_box[3])
            return new_image_segmentation
        else:
            return self


class InvalidSegmentError(Exception):
    pass
