from flask import Flask
from flask.ext.cors import CORS

app = Flask("data-jam" , template_folder= "./app/templates", static_folder='./app/static')

CORS(app, resources = {r"/listing/*" : {"origins" : "*"}})

# Entry point for all apps ....
from dashboard import controllers
