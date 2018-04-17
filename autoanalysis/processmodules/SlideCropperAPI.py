import argparse
import logging
import os
import sys
from os.path import join
from collections import OrderedDict
from autoanalysis.processmodules.imagecrop.ImageSegmenter import ImageSegmenter
from autoanalysis.processmodules.imagecrop.InputImage import InputImage
from autoanalysis.processmodules.imagecrop.TIFFImageCropper import TIFFImageCropper
import autoanalysis.processmodules.imagecrop.ImarisImage as I

class SlideCropperAPI(object):
    """
    Main Class for using SlideCropper functionality. All methods are class method based.     
    """
    def __init__(self, datafile,outputdir,showplots=False):
        # Load data
        try:
            if os.access(datafile,os.R_OK):
                ext_check = InputImage.get_extension(datafile)
                if ext_check != ".ims":
                    raise TypeError("{} is currently not a supported file type".format(ext_check))
                self.data = datafile
            else:
                self.data = None
                raise IOError('Unable to access datafile: {0}'.format(datafile))
            msg = "SlideCropper: Image file loaded from %s" % self.data
            print(msg)
            # Output
            if os.access(outputdir, os.R_OK):
                self.outputdir = outputdir
            else:
                raise IOError('Unable to access output directory: {0}'.format(outputdir))
            # Set config defaults
            self.cfg = self.getConfigurables()
            self.showplots = showplots
        except IOError as e:
            print(e.args[0])
            raise e
        except Exception as e:
            print(e.args[0])
            raise e

    def getConfigurables(self):
        '''
        List of configurable parameters in order with defaults
        :return:
        '''
        cfg = OrderedDict()
        cfg['BORDER_FACTOR']=1.3
        cfg['IMAGE_TYPE'] = '.ims'
        cfg['CROPPED_IMAGE_FILES'] = 'cropped'
        cfg['SEND_TO_CROP_PANEL'] = True
        return cfg

    def setConfigurables(self,cfg):
        '''
        Merge any variables set externally
        :param cfg:
        :return:
        '''
        if self.cfg is None:
            self.cfg = self.getConfigurables()
        for cf in cfg.keys():
            self.cfg[cf]= cfg[cf]
        cfg['CROPPED_IMAGE_FILES'] = 'cropped'
        cfg['SEND_TO_CROP_PANEL'] = True
        print("Config loaded")


    def segment_run(self):
        border_factor = float(self.cfg['BORDER_FACTOR'])
        image = I.ImarisImage(self.data)
        segmentations = ImageSegmenter.segment_image(border_factor, image.get_multichannel_segmentation_image())
        image.close_file()
        return segmentations

    def crop_run(self, segments):
        if self.data is not None:
            TIFFImageCropper.crop_input_images(self.data, segments, self.outputdir)
        else:
            raise ValueError('Error: Run failed: Image not loaded')


    def run(self):
        if self.data is not None:
            segments = self.segment_run()
            self.crop_run(segments)
        else:
            raise ValueError('Error: Run failed: Image not loaded')
        print("COMPLETE: done API crop running ")



    def _loadImage(self,file_path):
        '''
        Image files are very large and often archived. This will bring them back ready for processing.
        :param file_path: full path filename
        :return: filename from image obj
        '''
        image = None
        try:
            image = I.ImarisImage(file_path)
            print('Image loaded: ', image.get_filename())
            return image.get_filename()
        except IOError as e:
            print('ERROR: Unable to load image: ', file_path)
        finally:
            if image is not None:
                image.close_file()



    def crop_single_image(self, file_path, output_path):
        """
        Encapsulation method for cropping an individual image.
        :param file_path: String path to the desired file. Assumed to be .ims extension
        :param output_path: 
        :return: 
        """

        border_factor = float(self.cfg['BORDER_FACTOR'])
        image = I.ImarisImage(file_path)
        segmentations = ImageSegmenter.segment_image(border_factor, image.get_multichannel_segmentation_image())
        image.close_file()
        TIFFImageCropper.crop_input_images(file_path, segmentations, output_path)


    @classmethod
    def crop_all_in_folder(cls, folder_path, output_path, concurrent = False):
        """
        Handler to crop all images in a given folder. Will ignore non-compatible file types 
        :param folder_path: Path to the files wanted to be 
        :param output_path: Folder path to create all new folders and images in. 
        :param concurrent: Whether to multiprocess each file. (Current has not been tested) 
        """
        if concurrent:
            pid_list = []

        for filename in os.listdir(folder_path):
            file_path = "{}/{}".format(folder_path, filename)
            if concurrent:
                pid_list.append(SlideCropperAPI.spawn_crop_process(file_path, output_path))
            else:
                SlideCropperAPI.crop_single_image(file_path, output_path)

        if concurrent:
            for proc in pid_list:
                proc.join()



"""
    Testing Methods for API. Use above methods directly 
"""
def main(args):
    """
    Standard wrapper for API usage. Sets API up to call innerMain function. 
    """
    logfile = args.logfile
    logging.basicConfig(filename=logfile, level=logging.DEBUG, format=FORMAT)
    logging.captureWarnings(True)

    parent_pid = os.getpid()
    # Only log for first process created. Must check that process is the original.
    if os.getpid() == parent_pid:
        print("\nSlideCropper started with pid: {}".format(os.getpid()))
    if args.datafile is not None:
        SlideCropperAPI.crop_single_image(join(args.inputdir,args.datafile), args.outputdir)
    else:
        SlideCropperAPI.crop_all_in_folder(args.inputdir, args.outputdir)
    if os.getpid() == parent_pid:
        print("SlideCropper ended with pid: {}\n".format(os.getpid()))

def create_parser():
    """
    Create commandline parser
    :return:
    """

    parser = argparse.ArgumentParser(prog=sys.argv[0],
                                     description='''\
                Crops serial section images in large image files into separate images
                
                 ''')
    parser.add_argument('--datafile', action='store', help='Data file', default="AT8 sc2005f 32~B.ims")
    parser.add_argument('--outputdir', action='store', help='Output directory', default="Z:\\Micro Admin\\Jack\\output")
    parser.add_argument('--inputdir', action='store', help='Input directory', default="Z:\\Micro Admin\\Jack\\Adam")
    parser.add_argument('--logfile', action='store', help='Input directory', default="E:/SlideCropperLog.txt")
    parser.add_argument('--imagetype', action='store', help='Type of images to processed', default='.ims')

    return parser

####################################################################################################################
if __name__ == "__main__":

    parser = create_parser()
    args = parser.parse_args()
    main(args)
