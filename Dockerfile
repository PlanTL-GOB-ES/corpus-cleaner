FROM ubuntu:20.04

ENV LANG C.UTF-8

RUN  apt-get update \
  && apt-get -y install software-properties-common \
  && add-apt-repository ppa:deadsnakes/ppa \
  && apt-get update \
  && apt-get install -y apt-utils \
  && apt-get install -y wget \
  && apt-get install -y git \
  && apt-get install -y python3.8 \
  && apt-get install -y python3.8-dev \
  && apt-get install -y python3-pip \
  && pip3 install --upgrade pip \
  && apt-get install -y libjudy-dev \
  && apt-get install -y rsync \
  && apt-get install -y gawk \
  && apt-get install -y g++ \
  && apt-get install -y build-essential \
  && rm -rf /var/lib/apt/lists/*

ARG BRANCH=paragraph-info
RUN git clone https://github.com/PlanTL-GOB-ES/corpus-cleaner.git && cd /corpus-cleaner && git checkout $BRANCH

RUN mkdir  /cc

RUN mv /corpus-cleaner /cc

RUN rm -rf /cc/corpus-cleaner/data/

RUN rm -rf /cc/corpus-cleaner/output/

RUN pip3 install -r /cc/corpus-cleaner/requirements.txt

RUN bash /cc/corpus-cleaner/get-third-party-docker.sh

ENTRYPOINT ["bash", "/cc/corpus-cleaner/entrypoint.sh"]
