CREATE TABLE caregivers (row_id integer, cgid integer);

CREATE TABLE admissions (
    row_id integer,
    subject_id integer,
    hadm_id integer,
    admittime timestamp,
    dischtime timestamp,
    marital_status varchar
);

CREATE TABLE diagnoses_icd (
    row_id integer,
    subject_id integer,
    icd9_code varchar
);

CREATE TABLE patients (
    row_id integer,
    subject_id integer,
    gender varchar,
    dob timestamp,
    dod timestamp,
    expire_flag integer
);

CREATE TABLE icustays (
    row_id integer,
    subject_id integer,
    hadm_id integer,
    icustay_id integer,
    intime timestamp,
    outtime timestamp
);

CREATE TABLE prescriptions (
    row_id integer,
    subject_id integer,
    startdate timestamp,
    enddate timestamp,
    drug varchar,
    ndc varchar,
    dose_val_rx varchar,
    dose_unit_rx varchar,
    route varchar
);

COPY caregivers (row_id, cgid)
FROM
    '/var/lib/postgresql/mockdata/caregivers.csv' CSV HEADER;

COPY admissions (
    row_id,
    subject_id,
    hadm_id,
    admittime,
    dischtime,
    marital_status
)
FROM
    '/var/lib/postgresql/mockdata/admissions.csv' CSV HEADER;

COPY diagnoses_icd (row_id, subject_id, icd9_code)
FROM
    '/var/lib/postgresql/mockdata/diagnoses_icd.csv' CSV HEADER;

COPY patients (row_id, subject_id, gender, dob, dod, expire_flag)
FROM
    '/var/lib/postgresql/mockdata/patients.csv' CSV HEADER;

COPY icustays (row_id, subject_id, hadm_id, icustay_id, intime, outtime)
FROM
    '/var/lib/postgresql/mockdata/icustays.csv' CSV HEADER;

COPY prescriptions (
    row_id,
    subject_id,
    startdate,
    enddate,
    drug,
    ndc,
    dose_val_rx,
    dose_unit_rx,
    route
)
FROM
    '/var/lib/postgresql/mockdata/prescriptions.csv' CSV HEADER;