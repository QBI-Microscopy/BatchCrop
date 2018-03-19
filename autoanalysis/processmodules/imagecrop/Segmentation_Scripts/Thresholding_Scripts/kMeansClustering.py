import scipy.ndimage as nd
import numpy as np
import matplotlib.pyplot as plt

BGPCOUNT = 3
image = nd.imread("E:/test.jpg")
x_dim_image_edge = image.shape[0]
y_dim_image_edge = image.shape[1]

# mean intensity for each channel
# Averaged across axis separately. Shape = (x,y,3) -> (x -> 3) -> (1,3)
channel_mean_vector  = np.mean(np.mean(image, axis =1),axis =0 )


# Create a image vector with pixel values from the 2D corners of all channels. Used as a background intensity mean.
background_vector = np.zeros((2*BGPCOUNT,2*BGPCOUNT,3))
background_vector[0:BGPCOUNT, 0:BGPCOUNT, :] = image[0:BGPCOUNT, 0:BGPCOUNT, :]
background_vector[0:BGPCOUNT, BGPCOUNT:2*BGPCOUNT, :] = \
                image[0:BGPCOUNT, y_dim_image_edge-BGPCOUNT:y_dim_image_edge, :]

background_vector[BGPCOUNT:2*BGPCOUNT, 0:BGPCOUNT, :] = \
                image[x_dim_image_edge-BGPCOUNT:x_dim_image_edge, 0:BGPCOUNT, :]
background_vector[BGPCOUNT:2*BGPCOUNT, BGPCOUNT:2*BGPCOUNT, :] = \
                image[x_dim_image_edge-BGPCOUNT:x_dim_image_edge, y_dim_image_edge-BGPCOUNT:y_dim_image_edge, :]

background_channel_mean_vector = np.mean(np.mean(background_vector, axis =1),axis =0 )


#Choose channel for clustering based on maximum background-average intensity difference.
max_difference_channel = np.abs(background_channel_mean_vector - channel_mean_vector)
clustering_channel = np.argmax(max_difference_channel)
channel_image = image[:,:,clustering_channel]

# Set initial background, Ub and foreground Uo  intensity means as averages previously found.
Ub = background_channel_mean_vector[clustering_channel]
Uo = channel_mean_vector[clustering_channel]
Ua = (Ub + Uo)/2
print("Ub: {}".format(Ub))
print("Uo: {}".format(Uo))
print("Ua: {}".format(Ua))

for i in range(20):
    Ua_temp = np.mean(channel_image[np.where((abs(channel_image - Ua) < abs(channel_image - Uo)) & (abs(channel_image - Ua) < abs(channel_image - Ub)))])
    Ub_temp = np.mean(channel_image[np.where((abs(channel_image - Ub) < abs(channel_image - Uo)) & (abs(channel_image - Ub) < abs(channel_image - Ua)))])
    Uo_temp = np.mean(channel_image[np.where((abs(channel_image - Uo) < abs(channel_image - Ub)) & (abs(channel_image - Uo) < abs(channel_image - Ua)))])
    print("\nIteration {}".format(i))
    print("Ub: {}".format(Ub_temp))
    print("Uo: {}".format(Uo_temp))
    print("Ua: {}".format(Ua_temp))
    print("Ua difference: {}".format(Ua_temp-Ua))
    print("Ub difference: {}".format(Ub_temp-Ub))
    print("Uo difference: {}".format(Uo_temp-Uo))
    Ub = Ub_temp
    Uo = Uo_temp
    Ua = Ua_temp
binary_image = np.zeros((x_dim_image_edge, y_dim_image_edge))
binary_image[np.where((abs(channel_image-Uo) < abs(channel_image - Ub)) & (abs(channel_image-Uo) < abs(channel_image - Ub)))] = Uo
binary_image[np.where((abs(channel_image-Ua) < abs(channel_image - Ub)) & (abs(channel_image-Ua) < abs(channel_image - Uo)))] = Ua
binary_image[np.where((abs(channel_image-Ub) < abs(channel_image - Ua)) & (abs(channel_image-Ub) < abs(channel_image - Uo)))] = Ub
plt.imshow(binary_image)
plt.show()