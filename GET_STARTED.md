
# Get started!

To standardize data with the pipe, you need some data! Let's set up a database filled with the MIMIC III Clinical Database Demo.

## Load the MIMIC Database

First, register [here](https://mimic.physionet.org/gettingstarted/demo/) on the official website to get access to the demo data, it takes 30 seconds and you'll set a username and a password. This will be needed to download the data.

When you're done, go in your working directory and launch the docker postgres image

```
docker-compose up postgres-db
```

In the same directory, maybe in another tab, you can run the following to download the data. Make sure to replace `<login>` with the username you just set.

```
wget --user <login> --ask-password -A csv.gz -m -p -E -k -K -np https://physionet.org/works/MIMICIIIClinicalDatabaseDemo/files/
```

You will be ask to provide your password. Then, run the following sequence of operations to insert the data in the postgres database of the docker container.

```
mv physionet.org/works/MIMICIIIClinicalDatabaseDemo/files/version_1_4 static/resources

rm -r physionet.org

gzip -d static/resources/*.gz

curl https://raw.githubusercontent.com/MIT-LCP/mimic-code/master/buildmimic/postgres/postgres_create_tables.sql > ./static/postgres_create_tables.sql
curl https://raw.githubusercontent.com/MIT-LCP/mimic-code/master/buildmimic/postgres/postgres_load_data.sql > ./static/postgres_load_data.sql
curl https://raw.githubusercontent.com/MIT-LCP/mimic-code/master/buildmimic/postgres/postgres_add_indexes.sql > ./static/postgres_add_indexes.sql

docker exec -ti mimic_postgres-db_1 /bin/bash


psql -U mimicuser -d postgres

CREATE DATABASE mimic OWNER mimicuser;
\c mimic;
CREATE SCHEMA mimiciii;
set search_path to mimiciii;

\q

psql 'dbname=mimic user=mimicuser options=--search_path=mimiciii' -f /tmp/postgresql_mimic/postgres_create_tables.sql

psql 'dbname=mimic user=mimicuser options=--search_path=mimiciii' -f /tmp/postgresql_mimic/postgres_load_data.sql -v mimic_data_dir='/tmp/postgresql_mimic/resources/'

psql 'dbname=mimic user=mimicuser options=--search_path=mimiciii' -f /tmp/postgresql_mimic/postgres_add_indexes.sql

```
You can now connect and run normal sql:

```
psql 'dbname=mimic user=mimicuser options=--search_path=mimiciii'

select count(subject_id) from patients;
```

Et voilà! Let's now standardize this database in the FHIR format!

## Run the pipe