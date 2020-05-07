FROM ubuntu:18.04

RUN  apt-get update \
  && apt-get install -y wget \
  && apt-get install -y git \
  && apt-get install -y python3.7 \
  && apt-get install -y python3.7-dev \
  && apt-get install -y python3.7-pip \
  && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/TeMU-BSC/CorpusCleaner.git

RUN cd CorpusCleaner/

RUN rm -rf data/

RUN rm -rf output/

RUN ls -s /data data/

RUN ls -s /output output/

RUN python -m pip install -r requirements.txt

RUN bash get-third-party.sh

ENTRYPOINT ["python3.7", "clean.py"]
