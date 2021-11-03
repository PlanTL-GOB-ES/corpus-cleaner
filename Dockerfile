FROM ubuntu as intermediate

RUN apt-get update
RUN apt-get install -y git

ARG SSH_PRIVATE_KEY
ARG SSH_PUBLIC_KEY

RUN echo "$SSH_PRIVATE_KEY" > /etc/ssh/id_rsa && echo "$SSH_PUBLIC_KEY" > /etc/ssh/id_rsa.pub && chmod 600 /etc/ssh/id_rsa && chmod 600 /etc/ssh/id_rsa.pub && chmod 600 /etc/ssh/ && eval $(ssh-agent -s) && ssh-add /etc/ssh/id_rsa && ssh-add -l && cat /etc/ssh/id_rsa && cat /etc/ssh/id_rsa.pub && ssh-keyscan -t rsa github.com > /etc/ssh/known_hosts && GIT_SSH_COMMAND='ssh -i /etc/ssh/id_rsa -o IdentitiesOnly=yes -o StrictHostKeyChecking=no' git clone git@github.com:TeMU-BSC/corpus-cleaner.git


FROM ubuntu:18.04

COPY --from=intermediate /corpus-cleaner /corpus-cleaner

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


RUN mkdir /cc

RUN mv /corpus-cleaner /cc

RUN rm -rf /cc/corpus-cleaner/data/

RUN rm -rf /cc/corpus-cleaner/output/

RUN python3 -m pip install -r /cc/corpus-cleaner/requirements.txt

RUN bash /cc/corpus-cleaner/get-third-party-docker.sh

ENTRYPOINT ["bash", "/cc/corpus-cleaner/entrypoint.sh"]
