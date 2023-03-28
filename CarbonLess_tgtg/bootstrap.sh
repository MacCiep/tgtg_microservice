#!/bin/sh
export FLASK_APP=./tgtg_microservice/index.py
pipenv run flask run -p 8080