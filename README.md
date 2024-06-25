# 2023 NBA Prospect Dashboard

### Modeling and Displaying projected outcomes for the 2023 Draft Class

This is a multi-step project to take raw player data and output prospect dashboards, which serve to inform viewers on players' skillsets and projections, based on their college stats and measurables.

The data comes from the following sources:
- https://barttorvik.com/ (college player stats)
- https://www.basketball-reference.com/ (NBA player stats)
- https://www.kaggle.com/datasets/marcusfern/nba-draft-combine (combine stats)

Step-by-step, the process to develop these dashboards are as follows.

1. Downloading and merging data. Here, we run the `player_merges.py` script, which utilizes the `scrape_functions.py` module in order to get NBA and college player data. Next, the `peaks_merge.py` script is run to add NBA player peaks to the NBA player data, which will be used in later steps.
2. In the next step, a number of models are trained, to eventually be used.
  * First, unsupervised learning models to cluster NCAA players and NBA players are trained in order to identify the playstyle of a given player. This is can be viewed in `ncaa_clusters.ipynb` and `nba_clusters.ipynb`.
  * Second, classification models are trained to obtain 'star' and 'bust' probabilities, based on a BPM threshold. This can be viewed in `star_bust.ipynb`.
  * Last, models for predicting stats at peak (multi-output regression) and closest prospect comparisons (again, KNN clustering) are developed. These can be viewed in `predicting_peaks.ipynb` and `knn_peak_2.ipynb`.
3. In the last step, matplotlib is utilized to create visualizations that attempt to both visualize the current skillset and projected outcomes for players. The creation of these plots can be seen in `dashboard.ipynb`.

The final product, which are the prospect reports can be viewed in the file `draft_guide.pdf` above.
