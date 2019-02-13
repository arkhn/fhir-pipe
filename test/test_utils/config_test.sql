-- File to populate a test DB (note that the tables are not complete)
-- psql -f config_test.sql

DROP DATABASE IF EXISTS test;

CREATE DATABASE test;

\c test

CREATE TABLE CLIENT (
    ID SERIAL,
    CLIENT_ID varchar,
    NOM varchar,
    PRENOM varchar,
    ADRESSE_ID varchar
);

CREATE TABLE ANNONCE (
    ID SERIAL,
    CLIENT_ID varchar,
    TITRE varchar
);


CREATE TABLE ADRESSE (
    ID SERIAL,
    ADRESSE_ID varchar,
    ADRESSE varchar
);

INSERT INTO CLIENT (CLIENT_ID, NOM, PRENOM, ADRESSE_ID) VALUES (
    '01',
    'PASQUA',
    'Charles',
    '03'
);

INSERT INTO CLIENT (CLIENT_ID, NOM, PRENOM, ADRESSE_ID) VALUES (
    '02',
    'dassault',
    'serges',
    '04'
);

INSERT INTO ANNONCE (CLIENT_ID, TITRE) VALUES (
    '01',
    'Cherche une affaire'
);

INSERT INTO ANNONCE (CLIENT_ID, TITRE) VALUES (
    '02',
    'Vends des armes'
);

INSERT INTO ANNONCE (CLIENT_ID, TITRE) VALUES (
    '02',
    'Aime bien les cadeaux'
);

INSERT INTO ADRESSE (ADRESSE_ID, ADRESSE) VALUES (
    '03',
    'Fleury Mérogis'
);

INSERT INTO ADRESSE (ADRESSE_ID, ADRESSE) VALUES (
    '04',
    'La pitié'
);

-- psql -f config_test.sql