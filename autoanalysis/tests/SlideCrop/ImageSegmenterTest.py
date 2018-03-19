import unittest
from operator import itemgetter

import numpy as np
from version_two.src.SlideCrop.ImageSegmentation import ImageSegmentation as ImageSegmentation
from version_two.src.SlideCrop.ImarisImage import ImarisImage as ImarisImage

from autoanalysis.processmodules.SlideCrop import ImageSegmenter as ImageSegmenter

TESTFILE1 = "E:/testfile.ims"
MAXIMUM_ERROR = 0.1 # i.e 10% greater


class ImageSegmenterTest(unittest.TestCase):
    """
    Test Suite for ImageSegmenter
    """

    def test_segment_image(self):
        """
        Tests the Automated testing of ImageSegmenter.segment_image(arr) for the given TESTFILE and
        there corresponding correct manual segmentation. 
        """
        self.assertTrue(self.segment_and_test(TESTFILE1), "Successfully cropped TESTFILE1")

    def segment_and_test(self, file_path):
        """
        Worker function that processes the file paths from test_segment_image and compares against correct solutions.
        :param file_path: 
        :return: Boolean on whether the automated segmentation was within MAXIMUM_ERROR of the manual crop.  
        """
        image = ImarisImage(file_path)
        segmentations = ImageSegmenter.segment_image(image.get_segment_res_image())
        return self.compare_segmentations(segmentations.get_scaled_segments(1000, 1000),
                                          self.correct_testfile_one_segment().
                                          get_scaled_segments(1000, 1000))


    def compare_segmentations(self, test_segment, correct_segment):
        """
        Compares two specific box segments to whether the automated segment, test_segment is correct and accurate
        enough to the manual segment, correct_segment. 
        :param test_segment: The automated segment box to be tested. 
        :param correct_segment: The manual segment box to be tested against. 
        :return: Boolean on correctness and accuracy. 
        """
        if(len(test_segment) != len(correct_segment)):
         return False

        # sort test_segment, correct_segment to improve read times. sorted in order: x1, x2, y1, y2
        test_segment = sorted(test_segment, key=itemgetter(0,2,1,3))
        correct_segment = sorted(correct_segment, key=itemgetter(0,2,1,3))

        # Test sorted elements against correct_segments
        for test_seg, correct_seg in test_segment, correct_segment:
            if not self.compare_segment(test_seg, correct_seg):
                return False

        # All box segments passed. segmentation is correct
        return True

    def compare_segment(self, test_seg, correct_seg):
        """
         Compares two specific box segments to whether the automated segment, test_segment is correct and accurate
         enough to the manual segment, correct_segment. 
            Must check first two points test_(x1, y1) < correct_(x1, y1) &&
                                        test_(x2, y2) > correct_(x1, y1)
            i.e the two test segment points are outside the minimum rectangle defined by correct_segment
     
         :param test_segment: The automated segment box to be tested. 
         :param correct_segment: The manual segment box to be tested against. 
         :return: Boolean on correctness and accuracy. 
        """
                # upper-left & lower-right points are outside the correct segment
        return ((test_seg[0] <= correct_seg[0]) &
                (test_seg[1] <= correct_seg[1]) &
                (test_seg[2] >= correct_seg[2]) &
                (test_seg[3] >= correct_seg[3]) &

                # All errors in test_seg and correct_seg are within the MAXIMUM ERROR
                ((np.abs(1- np.divide(test_seg, correct_seg)) < MAXIMUM_ERROR).all()))


    def correct_testfile_one_segment(self):
        """
        Returns an imageSegmentation object with the minimum size rectangles that TESTFILE1 can have. 
        Segments inside these bounds are too tight for the segmentation. 
        """
        segments = ImageSegmentation(19328, 37504)
        segments.add_segmentation(1376, 20088, 8366, 26808)
        segments.add_segmentation(2032,1240, 7272, 8664)
        segments.add_segmentation(3472, 10488, 8272, 11792)
        segments.add_segmentation(5136, 30840, 12680, 35512)
        segments.add_segmentation(10472, 21384, 15616, 29128)
        segments.add_segmentation(11032, 2184, 15784, 9648)
        segments.add_segmentation(11184, 11752, 15864, 19112)
        return segments.get_scaled_segments(1000, 1000)

if __name__ == '__main__':
    unittest.main()

