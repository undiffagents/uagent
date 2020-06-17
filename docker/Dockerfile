FROM ubuntu:18.04

# install python
RUN apt-get update --fix-missing && apt-get install -y \
    python3.8 \
    python3.8-dev \
    python3-pip \
    && rm -fr /var/lib/apt/lists/*

# install other
RUN apt-get update --fix-missing && apt-get install -y \
    openjdk-11-jdk \
    ruby-full \
    swi-prolog \
    && rm -fr /var/lib/apt/lists/*

# make base directory
RUN mkdir -p /usr/src/uagent
WORKDIR /usr/src/uagent

# install python packages
COPY docker/requirements.txt ./docker/requirements.txt
RUN pip3 install --no-cache-dir -r docker/requirements.txt

# install project libraries
COPY lib lib
RUN cd lib/ape && make build

# copy all files to container
COPY . .

# run entry script
ENTRYPOINT [ "bash", "run.sh" ]
