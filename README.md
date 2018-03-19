# SlideCrop
An automated microscope slide cropping application for various types of file formats (primarily .ims extensions). Provides automatic segmentation of separate regions of interest in an image and produces a series of segmented images over the original image's channel, time and z planes. 

## Getting Started
### Dependencies
SlideCrop has the following dependencies: 
* Numpy
* Scipy
* H5py
* Skimage
* PIL (pillow)
* WXPython
*

## Development
Notes for future development. Wiki pages for more detailed notes. 

### InputImage Interface
Interface for image extensions for microscope slides that can be segmented and cropped. Currently only supporting .ims extensions. 

### ImageCropper Interface
Interface for producing output segmented images. Specifies an implementation for producing specific output extensions. Currently only supporting .tiff extensions. 

### ImageSegmenter Class
Implementation of the current algorithm to identify regions of interest and produce a series of bounding boxes for their cropping. 

## Issues
Here are some aspect to the project for future development if they are deemed necessary
* Improving speeds by multiprocessing the process for each .ims file or for each segmentation in an individual image.
Currently there is base implementation for this except for considerations of protecting against memory crashes due to
excessive multiprocessing (i.e. automatically knowing if there would be enough memory for another process)
* Manual Cropping of single image.
* Front GUI for cropping
* File types other than .IMS
* Extra dimensional data (numerous z-planes or time planes)
* Dynamically chose image segmentation dimensions. Currently the image analysis is done in a fixed, preset size.
* Reducing "Low resolution sliding", the problem of constructing segments in a higher resolution produces rounding
errors for segment box sizes in lower dimensions typically causing segments to lower pixel regions.

