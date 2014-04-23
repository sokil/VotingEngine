#!/bin/sh

cd ..
export APPLICATION_ENV=${1-production}
gunicorn -D -w 4 -b 127.0.0.1:9001 bootstrap:app
