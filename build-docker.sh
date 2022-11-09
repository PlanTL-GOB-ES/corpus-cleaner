#!/usr/bin/env bash
ssh_key_name=$(ls -l  ../.ssh/ | grep -oP "id.*" | head -n 1)
docker build --build-arg SSH_PRIVATE_KEY="$(cat ~/.ssh/$ssh_key_name)" --build-arg SSH_PUBLIC_KEY="$(cat ~/.ssh/$ssh_key_name.pub)" --no-cache -t corpuscleaner .
