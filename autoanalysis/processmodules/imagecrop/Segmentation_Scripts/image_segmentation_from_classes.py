import version_two.src.SlideCrop.ImarisImage as I
from version_two.src.SlideCrop.ImageSegmenter import ImageSegmenter as seg

from autoanalysis.processmodules.imagecrop.TIFFImageCropper import TIFFImageCropper


def main():
    FILE = "E:/testdata2/170818_APP_1878 UII_BF~B.ims" # "E:/testdata1/AT8 tg124m 6~B.ims"  # "E:/testdata2/170818_APP_1878 UII_BF~B.ims" # "E:/testdata1/AT8 tg124m 6~B.ims" #
    image = I.ImarisImage(FILE)

    channelled_image = image.get_multichannel_segmentation_image()

    segmentations = seg.segment_image(channelled_image)

    image.close_file()
    TIFFImageCropper.crop_input_images(FILE, segmentations, "E:/FirstTest")



if __name__ == '__main__':
    main()


