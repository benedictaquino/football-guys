import numpy as np
import scipy as sp
import dionysus as d
from itertools import combinations
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import AgglomerativeClustering

class ClutchMapper:

    def __init__(self, data, labels):
        '''
        The ClutchMapper object is a loose implementation of the Mapper algorithm
        designed to work with NFL Fantasy data

        PARAMETERS
        ----------
        data: {array} point cloud data

        labels: {array} labels from clustering the data in a reduced dimensionality
        '''
        self.data = data
        self.labels = labels

    def build_cover(self):
        '''
        This method builds a cover for point cloud data made up of sets of 
        overlapping hyperspheres

        RETURNS
        -------
        cover: {dict} the cover of the data such that the dicionary keys are the 
                    labels and the values are a tuple containing the centroid and
                    radius of the hypersphere 
        '''
        self.cover_ = {}

        for label in self.labels:
            ind = np.where(self.labels==label)
            cluster = self.data[ind]
            centroid = self.data[ind].mean(axis=0).reshape(1,-1)
            radius = np.linalg.norm(centroid - cluster, axis=1).max()
            self.cover_[label] = (centroid, radius)

        return self

    def build_complex(self, p):
        '''
        This function constructs the simplices for a simplicial complex given a 
        cover, data, and a threshold of overlapping points

        PARAMETERS
        ----------
        cover: {dict} a dictionary containing information on the cover consisting of
                    hyperspheres that cover the point cloud data

        data: {array} the point cloud data

        p: {int} the number of observations that must be in the intersection of 
                hyperspheres to create an edge, face, or tetrahedra

        RETURNS
        -------
        simplices: {list} a list of lists containing the simplices, each simplex is 
                        a list of the vertices that build the simplex.
        '''
        vertices = list(self.cover_.keys())
        
        simplicial_complex = []

        for i,j in combinations(vertices, 2):
            centroid_i, radius_i = self.cover_[i]
            centroid_j, radius_j = self.cover_[j]

            dist_vec_i = np.linalg.norm(centroid_i - self.data, axis = 1)
            dist_vec_j = np.linalg.norm(centroid_j - self.data, axis = 1)

            overlap_i = (dist_vec_i < radius_i).astype(int)
            overlap_j = (dist_vec_j < radius_j).astype(int)

            overlap_count = (overlap_i + overlap_j == 2).sum()

            if overlap_count > p:
                simplicial_complex.append([i,j])

        for i,j,k in combinations(vertices, 3):
            centroid_i, radius_i = self.cover_[i]
            centroid_j, radius_j = self.cover_[j]
            centroid_k, radius_k = self.cover_[k]

            dist_vec_i = np.linalg.norm(centroid_i - self.data, axis = 1)
            dist_vec_j = np.linalg.norm(centroid_j - self.data, axis = 1)
            dist_vec_k = np.linalg.norm(centroid_k - self.data, axis = 1)

            overlap_i = (dist_vec_i < radius_i).astype(int)
            overlap_j = (dist_vec_j < radius_j).astype(int)
            overlap_k = (dist_vec_k < radius_k).astype(int)

            overlap_count = (overlap_i + overlap_j + overlap_k == 3).sum()

            if overlap_count > p:
                simplicial_complex.append([i,j,k])

        for i,j,k,l in combinations(vertices, 4):
            centroid_i, radius_i = self.cover_[i]
            centroid_j, radius_j = self.cover_[j]
            centroid_k, radius_k = self.cover_[k]
            centroid_l, radius_l = self.cover_[l]

            dist_vec_i = np.linalg.norm(centroid_i - self.data, axis = 1)
            dist_vec_j = np.linalg.norm(centroid_j - self.data, axis = 1)
            dist_vec_k = np.linalg.norm(centroid_k - self.data, axis = 1)
            dist_vec_l = np.linalg.norm(centroid_l - self.data, axis = 1)

            overlap_i = (dist_vec_i < radius_i).astype(int)
            overlap_j = (dist_vec_j < radius_j).astype(int)
            overlap_k = (dist_vec_k < radius_k).astype(int)
            overlap_l = (dist_vec_l < radius_l).astype(int)

            overlap_count = (overlap_i + overlap_j + overlap_k + overlap_l == 4).sum()

            if overlap_count > p:
                simplicial_complex.append([i,j,k,l])

        return simplicial_complex

    def build_filtration(self, p):
        '''
        This method constructs a filtration given a cover and the data
        
        RETURNS
        -------
        filtration {dionysus.Filtration} a filtration of simplicial complices
        '''
        self.build_cover()

        vertices = [[k] for k in self.cover_.keys()]
        t = 0
        self.filtration_ = d.Filtration()

        for vertex in vertices:
            self.filtration_.append(d.Simplex(vertex, t))
            
        for p in range(p,-2,-1):
            t += 1
            simplicial_complex = self.build_complex(p)
            
            for simplex in simplicial_complex:
                self.filtration_.append(d.Simplex(simplex, t))

        self.filtration_.sort()

        return self.filtration_