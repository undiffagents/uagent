FROM ubuntu:18.04

# install software
RUN apt-get update --fix-missing && apt-get install -y \
    software-properties-common \
    python3.7 python3.7-dev python3-pip \
    openjdk-11-jdk \
    ruby-full \
    swi-prolog \
 && rm -fr /var/lib/apt/lists/*

# make base directory
RUN mkdir -p /usr/src/uagent
WORKDIR /usr/src/uagent

# install python packages
COPY docker/python.txt ./docker/python.txt
RUN pip3 install --no-cache-dir -r docker/python.txt

# install project libraries
COPY lib lib
RUN cd lib/ape && make build

# copy all files to container
COPY . .

# run entry script
ENTRYPOINT [ "bash", "run.sh" ]
