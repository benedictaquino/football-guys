import os
import sys
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)
from flask import Flask, render_template, request, jsonify
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly.plotly as py
import json

server = Flask(__name__)
# app = Flask(__name__)

@server.route('/')
@server.route('/index')
def index():
    return render_template('index.html')

@server.route('/about')
def about():
    return render_template('about.html')

@server.route('/projects')
def projects():
    return render_template('projects.html')

@server.route('/mapping-the-clutch-gene')
def mapping_the_clutch_gene():
    return render_template('mapping_the_clutch_gene.html')

@server.route('/old_index')
def old_index():
    return render_template('old_index.html')

app = dash.Dash(__name__, server=server)

with open('data/simplicial_complex.pkl', 'rb') as f:
    simplicial_complex = go.Figure(json.load(f))

app.layout = html.Div(children=[
    dcc.Graph(
        id='example-graph',
        figure=simplicial_complex
    )
])

@server.route("/qb-complex")
def qb_complex():
    return app.index()

if __name__ == '__main__':
    server.run(host='0.0.0.0', port=8000, debug=True)
