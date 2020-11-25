#!/usr/bin/env bash

docker build --build-arg SSH_PRIVATE_KEY="$(cat ~/.ssh/id_rsa_github)" --build-arg SSH_PUBLIC_KEY="$(cat ~/.ssh/id_rsa_github.pub)" --no-cache -t corpuscleaner .
