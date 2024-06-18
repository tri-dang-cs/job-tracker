#!/bin/sh

cd $(dirname $0)

flask --app backend.app run-service
