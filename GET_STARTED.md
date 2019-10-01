
# Get started!

Learn how to standardize data using the pipe!

## Cheatsheet

```shell
make install # creates a virtual environment and install the dependencies
make build # build the docker image
make publish # publish the docker image to the docker hub
```

## 1 Configuration

But first, you need some data! We will use the MIMIC III Clinical Database Demo, for which you need to get credentials. It's quite straightforward: register [on the Physionet website](https://mimic.physionet.org/gettingstarted/demo/) to get access to the demo data, it takes 30 seconds and you will get a username and a password. Then, access [this page](https://physionet.org/works/MIMICIIIClinicalDatabaseDemo/) to sign the agreement needed to download the data (_you don't need to download the data yourself_) or click on this button:

[![Physionet Agreement](https://img.shields.io/badge/Physionet-Sign%20Agreement-green.svg?style=for-the-badge)](https://physionet.org/pnw/a/self-register?project=/works/MIMICIIIClinicalDatabaseDemo/index.shtml)


Then, copy `.env.example` into `.env` and edit the file last to add your physionet credentials.

```
cp .env.example .env
vi .env
source .env
```

## 2-A Docker Setup

You can use Docker to start quickly playing with demos. Alternatively, the **[2.B Manual Setup](#2-b-manual-setup)** section explains how to install the pipeline step by step.

Start [or install](https://docs.docker.com/install/#supported-platforms) Docker, and then build the docker images.
```
docker-compose build
```

Then start the services:
```
docker-compose up
```

Then, switch to another tab and connect to the pipeline container:

```
docker exec -ti arkhn-pipe-mimic /bin/bash
```

You can now directly go to **[3 Launch the pipe](#3-launch-the-pipe)**.

## 2-B Manual Setup

If you're not experienced with the project, we recommend that you first go through the **[2.A Docker Setup](#2-a-docker-setup)**. We still use Docker to get the MIMIC database set up along with the database where the FHIR data will be stored, but the ETL will be run from your local computer.

Open `docker-compose.yml` to check that the local ports used are not used by your current apps.
```
vi docker-compose.yml 
```

Run in specific tabs the two database containers we depend on:
```
docker-compose up --build mimic-db
docker-compose up --build fhirbase
```

Check that the container ports defined in `config.yml` match with those specified in `docker-compose.yml`

```
vi config.yml
```

Run the python setup to use our commands in the terminal:

```
# you might need to install packages manually:
pip install -r requirements.txt

python setup.py install
```

## 3. Launch the pipe


And to run to whole pipe

```
fhirpipe-run --project=Mimic
```

> You can use the option `--use-graphql-file=True` to fetch the mapping rules directly from a static file instead of the [pyrog](https://github.com/arkhn/pyrog) api. In this case, you need to provide a token in `config.yml` for the graphql access. Contact us at [contact@arkhn.org](mailto:contact@arkhn.org?subject=Ask%20access%20to%20GraphQL%20api) to get one.

You can also run the pipe on a single FHIR resource:

```
fhirpipe-run-resource --project=Mimic --resource=Patient
```

Et voilà!

---

## Miscellaneous

#### Check the fhirbase

You can check fhirbase to see if the data was correctly loaded (_make sure the port is correct_):

```
psql -h 0.0.0.0 -p 5433 -U postgres -d fhirbase
fhirbase=# select count(*) from patient;
```

#### Check for data in the mimic container

To check if the data was correctly loaded in the mimic container, you can execute this in a new terminal:

```
$ docker exec -ti fhir-pipe-mimic-db psql -d mimic -U mimicuser -c 'SELECT count(subject_id) FROM patients'
 count
-------
   100
(1 row)
```

#### Install packages on the container

You might want to change stuff directly on the container.

Example for `nano`:
```
apt update
apt install nano
```

#### Reload the mimic container

You can then shutdown the database with `ctrl-c` or with `docker-compose down mimic-db`

In case of troubles, note that the setup scripts are executed only if the PSQL database is empty.
To clear the previously build dockers and databases to re-start from a clean state, please run :

```
docker-compose down mimic-db
docker volume rm fhir-pipe-mimic-db
```

And, after that, if you have to re-build the docker (for example to take into account the values setup in `.env` file), please run :

```
docker-compose build mimic-db
```

> :warning: You may experience trouble if the postgres port is already taken. You can modify it in `docker-compose.yml`



#### Manual setup of fhirbase

Get the image and fill the database

```
docker pull fhirbase/fhirbase:latest

docker run --rm -p 3000:3000 -p 5433:5432 -d --name fhir-pipe-fhirbase fhirbase/fhirbase:latest

# Wait a few seconds...
docker exec fhir-pipe-fhirbase psql -c "CREATE DATABASE fhirbase"

# Fill the db
docker exec fhir-pipe-fhirbase fhirbase -d fhirbase --fhir=3.0.1 init # if it fails => it's already good, skip it
docker exec fhir-pipe-fhirbase fhirbase -d fhirbase --fhir=3.0.1 load /bundle.ndjson.gzip
```

#### Install the pipe locally

You should install it in an isolated virtual environment, by using virtualenv or Pipenv for example.

```
pip install -r requirements.txt
pip install -e .
```

 Make sure you already have the docker containers with mimic and fhirbase running.

Copy `config_local.yml` (from the `fhirpipe` directory) into `config.yml` and put there your credentials. (Don't forget to change the postgres ports if needed).

```
cp config_local.yml config.yml
```

Finish the install and run the tests to check all works fine
```
cd ..
python setup.py install
python setup.py test
```

#### Run the pipe locally

Let's now run locally the pipeline!

You are all set! Run:

```
fhirpipe-run --project=Mimic --resource=Patient --main-table=Patients --use-graphql-file=True
```

Remove `--use-graphql-file=True` to get the latest mapping rules from the pyrog api.

