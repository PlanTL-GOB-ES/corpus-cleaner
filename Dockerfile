FROM ubuntu:18.04

RUN  apt-get update \
  && apt-get install -y apt-utils \
  && apt-get install -y wget \
  && apt-get install -y git \
  && apt-get install -y python3 \
  && apt-get install -y python3-dev \
  && apt-get install -y python3-pip \
  && apt-get install -y libjudy-dev \
  && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/TeMU-BSC/CorpusCleaner.git

RUN rm -rf CorpusCleaner/data/

RUN rm -rf CorpusCleaner/output/

RUN ln -s /data CorpusCleaner/data

RUN ln -s /output CorpusCleaner/output

RUN python3 -m pip install -r CorpusCleaner/requirements.txt

RUN bash CorpusCleaner/get-third-party.sh

ENTRYPOINT ["python3", "CorpusCleaner/clean.py"]
