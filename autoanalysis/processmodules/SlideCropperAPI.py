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
    def __init__(self, datafile, outputdir):
        # Set config values
        self.cfg = self.getConfigurables()
        self.status = 0
        self.imgfile = None
        # Load data
        if os.access(datafile,os.R_OK):
            ext_check = InputImage.get_extension(datafile)
            if ext_check != self.cfg['IMAGE_TYPE']: #".ims":
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



    def getConfigurables(self):
        '''
        List of configurable parameters in order with defaults
        :return:
        '''
        cfg = OrderedDict()
        cfg['BORDER_FACTOR']=1.3
        cfg['IMAGE_TYPE'] = '.ims'
        cfg['CROPPED_IMAGE_FILES'] = 'cropped'
        cfg['MAX_MEMORY'] = 5000000000 #5GB
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
        logging.debug("SlideCropperAPI:Config loaded")


    def isRunning(self):
        return self.status == 1

    def run(self):
        self.status = 1
        try:
            if self.imgfile is not None:
                # Load to Image Cropper
                border_factor = float(self.cfg['BORDER_FACTOR'])
                memu = int(self.cfg['MAX_MEMORY'])
                tic = TIFFImageCropper(self.imgfile, border_factor, self.outputdir, memu)
                pid_list = tic.crop_input_images()
                msg = 'Run: cropping done - new images in %s [%d pages]' % (self.outputdir,pid_list)
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
    parser.add_argument('--datafile', action='store', help='Data file', default="NG_GAD67_GFP16~B.ims")
    parser.add_argument('--outputdir', action='store', help='Output directory', default="Z:\\Micro Admin\\Jack\\output")
    parser.add_argument('--inputdir', action='store', help='Input directory', default="Z:\\Micro Admin\\Jack\\NG_Gad")
    parser.add_argument('--imagetype', action='store', help='Type of images to processed', default='.ims')

    return parser


####################################################################################################################
if __name__ == "__main__":
    from autoanalysis.gui.ImageViewer import ImageViewer
    from glob import iglob
    import wx
    from os.path import basename,splitext

    parser = create_parser()
    args = parser.parse_args()
    slidecropper = SlideCropperAPI(join(args.inputdir, args.datafile), args.outputdir)
    slidecropper.run()
    # check output with ImageViewer
    imgapp = wx.App()
    imglist = [x for x in iglob(join(args.outputdir,splitext(basename(args.datafile))[0], "*.tiff"))]
    frame = ImageViewer(imglist)
    imgapp.MainLoop()
