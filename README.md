# datajam
Experiments with Data .

The objective of this repo is for anyone to start experimenting with some sort of data.

I started experimenting with my lastfm listening history . I plan to expand this to more publically available data.

The prerequisite for anyone to use this repo (right now) is to have elasticsearch and have a lastfm scrobbling history .

# Getting Started

- You can put in your api key in the scripts/last_fm.py file and pass your username . This will index all your data into elasticsearch.

- Use nginx to serve all your static file needs , config will be inside the conf folder ...

- Create an elasticsearch index with the specified mapping in the conf/elasticsearch.conf .


The default page of the server will provide a an artist search and a from and to date filters ..
This draws an hourly histogram with the probability of each hour available on hover .


#TODO
- Start gathering genre data from http://acousticbrainz.org/22337e71-0bf8-4fa9-86eb-2f8e7e085474/high-level .. helps in classifying genres to each track .
