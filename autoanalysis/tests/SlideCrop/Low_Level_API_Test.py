"""
    Script to compare and test the memory and time efficiency of the low and high APIs for HDF and h5py. Following
    features are tested as they are the most common use in SlideCropper:
        - Opening, loading and closing files from Disk
        - Opening subslices into RAM and manipulating datasets
        - Creating new HDF and TIFF files, filling datasets from .IMS files
        - Iterating through file groups and performing operations on the data.
"""

import h5py
import numpy as np
import random
from  memory_profiler import *
from line_profiler import *



FILEDIRECTORY = "E:/"
MAINFILEPATH = (FILEDIRECTORY + "trial.hdf").encode()
EXISTING_FILE = "E:/testing1.hdf".encode()
USED_PATH = "".join((FILEDIRECTORY, "empty", str(random.getrandbits(10)))).encode() # + ".hdf"
OPER_PATH = (FILEDIRECTORY + "empty401235.hdf").encode()

@profile
def opening_and_creating_files():
    # Open existing File
    exisiting_file = h5py.File(EXISTING_FILE)

    # Save into new directory
    exisiting_file.copy(exisiting_file, MAINFILEPATH)
    new_file = h5py.File(MAINFILEPATH)

    #Close First
    new_file.close()
    #Close Second
    exisiting_file.close()

@profile
def create_dataset(path, size):

    F = h5py.h5f.create(path.encode())
    dims = (size, size, size)
    # Create standard, random dataset
    r_space = h5py.h5s.create_simple(dims)

    r_set  = np.random.randint(0, 1000, size=dims, dtype='i')
    r_d_set = h5py.h5d.create(F, "standard".encode(), h5py.h5t.STD_U16LE, r_space)
    r_d_set.write(r_space, r_space, r_set)

    # float dataset
    f_set = np.random.rand(size,size, size)
    f_d_set = h5py.h5d.create(F, "float".encode(), h5py.h5t.IEEE_F32LE, r_space)
    f_d_set.write(r_space, r_space, f_set)
    #del f_set
    #Create New Group
    sub = h5py.h5g.create(F, "subgroup".encode())

    # chunked dataset
    chunk_dim = (10,10,10)
    c_set = np.random.randint(0, 1000, size=dims, dtype='i')

    # Create the "dataset creation property list" and set the chunk size.
    dcpl = h5py.h5p.create(h5py.h5p.DATASET_CREATE)
    dcpl.set_chunk(chunk_dim)

    c_d_set = h5py.h5d.create(sub, "chunked".encode(), h5py.h5t.STD_U16LE, r_space, dcpl)
    c_d_set.write(r_space, r_space, c_set)
    #del c_set

    #Create Nested Group
    nest = h5py.h5g.create(sub, "nested".encode())

    # Compressed Dataset
    dcpl_comp = h5py.h5p.create(h5py.h5p.DATASET_CREATE)
    dcpl_comp.set_chunk((200,200,200))
    dcpl_comp.set_deflate(3)

    co_d_set = h5py.h5d.create(nest, "compressed".encode(), h5py.h5t.STD_U16LE, r_space, dcpl_comp)
    #co_d_set.write(r_space, r_space, r_set)
    F.close()

#  Typical operations when performing analysis of IMS file on SlideCrop
#@profile
def slicing_and_operating_datasets(PATH):
    """
    Terms used in dataspace slabbing
        - offset: Initial offset to start data collection
        - Count: Number of Block to be selected from the data
        - Stride: Direction vector to move selection point after each selection of a block. 
            For (x,y) moves (x,o) selects a block, then (0,y) and selects another. 
        - Block: Size of a block to be selected
    
    Used in .select_hyperslab(start, count, stride, block)
    """

    file = h5py.h5f.open(PATH.encode())

    #Slicing sequential data
    r_set= h5py.h5d.open(file, "standard".encode())
    data_space = r_set.get_space()

    slicer1 = np.zeros((1,400))
    slicer2 =np.zeros((1,400, 1))
    slicer3 = np.zeros((400,1,1))
    slicer4 = np.zeros((400, 20, 20))
    slicer5 = np.zeros((20,20, 400))

    #r_set[0,0,:]
    data_space.select_hyperslab((0, 0, 0), (1, 1, 1), (1, 1, 1), (1,1,r_set.shape[2]))
    r_set.read(h5py.h5s.ALL, data_space, slicer1)

    # r_set[0,:,0]
    data_space.select_hyperslab((0,0,0), (1, 1, 1), (1, 1, 1), (1, r_set.shape[1], 1))
    r_set.read(h5py.h5s.ALL, data_space, slicer2)

    #r_set[:,0,0]
    data_space.select_hyperslab((0,0,0), (1, 1, 1), (1, 1, 1), (r_set.shape[0], 1,1))
    r_set.read(h5py.h5s.ALL, data_space, slicer3)

    #r_set[:,1:20,1:20]
    data_space.select_hyperslab((0,0,0), (r_set.shape[0], 1, 1), (1,0,0), (1,19,19))
    r_set.read(h5py.h5s.ALL, data_space, slicer4)

    #r_set[1:20,1:20, :]
    data_space.select_hyperslab((0, 0, 0), (1, 1, r_set.shape[2]), (0, 0, 1), (1, 19, 19))
    r_set.read(h5py.h5s.ALL, data_space, slicer5)

    """
    #Slicing chunked Data
    sub = h5py.h5g.open(file, "subgroup".encode())
    ch_set = h5py.h5d.open(sub, "chunked".encode())
    slicech1 = ch_set[0, 0, :]
    slicech2 = ch_set[0, :, 0]
    slicech3 = ch_set[:, 0, 0]
    slicech4 = ch_set[:, 1:20, 1:20]
    slicech5 = ch_set[1:20, 1:20, :]


    # Slicing compressed Data

    c_group = h5py.h5g.open(sub, "nested".encode())
    c_set = h5py.h5g.open(c_group, "compressed".encode())
    slicec1 = c_set[0, 0, :]
    slicec2 = c_set[0, :, 0]
    slicec3 = c_set[:, 0, 0]
    slicec4 = c_set[:, 1:20, 1:20]
    slicec5 = c_set[1:20, 1:20, :]
    """
    file.close()

#  Typical operations for saving and sending data into .tiff file formats
def tiff_and_ims_operations():
    pass

#  Typical operations when iterating over grouped datasets in IMS
def groups_iteration():
    pass

# Typical operations when cropping in SlideCrop application
def cropping_IMS_to_hdf():
    pass

@profile
def test(path):
    file = h5py.File(path)
    r_set = file.get("standard")
    r_set_c = r_set[:,:,:]
    del r_set_c

@profile
def run(PATH):
    file = h5py.h5f.open(PATH.encode())
    # Slicing sequential data
    r_set = h5py.h5d.open(file, "standard".encode())
    data_space = r_set.get_space()
    slicer1 = np.zeros((1, 400))
    slicer2 = np.zeros((1, 400, 1))
    slicer3 = np.zeros((400, 1, 1))
    slicer4 = np.zeros((400, 20, 20))
    slicer5 = np.zeros((20, 20, 400))
    # r_set[0,0,:]
    data_space.select_hyperslab((0, 0, 0), (1, 1, 1), (1, 1, 1), (1, 1, r_set.shape[2]))
    r_set.read(h5py.h5s.ALL, data_space, slicer1)

    file.close()


if __name__ == '__main__':
    #slicing_and_operating_datasets("E:/lowtesting111.hdf")
     run("E:/low30.hdf")
