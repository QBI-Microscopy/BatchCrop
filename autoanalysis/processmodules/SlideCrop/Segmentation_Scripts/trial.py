import os

import numpy as np
import scipy.misc as misc
import scipy.ndimage as ndimage
from skimage import io

from autoanalysis.processmodules.SlideCrop import ImageSegmenter as seg

WORK_DIR = "E:/"
im = io.imread(WORK_DIR + "testdata2_resolution3/170818_APP_1878 UII_BF~B.jpg") #"testdata1_resolution3/AT8 wt2223m 11~B.jpg") # "testdata2_resolution3/170818_APP_1878 UII_BF~B.jpg") #'testfile4.jpg') #"testdata1_resolution3/AT8 wt2223m 11~B.jpg") #  'testfile4.jpg') # "testdata2_resolution4/170818_APP_1878 UII_BF~B.jpg") # "'td11.png') # 'testfile4.jpg')
im = misc.imresize(im, 0.2)
print(im.shape)
histogram = seg._image_histogram(im)
cluster = seg._k_means_iterate(histogram, 5)

print(cluster)

res_dir = "{}{}/".format(WORK_DIR, os.getpid())
if not os.path.exists(res_dir):
    os.makedirs(res_dir)

channel_im = seg._optimal_thresholding_channel_image(im)
misc.imsave("{}{}".format(res_dir, "1initial_photo.png"), channel_im)
print("Initial photo saved")
black_objects = seg._has_dark_objects(channel_im)
binary = seg._apply_cluster_threshold(cluster, channel_im, seg._background_average_vector(channel_im))

binary = binary.astype(int)
if black_objects:
    binary = 255 - binary
    black_objects = not black_objects

misc.imsave("{}{}".format(res_dir, "2thresholded_photo.png"), binary)
del channel_im
print("thresholded image saved")

bwfill = ndimage.binary_fill_holes(binary, structure=np.ones((10,10)))
bwerode = ndimage.binary_erosion(bwfill, structure=np.ones((2,2)), iterations=1)

# Get the geatures and count in the final (filled then eroded ndarray)
imlabeled, num_features = ndimage.measurements.label(bwerode, output=np.dtype("int"))
sizes = ndimage.sum(bwerode, imlabeled, range(num_features + 1))
mask_size = sizes < 1000
misc.imsave("E:/imlabelledfirstLRESULT1.jpg", imlabeled)

# get non-object pixels and set to zero
remove_pixel = mask_size[imlabeled]
imlabeled[remove_pixel] = 0
labels = np.unique(imlabeled)
misc.imsave("E:/imlabelledLRESULT1.jpg", imlabeled)

# ndimage
label_clean = np.searchsorted(labels, imlabeled)

# Iterate through range and make array of 0, 1, ..., len(labels)
lab = []
for i in range(len(labels) - 1):
    lab.append(i + 1)


objs = ndimage.measurements.find_objects(label_clean, max_label=len(labels))
print(objs)
print(len(objs))
misc.imsave("E:/TRIALRESULT1.jpg", label_clean)

# If any objects have been found, return
# return value will be array of tuple of 2 slice Objects
# [(slice(0, 2, None), slice(0, 3, None)), (slice(2, 5, None), slice(2, 5, None))]
# Analogous to label_clean[0:2, 0:3] for the first tuple

