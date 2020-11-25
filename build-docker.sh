#!/usr/bin/env bash

docker build --build-arg SSH_PRIVATE_KEY=$1--no-cache -t corpuscleaner .