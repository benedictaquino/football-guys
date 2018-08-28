# Mapping the Clutch Gene

The goal of this project is to implement the Mapper algorithm on NFL Fantasy
Football data in order to visualize and analyze the point cloud data. Using
information gained from topological data analysis, I aim to make a model that
optimizes daily fantasy line-ups. Ideally, analyzing the simplical complices
that result from my implementation of the Mapper algorithm will yield a 
meaningful and novel way to group together players.

## [Technical Report](report.md)

## To-do
- [x] Gather data
- [x] Clean data and insert into to Postgres database
- [ ] Create optimization function
- [ ] Construct base model using traditional clustering algorithms and
    time series analysis to make predictions
- [ ] Make predictions and test on last season's data
- [ ] Implement Mapper algorithm and compare to base model
- [ ] Visualize the simplicial complex
- [ ] Create interactive web app
