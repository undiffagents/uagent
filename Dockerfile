FROM ubuntu:18.04

# update apt-get
RUN apt-get update --fix-missing
RUN apt-get install -y software-properties-common

# install python
RUN apt-get install -y python3.7 python3.7-dev python3-pip

# install java
RUN apt-get install -y openjdk-11-jdk

# install ruby
RUN apt-get install -y ruby-full

# install prolog
RUN apt-get install -y swi-prolog

# make base directory
RUN mkdir -p /usr/src/uagent
WORKDIR /usr/src/uagent

# install python packages
COPY docker/requirements.txt ./docker/requirements.txt
RUN pip3 install --no-cache-dir -r docker/requirements.txt

# install libraries
COPY lib lib
RUN cd lib/ape && make build

# copy all files to container
COPY . .

# run entry script
ENTRYPOINT [ "bash", "docker/start.sh" ]
