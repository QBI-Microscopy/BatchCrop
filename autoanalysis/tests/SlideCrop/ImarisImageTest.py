import unittest

import numpy as np

from autoanalysis.processmodules.SlideCrop import ImarisImage

TESTFILE_PATH = "E:/testfile.ims"
class ImarisImageTest(unittest.TestCase):
    """
    Test Suite for ImarisImage
    """
    def setUp(self):
        self.Image = ImarisImage.ImarisImage(TESTFILE_PATH)
        self.lowest_res = self.Image.get_resolution_levels() - 1
    def tearDown(self):
        pass

    def test_two_dim_data(self):
        test_array = self.Image.get_two_dim_data(self.lowest_res)
        self.assertEqual(test_array.shape,(1280, 640),
                         "get_two_dim_data tested with no region specified")

        test_array = self.Image.get_two_dim_data(self.lowest_res, region =[500, 500, 505, 505])
        self.assertEqual(test_array.shape,(5,5),
                         "get_two_dim_data tested with region specified")
        self.assertTrue((test_array[0:5,0:5] == [[11, 12, 13,  0,  0],
                                               [12, 10, 12,  0,  0],
                                               [10, 11, 11,  0,  0],
                                               [10, 12, 11,  0,  0],
                                               [11, 13, 11,  0,  0]]).all(),
                         "get_two_dim_data returns correct values")

    def test_get_euclidean_subset_in_resolution(self):
        test_array = self.Image.get_euclidean_subset_in_resolution(self.lowest_res, [0,1], [0,3], [0,1], [500, 505],
                                                                                    [500, 505])
        self.assertEqual(test_array.shape, (1,3,1,5,5), "get_euclidean_subset_in_resolution returns correct shape"
                                                            " array")
        self.assertTrue((test_array[0, 0, 0, :,:] == np.array([[11, 12, 13,  0,  0],
                                                    [12, 10, 12,  0,  0],
                                                    [10, 11, 11,  0,  0],
                                                    [10, 12, 11,  0,  0],
                                                    [11, 13, 11,  0,  0]])).all(),
                         "get_euclidean_subset_in_resolution returns correct valued array")



    def test_get_low_res_image(self):
        self.assertEqual(self.Image.get_low_res_image().shape, (1, 1280, 640), "get_low_res_image returns correct "
                                                                               "shaped array")
        self.assertTrue((self.Image.get_low_res_image()[0, 505:510, 500:505] == [[13, 10, 11,  0,  0],
                                                                               [11, 11, 12,  0,  0],
                                                                               [11, 12, 12,  0,  0],
                                                                               [11, 11, 11,  8,  0],
                                                                               [11, 11, 12, 11,  0]]).all(),
                         "get_low_res_image returns correct valued array")

    def test_get_segment_res_image(self):
        segment_res_image = self.Image.get_segment_res_image()
        self.assertEqual(segment_res_image.shape, (1, 4736, 2432),"get_segment_res_image returns correct shape array")


    def test_change_segment_res(self):
        self.Image.change_segment_res(4)
        segment_res_image = self.Image.get_segment_res_image()
        self.assertEqual(segment_res_image.shape, (1, 9472, 4864), "get_segment_res_image returns correct shape array"
                                                                   "after correction")

    def test_get_resolution_channel_levels(self):
        self.assertEqual(self.Image.get_channel_levels(), 3, "get_channel_levels returns correct value")
        self.assertEqual(self.Image.get_resolution_levels(), 8, "get_resolution_levels returns correct value")

    def test_resolution_dimensions(self):
        self.assertEqual(self.Image.resolution_dimensions(self.lowest_res), [640, 1280, 1, 3, 1], "resolution_dimensions returns"
                                                                                    "correct array")

    def test_image_dimensions(self):
        self.assertEqual(self.Image.image_dimensions(), [(149888, 77184),
                                                         (75008, 38656),
                                                         (37504, 19328),
                                                         (18816, 9728),
                                                         (9472, 4864),
                                                         (4736, 2432),
                                                         (2432, 1280),
                                                         (1280, 640)], "image_dimensions correct")

    def test_metadata_json(self):
        pass

    def test_metadata_from_path(self):
        pass

if __name__ == '__main__':
    unittest.main()