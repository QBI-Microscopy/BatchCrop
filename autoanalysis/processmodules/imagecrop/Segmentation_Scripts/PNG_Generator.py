import scipy.misc

from autoanalysis.processmodules.imagecrop import ImarisImage as I

DIRECTORY = "E:/questionable_testdata"
import os
resolution = 4
directory = os.fsencode(DIRECTORY)
res_dir = "E:/_resolution{}/".format(resolution)
if not os.path.exists(res_dir):
    os.makedirs(res_dir)

for filename in os.listdir(directory):
    file = filename.decode("utf-8")
    print(file)
    image = I.ImarisImage(DIRECTORY + "/" + file)
    for i in range(image.get_channel_levels()):
        if not 'image_array' in locals():
            image_array = image.get_two_dim_data(resolution, c = i)
        else:
            image_array += image.get_two_dim_data(resolution, c = i)
    image_array = image_array * (1/image.get_channel_levels())
    scipy.misc.imsave(res_dir + file[:-4] + "{0}combined.jpg".format(i), image_array)
    del image_array
    del image