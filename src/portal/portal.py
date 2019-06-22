#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#---------------------------------------------------------------------------#
#-----------------             BAKALÁŘSKÁ PRÁCE            -----------------#
#----------------- Aktualizace portálu evropských projektů -----------------#
#-----------------     a jeho rozšíření o identifikaci     -----------------#
#-----------------     výsledků, souvisejících s tématy    -----------------#
#-----------------          nově vypisovaných výzev        -----------------#
#-----------------              FIT VUT v Brně             -----------------#
#----------------- Autor: Jiří Furda (2018-2019)           -----------------#
#----------------- Vedoucí: Doc. RNDr. Pavel Smrž, Ph.D.   -----------------#
#----------------------- Poslední úpravy: 13.5.2019 ------------------------#
#--- Soubor: portal.py                                        Verze: 1.0 ---#
#-------- http://knot.fit.vutbr.cz/wiki/index.php/rrs_eu_projects14 --------#
#--------------------- Licence: BUT Open source licence --------------------#
#---------------------------------------------------------------------------#


from flask import Flask, request
from werkzeug.urls import url_encode
from controllers.project_controller import project_controller
from controllers.topic_controller import topic_controller
from controllers.facet_controller import facet_controller
from controllers.search_controller import search_controller
import arrow


# Create Flask instance
app = Flask(__name__)


# Register controllers
app.register_blueprint(project_controller)
app.register_blueprint(topic_controller)
app.register_blueprint(search_controller)
app.register_blueprint(facet_controller)


# Global heleper functions
@app.template_global()
def modify_query(**new_values):
    ''' Modifies GET parameters query '''
    args = request.args.copy()

    for key, value in new_values.items():
        args[key] = value

    return '{}?{}'.format(request.path, url_encode(args))

@app.template_global()
def format_date(date):
    ''' Formates date '''
    parsed = arrow.get(date)
    return parsed.format('DD. MM. YYYY')


# Run Flask website
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=2021)
