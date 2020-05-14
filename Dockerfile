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
  && rm -rf /var/lib/apt/lists/*

RUN git clone --single-branch --branch singularity https://github.com/TeMU-BSC/CorpusCleaner.git

RUN mkdir /scratch

RUN mv /CorpusCleaner /scratch

RUN rm -rf /scratch/CorpusCleaner/data/

RUN rm -rf /scratch/CorpusCleaner/output/

RUN python3 -m pip install -r /scratch/CorpusCleaner/requirements.txt

RUN bash /scratch/CorpusCleaner/get-third-party-docker.sh

ENTRYPOINT ["bash", "/scratch/CorpusCleaner/entrypoint.sh"]
