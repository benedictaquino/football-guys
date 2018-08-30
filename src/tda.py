import numpy as np
import scipy as sp
import dionysus as d
from itertools import combinations
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import AgglomerativeClustering
import plotly.plotly as py
import plotly.graph_objs as go
import plotly.figure_factory as FF
import igraph as ig

class ClutchMapper:

    def __init__(self):
        '''
        The ClutchMapper object is am implementation of the Mapper algorithm
        designed to work with NFL Fantasy data
        '''
    
    def fit(self, data, labels):
        '''
        PARAMETERS
        ----------
        data: {array} point cloud data

        labels: {array} labels from clustering the data in a reduced dimensionality
        '''
        self.data = data
        self.labels = labels
        self.vertices_ = np.unique(labels)
        self._build_cover()
        n = len(self.vertices_)

        self.overlap_ = np.zeros((n,n,n), dtype=int)

        for i,j,k in combinations(self.vertices_, 3):
            centroid_i, radius_i = self.cover_[i]
            centroid_j, radius_j = self.cover_[j]
            centroid_k, radius_k = self.cover_[k]

            dist_vec_i = np.linalg.norm(centroid_i - self.data, axis = 1)
            dist_vec_j = np.linalg.norm(centroid_j - self.data, axis = 1)
            dist_vec_k = np.linalg.norm(centroid_k - self.data, axis = 1)

            overlap_i = (dist_vec_i < radius_i).astype(int)
            overlap_j = (dist_vec_j < radius_j).astype(int)
            overlap_k = (dist_vec_k < radius_k).astype(int)

            self.overlap_[i,i,j] = (overlap_i + overlap_j == 2).sum()
            self.overlap_[i,i,k] = (overlap_i + overlap_k == 2).sum()
            self.overlap_[j,j,k] = (overlap_i + overlap_k == 2).sum()
            self.overlap_[i,j,k] = (overlap_i + overlap_j + overlap_k == 3).sum()

    def _build_cover(self):
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

        for vertex in self.vertices_:
            ind = np.where(self.labels==vertex)
            cluster = self.data[ind]
            centroid = self.data[ind].mean(axis=0).reshape(1,-1)
            radius = np.linalg.norm(centroid - cluster, axis=1).max()
            self.cover_[vertex] = (centroid, radius)

        return self

    def build_complex(self, p, k = 3):
        '''
        This function constructs the simplices for a simplicial complex given a 
        cover, data, and a threshold of overlapping points

        PARAMETERS
        ----------
        p: {int} the number of observations that must be in the intersection of 
                hyperspheres to create an edge, face, or tetrahedra

        # TODO: Implement this
        k: {int} specifify up to which dimension k-simplex to calculate

        RETURNS
        -------
        simplices: {list} a list of lists containing the simplices, each simplex is 
                        a list of the vertices that build the simplex.
        '''

        # Vertices are the hyperspheres in our cover
        simplicial_complex = [[vertex] for vertex in self.vertices_]

        # Edges
        for i,j in combinations(self.vertices_, 2):
            if self.overlap_[i,i,j] > p:
                simplicial_complex.append([i,j])

        # Faces
        for i,j,k in combinations(self.vertices_, 3):
            if self.overlap_[i,j,k] > p:
                simplicial_complex.append([i,j,k])

        # # Tetrahedra
        # for i,j,k,l in combinations(vertices, 4):
        #     centroid_i, radius_i = self.cover_[i]
        #     centroid_j, radius_j = self.cover_[j]
        #     centroid_k, radius_k = self.cover_[k]
        #     centroid_l, radius_l = self.cover_[l]

        #     dist_vec_i = np.linalg.norm(centroid_i - self.data, axis = 1)
        #     dist_vec_j = np.linalg.norm(centroid_j - self.data, axis = 1)
        #     dist_vec_k = np.linalg.norm(centroid_k - self.data, axis = 1)
        #     dist_vec_l = np.linalg.norm(centroid_l - self.data, axis = 1)

        #     overlap_i = (dist_vec_i < radius_i).astype(int)
        #     overlap_j = (dist_vec_j < radius_j).astype(int)
        #     overlap_k = (dist_vec_k < radius_k).astype(int)
        #     overlap_l = (dist_vec_l < radius_l).astype(int)

        #     overlap_count = (overlap_i + overlap_j + overlap_k + overlap_l == 4).sum()

        #     if overlap_count > p:
        #         simplicial_complex.append([i,j,k,l])

        return simplicial_complex

    def build_filtration(self):
        '''
        This method constructs a filtration given a cover and the data
        
        RETURNS
        -------
        filtration {dionysus.Filtration} a filtration of simplicial complices
        '''
        self.filtration_ = d.Filtration()
        start = len(self.data)
            
        for t, p in enumerate(range(start, -1,-1)):
            simplicial_complex = self.build_complex(p)
            
            for simplex in simplicial_complex:
                self.filtration_.append(d.Simplex(simplex, t))

        self.filtration_.sort()

        return self.filtration_

def visualize_complex(simplicial_complex, title=None):
    '''
    This function constructs a visualization of the given simplical complex

    PARAMETERS
    ----------
    simplicial_complex: {list} a list containing simplices of the complex

    title: {str} title of the plot

    filename: {str} filename of the output plot

    RETURNS
    -------
    fig: {plotly.graph_objs.Figure}
    '''


    vertices = np.array([simplex for simplex_list in simplicial_complex for simplex in simplex_list if len(simplex_list) == 1])
    edges = np.array([simplex for simplex in simplicial_complex if len(simplex) == 2])
    faces = np.array([simplex for simplex in simplicial_complex if len(simplex) == 3])
    # tetrahedra = np.array([simplex for simplex in simplicial_complex if len(simplex) == 4])

    g = ig.Graph()
    n_vertices = len(vertices)
    g.add_vertices(n_vertices)
    g.add_edges(edges)
    layt = g.layout('kk', dim=3)

    x_vertex=[layt[k][0] for k in range(n_vertices)]
    y_vertex=[layt[k][1] for k in range(n_vertices)]
    z_vertex=[layt[k][2] for k in range(n_vertices)]

    x_edge = []
    y_edge = []
    z_edge = []

    for edge in edges:
        x_edge += [layt[edge[0]][0], layt[edge[1]][0], None]
        y_edge += [layt[edge[0]][1], layt[edge[1]][1], None]
        z_edge += [layt[edge[0]][2], layt[edge[1]][2], None]

    i, j, k = faces.T

    data = [
        go.Scatter3d(
            x = x_vertex,
            y = y_vertex,
            z = z_vertex,
            mode = 'markers',
            name = 'Vertices',
            marker=dict(symbol='circle',
                                size=6,
                                color=vertices,
                                colorscale='Viridis',
                                line=dict(color='rgb(50,50,50)', width=0.5)
                                ),
                text=vertices,
                hoverinfo='text'
        ),
        go.Scatter3d(
            x = x_edge,
            y = y_edge,
            z = z_edge,
            mode = 'lines',
            name = 'Edges'
        ),
        go.Mesh3d(
            x = x_vertex,
            y = y_vertex,
            z = z_vertex,
            i = i,
            j = j,
            k = k,
            opacity = 0.4,
            name = 'Faces'
        )
    ]

    axis=dict(showbackground=False,
            showline=False,
            zeroline=False,
            showgrid=False,
            showticklabels=False,
            title=''
            )

    layout = go.Layout(
            title=title,
            width=800,
            height=600,
            showlegend=False,
            scene=dict(
                xaxis=dict(axis),
                yaxis=dict(axis),
                zaxis=dict(axis),
            ),
        margin=dict(
            t=100
        )
    )
    fig = go.Figure(data=data, layout=layout)

    return fig