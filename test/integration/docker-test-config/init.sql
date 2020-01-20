CREATE TABLE patients (
    row_id integer,
    subject_id integer,
    gender varchar,
    dob timestamp
);

CREATE TABLE admissions (subject_id integer, language varchar);

CREATE TABLE services (row_id integer, subject_id integer, curr_service varchar);

COPY patients (row_id, subject_id, gender, dob)
FROM
    '/var/lib/postgresql/mockdata/patients.csv' CSV HEADER;

COPY admissions (subject_id, language)
FROM
    '/var/lib/postgresql/mockdata/admissions.csv' CSV HEADER;

COPY services (row_id, subject_id, curr_service)
FROM
    '/var/lib/postgresql/mockdata/services.csv' CSV HEADER;