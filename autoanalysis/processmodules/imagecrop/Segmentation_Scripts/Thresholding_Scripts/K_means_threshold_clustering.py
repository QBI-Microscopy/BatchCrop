import scipy.ndimage as nd
import numpy as np

def closest_index(ndarray, value):
    """
    Returns the index in ndarray of the number which is closest to value. 
    """
    return np.argmin(np.abs(ndarray - value))


K_Clusters = 10
BGPCOUNT = 40  #  Background Pixel Count: Pixel length of the squares to be used in the image corners.
SENSITIVITY_THRESHOLD = 0.01
image = nd.imread("E:/test2.jpg")
x_dim = image.shape[0]
y_dim = image.shape[1]


"""
Channel Selection
"""
if image.ndim == 3:
    # Find mean intensity for each channel
    # Averaged across axis separately. Shape = (x,y,3) -> (x -> 3) -> (1,3)
    channel_mean_vector = np.mean(np.mean(image, axis=1), axis=0)

    #  Find x & y indices for the four corner squares of size BGPCOUNT * BGPCOUNT
    background_index_x_list = []
    background_index_y_list = []
    for i in range(BGPCOUNT):
        background_index_x_list.append(i);
        background_index_y_list.append(i);
        background_index_x_list.append(x_dim - (i + 1));
        background_index_y_list.append(y_dim - (i + 1));

    # Create a image vector with pixel values from the 2D corners of all channels. Used as a background intensity mean.
    background_vector = image[background_index_x_list, background_index_y_list, :];

    background_channel_mean_vector = np.mean(np.mean(background_vector, axis=1), axis=0)

    # Choose channel for clustering based on maximum difference in background and average intensity
    max_difference_channel = np.abs(background_channel_mean_vector - channel_mean_vector)
    clustering_channel = np.argmax(max_difference_channel)
    channel_image = image[:, :, clustering_channel]
else:
    # if 2D, just choose the only channel possible
    channel_image = image.copy()

"""
Histogram creation and variable definitions
"""
# Iterate through pixels of image and use histogram as tally where index is the intensity 0-255 inclusive
histogram = np.zeros((256))
index_histogram = -1 * np.ones((256))
for pixel in channel_image:
    histogram[pixel] += 1

# Initiate k clusters equidistant on the domain of the channel intensity
cluster_vector = np.linspace(np.min(channel_image), np.max(channel_image), num=K_Clusters)
cluster_temp_vector = cluster_vector.copy()
cluster_vector_totals = np.zeros(K_Clusters)
cluster_vector_count = np.zeros(K_Clusters)

"""
K-means iteration
"""
while (1):

    # Find closest cluster for each pixel intensity in histogram
    index_histogram = [closest_index(cluster_vector, i) for i in range(256)]

    # for each cluster, find mean of clustered pixel intensities
    # histogram[i] is number of pixels at intensity i
    for k in range(K_Clusters):
        weighted_mean_sum = sum(ind * histogram[ind] for ind in range(256) if index_histogram[ind] == k)
        pixel_count = sum(histogram[ind] for ind in range(256) if index_histogram[ind] == k)
        cluster_temp_vector[k] = weighted_mean_sum / pixel_count

    # If all clusters change less than the threshold -> finish iteration
    if (np.abs(cluster_vector / cluster_temp_vector - 1) < SENSITIVITY_THRESHOLD).all():
        cluster_vector = cluster_temp_vector
        break
    cluster_vector = cluster_temp_vector.copy()

print("Final Cluster Intensities: {}".format(cluster_vector))
