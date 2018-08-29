# Mapping the Clutch Gene

The goal of this project is to implement the Mapper algorithm on NFL Fantasy
Football data in order to visualize and analyze the point cloud data. Ideally, 
analyzing the simplical complices that result from my implementation of the 
Mapper algorithm will yield a meaningful and novel way to group together 
players.

## [Technical Report](report.md)

## To-do
- [x] Gather data
- [x] Clean data and insert into to Postgres database
- [x] Implement Mapper algorithm to build a simplicial complex
- [x] Generalize code from [notebook](notebooks/TDA.ipynb)
- [ ] Visualize the simplicial complices
- [ ] Analyze barcode diagrams
- [ ] Create interactive visualization
- [ ] Deploy Flask web app on AWS EC2 instance

## Stretch/Tangential Goals
- [ ] Optimize code
- [ ] Use information gained from topological data analysis to develop a model
      that can be used to optimize daily fantasy lineups
