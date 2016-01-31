from app import app

from flask import jsonify,  render_template , request

from dateutil.parser import parse
from elasticsearch import Elasticsearch

client = Elasticsearch()

@app.route('/')
def index():
    # Render root template here ...
    return render_template('dashboard/index.html')

# Supposed to be open only for ajax calls ....
@app.route('/listing/')
def get_user_track_listing ():

    response    = {}

    username    =  request.args.get("username")

    artist_name = request.args.get("artist")

    if not username:
        response["error"] = "Make an effort to pass the username"
        return jsonify(response)


    es_dsl = {
        "query": {
            "filtered": {
                "filter": {
                    "bool": {
                        "must": [{"term": {"user": username}}],
                    }
                }
            }
        },
        # Setting this to a very high value for now ...
        "size" : 1000000
    }



    if (artist_name) :
        es_dsl["query"]["filtered"]["query"] =  {"match" : { "artist.text" : artist_name}}

    fromdate = request.args.get("fromdate")
    todate   = request.args.get("todate")

    if (fromdate and todate) :
        es_dsl["query"]["filtered"]["filter"]["bool"]["must"].append(
            {
                "range" : {
                    "date" : {
                        "gte" : fromdate,
                        "lte" : todate,
                        "format": "dd/mm/yyyy"
                    }
                }
            }
        )



    es_response = client.search(
        index = "lastfm",
        body=es_dsl
    )

    user_data = []

    for hit in es_response['hits']['hits']:
        user_data.append(hit["_source"])


    response["data"] = user_data
    return jsonify(response)



@app.route('/artists/top')
def get_top_artists():


    response = {}

    username =  request.args.get("username")

    if not username:
        response["error"] = "Make an effort to pass the username"
        return jsonify(response)


    es_dsl = {
        "query": {
            "filtered": {
                "filter": {
                    "bool": {
                        "must": [{"term": {"user": username}}],
                    }
                }
            }
        },
        # Only supposed to fetch aggregations anyway
        "size" : 0,
        "aggs" : {
            "top_artists" : {
                "terms" : {
                    "field" : "artist.text.raw",
                    "size"   : 10
                }
            }
        }
    }



    fromdate = request.args.get("fromdate")
    todate   = request.args.get("todate")


    if (fromdate and todate) :
        es_dsl["query"]["filtered"]["filter"]["bool"]["must"].append(
            {
                "range" : {
                    "date" : {
                        "gte" : fromdate,
                        "lte" : todate,
                        "format": "dd/mm/yyyy"
                    }
                }
            }
        )

    es_response = client.search(
        index = "lastfm",
        body=es_dsl
    )


    user_data = []

    user_data = es_response.get("aggregations", {}).get("top_artists", {}).get("buckets", [])

    response["data"] = user_data

    return jsonify(response)


@app.route('/artists/time')
def get_artist_time():
    '''
    The intent of this api is to give time range aggregations
    on the artist name ...

    Useful for fetching what artist was I majorly listening to
    at that hour of the day ....

    '''

    response = {}

    username =  request.args.get("username")

    if not username:
        response["error"] = "Make an effort to pass the username"
        return jsonify(response)


    es_dsl = {
        "query": {
            "filtered": {
                "filter": {
                    "bool": {
                        "must": [{"term": {"user": username}}],
                    }
                }
            }
        },
        # Only supposed to fetch aggregations anyway
        "size" : 0,
        "aggs" : {
            "per_hour" : {
                "date_histogram" : {
                    "field"    : "date",
                    "interval" : "hour",
                    "format"   : "YYYY-MM-dd HH:mm:ss"
                },
                "aggs" : {
                    "top_artists" : {
                        "terms" : {
                            "field" : "artist.text.raw"
                        }
                    }
                }
            }
        }
    }


    fromdate = request.args.get("fromdate")
    todate   = request.args.get("todate")


    if (fromdate and todate) :
        es_dsl["query"]["filtered"]["filter"]["bool"]["must"].append(
            {
                "range" : {
                    "date" : {
                        "gte" : fromdate,
                        "lte" : todate,
                        "format": "dd/mm/yyyy"
                    }
                }
            }
        )


    es_response = client.search(
        index = "lastfm",
        body=es_dsl
    )

    # A dictionary clubbing all artists
    # per hour


    user_data = {}

    top_artists_per_hour = es_response.get("aggregations", {}).get("per_hour", {}).get("buckets", [])

    for per_hour in top_artists_per_hour:
        # Identify the hour first from the per_hour bucket
        hour = parse(per_hour["key_as_string"]).hour


        if  not (hour in user_data) :
            user_data[hour] = {}

        for artist in per_hour["top_artists"]["buckets"] :

            artist_count    = artist["doc_count"]
            artist_name     = artist["key"]

            if not (artist_name in user_data[hour]) :
                user_data[hour][artist_name] = artist_count
            else :
                user_data[hour][artist_name] += artist_count

    response["data"] = user_data

    return jsonify(response)
