import unittest

from autoanalysis.processmodules.imagecrop.ImageSegmentation import ImageSegmentation as ImageSegmentation
from autoanalysis.processmodules.imagecrop.ImageSegmentation import InvalidSegmentError as InvalidSegmentError


class ImageSegmentationTest(unittest.TestCase):
    """
    Test Suite for ImageSegmentation
    """

    def setUp(self):
        self.object = ImageSegmentation(20, 20)
        self.object.add_segmentation(0, 0, 10, 10)
        self.object.add_segmentation(10, 0, 20, 10)
        self.object.add_segmentation(0, 10, 10, 20)
        self.object.add_segmentation(10, 10, 20, 20)

    def test_get_scaled_segments(self):
        test_result = self.object.get_scaled_segments(500, 1000)
        self.assertTrue([0, 0, 250, 500] in test_result, "Box 1 scaled correctly")
        self.assertTrue([250, 0, 500, 500] in test_result, "Box 2 scaled correctly")
        self.assertTrue([0, 500, 250, 1000] in test_result, "Box 2 scaled correctly")
        self.assertTrue([250, 500, 500, 1000] in test_result, "Box 2 scaled correctly")
        self.assertTrue(len(test_result) == 4, "Contains exactly the inputted boxes")

    def test_get_relative_segments(self):
        test_result = self.object.get_relative_segments()
        self.assertTrue([0, 0, 0.5, 0.5] in test_result, "Box 1 scaled correctly")
        self.assertTrue([0.5, 0, 1, 0.5] in test_result, "Box 2 scaled correctly")
        self.assertTrue([0, 0.5, 0.5, 1] in test_result, "Box 2 scaled correctly")
        self.assertTrue([0.5, 0.5, 1, 1] in test_result, "Box 2 scaled correctly")
        self.assertTrue(len(test_result) == 4, "Contains exactly the inputted boxes")

    ##  Following tests are all for illegal values being used in the add_segmentation method.
    def test_negative_point(self):
        with self.assertRaises(InvalidSegmentError):
            self.object.add_segmentation(-5, 0, 0, 5)

    def test_x_values(self):
        with self.assertRaises(InvalidSegmentError):
            self.object.add_segmentation(10, 0, 5, 5)

    def test_y_values(self):
        with self.assertRaises(InvalidSegmentError):
            self.object.add_segmentation(0, 10, 5, 5)

    def test_points_off_image(self):
        with self.assertRaises(InvalidSegmentError):
            self.object.add_segmentation(0, 0, 30, 30)


if __name__ == '__main__':
    unittest.main()
