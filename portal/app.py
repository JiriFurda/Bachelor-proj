#!/usr/bin/env python2

from flask import Flask, request
from werkzeug.urls import url_encode
#from controllers.homepage_controller import homepage_controller
from controllers.project_controller import project_controller
from controllers.topic_controller import topic_controller
from controllers.facet_controller import facet_controller
from controllers.search_controller import search_controller

app = Flask(__name__)


#app.register_blueprint(homepage_controller)
app.register_blueprint(project_controller)
app.register_blueprint(topic_controller)
app.register_blueprint(search_controller)
app.register_blueprint(facet_controller)

@app.template_global()
def modify_query(**new_values):
    args = request.args.copy()

    for key, value in new_values.items():
        args[key] = value

    return '{}?{}'.format(request.path, url_encode(args))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=2021)
