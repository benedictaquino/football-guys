import os
import sys
module_path = os.path.abspath(os.path.join(".."))
if module_path not in sys.path:
    sys.path.append(module_path)
from flask import Flask, render_template, request, jsonify
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly.plotly as py
import json
import numpy as np
import pymongo
from src.data_pipeline import query_avg, query_week

server = Flask(__name__)

@server.route('/')
@server.route('/index')
def index():
    return render_template('index.html')

@server.route('/about')
def about():
    return render_template('about.html')

@server.route('/projects')
def projects():
    return render_template('projects.html',
                           title="Projects")

positions = ['QB', 'RB', 'WR', 'TE', 'DEF', 'K', 'LB', 'DB', 'DL']

@server.route('/mapping-the-clutch-gene')
def mapping_the_clutch_gene():
    return render_template('mapping_the_clutch_gene.html',
                           title="Mapping the Clutch Gene",
                           positions=positions,
                           weeks=list(range(1,18)))

app = dash.Dash(__name__, server=server)

weeks = ['AVG'] + list(range(1,18))

app.layout = html.Div(children=[
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='position',
                options=[{'label': pos, 'value': pos.lower()} for pos in positions],
                value='qb'
            ),
            dcc.RadioItems(
                id='complex-type',
                options=[{'label': i, 'value': i.lower()} for i in ['Landmark', 'Observer']],
                value='landmark',
                labelStyle={'display': 'inline-block'}
            )
        ],
        style={'width': '48%', 'float': 'left', 'display': 'inline-block'}),
        html.Div([
            dcc.Dropdown(
                id='week',
                options=[{'label': i, 'value': i} for i in weeks],
                value=1
            ),
            dcc.RadioItems(
                id='year',
                options=[{'label': i, 'value': i} for i in [2017, 2018]],
                value=2018,
                labelStyle={'display': 'inline-block'}
            )
        ],
        style={'width': '48%', 'float': 'right', 'display': 'inline-block'})
    ]),
    dcc.Graph(
        id='complex'
    ),
    html.Div([
        dcc.Slider(
                id='t-slider',
                min=0.0,
                max=10.0,
                value=2.5,
                step=0.5,
                marks={str(t): str(t) for t in np.arange(0.0,10.1,0.5)}
            )
    ],
        style={'margin-top': '25px', 'margin-bottom': '50px'}
    ),
    html.Div([
        dcc.Graph(
            id='table'
        )
    ])
])

@server.route("/complex")
def nfl_complex():
    return app.index()

@app.callback(
    dash.dependencies.Output('complex', 'figure'),
    [dash.dependencies.Input('position', 'value'),
     dash.dependencies.Input('complex-type', 'value'),
     dash.dependencies.Input('t-slider', 'value'),
     dash.dependencies.Input('week', 'value'),
     dash.dependencies.Input('year', 'value')]
)
def update_graph(pos, complex_type, t, week, year):
    if week == 'AVG':
        week = week.lower()
    else:
        week = 'week_{}'.format(week)
    name = '{}_{}_{}_complex_{}_{}'.format(pos, week, complex_type, float(t), year)
    complex_data = COMPLEXES.find_one({'name': name})
    del complex_data['name']
    figure = go.Figure(complex_data)
    return figure

@app.callback(
    dash.dependencies.Output('table', 'figure'),
    [dash.dependencies.Input('position', 'value'),
     dash.dependencies.Input('t-slider', 'value'),
     dash.dependencies.Input('week', 'value'),
     dash.dependencies.Input('year', 'value')]
)
def update_table(pos, t, week, year):
    if week == 'AVG':
        df = query_avg(pos=pos.upper(), year=year)
    else:
        df = query_week(week=week, year=year, pos=pos.upper())

    trace = go.Table(
        header=dict(values=list(df.columns[1:4])),
        cells=dict(values=df.iloc[:,1:4].values.T)
    )

    figure = go.Figure([trace])

    return figure

# Make dash pretty
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

if __name__ == '__main__':
    client = pymongo.MongoClient()
    db_name = 'nfl'
    db = client[db_name]
    collection_name = 'complexes'
    COMPLEXES = db[collection_name]

    server.run(host='0.0.0.0', port=8000, debug=True)
