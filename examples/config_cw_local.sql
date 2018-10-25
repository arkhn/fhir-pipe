-- File to populate a mock CW DB (note that the tables are not complete)
-- psql -f config_cw_local.sql

DROP DATABASE IF EXISTS cw_local;

CREATE DATABASE cw_local;

\c cw_local

CREATE TABLE PATIENT (
    ID SERIAL,
    NOPAT varchar,
    DTNAIS varchar,
    NOMPAT varchar,
    PREPAT varchar,
    SEXE varchar,
    DECEDE varchar,
    DTDECES varchar
);

INSERT INTO PATIENT (NOPAT, DTNAIS, NOMPAT, PREPAT, SEXE, DECEDE, DTDECES) VALUES (
    '0000000283',
    '19700401',
    'SARDOU',
    'MICHELLE',
    'F',
    'N',
    ''
);

INSERT INTO PATIENT (NOPAT, DTNAIS, NOMPAT, PREPAT, SEXE, DECEDE, DTDECES) VALUES (
    '0000000285',
    '19940506',
    'KIRIKOU',
    'MARCEL',
    'M',
    'O',
    '20180922'
);


CREATE TABLE MEDECIN (
    ID SERIAL,
    NOMED varchar,
    GENRE varchar,
    NOM varchar,
    PRENOM varchar,
    ADR1 varchar,
    ADR2 varchar,
    ADR3 varchar,
    ADR4 varchar,
    CP varchar,
    VILLE varchar,
    TEL varchar,
    FAX varchar,
    TEL2 varchar,
    NOSPE varchar,
    RPPS varchar,
    ADELI varchar
);

INSERT INTO MEDECIN (NOMED, GENRE, NOM, PRENOM, ADR1, ADR2, ADR3, ADR4, CP, VILLE, TEL, FAX, TEL2, NOSPE, RPPS, ADELI) VALUES (
    '0000000058',
    'F',
    'MAROUDE',
    'Joselyne',
    'DE RADIOLOGIE',
    'HOPITAL CHARLES PASQUA',
    '9 rue des Sablons',
    'NaN',
    '54000',
    'MARSEILLE',
    '01-80-71-00-00 ()',
    '01-80-71-00-00 ()',
    '----()',
    '0000000001',
    '10000806106',
    '921304809'
);

INSERT INTO MEDECIN (NOMED, GENRE, NOM, PRENOM, ADR1, ADR2, ADR3, ADR4, CP, VILLE, TEL, FAX, TEL2, NOSPE, RPPS, ADELI) VALUES (
    '0000000059',
    'F',
    'Jugulaire',
    'Wilfried',
    'NaN',
    'NaN',
    '90 rue des SOleils',
    'NaN',
    '79100',
    'FORET EN FORET',
    '01-80-71-00-00 ()',
    '',
    '----()',
    '0000000007',
    '10000906306',
    '932104809'
);

CREATE TABLE PATADR (
    ID SERIAL,
    NOPAT varchar,
    ADR1 varchar,
    ADR2 varchar,
    ADR3 varchar,
    ADR4 varchar,
    CP varchar,
    VILLE varchar,
    TEL varchar,
    NOPAYS varchar
);

INSERT INTO PATADR (NOPAT, ADR1, ADR2, ADR3, ADR4, CP, VILLE, TEL, NOPAYS) VALUES (
    '0000000283',
    '3 rue Soufflot',
    'Batiment 23',
    '',
    '',
    '75005',
    'Paris 5e',
    '01-34.87 21 00',
    '0000000001'
);

INSERT INTO PATADR (NOPAT, ADR1, ADR2, ADR3, ADR4, CP, VILLE, TEL, NOPAYS) VALUES (
   '0000000285',
   '69 Bvd St Germain',
   'Hôtel de Guermantes',
    '',
    '',
   '75006',
   'Paris',
   '01-00.87 20 00',
   '0000000014'
);

CREATE TABLE PAYS (
   ID SERIAL,
   NOPAYS varchar,
   LIBELLE varchar
);

INSERT INTO PAYS (NOPAYS, LIBELLE) VALUES (
   '0000000001',
   'FRANCE'
);

INSERT INTO PAYS (NOPAYS, LIBELLE) VALUES (
   '0000000014',
   'LIECHTENSTEIN'
);

CREATE TABLE SPEMED (
   ID SERIAL,
   NOSPE varchar,
   LIBELLE varchar
);

INSERT INTO SPEMED (NOSPE, LIBELLE) VALUES (
   '0000000001',
   'MEDECINE GENERALE'
);

INSERT INTO SPEMED (NOSPE, LIBELLE) VALUES (
   '0000000007',
   'NEURO-CHIRURGIE'
);

INSERT INTO SPEMED (NOSPE, LIBELLE) VALUES (
   '0000000009',
   'PNEUMOLOGIE'
);

CREATE TABLE PATCOMP (
	ID SERIAL,
	TRAITANT_DECLARE varchar,
	STATUT_DDN varchar,
	TELPORT varchar,
	INSEE varchar,
	NOMUT varchar,
	NOCAISSE varchar,
	RELIGION varchar,
	TYPETXT varchar,
	ALD varchar,
	DECES_SANG varchar,
	STATUTID varchar,
	ID_DOUTE varchar,
	LIB_DOUTE varchar,
	ID_USURPATION varchar,
	PIECE_VALIDANTE varchar,
	RECID varchar,
	NOPAT varchar,
	NUMARCH varchar,
	SITUAFAM varchar,
	PROFESSION varchar,
	CODEPCS varchar,
	NBENFANT varchar,
	NBFRERE varchar,
	NUMSECU varchar,
	TAUXPEC varchar,
	MUTUELLE varchar,
	HRNAIS varchar,
	CPNAIS varchar,
	VILLENAIS varchar,
	GRPSANG varchar,
	RHESUS varchar,
	DTMAJ varchar,
	DTDERNLE varchar,
	LIEUDERNLE varchar,
	NONATION varchar,
	NOLANGUE varchar,
	NOPAYS varchar,
	ETAT varchar,
	TIMESTAMP varchar,
	HOST varchar,
	PHENO varchar,
	KELL varchar,
	RAI varchar,
	NOUTILRAI varchar,
	CODEASP varchar,
	IDPROT varchar,
	PERHOSP varchar,
	TELPROF varchar
);

INSERT INTO PATCOMP (TRAITANT_DECLARE, STATUT_DDN, TELPORT, INSEE, NOMUT, NOCAISSE, RELIGION, TYPETXT, ALD, DECES_SANG, STATUTID, ID_DOUTE, LIB_DOUTE, ID_USURPATION, PIECE_VALIDANTE, RECID, NOPAT, NUMARCH, SITUAFAM, PROFESSION, CODEPCS, NBENFANT, NBFRERE, NUMSECU, TAUXPEC, MUTUELLE, HRNAIS, CPNAIS, VILLENAIS, GRPSANG, RHESUS, DTMAJ, DTDERNLE, LIEUDERNLE, NONATION, NOLANGUE, NOPAYS, ETAT, TIMESTAMP, HOST, PHENO, KELL, RAI, NOUTILRAI, CODEASP, IDPROT, PERHOSP, TELPROF) VALUES (
'', '', '', '27970', '', '', '', '', '', '', '', '', '', '', '', '', '0000000283', '', 'M', '', '', '', '', '189000111222000', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''
);
INSERT INTO PATCOMP (TRAITANT_DECLARE, STATUT_DDN, TELPORT, INSEE, NOMUT, NOCAISSE, RELIGION, TYPETXT, ALD, DECES_SANG, STATUTID, ID_DOUTE, LIB_DOUTE, ID_USURPATION, PIECE_VALIDANTE, RECID, NOPAT, NUMARCH, SITUAFAM, PROFESSION, CODEPCS, NBENFANT, NBFRERE, NUMSECU, TAUXPEC, MUTUELLE, HRNAIS, CPNAIS, VILLENAIS, GRPSANG, RHESUS, DTMAJ, DTDERNLE, LIEUDERNLE, NONATION, NOLANGUE, NOPAYS, ETAT, TIMESTAMP, HOST, PHENO, KELL, RAI, NOUTILRAI, CODEASP, IDPROT, PERHOSP, TELPROF) VALUES (
'', '', '', '262000111222000', '', '', '', '', '', '', '', '', '', '', '', '', '0000000285', '', 'V', '', '', '', '', 'NaN', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''
);


CREATE TABLE TYPELIEN (
	ID SERIAL,
	NOLIEN_PARENTE varchar,
	GENRE varchar,
	NOLIEN_PAR_INV varchar,
	AUTORISATION_OPERATION varchar,
	CONSENTEMENT_OPERATION varchar,
	LIENFAMILIAL varchar,
	RECID varchar,
	NOTYPELIEN varchar,
	CODE varchar,
	LIBELLE varchar,
	ETAT varchar,
	TIMESTAMP varchar
);

INSERT INTO TYPELIEN (NOLIEN_PARENTE, GENRE, NOLIEN_PAR_INV, AUTORISATION_OPERATION, CONSENTEMENT_OPERATION, LIENFAMILIAL, RECID, NOTYPELIEN, CODE, LIBELLE, ETAT, TIMESTAMP) VALUES (
'', '', '', '', '', 'Pere', '', '0000000001', '', '', '', ''
);

INSERT INTO TYPELIEN (NOLIEN_PARENTE, GENRE, NOLIEN_PAR_INV, AUTORISATION_OPERATION, CONSENTEMENT_OPERATION, LIENFAMILIAL, RECID, NOTYPELIEN, CODE, LIBELLE, ETAT, TIMESTAMP) VALUES (
'', '', '', '', '', 'Mere', '', '0000000002', '', '', '', ''
);

INSERT INTO TYPELIEN (NOLIEN_PARENTE, GENRE, NOLIEN_PAR_INV, AUTORISATION_OPERATION, CONSENTEMENT_OPERATION, LIENFAMILIAL, RECID, NOTYPELIEN, CODE, LIBELLE, ETAT, TIMESTAMP) VALUES (
'', '', '', '', '', 'Femme', '', '0000000003', '', '', '', ''
);

INSERT INTO TYPELIEN (NOLIEN_PARENTE, GENRE, NOLIEN_PAR_INV, AUTORISATION_OPERATION, CONSENTEMENT_OPERATION, LIENFAMILIAL, RECID, NOTYPELIEN, CODE, LIBELLE, ETAT, TIMESTAMP) VALUES (
'', '', '', '', '', 'Mari', '', '0000000004', '', '', '', ''
);

CREATE TABLE PAT_PAP (
	ID SERIAL,
	RECID varchar,
	NOPC varchar,
	NOPAT varchar,
	NOM varchar,
	PRENOM varchar,
	ADR1 varchar,
	ADR2 varchar,
	ADR3 varchar,
	ADR4 varchar,
	CP varchar,
	VILLE varchar,
	NOPAYS varchar,
	TELDOM varchar,
	TELPROF varchar,
	TELMOB varchar,
	NOMAILADR varchar,
	NOTYPE_LP varchar,
	COMMENTAIRE varchar,
	ETAT varchar,
	TIMESTAMP varchar,
	NOPCEXT varchar,
	NOADREDIFACT varchar,
	GENRE varchar
);

INSERT INTO PAT_PAP (RECID, NOPC, NOPAT, NOM, PRENOM, ADR1, ADR2, ADR3, ADR4, CP, VILLE, NOPAYS, TELDOM, TELPROF, TELMOB, NOMAILADR, NOTYPE_LP, COMMENTAIRE, ETAT, TIMESTAMP, NOPCEXT, NOADREDIFACT, GENRE) VALUES (
'', '', '0000000283', 'GOTTAR', 'Michel', '', '', '', '', '', '', '', '0666775328', '', '', '', '0000000001', '', '', '', '', '', ''
);

INSERT INTO PAT_PAP (RECID, NOPC, NOPAT, NOM, PRENOM, ADR1, ADR2, ADR3, ADR4, CP, VILLE, NOPAYS, TELDOM, TELPROF, TELMOB, NOMAILADR, NOTYPE_LP, COMMENTAIRE, ETAT, TIMESTAMP, NOPCEXT, NOADREDIFACT, GENRE) VALUES (
'', '', '0000000285', 'Guermantes', 'Alphonse', '', '', '', '', '', '', '', '06 86 79 53 63', '', '', '', '0000000002', '', '', '', '', '', ''
);

INSERT INTO PAT_PAP (RECID, NOPC, NOPAT, NOM, PRENOM, ADR1, ADR2, ADR3, ADR4, CP, VILLE, NOPAYS, TELDOM, TELPROF, TELMOB, NOMAILADR, NOTYPE_LP, COMMENTAIRE, ETAT, TIMESTAMP, NOPCEXT, NOADREDIFACT, GENRE) VALUES (
'', '', '0000000285', 'De Saint Loup', 'Robert', '', '', '', '', '', '', '', '', '', '07 86 29 00 61', '', '0000000003', '', '', '', '', '', ''
);


-- psql -f config_cw_local.sql