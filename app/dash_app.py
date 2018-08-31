import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly.plotly as py
import json

app = dash.Dash()

with open('data/simplicial_complex.pkl', 'rb') as f:
    simplicial_complex = json.load(f)

if __name__ == '__main__':
    app.run_server(debug=True)
    print(simplicial_complex)