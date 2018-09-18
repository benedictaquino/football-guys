import os
import sys
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

from src.data_pipeline import *
from src.tda import *

from sched import scheduler
from time import time, sleep, localtime, strftime

def get_2018_data(week):
    if week < 18:
        stat_df = stat_scrape(week=week, year=2018)

        if type(stat_df) != pd.DataFrame:
            print("Failed to retrieve fantasy stats for Week {} 2018.".format(week))
        else:
            to_database(stat_df, table_name='fantasy')
            print("Successfully retrieved fantasy stats for Week {} 2018.".format(week))   

    positions = ['QB', 'RB', 'WR', 'TE', 'K', 'DEF', 'LB', 'DB', 'DL']
    n_sets = [5, 12, 12, 11, 8, 7, 11, 7, 10]

    for n, pos in zip(n_sets, positions):
        if week < 18:
            df = query_week(week=week, year=2018, pos=pos)
            df = df.iloc[:100]
            X = df['weekpts'].values.reshape(-1,1)
        else:
            df = query_avg(pos, year=2018)
            df = df.iloc[:100]
            X = df['avg_points'].values.reshape(-1,1)

        names = list(df['name'].values)
        agg = AgglomerativeClustering(n_clusters=n, linkage='ward')
        labels = agg.fit_predict(X)

        stats = df.iloc[:,4:].values

        scaler = StandardScaler()
        scaled_stats = scaler.fit_transform(stats)

        cmapper = ClutchMapper()
        cmapper.fit(scaled_stats, labels)

        for i in np.arange(0,10.1,0.5):
            observer_complex, landmark_complex = cmapper.build_complex(i)

            observer_fig = visualize_complex(observer_complex, '2018 {} Week {}: Observer Complex at t={}'.format(pos, week, i))
            landmark_fig = visualize_complex(landmark_complex, '2018 {} Week {}: Landmark Complex at t={}'.format(pos, week, i), names)

            visualization_to_db(observer_fig, '{}_week_{}_observer_complex_{}_2018'.format(pos.lower(), week, i))
            visualization_to_db(landmark_fig, '{}_week_{}_landmark_complex_{}_2018'.format(pos.lower(), week, i))

        observer_f, landmark_f = cmapper.build_filtrations()

        observer_ph = d.homology_persistence(observer_f)
        landmark_ph = d.homology_persistence(landmark_f)

        observer_dgms = d.init_diagrams(observer_ph, observer_f)
        landmark_dgms = d.init_diagrams(landmark_ph, landmark_f)

        observer_barcode = plt.figure(figsize=(15,10))
        observer_barcode_title = "2018 {} Week {}: Barcode Diagram for $\\beta_0$ of the Observer Complex".format(pos, week)
        plt.title(observer_barcode_title)
        d.plot.plot_bars(observer_dgms[0])
        observer_barcode_filepath="../plots/2018/week{}/{}_barcode_observer.png".format(week,pos.lower())
        observer_barcode.savefig(observer_barcode_filepath)
        plt.close(observer_barcode)
        print("Saved {} to {}".format(observer_barcode_title, observer_barcode_filepath))

        landmark_barcode = plt.figure(figsize=(15,10))
        landmark_barcode_title="2018 {} Week {}: Barcode Diagram for $\\beta_0$ of the Landmark Complex".format(pos, week)
        plt.title(landmark_barcode_title)
        d.plot.plot_bars(landmark_dgms[0])
        landmark_barcode_filepath="../plots/2018/week{}/{}_barcode_landmark.png".format(week,pos.lower())
        landmark_barcode.savefig(landmark_barcode_filepath)
        plt.close(landmark_barcode)
        print("Saved {} to {}".format(landmark_barcode_title, landmark_barcode_filepath))

    print("Got data.")

s = scheduler(time, sleep)

def foo(bar):
    print(bar)

def data_scheduler(week):
    if week > 18:
        return

    print("Start:", strftime("%H:%M:%S, %A, %x", localtime(time())))
    s.enter(608400, 1, get_2018_data, kwargs = {'week': week})
    s.enter(608400, 2, data_scheduler, kwargs = {'week': week+1})
    s.run()

if __name__ == "__main__":
    data_scheduler(week=3)
 
