# RecommendFromLink
Using both R and Python to recommend based on 1000 users.

The basis of this repository is to recommend games based on the play-time of 1000 users.
The 1000 users were picked as friends of friends of friends... of my (narquie) friends on steam.
The file that contains these 1000 users is Ratio_CSV.csv.
The "Addendum" file that the python script creates is provided to the R script to compare against the 1000 users.

To use the script, place your steam page link (mine is http://steamcommunity.com/id/stabstabstab/games/?tab=all) into "overall_dict" and "stack". The python script will ping your steam page and pull all video games you play and record it in "Addendum".

The R script will read addendum and compare your video game playing sessions against others, and try to compare games you haven't played with games that others have played (collaborative filtering). It will then recommend the top 20 games that you might like the in the command line.
