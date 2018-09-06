# [Mapping the Clutch Gene](http://benedictaquino.com/mapping-the-clutch-gene)

The goal of this project is to utilize computational topology to understand the 
structure of a high-dimensional data set in an effort to overcome the [curse of 
dimensionality]. One of the obvious issues with high-dimensional data sets is 
that it becomes difficult to visualize. I aim to use topological methods to 
construct [simplicial complexes] that represent the data. Ideally, I will be 
able to glean valuable insights about the data throughinspection of these 
complexes.

I analyzed the 2017 Fantasy Football data that I sourced from the 
[NFL Fantasy Football API](http://api.fantasy.nfl.com/). The data is fairly 
high-dimensional, especially relative to the amount of observations.

[curse of dimensionality]: https://en.wikipedia.org/wiki/Curse_of_dimensionality
[simplicial complexes]: https://en.wikipedia.org/wiki/Simplicial_complex

## Topological Data Analysis

The idea here is to map the data to a low-dimensional representation. Since I am
looking at Fantasy Football data, I believe that the fantasy points of each 
player is a good low-dimensional projection. It is easy to interpret as a 
metric for a players performance, especially when looking at individual 
positions.

From there, I began exploring the data on the players by position. For each 
position, I grouped the players based on their fantasy points. These groups
are create a [cover] of the data. Then, I take this cover and pull it back to 
the full high-dimensional data set (excluding the fantasy points themselves). 
In the low-dimensional data set, the sets in the cover are just 1-dimensional 
intervals. In a two-dimensional space, sets of a cover would be 2-dimensional,
and so on. Anything above three dimensions is difficult to visualize, so in 
order to visualize my cover I lookg at the [nerve] of my cover.

From there I utilized [landmark-based navigation]. I used the centroids of the 
sets in my cover as my observers, and each data point representing each player 
as my landmarks. Visibility was the defined by a distance metric to each point. 
Then I from there I construct [filtrations] with varying levels of visibility.
Then I computed their [persistent homologies], which provide insight about the 
structure of the complexes.

[cover]: https://en.wikipedia.org/wiki/Cover_(topology)
[nerve]:  https://en.wikipedia.org/wiki/Nerve_of_a_covering
[landmark-based navigation]: https://www.math.upenn.edu/~ghrist/preprints/landmarkvisibility.pdf
[filtrations]: https://en.wikipedia.org/wiki/Filtration_(mathematics)
[persistent homologies]: https://en.wikipedia.org/wiki/Persistent_homology 



### [Technical Report](report.md)

### [Interactive Web App](http://benedictaquino.com/mapping-the-clutch-gene)

### Tools Used

- [Python](https://www.python.org/)
    - [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
    - [pandas](https://pandas.pydata.org/)
    - [NumPy](http://www.numpy.org/)
    - [matplotlib](https://matplotlib.org/)
    - [seaborn](https://seaborn.pydata.org/)
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

## Results

I constructed a filtration for each position and week, as well as the overall 
average by position, for a total of 6804 complexes. Initial inspection of the 
complexes seems to group players nicely by their fantasy output, and they help
indicate which initial clusters should be combined. 

## Further Steps

One tangential realization is that landmark-based navigation would be an 
excellent tool for visualization of an unsupervised learning method such as SVD
or NMF. Using discovered latent features as observations and the individual data 
points as landmarks (or vice-versa) should yield interesting results and is 
something I plan on tackling in the future.

