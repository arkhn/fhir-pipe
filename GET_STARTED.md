
# Get started!

To standardize data with the pipe, you need some data! Let's set up a database filled with the MIMIC III Clinical Database Demo.

## Configure MIMIC demo dataset credentials

First, register [here](https://mimic.physionet.org/gettingstarted/demo/) on the official website to get access to the demo data, it takes 30 seconds and you'll set a username and a password. This will be needed to download the data.

Then copy `.env.example` into `.env` and edit this last to configure it with yours physionet credentials.

## Build the database docker

This will download the data sources and load its to the PSQL database. The logs should give you hints
if anything is going wrong.

```
docker-compose up mimic-db
```

To check if data are well loaded, you can execute this in a new terminal :

```
$ docker exec -ti fhir-pipe-mimic-db psql -d mimic -U mimicuser -c 'SELECT count(subject_id) FROM patients'
 count
-------
   100
(1 row)
```

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

Et voilà! Let's now standardize this database in the FHIR format!

## Setup the fhirbase

Get the image and fill the database

```
docker pull fhirbase/fhirbase:latest

docker run --rm -p 3000:3000 -d --name fhir-pipe-fhirbase fhirbase/fhirbase:latest

docker exec fhir-pipe-fhirbase psql -c "CREATE DATABASE fhirbase"

# Fill the db

docker exec fhir-pipe-fhirbase fhirbase -d fhirbase --fhir=3.0.1 init

docker exec fhir-pipe-fhirbase fhirbase -d fhirbase --fhir=3.0.1 load /bundle.ndjson.gzip
```

> How does this relates to the container defined in the docker-compose.yml ?

## Install the pipe locally

You should install it in an isolated virtual environment, by using virtualenv or Pipenv for example.

```
pip install -r requirements.txt
pip install -e .
```

## Run the pipe

Run locally the pipeline. You should already have the docker containers with mimic and fhirbase running.
You need to get the config.yml file, extracted from pyrog, into the fhirpipe sub-directory.

```
fhirpipe-run --project=Mimic --resource=Patient --main-table=Patients --use-graphql-file=True
```

Remove `--use-graphql-file=True` to get the latest mapping rules from the pyrog project.