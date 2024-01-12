from sklearn.cluster import KMeans
import numpy as np
import cv2

def cluster_features(features, num_clusters=70):
    features = np.array(features)
    kmeans = KMeans(n_clusters=num_clusters, random_state=0)
    kmeans.fit(features)
    return kmeans.cluster_centers_, kmeans.labels_

def sift_descriptor(image, sift):
    k = 100
    keypoints = sift.detect(image, None)
    size_around_centroids = [[] for _ in range(k)]
    res_around_centroids = [[] for _ in range(k)]
    octave_around_centroids = [[] for _ in range(k)]
    angle_around_centroids = [[] for _ in range(k)]
    if keypoints is not None:
        pt_keypoint = [item.pt for item in keypoints]
        if (len(pt_keypoint) < k):
            raise ValueError("Number of samples should be greater than or equal to 100")
        res_keypoint = [item.response for item in keypoints]
        octave_keypoint = [item.octave for item in keypoints]
        size_keypoint = [item.size for item in keypoints]
        anggle_keypoint = [item.angle for item in keypoints]
        pt_centroids, pt_labels = cluster_features(pt_keypoint, k)
        fixed_keypoints = [] 

        for j in range(len(pt_keypoint)):
            cluster_label = pt_labels[j]
            size_around_centroids[cluster_label].append(size_keypoint[j])
            res_around_centroids[cluster_label].append(res_keypoint[j])
            octave_around_centroids[cluster_label].append(octave_keypoint[j])
            angle_around_centroids[cluster_label].append(anggle_keypoint[j])
        for cluster_idx, sizes, octaves, responses, angles in zip(np.arange(0,k), size_around_centroids, octave_around_centroids, res_around_centroids, angle_around_centroids):
            centroid = pt_centroids[cluster_idx]
            size = np.mean(sizes)
            oct = np.max(octaves)
            res = np.max(responses)
            angle = np.max(angles)
            temp_fixeds_keypoint = cv2.KeyPoint(x=centroid[0], y=centroid[1], angle=angle, size=size, response=res, octave=oct, class_id=cluster_idx)
            fixed_keypoints.append(temp_fixeds_keypoint)
        fixed_keypoints = np.array(fixed_keypoints)
        fixed_keypoints, descriptors = sift.compute(image, fixed_keypoints)
    return fixed_keypoints, descriptors

def euclid_distance(descriptor1, descriptor2):
    descriptor1 = np.array(descriptor1)
    descriptor2 = np.array(descriptor2)
    return np.linalg.norm(descriptor1 - descriptor2)

def match_best_image(test_image, train_descriptors, train_keypoints, class_labels, sift):
    best_match_class = None
    min_sum_distance = float('inf')
    for class_label, train_descriptor, train_keypoint in zip(class_labels, train_descriptors, train_keypoints):
        _, test_desc = sift.compute(test_image, train_keypoint)
        sum_distance = euclid_distance(test_desc, train_descriptor)
        if sum_distance < min_sum_distance:
            min_sum_distance = sum_distance
            best_match_class = class_label
    return best_match_class
