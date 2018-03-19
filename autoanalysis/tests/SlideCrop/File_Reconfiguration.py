import h5py
import numpy as np
import timeit as T
import random
#from line_profiler import *
from memory_profiler import *


FILEPATH = "E:/mockfunction.hdf"
def import_hdf_File():
    return h5py.File(FILEPATH, "r+")


"""
    The purpose of this test, compress_file is to determine the possibility of changing the structure of the hdf file
    starting from the .IMS file to a .hdf file that will be more effective at being chunked, hence cropped when chunked.
    Chunking will change the way the array is stored in memory, so instead of a sequential order (row by row,
    plane by plane), a specified "chunk" can be stored together. A Chunk can be thought as a cube in 3D. For example a 
    chunk of (2x2x2). Instead of a sequential ordering, each chunk is stored sequentially. This can mean for some
    slicing patterns (such as slicing a ROI over three colour planes) chunking will require less reads from disk and
    less computation to apply a crop on a ROI. If this format transformation is efficient it can be done when the file
    is loaded in. Then, when cropping occurs,slicing can be done more effectively by chunk. Although technically, the
    method below makes four dimensional images, most .IMS created wont have a time dimension, hence will be (1,c,x,y) 
    The method below iterates through the desired array of Resolution levels, res_Levels and will create a 4D image to
    add as a dataset to a hdf file that will be saved at out_path path. 
"""
@profile
def compress_file(res_Levels, out_path, filepath):
    for resLev in res_Levels:
        file = h5py.File(filepath, "r+")
        for timepoint in range(len(file["DataSet/ResolutionLevel " + str(resLev)])):
            for channel in range(
                    len(file["DataSet/ResolutionLevel " + str(resLev) + "/TimePoint " + str(timepoint) + "/"])):

                #  Data path for this iteration of resolution, channel and timepoint
                channel_data_path = "DataSet/ResolutionLevel " + str(resLev) + "/TimePoint " + str(
                    timepoint) + "/Channel " + str(channel) + "/Data"

                # if channel==0, create time_data variable
                if not channel:
                    time_data = file[channel_data_path]
                #  else simply add this channel as another plane in time_data
                else:

                    time_data = np.dstack((time_data, file[channel_data_path]))

            # first timepoint (timepoint ==0) make this resolution's data equal to the data image at timepoint0
            if not timepoint:
                resLev_data = time_data
            #  otherwise stack the new timepoint onto the existing image (Create )
            else:

                resLev_data = np.concatenate([resLev_data, time_data], axis=0)

        #  with reslevel_data, on each iteration open the output hdf5 and store the reslevel as its own reslevel dataset,
        #  then close to save RAM.
        file.close()
        out_file = h5py.File(out_path)
        out_file.create_dataset("resolution_level_" + str(resLev), data=resLev_data) # , compression="gzip", compression_opts=9)
        resLev_data = []
        time_data = []

        out_file.close()


def run_compress_file():
    result_dict = {}
    testing_array =  [[7],[6,7],[5,6,7],[4,5,6,7],[3,4,5,6,7],[2,3,4,5,6,7]]#,[1,2,3,4,5,6,7]] # ,[0,1,2,3,4,5,6,7]]
    for res_Levels in testing_array:
        output = OUTPUTPATH + str(res_Levels) + "hdf"

        result = T.Timer(lambda: compress_file(res_Levels, output)).timeit(1)
        print(str(res_Levels) + ": " + str(result))
        result_dict[str(res_Levels)] = (result)
    return result_dict


if __name__ == '__main__':
    run_compress_file()

"""
    Results from compress_file are as followed (individual file times are difference in arrayed resolutions): 
    7 :  0.027      7: 0.027
    6-7: 0.098      6: 0.071
    5-7: 0.404      5: 0.306
    4-7: 1.798      4: 1.394
    3-7: 7.58       3: 5.782
    2-7: 30.00      2: 22.42
    1-7: 156.47     1: 126.47
    0-7:  not enough memory to test 0-7 or even just 0
"""

"""
    [7]: 0.027910292211821147
    [6]: 0.20617825676834384
    [5]: 0.6967104594085974
    [4]: 2.275472083643173
    [3]: 7.130865532552523
    [2]: 25.805064140303475
    [1]: 121.89846947772466
"""
"""
    [7]: 0.025695308133768618
    [6, 7]: 0.09464625099483015
    [5, 6, 7]: 0.3888985819063605
    [4, 5, 6, 7]: 1.7836597806848535
    [3, 4, 5, 6, 7]: 8.060953114926324
    [2, 3, 4, 5, 6, 7]: 33.40561499396804
    [1, 2, 3, 4, 5, 6, 7]: 157.36506977573052
"""

"""
    Results for using np.concatenate and np.stack on varying size n x n matrices for a 100 000 iterations

    |   n   |  Concatenate  | Stack | 
    |   10  |     0.16      |  0.81 | 
    |   50  |     0.39      | 1.16  | 
    |  100  |     1.23      | 2.19  | 
    |  500  |     171.07    | 177.0 |  * 10 times the time for 10 000 iteration 
    | 1000  |     774.7     |790.15 |  * 1000 times the time for 100 iterations

"""

"""

New Times with memory erasing lines in (reinstantiating lists to empty lists)

[7]: 0.08187914203101923
[6, 7]: 0.23220891837650576
[5, 6, 7]: 0.6880336298163721
[4, 5, 6, 7]: 1.8122360133123465
[3, 4, 5, 6, 7]: 5.393509158069653
[2, 3, 4, 5, 6, 7]: 19.16229577332063
[1, 2, 3, 4, 5, 6, 7]: 87.89015727938481
"""

"""
Testing with and without Ram improvements (as above) in batch averages of three 

|        Set        | Without |  With  | With and Compressed | 
|[2, 3, 4, 5, 6, 7] | 38.19   | 15.77  | 

"""


"""
Clearly Reconfiguring the file in this fashion is unusable for two reasons. Firstly, this operation for cannot
successful perform on all resolution levels. In fact, there isn't sufficient RAM to even perform it on res_Levels =[0].
This is based on a 16 GB RAM. Secondly the time required for 1-7 is a problem implementing at either the opening,
segmenting or cropping of the file. 
"""
