FROM ubuntu:18.04

ENV LANG C.UTF-8

RUN  apt-get update \
  && apt-get install -y apt-utils \
  && apt-get install -y wget \
  && apt-get install -y git \
  && apt-get install -y python3 \
  && apt-get install -y python3-dev \
  && apt-get install -y python3-pip \
  && apt-get install -y libjudy-dev \
  && apt-get install -y rsync \
  && apt-get install -y gawk \
  && rm -rf /var/lib/apt/lists/*

RUN git clone --branch master --single-branch https://github.com/TeMU-BSC/corpus-cleaner.git

RUN mkdir /cc

RUN mv /corpus-cleaner /cc

RUN rm -rf /cc/corpus-cleaner/data/

RUN rm -rf /cc/corpus-cleaner/output/

RUN python3 -m pip install -r /cc/corpus-cleaner/requirements.txt

RUN bash /cc/corpus-cleaner/get-third-party-docker.sh

ENTRYPOINT ["bash", "/cc/corpus-cleaner/entrypoint.sh"]
