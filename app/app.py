import os
import sys
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/projects')
def projects():
    return render_template('projects.html')

@app.route('/mapping-the-clutch-gene')
def mapping_the_clutch_gene():
    return render_template('mapping_the_clutch_gene.html')

@app.route('/old_index')
def old_index():
    return render_template('old_index.html')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
