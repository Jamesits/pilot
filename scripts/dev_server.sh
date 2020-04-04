#!/bin/bash

cd "$( dirname "${BASH_SOURCE[0]}" )"/..

export FLASK_APP='pilot/__main__.py'
export FLASK_ENV='development'

flask run --host=0.0.0.0