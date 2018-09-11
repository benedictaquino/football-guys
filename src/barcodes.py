import os
import sys
module_path = os.path.abspath("..")
if module_path not in sys.path:
    sys.path.append(module_path)

import pandas as pd
import dionysus as d
import matplotlib.pyplot as plt
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from src.tda import ClutchMapper
from src.data_pipeline import query_avg, query_week

plt.style.use('ggplot')

positions = ['QB', 'RB', 'WR', 'TE', 'K', 'DEF', 'LB', 'DB', 'DL']
n_sets = [5, 12, 12, 11, 8, 7, 11, 7, 10]

# for n, pos in zip(n_sets, positions):
#     for week in range(1,18):
#         df = query_week(week=week, pos=pos)
#         df = df.iloc[:100]
#         names = list(df['name'].values)
#         X = df['weekpts'].values.reshape(-1,1)
#         agg = AgglomerativeClustering(n_clusters=n, linkage='ward')
#         labels = agg.fit_predict(X)

#         stats = df.iloc[:,4:].values

#         scaler = StandardScaler()
#         scaled_stats = scaler.fit_transform(stats)

#         cmapper = ClutchMapper()
#         cmapper.fit(scaled_stats, labels)

#         observer_f, landmark_f = cmapper.build_filtrations()

#         observer_ph = d.homology_persistence(observer_f)
#         landmark_ph = d.homology_persistence(landmark_f)

#         observer_dgms = d.init_diagrams(observer_ph, observer_f)
#         landmark_dgms = d.init_diagrams(landmark_ph, landmark_f)

#         observer_barcode = plt.figure(figsize=(15,10))
#         observer_barcode_title = "2017 {} Week {}: Barcode Diagram for $\\beta_0$ of the Observer Complex".format(pos,week)
#         plt.title(observer_barcode_title)
#         d.plot.plot_bars(observer_dgms[0])
#         observer_barcode_filepath="plots/week{}/{}_barcode_observer.png".format(week,pos.lower())
#         observer_barcode.savefig(observer_barcode_filepath)
#         plt.close(observer_barcode)
#         print("Saved {} to {}".format(observer_barcode_title, observer_barcode_filepath))

#         landmark_barcode = plt.figure(figsize=(15,10))
#         landmark_barcode_title="2017 {} Week {}: Barcode Diagram for $\\beta_0$ of the Landmark Complex".format(pos,week)
#         plt.title(landmark_barcode_title)
#         d.plot.plot_bars(landmark_dgms[0])
#         landmark_barcode_filepath="plots/week{}/{}_barcode_landmark.png".format(week,pos.lower())
#         landmark_barcode.savefig(landmark_barcode_filepath)
#         plt.close(landmark_barcode)
#         print("Saved {} to {}".format(landmark_barcode_title, landmark_barcode_filepath))


for n, pos in zip(n_sets, positions):
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

    observer_f, landmark_f = cmapper.build_filtrations()

    observer_ph = d.homology_persistence(observer_f)
    landmark_ph = d.homology_persistence(landmark_f)

    observer_dgms = d.init_diagrams(observer_ph, observer_f)
    landmark_dgms = d.init_diagrams(landmark_ph, landmark_f)

    observer_barcode = plt.figure(figsize=(15,10))
    observer_barcode_title = "2018 {} Week 1: Barcode Diagram for $\\beta_0$ of the Observer Complex".format(pos)
    plt.title(observer_barcode_title)
    d.plot.plot_bars(observer_dgms[0])
    observer_barcode_filepath="plots/2018/week1/{}_barcode_observer.png".format(week,pos.lower())
    observer_barcode.savefig(observer_barcode_filepath)
    plt.close(observer_barcode)
    print("Saved {} to {}".format(observer_barcode_title, observer_barcode_filepath))

    landmark_barcode = plt.figure(figsize=(15,10))
    landmark_barcode_title="2018 {} Week 1: Barcode Diagram for $\\beta_0$ of the Landmark Complex".format(pos)
    plt.title(landmark_barcode_title)
    d.plot.plot_bars(landmark_dgms[0])
    landmark_barcode_filepath="plots/2018/week1/{}_barcode_landmark.png".format(week,pos.lower())
    landmark_barcode.savefig(landmark_barcode_filepath)
    plt.close(landmark_barcode)
    print("Saved {} to {}".format(landmark_barcode_title, landmark_barcode_filepath))


