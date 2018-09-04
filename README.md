# [Mapping the Clutch Gene](http://benedictaquino.com/mapping-the-clutch-gene)

The goal of this project is to utilize computational topology to understand the 
structure of a high-dimensional data set in an effort to overcome the [curse of 
dimensionality](https://en.wikipedia.org/wiki/Curse_of_dimensionality). One of 
the obvious issues with high-dimensional data sets is that it becomes difficult 
to visualize. I aim to use topological methods to construct a [simplicial 
complexes](https://en.wikipedia.org/wiki/Simplicial_complex) that represent the 
data. Ideally, I will be able to glean valuable insights about the data through
inspection of these complexes.

I analyzed the 2017 Fantasy Football data that I sourced from the 
[NFL Fantasy Football API](http://api.fantasy.nfl.com/). The data is fairly 
high-dimensional, especially relative to the amount of observations.

## Topological Data Analysis

The idea here is to map the data to a low-dimensional representation. Since I am
looking at Fantasy Football data, I believe that the fantasy points of each  
player was a good low-dimensional projection. It is easy to interpret as a 
metric for a players performance, especially when looking at individual 
positions.

From there, I began exploring the data on the players by position. For each 
position, I grouped the players based on their fantasy points. These groups
are just intervals that create a 
[cover](https://en.wikipedia.org/wiki/Cover_(topology)) of the data.
Then, I take this cover and map them it to the full high-dimensional data set 
(excluding the fantasy points themselves). In the low-dimensional data set,
the sets in the cover are just intervals, such as all the players who's 
average weekly fantasy points are between 10 and 15. If the data set were 
two-dimensional, the sets in my cover would be circles, and in three-dimensions
they would be spheres. So in an n-dimensional data set my cover consists of 
n-sphere. Anything above three dimensions is difficult to visualize, so in order
to visualize my cover I constructed the 
[nerve](https://en.wikipedia.org/wiki/Nerve_of_a_covering) of my cover, which is
a simplicial complex.

From there I used a method called 
[landmark-based navigation](https://www.math.upenn.edu/~ghrist/preprints/landmarkvisibility.pdf) 
to construct another equivalent simplicial complex that represents the data. 
Then I from there I construct 
[filtrations](https://en.wikipedia.org/wiki/Filtration_(mathematics)), which are
essentially a series of simplicial complexes, and computed their 
[persistent homologies](https://en.wikipedia.org/wiki/Persistent_homology), 
which provide insight about the structure of the complexes.

### [Technical Report](report.md)

### [Interactive Web App](http://benedictaquino.com/mapping-the-clutch-gene)

### Tools Used

- [Python](https://www.python.org/)
    - [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
    - [pandas](https://pandas.pydata.org/)
    - [NumPy](http://www.numpy.org/)
    - [SQLAlchemy](https://www.sqlalchemy.org/)
    - [Psycopg](http://initd.org/psycopg/)
    - [Dionysus 2](http://www.mrzv.org/software/dionysus2/)
    - [Plotly](https://plot.ly/)
    - [iGraph](http://igraph.org/redirect.html)
    - [Flask](http://flask.pocoo.org/)
    - [Dash](https://plot.ly/products/dash/)
    - [PyMongo](https://api.mongodb.com/python/current/)
- [PostgreSQL](https://www.postgresql.org/)
- [MongoDB](https://www.mongodb.com/)
- [Material Kit Bootstrap Template by Creative Tim](https://demos.creative-tim.com/material-kit/index.html)