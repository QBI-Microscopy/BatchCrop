import logging
import os
from os.path import basename, splitext, join, exists

import javabridge
import bioformats.formatreader

import autoanalysis.processmodules.imagecrop.ImarisImage as I

class BioformatsImageReader(object):
    def __init__(self, imgfile, output_path):

        self.imgfile = imgfile
        try:
            self.image = I.ImarisImage(self.imgfile)
            if not os.path.isdir(output_path):
                raise IOError('Invalid output directory: ', output_path)
            else:
                # create unique output directory from image filename
                filename = basename(imgfile)
                new_folder = splitext(filename)[0]
                image_folder = join(output_path, new_folder)
                if not os.path.isdir(image_folder):
                    os.makedirs(image_folder)

                self.output_folder = image_folder
            javabridge.jutil.attach()
            self.basicmeta = javabridge.jutil.to_string(
                bioformats.formatreader.make_iformat_reader_class().getMetadata(bioformats.ImageReader(imgfile).rdr)).split(',')
            self.basicmeta = sorted(self.basicmeta)
            self.omemeta = bioformats.get_omexml_metadata(imgfile).split("></")
            self.omemeta1 = self.omemeta[0].split(".xsd")
            self.omemeta2 = self.omemeta[1:]
            javabridge.jutil.detach()
        except Exception as e:
            raise (e)


    def make_metadata(self):
        rtn = 0
        outputfile = join(self.output_folder, basename(self.image.get_name()) + "_metadata" + ".txt")
        if exists(outputfile):
            os.remove(outputfile)

        with open(outputfile, 'w') as f:
            for item in self.basicmeta:
                f.write("%s\n" % item)
            for item in self.omemeta1:
                f.write("%s\n" % item)
            for item in self.omemeta2:
                f.write("%s\n" % item)

        rtn = 1
        msg = "Finished writing image metadata"
        print(msg)
        logging.info(msg)
        return rtn