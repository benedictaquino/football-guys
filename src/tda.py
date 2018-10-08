import os
import sys
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)
import pandas as pd
import numpy as np
import dionysus as d
from itertools import product, combinations
from scipy.spatial.distance import cdist
import plotly.plotly as py
import plotly.graph_objs as go
import plotly.figure_factory as FF
import igraph as ig
import pymongo

class ClutchMapper:

    def __init__(self, metric='euclidean'):
        '''
        The ClutchMapper object is am implementation of landmark-based 
        navigation designed to work with NFL Fantasy data. 

        Note: I named the observation complexes and related variables with the 
        'observer' prefix instead of 'observation' because 'observer' and 
        'landmark' have the same character length.
        '''
        self.metric = 'euclidean'
    
    def fit(self, data, labels):
        '''
        PARAMETERS
        ----------
        data: {array} point cloud data that become the landmarks

        labels: {array} labels from clustering the data in a reduced 
                dimensionality that become the observers
        '''
        self.landmarks_ = data
        self.labels = labels
        self.unique_labels_ = [np.asscalar(label) for label in np.unique(self.labels)]
        self._build_cover()
        self.observers_ = np.array([self.cover_[i][0].flatten() for i in self.cover_])
        self.O_ = range(len(self.observers_))
        self.L_= range(len(self.landmarks_))
        self.distances_ = cdist(self.observers_, self.landmarks_, metric=self.metric)
        # self.build_filtrations()

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

        for vertex in self.unique_labels_:
            ind = np.where(self.labels==vertex)
            cluster = self.landmarks_[ind]
            centroid = self.landmarks_[ind].mean(axis=0).reshape(1,-1)
            radius = np.linalg.norm(centroid - cluster, axis=1).max()
            self.cover_[vertex] = (centroid, radius)

        return self

    def build_complex(self, p, k = 3):
        '''
        This function constructs the simplices for a simplicial complex given a 
        cover, data, and a threshold of overlapping points

        PARAMETERS
        ----------
        p: {float} the visibility threshold to form simplices

        # TODO: Implement this
        k: {int} specifify up to which dimension k-complex to calculate

        RETURNS
        -------
        landmark_complex: {list} a list of lists containing the simplices
        observer_complex: {list} a list of lists containing the simplices
        '''
        # Subtract the distances computed in the fit method from p to see which
        # observations and landmarks are visible to each other
        within_p = np.sign(p - self.distances_)
        # If within_p[o,l] is -1, l is more than p from o
        # If within_p[o,l] is 1, l is within p of o

        # Observation Complex
        # ----------------
        # Observation are the centroids of the cover we build 
        # k-simplices are collections of (k+1) distinct observations that have
        # some landmark in common
        observer_complex = [] # instantiate complex as an empty list


        # 0-simplices (vertices) are added when an observation is visible
        # to a landmark
        for i in self.O_:
            for l in self.L_:
                if within_p[i,l]== 1:
                    observer_complex.append([i])
                    break

        # 1-simplices (edges) are added when an two observations are visible to
        # a landmark
        for i,j in combinations(self.O_, 2):
            for l in self.L_:
                if within_p[i,l]+within_p[j,l] == 2:
                    observer_complex.append([i,j])
                    break

        # 2-simplices (faces) are added when three observations are visible to 
        # a landmark
        for i,j,k in combinations(self.O_,3):
            for l in self.L_:
                if within_p[i,l]+within_p[j,l]+within_p[k,l] == 3:
                    observer_complex.append([i,j,k])
                    break

        # # 3-simplices (tetrahedra) are added when four observations are 
        # # visible to a landmark
        # for i,j,k,h in combinations(self.O_,4):
        #     for l in self.L_:
        #         if within_p[i,l]+within_p[j,l]+within_p[k,l]+within_p[h,l] == 4:
        #             observer_complex.append([i,j,k,h])
        #             break

        # Landmark Complex
        # ----------------
        # Landmarks are the data points of each player 
        # k-simplexes are collections of (k+1) distinct landmarks that have some
        # observation in common
        landmark_complex = [] # instantiate complex as a list

        # 0-simplices (vertices) are added when a landmark is visible to an 
        # observation
        for i in self.L_:
            for o in self.O_:
                if within_p[o,i] == 1:
                    landmark_complex.append([i])
                    break


        # 1-simplices (edges) are added when two landmarks are visible to an
        # observation
        for i,j in combinations(self.L_, 2):
            for o in self.O_:
                if within_p[o,i]+within_p[o,j] == 2:
                    landmark_complex.append([i,j])
                    break

        # 2-simplices (faces) are added when three landmarks are visible to an
        # observation
        for i,j,k in combinations(self.L_,3):
            for o in self.O_:
                if within_p[o,i]+within_p[o,j]+within_p[o,k] == 3:
                    landmark_complex.append([i,j,k])
                    break

        # # 3-simplices (tetrahedra) are added when four landmarks are visible 
        # # to an observation
        # for i,j,k,h in combinations(self.L_4):
        #     for o in self.O_:
        #         if within_p[o,i]+within_p[o,j]+within_p[o,k]+within_p[o,h] == 4:
        #             landmark_complex.append([i,j,k,h])
        #             break

        return observer_complex, landmark_complex

    def build_filtrations(self):
        '''
        This method constructs a filtration given a cover and the data
        
        RETURNS
        -------
        filtration {dionysus.Filtration} a filtration of simplicial complices
        '''
        # Instantiate the filtration objects
        self.observer_filtration_ = d.Filtration()
        self.landmark_filtration_ = d.Filtration()

        # Set the end of the filtration to be the maximum visibility
        end = self.distances_.max()
        
        # Build iterative complexes and add simplices to filtration with the 
        # visibility threshold they were born
        for p in np.linspace(0,end):
            observer_complex, landmark_complex = self.build_complex(p)
            
            for simplex in observer_complex:
                self.observer_filtration_.append(d.Simplex(simplex, p))

            for simplex in landmark_complex:
                self.landmark_filtration_.append(d.Simplex(simplex, p))

        # Sort the filtrations
        self.observer_filtration_.sort()
        self.landmark_filtration_.sort()


        return self.observer_filtration_, self.landmark_filtration_

def visualize_complex(simplicial_complex, title=None, names=None):
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
    vertices = [simplex for simplex_list in simplicial_complex for simplex in simplex_list if len(simplex_list) == 1]
    simplex_dict = {v:i for i,v in enumerate(vertices)}
    edges = [simplex for simplex in simplicial_complex if len(simplex) == 2]
    edge_list = [[simplex_dict[edge[0]], simplex_dict[edge[1]]] for edge in edges]
    faces = [simplex for simplex in simplicial_complex if len(simplex) == 3]
    face_list = [[simplex_dict[face[0]], simplex_dict[face[1]], simplex_dict[face[2]]] for face in faces]
    # tetrahedra = [simplex for simplex in simplicial_complex if len(simplex) == 4]

    g = ig.Graph()
    g.add_vertices(vertices)
    g.add_edges(edge_list)
    layt = g.layout('kk_3d')

    x_vertex=[layt[k][0] for k in range(len(vertices))]
    y_vertex=[layt[k][1] for k in range(len(vertices))]
    z_vertex=[layt[k][2] for k in range(len(vertices))]

    x_edge = []
    y_edge = []
    z_edge = []

    for edge in edge_list:
        x_edge += [layt[edge[0]][0], layt[edge[1]][0], None]
        y_edge += [layt[edge[0]][1], layt[edge[1]][1], None]
        z_edge += [layt[edge[0]][2], layt[edge[1]][2], None]

    if names == None:
        names = vertices
    else:
        names = list(np.array(names)[vertices])
        
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
                text=names,
                hoverinfo='text'
        ),
        go.Scatter3d(
            x = x_edge,
            y = y_edge,
            z = z_edge,
            mode = 'lines',
            name = 'Edges'
        ),
    ]

    if len(faces) > 0:
        i, j, k = np.array(face_list).T
        data.append(
            go.Mesh3d(
                x = x_vertex,
                y = y_vertex,
                z = z_vertex,
                i = [np.asscalar(n) for n in i],
                j = [np.asscalar(n) for n in j],
                k = [np.asscalar(n) for n in k],
                opacity = 0.25,
                name = 'Faces'
            )
        )
        

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

client = pymongo.MongoClient()
db_name = 'nfl'
db = client[db_name]
collection_name = 'complexes'
COMPLEXES = db[collection_name]
COMPLEXES.create_index([('name', pymongo.ASCENDING)], unique=True)

def visualization_to_db(figure, name):
    fig_json = figure.to_plotly_json()
    fig_json['name'] = name
    COMPLEXES.insert_one(fig_json)

if __name__ == '__main__':
    from sklearn.cluster import AgglomerativeClustering
    from sklearn.preprocessing import StandardScaler
    from src.data_pipeline import engine, query_avg, query_week

    positions = ['QB', 'RB', 'WR', 'TE', 'K', 'DEF', 'LB', 'DB', 'DL']
    n_sets = [5, 12, 12, 11, 8, 7, 11, 7, 10]

    for n, pos in zip(n_sets, positions):
        df = query_week(week=1, year=2018, pos=pos)
        df = df.iloc[:100]
        names = list(df['name'].values)
        X = df['weekpts'].values.reshape(-1,1)
        agg = AgglomerativeClustering(n_clusters=n, linkage='ward')
        labels = agg.fit_predict(X)

        stats = df.iloc[:,4:].values

        scaler = StandardScaler()
        scaled_stats = scaler.fit_transform(stats)

        cmapper = ClutchMapper()
        cmapper.fit(scaled_stats, labels)

        for i in np.arange(0,10.1,0.5):
            observer_complex, landmark_complex = cmapper.build_complex(i)

            observer_fig = visualize_complex(
                               observer_complex,
                               '2018 {} Week 1: Observer Complex at t={}'.\
                                       format(pos, i)
                               )
            landmark_fig = visualize_complex(
                               landmark_complex,
                               '2018 {} Week 1: Landmark Complex at t={}'.\
                                       format(pos, i), names
                               )

            visualization_to_db(observer_fig,
                '{}_week_1_observer_complex_{}_2018'.format(pos.lower(), i))
            visualization_to_db(landmark_fig,
                '{}_week_1_landmark_complex_{}_2018'.format(pos.lower(), i))

        print("Got {} data for 2018 week 1".format(pos))

    # for n, pos in zip(n_sets, positions):
        for week in range(1,18):
            df = query_week(week=week, pos=pos)
            df = df.iloc[:100]
            names = list(df['name'].values)
            X = df['weekpts'].values.reshape(-1,1)
            agg = AgglomerativeClustering(n_clusters=n, linkage='ward')
            labels = agg.fit_predict(X)

            stats = df.iloc[:,4:].values

            scaler = StandardScaler()
            scaled_stats = scaler.fit_transform(stats)

            cmapper = ClutchMapper()
            cmapper.fit(scaled_stats, labels)

            for i in np.arange(0,10.1,0.5):
                observer_complex, landmark_complex = cmapper.build_complex(i)

                observer_fig = visualize_complex(
                                   observer_complex,
                                   '2017 {} Week {}: Observer Complex at t={}'.\
                                        format(pos, week, i)
                                   )
                landmark_fig = visualize_complex(
                                   landmark_complex,
                                   '2017 {} Week {}: Landmark Complex at t={}'.\
                                        format(pos, week, i), names
                                   )

                visualization_to_db(observer_fig,
                    '{}_week_{}_observer_complex_{}_2017'.\
                            format(pos.lower(), week, i))
                visualization_to_db(landmark_fig, 
                    '{}_week_{}_landmark_complex_{}_2017'.\
                            format(pos.lower(), week, i))

            print("Got {} data for 2017 week {}".format(pos,week))

        df = query_avg(pos)
        df = df.iloc[:100]
        names = list(df['name'].values)
        X = df['avg_points'].values.reshape(-1,1)
        agg = AgglomerativeClustering(n_clusters=n, linkage='ward')
        labels = agg.fit_predict(X)

        stats = df.iloc[:,4:].values

        scaler = StandardScaler()
        scaled_stats = scaler.fit_transform(stats)

        cmapper = ClutchMapper()
        cmapper.fit(scaled_stats, labels)

        for i in np.arange(0,10.1,0.5):
            observer_complex, landmark_complex = cmapper.build_complex(i)

            observer_fig = visualize_complex(
                               observer_complex,
                               '2017 {} AVG: Observer Complex at t={}'.\
                                   format(pos, i)
                               )
            landmark_fig = visualize_complex(
                               landmark_complex,
                               '2017 {} AVG: Landmark Complex at t={}'.\
                                   format(pos, i), names
                               )

            visualization_to_db(observer_fig,
                '{}_avg_observer_complex_{}_2017'.format(pos.lower(), i))
            visualization_to_db(landmark_fig,
                '{}_avg_landmark_complex_{}_2017'.format(pos.lower(), i))

        print("Got all {} complexes!".format(pos))
