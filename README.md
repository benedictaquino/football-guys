# [Mapping the Clutch Gene](http://benedictaquino.com/mapping-the-clutch-gene)

The goal of this project is to utilize computational topology to understand the 
structure of a high-dimensional data set in an effort to overcome the [curse of 
dimensionality]. The most obvious issue with high dimensionality is that 
visualization becomes difficult. Another issue with high dimensionality is that 
the concept of distance loses meaning as the number of dimensions grow, so 
clustering becomes difficult. My goal was to construct simplicial complexes that
represented the data in order to tackle these problems.

## Data

I analyzed the 2017 Fantasy Football data that I sourced from the 
[NFL Fantasy Football API](http://api.fantasy.nfl.com/). The data is fairly 
high-dimensional, especially relative to the amount of observations.

[curse of dimensionality]: https://en.wikipedia.org/wiki/Curse_of_dimensionality
[simplicial complexes]: https://en.wikipedia.org/wiki/Simplicial_complex

## Topological Data Analysis

The first step here is to map the data to a low-dimensional representation. 
Since I am looking at Fantasy Football data, I believe that the fantasy points 
of each player is a good low-dimensional projection. It is easy to interpret as 
a metric for a players performance, especially when looking at individual 
positions.

From there, I began exploring the data on the players by position. For each 
position, I grouped the players based on their fantasy points. These groups
create a [cover] of the data. Then, I take this cover and pull it back to the
full high-dimensional data set (excluding the fantasy points themselves). In the
low-dimensional data set, the sets in the cover are just 1-dimensional 
intervals. In a two-dimensional space, sets of a cover would be 2-dimensional,
and so on. Anything above three dimensions is difficult to visualize, so in 
order to visualize my cover I look at the [nerve] of my cover.

From there I utilized [landmark-based navigation]. I used the centroids of the 
sets in my cover as my observers, and each data point representing each player 
as my landmarks. Visibility was defined by a distance metric to each point. Then
from there I construct [filtrations] of simplicial complexes as visibility 
increases. Then I computed the [persistent homologies] of the filtrations, which
provide insight about the structure of the complexes.

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
    - [SciPy](https://www.scipy.org/)
    - [scikit-learn](http://scikit-learn.org/stable/)
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

I constructed a landmark and observation filtration for each position and week,
as well as the overall average by position. Each filtation had 50 simplicial 
complexes, for a combined total of 17,100 complexes. I believe the persistent 
homologies can be used to refine the initial clusters and decide which should 
be combined. The barcode diagrams provide insight into how many "true" clusters 
there are.

## Further Steps

The next obvious step would be to implement code that utilizes the computed 
persistent homologies to refine the initial clusters. As well, using better 
initial clusters may provide more interesting results.

However, before utilizing the persistent homologies I would like to optimize my 
code. There is definitely a bit of redundancy that can potentially be improved
with recursion when building the complexes. As well, I attempted to implement
multiprocessing and threading as seen in [makeitfaster.py], however due to an
issue with being unable to pickle `dionysus.Filtration` objects I would have to
rewrite significant portions of that code for it to function.

Also, I did implement a parameter in the `ClutchMapper` class that allows one to
use different distance metrics, when computing visibility, so experimenting with
other metrics might yield interesting results. I used euclidean distance to 
calculate visibility throughout my project.

One tangential realization is that landmark-based navigation would be an 
excellent tool for visualization of an unsupervised learning method such as SVD
or NMF. Using discovered latent features as observations and the individual data 
points as landmarks (or vice-versa) should yield interesting results and is 
something I plan on tackling in the future.

[makeitfaster.py]: src/makeitfaster.py
