import numpy as np
import scipy as sp
import dionysus as d
from itertools import combinations

def complex_builder(cover, data, p):
    vertices = list(cover.keys())
    
    simplices = []

    for i,j in combinations(vertices, 2):
        centroid_i, radius_i = cover[i]
        centroid_j, radius_j = cover[j]

        dist_vec_i = np.linalg.norm(centroid_i - data, axis = 1)
        dist_vec_j = np.linalg.norm(centroid_j - data, axis = 1)

        overlap_i = (dist_vec_i < radius_i).astype(int)
        overlap_j = (dist_vec_j < radius_j).astype(int)

        overlap_count = (overlap_i + overlap_j == 2).sum()

        if overlap_count > p:
            simplices.append([i,j])

    for i,j,k in combinations(vertices, 3):
        centroid_i, radius_i = cover[i]
        centroid_j, radius_j = cover[j]
        centroid_k, radius_k = cover[k]

        dist_vec_i = np.linalg.norm(centroid_i - data, axis = 1)
        dist_vec_j = np.linalg.norm(centroid_j - data, axis = 1)
        dist_vec_k = np.linalg.norm(centroid_k - data, axis = 1)

        overlap_i = (dist_vec_i < radius_i).astype(int)
        overlap_j = (dist_vec_j < radius_j).astype(int)
        overlap_k = (dist_vec_k < radius_k).astype(int)

        overlap_count = (overlap_i + overlap_j + overlap_k == 3).sum()

        if overlap_count > p:
            simplices.append([i,j,k])

    for i,j,k,l in combinations(vertices, 4):
        centroid_i, radius_i = cover[i]
        centroid_j, radius_j = cover[j]
        centroid_k, radius_k = cover[k]
        centroid_l, radius_l = cover[l]

        dist_vec_i = np.linalg.norm(centroid_i - data, axis = 1)
        dist_vec_j = np.linalg.norm(centroid_j - data, axis = 1)
        dist_vec_k = np.linalg.norm(centroid_k - data, axis = 1)
        dist_vec_l = np.linalg.norm(centroid_l - data, axis = 1)

        overlap_i = (dist_vec_i < radius_i).astype(int)
        overlap_j = (dist_vec_j < radius_j).astype(int)
        overlap_k = (dist_vec_k < radius_k).astype(int)
        overlap_l = (dist_vec_l < radius_l).astype(int)

        overlap_count = (overlap_i + overlap_j + overlap_k + overlap_l == 4).sum()

        if overlap_count > p:
            simplices.append([i,j,k,l])

    return simplices