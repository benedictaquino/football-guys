# Technical Report

## Data

I scraped the relevant data from [RotoGuru](http://rotoguru.net/) and the 
[NFL Fantasy API](http://api.fantasy.nfl.com/) and stored it in a Postgres 
database. Details can be seen in the [data_pipeline.py](src/data_pipeline.py) 
script. The functions in data_pipeline.py scrape the data to pandas DataFrames,
then using SQLAlchemy the data is inserted into Postgres. [Here](data/nfl.sql)
is the SQL dump file.

## [Topological Data Analysis](notebooks/TDA.ipynb)

I chose to use the average fantasy points of each player for my initial 
impementation of the Mapper algorithm. Since fantasy points are essentially a
linear combination of their performance statistics, I felt it was a good 
low-dimensional representation of each player. 
