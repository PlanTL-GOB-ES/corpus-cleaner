#!/usr/bin/env bash
branch=$1

# First, create release note for the current version
RELEASE_NOTE="release-note-container.txt"
echo "Branch: ${branch}" > ${RELEASE_NOTE}
start=$(git log master..${branch} | grep -n commit | sed -n "1p" | cut -d ":" -f 1)
end=$(git log | grep -n commit | sed -n "2p" | cut -d ":" -f 1)
end=$(echo ${end} - 1 | bc)
echo $(git log | sed -n "${start},${end}p") >> ${RELEASE_NOTE}

docker build  -t corpuscleaner --build-arg BRANCH=$branch .