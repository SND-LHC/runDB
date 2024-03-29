# conditionsDB package

## Quickstart

### Prerequisite on client machines (ubuntu)

`pip install mongoengine`

### To access the conditions database on sndrundb.cern.ch:

1. Make an .ssh key on your (local, ie outside the cern.ch domain) machine using the command: `ssh-keygen -t rsa`; giva an empty passphrase).
2. Copy the id_rsa.pub key to your .ssh directory on lxplus.
3. Edit the ~/.ssh/config file on your local machine to define a tunnel (create it if it doesn't exist):

``` ssh-config
Host sndtun
  Hostname lxtunnel.cern.ch
  User your_lxplus_userid
  LocalForward 27017 sndrundb.cern.ch:27017
```

4. Edit the file conditionsDatabase/config.yml:

``` yaml
db_type: mongo
mongo:
  db_name: sndrundb
  host: localhost
  password: "sndrundb"
  port: 27017
  user: "sndatlhc"
```

5. Start the tunnel with the command: `ssh -N -f -q sndtun` or `ssh -L 27017:sndrundb.cern.ch:27017 lxtunnel -N`

6. It might be necessary to install kinit and do a `kinit userid@lxplus.cern.ch` before starting the tunnel.

### To add the geometry to the db from geofile_full.conical.Pythia8-TGeant4.root:

1. `export FAIRSHIP_ROOT=$SNDSW_ROOT`
2. make a geometry file with run_simScript.py
3. `python conditionsDatabase/snd_condDB.py` (takes appr. mins)

### To list the detectors in the database:

`python list_conDB.py -l n`, where n is the desired level.

### To add external dictionaries with conditions data to the database (for the SciFi)

`python scifi_conDB.py`

## Introduction

This package provides functionality to communicate with a conditions database (CDB) storage back-end.
It provides a generic API that facilitates storage and retrieval of conditions data from any supported
storage back-end.

### Supported storage back-ends
Currently, the following storage back-ends are supported:

* MongoDB

Installation on separate linux (centos) machine: follow instructions from https://docs.mongodb.com/manual/tutorial/install-mongodb-on-red-hat/

```bash
sudo systemctl stop mongod
sudo vi /etc/mongod.conf: bindIp: 0.0.0.0 # (tells mongo to listen to outside IPs)
sudo firewall-cmd --permanent --add-port 27017/tcp # (opens mongo's listening port to the firewall)
sudo firewall-cmd --reload # (reload the firewall)
sudo netstat -tunlp # (check that the port 27017 is open to tcp)
sudo systemctl start mongod
```

## Package structure

* [**databases/**] Contains storage back-end adapters. More information about these adapters can be found in the readme inside this directory.
* [**demo/**] Contains a documented demo script that demonstrates how to use the conditionsDB API.
* [**tests/**] Contains unit tests, regression tests and benchmarking scripts for this package and all supported storage adapters. More information about these tests and scripts can be found in the readme inside this directory.
* [**config.yml**] Default configuration file that will be used by the package's API factory to produce a CDB API instance.
* [**Dockerfile**] Example Dockerfile that generates a Docker image with a MongoDB server installed.
* [**Doxyfile**] Configuration file for Doxygen. See Documentation generation for more info.
* [**factory.py**] Module that implements the CDB API factory.
* [**interface.py**] Module that defines the CDB API.
* [**requirements.txt**] Package's Python dependencies list. Can be used by PIP to install the required package dependencies on the target machine.
* [**start_mongodb_locally.sh**] Shell script that starts a local MongoDB server (if installed). See further documentation inside the script.
* [**User manual.pdf**] User manual describing database set up procedures and main API use-cases.

## Package dependencies
### Python
The required Python dependencies for this package are listed in the `requirements.txt` file. This file can be used by PIP to automatically install these dependencies. Run `pip install -r requirements.txt` from the current directory to install all dependencies.

Make sure to update the `requirements.txt` file whenever there are new dependencies (e.g. when a new storage back-end adapter is implemented).

### Storage back-ends
Storage back-ends actually store the conditions data. A storage back-end can consist of a full-fledged database management system (like MongoDB) or consist of a simple text file. The corresponding back-end adapter will take care of all the necessary translations and operations between the CDB API and the storage back-end. In order to use a specific storage back-end this back-end must be available to the system (i.e. FairSHiP). For every supported storage back-end the required dependencies are listed below.

* [**MongoDB**] A MongoDB server, either installed locally or available via the network. See the User Manual for more info on how to set up a MongoDB server.

### aliBuild integration
Most of the FairSHiP users rely on the automatic building tool aliBuild (http://alisw.github.io/alibuild/). This tool uses build recipies to install all dependencies on the target machine, in correct order. These build recipies are located in a special repository: https://github.com/ShipSoft/shipdist. The dependencies for the CDB API are Python modules. In order for aliBuild to install these modules, we updated the relevant build recipe: `python_modules.sh`. The added Python dependencies are the same as the ones defined in `requirements.txt`.

## Documentation generation
For the generation of an API reference manual we use the documentation generator Doxygen. Configuration for Doxygen can be found in the `Doxyfile`. In order to (re)generate the documentation, you should first install Doxygen. Then inside the package's root folder ("conditionsDatabase") you will be able to find the Doxyfile, which is currently configured for the project. The commands that you should run are the following:

`doxygen Doxyfile` ---> produces the latex and html files for the reference manual.

`cd docs/latex` 	 ---> Inside this folder there is a makefile, which will produce the pdf.

`make pdf`	 ---> Produces the pdf. The name of the file will be "refman.pdf".

## Supported Python version
This package is developed to work with Python 2. However, wherever possible we tried to use constructs that are compatible with both Python 2 and 3. Also, whenever relevant we documented the code with updates that can be applied when porting to Python 3.
