from app import app

from flask import jsonify,  render_template


from elasticsearch import Elasticsearch

client = Elasticsearch()

@app.route('/')
def index():
    # Render root template here ...
    return render_template('dashboard/index.html')

# Supposed to be open only for ajax calls ....
@app.route('/listing/<username>')
def get_user_track_listing (username):
    '''
    This username goes to ES  ...
    Can have time based queries later.
    '''

    response = {}

    if not username:
        response["error"] = "Make an effort to pass the username"
        return jsonify(response)



    es_response = client.search(
        index = "lastfm",
        body={
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
    )

    user_data = []

    for hit in es_response['hits']['hits']:
        user_data.append(hit["_source"])


    response["data"] = user_data
    return jsonify(response)
