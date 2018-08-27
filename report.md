# Technical Report

## Data

I scraped the relevant data from [RotoGuru](http://rotoguru.net/) and the 
[NFL Fantasy API](http://api.fantasy.nfl.com/) and stored it in a Postgres 
database. Details can be seen in the [data_pipeline.py](src/data_pipeline.py) 
script.

## Optimization

Before I began making predictions, I created an optimizer that takes daily
fantasy point projections and salaries, then creates an optimaly lineup subject
to the constraints of the rules. Code and details can be found in my 
[Optimization](notebooks/optimization.ipynb) notebook. I utilized 
[Gurobi]