To run the system using Docker:

* Install Docker Desktop for your machine: https://www.docker.com

* Create a Docker account: https://hub.docker.com

* Run Docker on your machine and log in
  - This will start a background server

* Open a shell and go to the uagent source code

* If this is your first time, you will need to create a local docker machine as follows:

    docker/create.sh

* To run the uagent code, simply enter:

    docker/run.sh

  - The first time you run this, it will create a clean ubuntu virtual machine and then
    will install all the various languages and packages needed for the project.
  - When you run this subsequent times, it will use cached versions of the virtual
    machine and will skip directly to running the new code.
