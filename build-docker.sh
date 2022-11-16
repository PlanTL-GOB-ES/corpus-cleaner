#!/usr/bin/env bash
branch=$1

docker build  -t corpuscleaner --build-arg BRANCH=$branch .