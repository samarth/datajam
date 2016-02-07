import requests
import json
import hashlib

import time

from dateutil.parser import parse
from datetime import timedelta, datetime

from elasticsearch import Elasticsearch
es = Elasticsearch()

class LastFmRequestor:

    def __init__(self, api_key = "", user = ""):

        self.api_key = api_key
        self.host = "http://ws.audioscrobbler.com/2.0/"
        self.user = user


    def get_recent_tracks(self):

        if not hasattr(self, "recent_tracks_page_tracker"):
            self.recent_tracks_page_tracker = 1

        api = "user.getRecentTracks"

        track_listing_url = "%s?method=%s&api_key=%s&user=%s&format=json&limit=200"  % (self.host , api , self.api_key , self.user)

        track_listing_url += "&page=" + str(self.recent_tracks_page_tracker)

        track_listing_req = requests.get(track_listing_url)

        self.recent_tracks_page_tracker += 1

        return json.loads(track_listing_req.text)



def is_location_shimla(date):
    '''

    Will ignore this data for a while ...

    Takes in a date and determines if it lies in the period when I was in shimla or not.

    The approx. definition of me being in shimla ->
    2009 -> 2013

    June 2013 onwards -> Delhi
    '''

    threshold_date = parse("1 June 2013")

    if (date < parse(threshold_date)):
        return True

    return False


def get_id_hash(track_dict):
    m = hashlib.md5()
    m.update(track_dict["user"] + track_dict["mbid"] + str(track_dict["date"]))
    return m.hexdigest()


def insert_recent_tracks_data (recent_tracks_data):

    '''
    The idea is to extract useful bits from json and correspondingly hit the open weather api
    to get the weather. Alternatively , I can store this data in mysql and then hit open weather api
    independently.

    Also returns a boolean saying if the next page has to be crawled or not ...

    '''

    tracks = recent_tracks_data["recenttracks"]["track"]
    user = recent_tracks_data["recenttracks"]["@attr"]["user"]

    for track in tracks :


        track_dict = {}

        track_dict["user"] = user

        track_dict["name"] = track["name"]

        # Also store mbid for analytics later ....
        track_dict["mbid"] = track["mbid"]

        track_dict["artist"] = {}
        track_dict["artist"]["text"] = track["artist"]["#text"]
        track_dict["artist"]["mbid"] = track["artist"]["mbid"]

        track_dict["album"] = {}
        track_dict["album"]["text"] = track["album"]["#text"]
        track_dict["album"]["mbid"] = track["album"]["mbid"]

        # Time zone patch ...
        # The date object is none when the track is being scrobbled.Safe assumption to put
        # the immediate timestamp.
        if (track.get("date") is None):
            track_dict["date"] =  parse(datetime.now().strftime("%Y-%m-%d %H:%M"))
        else:
            track_dict["date"]   = parse(track["date"]["#text"]) + timedelta(hours=5, minutes = 30)



        # The id of the doc will be a hash of the track_dict["date"] and
        # the track mbid

        es.index(index="lastfm", doc_type="track", body=track_dict, id = get_id_hash(track_dict))



def init():

    last_fm_requestor = LastFmRequestor(api_key = "<YOUR_API_KEY>" , user = "<YOUR_LASTFM_USERNAME>" )

    tracks = last_fm_requestor.get_recent_tracks()
    total_pages = tracks["recenttracks"]["@attr"]["totalPages"]

    insert_recent_tracks_data(tracks)
    print "Total Pages : ", total_pages

    while ( last_fm_requestor.recent_tracks_page_tracker <= int(total_pages)):
        print "Current Page: " , last_fm_requestor.recent_tracks_page_tracker
        insert_recent_tracks_data(last_fm_requestor.get_recent_tracks())


init()
