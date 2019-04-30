
# Get started!

To standardize data with the pipe, you need some data! Let's set up a database filled with the MIMIC III Clinical Database Demo.

## Configuration & Setup

First, register [on the Physionet website](https://mimic.physionet.org/gettingstarted/demo/) on the official website to get access to the demo data, it takes 30 seconds and you will get a username and a password. Access [this page](https://physionet.org/works/MIMICIIIClinicalDatabaseDemo/) to sign the agreement needed to download the data.

Then copy `.env.example` into `.env` and edit this last to configure it with your physionet credentials.

```
cp .env.example .env
source .env
```

In the fhir-pipe repo, copy `config_demo.yml` (from the `fhirpipe` directory) into `config.yml` and put there your credentials, check that the ports are valid.

```
cp config_demo.yml config.yml
```

## Launch the pipe


```
docker-compose up --build arkhn-pipe-mimic
```

Then, connect to the pipe container:

```
docker exec -ti arkhn-pipe-mimic /bin/bash
```

And to run to whole pipe

```
fhirpipe-run --project=Mimic
```

> You can add `--use-graphql-file=True` if you prefer to fetch the  mapping rules from a static file instead of the [pyrog](https://github.com/arkhn/pyrog) api

You can also run the pipe on a single FHIR resource:

```
fhirpipe-run-resource --project=Mimic --resource=Patient --use-graphql-file=True
```

Et voilà!

---

## Miscellaneous

#### Check the fhirbase

You can check fhirbase to see if the data was correctly loaded:

```
psql -h 0.0.0.0 -p 5433 -U postgres -d fhirbase
fhirbase=# select count(*) from patient;
```

#### Check for data in mimic container

To check if the data has been correctly loaded in the mimic container, you can execute this in a new terminal:

```
$ docker exec -ti fhir-pipe-mimic-db psql -d mimic -U mimicuser -c 'SELECT count(subject_id) FROM patients'
 count
-------
   100
(1 row)
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

Copy `config_demo.yml` (from the `fhirpipe` directory) into `config.yml` and put there your credentials. (Don't forget to change the postgres ports if needed).

```
cp config_demo.yml config.yml
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

