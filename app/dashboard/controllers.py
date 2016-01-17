from app import app

from flask import jsonify,  render_template , request


from elasticsearch import Elasticsearch

client = Elasticsearch()

@app.route('/')
def index():
    # Render root template here ...
    return render_template('dashboard/index.html')

# Supposed to be open only for ajax calls ....
@app.route('/listing/')
def get_user_track_listing ():
    '''
    This username goes to ES  ...
    Can have time based queries later.
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
        # Setting this to a very high value for now ...
        "size" : 1000000
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

    for hit in es_response['hits']['hits']:
        user_data.append(hit["_source"])


    response["data"] = user_data
    return jsonify(response)
