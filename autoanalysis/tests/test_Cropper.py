from os.path import join

import unittest2 as unittest

from autoanalysis.processmodules.SlideCropperAPI import SlideCropperAPI, create_parser


class TestCropper(unittest.TestCase):
    def setUp(self):
        parser = create_parser()
        args = parser.parse_args()
        # TEST DATA
        self.datafile = join(args.inputdir,args.datafile)
        self.outputdir = join(args.outputdir)
        fd = SlideCropperAPI(self.datafile, self.outputdir)
        cfg = fd.getConfigurables()
        cfg['IMAGE_TYPE'] = args.imagetype

        for c in cfg.keys():
            print("config set: ", c, "=", cfg[c])
        fd.setConfigurables(cfg)
        self.fd = fd

    def test_loadimage(self):
        imgdata = self.fd._loadImage(self.datafile)
        print(imgdata)
        self.assertIsNotNone(imgdata)

