import argparse
import logging
import os
import sys
from collections import OrderedDict
from os.path import join, splitext

from autoanalysis.processmodules.imagecrop.TIFFImageCropper import TIFFImageCropper


class SlideCropperAPI(object):
    """
    Main Class for using SlideCropper functionality. All methods are class method based.     
    """

    def __init__(self, datafile, outputdir):
        # Set config values
        self.cfg = self.getConfigurables()
        self.status = 0
        self.imgfile = None
        # Load data
        if os.access(datafile, os.R_OK):
            ext_check = self.get_extension(datafile)
            if ext_check.lower() != ".ims":
                raise TypeError("{} is currently not a supported file type".format(ext_check))
            self.imgfile = datafile
            msg = "Image file loaded from %s" % self.imgfile
            print(msg)
            logging.info(msg)
        else:
            raise IOError('Unable to access datafile: {0}'.format(datafile))

        # Output
        if os.access(outputdir, os.W_OK):
            self.outputdir = outputdir
        else:
            raise IOError('Unable to write to output directory: {0}'.format(outputdir))

    def get_extension(self, file_path):
        """
        :return: The extension of the inputted file.
        """
        path_split = splitext(file_path)
        return path_split[1]

    def getConfigurables(self):
        '''
        List of configurable parameters in order with defaults
        :return:
        '''
        cfg = OrderedDict()
        cfg['BORDER_FACTOR'] = 3  # %of pixels for border
        #cfg['IMAGE_TYPE'] = '.ims'  # File type of original
        cfg['CROPPED_IMAGE_FILES'] = 'cropped'  # output directory
        cfg['MAX_MEMORY'] = 80  # % of memory to quit
        cfg['LIGHT_BG_THRESHOLD'] = 'auto'
        cfg['DARK_BG_THRESHOLD'] = 'auto'
        cfg['OFFSET'] = 0  # range from 0-2 smaller is less shift
        cfg['RESOLUTION'] = 'High'  # 'High', 'Low', or 'Both'
        return cfg

    def setConfigurables(self, cfg):
        '''
        Merge any variables set externally
        :param cfg:
        :return:
        '''
        if self.cfg is None:
            self.cfg = self.getConfigurables()
        for cf in cfg.keys():
            self.cfg[cf] = cfg[cf]
        logging.debug("SlideCropperAPI:Config loaded")

    def isRunning(self):
        return self.status == 1

    def run(self):
        self.status = 1
        try:
            if self.imgfile is not None:
                # Load to Image Cropper
                border_factor = int(self.cfg['BORDER_FACTOR'])
                memmax = int(self.cfg['MAX_MEMORY'])
                lightbg = self.cfg['LIGHT_BG_THRESHOLD']
                darkbg = self.cfg['DARK_BG_THRESHOLD']
                offset = float(self.cfg['OFFSET'])
                resolution = self.cfg['RESOLUTION']
                tic = TIFFImageCropper(self.imgfile, border_factor, self.outputdir, memmax, lightbg, darkbg, offset, resolution)
                pid_list = tic.crop_input_images()
                tic.image.close_file()
                msg = 'Run: cropping done - new images in %s [%d pages]' % (self.outputdir, pid_list)
                logging.info(msg)
                print(msg)
            else:
                raise ValueError('Run failed: Image not loaded')

        except Exception as e:
            raise e
        finally:
            self.status = 0
            logging.info("Run finished")


"""
    Testing Methods for API.
"""


def create_parser():
    """
    Create commandline parser
    :return:
    """

    parser = argparse.ArgumentParser(prog=sys.argv[0],
                                     description='''\
                Crops serial section images in large image files into separate images
                
                 ''')
    parser.add_argument('--datafile', action='store', help='Data file', default="145.1~B.ims")
    parser.add_argument('--outputdir', action='store', help='Output directory', default="C:\\Users\\uqathom9\\Documents\\Microscopy\\BatchCrop")
    parser.add_argument('--inputdir', action='store', help='Input directory', default="C:\\Users\\uqathom9\\Desktop")
    parser.add_argument('--imagetype', action='store', help='Type of images to processed', default='.ims')

    return parser


####################################################################################################################
if __name__ == "__main__":
    from autoanalysis.gui.ImageViewer import ImageViewer
    from glob import iglob
    import wx
    from os.path import basename, splitext

    parser = create_parser()
    args = parser.parse_args()
    slidecropper = SlideCropperAPI(join(args.inputdir, args.datafile), args.outputdir)
    slidecropper.run()
    # check output with ImageViewer
    imgapp = wx.App()
    imglist = [x for x in iglob(join(args.outputdir, splitext(basename(args.datafile))[0], "*.tiff"))]
    frame = ImageViewer(imglist)
    imgapp.MainLoop()
