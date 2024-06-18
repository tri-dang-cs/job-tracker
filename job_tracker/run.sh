#!/bin/sh

cd $(dirname $0)

flask --app backend.app run --host 0.0.0.0