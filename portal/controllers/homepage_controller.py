#!/usr/bin/env python2

from flask import Blueprint, Flask, url_for
from controllers.project_controller import index as projects_index

homepage_controller = Blueprint('homepage', __name__)
"""

@homepage_controller.route('/')
def index():
    return projects_index()
"""