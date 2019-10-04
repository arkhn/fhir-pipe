-- -------------------------------------------------------------------------------
--
-- Load data into the MIMIC-III schema
--
-- -------------------------------------------------------------------------------

--------------------------------------------------------
--  File created - Thursday-August-27-2015
--------------------------------------------------------

-- Change to the directory containing the data files
\cd /mimic_data

-- If running scripts individually, you can set the schema where all tables are created as follows:
-- SET search_path TO mimiciii;

-- Restoring the search path to its default value can be accomplished as follows:
-- SET search_path TO "$user",public;


--------------------------------------------------------
--  Load Data for Table ADMISSIONS
--------------------------------------------------------

\copy ADMISSIONS FROM 'admissions.csv' DELIMITER ',' CSV HEADER NULL ''

--------------------------------------------------------
--  Load Data for Table CALLOUT
--------------------------------------------------------

\copy CALLOUT from 'callout.csv' delimiter ',' csv header NULL ''

--------------------------------------------------------
--  Load Data for Table CAREGIVERS
--------------------------------------------------------

\copy CAREGIVERS from 'caregivers.csv' delimiter ',' csv header NULL ''

--------------------------------------------------------
--  Load Data for Table CHARTEVENTS
--------------------------------------------------------

\copy CHARTEVENTS from 'chartevents.csv' delimiter ',' csv header NULL ''

--------------------------------------------------------
--  Load Data for Table CPTEVENTS
--------------------------------------------------------

\copy CPTEVENTS from 'cptevents.csv' delimiter ',' csv header NULL ''

--------------------------------------------------------
--  Load Data for Table DATETIMEEVENTS
--------------------------------------------------------

\copy DATETIMEEVENTS from 'datetimeevents.csv' delimiter ',' csv header NULL ''

--------------------------------------------------------
--  Load Data for Table DIAGNOSES_ICD
--------------------------------------------------------

\copy DIAGNOSES_ICD from 'diagnoses_icd.csv' delimiter ',' csv header NULL ''

--------------------------------------------------------
--  Load Data for Table DRGCODES
--------------------------------------------------------

\copy DRGCODES from 'drgcodes.csv' delimiter ',' csv header NULL ''

--------------------------------------------------------
--  Load Data for Table D_CPT
--------------------------------------------------------

\copy D_CPT from 'd_cpt.csv' delimiter ',' csv header NULL ''

--------------------------------------------------------
--  Load Data for Table D_ICD_DIAGNOSES
--------------------------------------------------------

\copy D_ICD_DIAGNOSES from 'd_icd_diagnoses.csv' delimiter ',' csv header NULL ''

--------------------------------------------------------
--  Load Data for Table D_ICD_PROCEDURES
--------------------------------------------------------

\copy D_ICD_PROCEDURES from 'd_icd_procedures.csv' delimiter ',' csv header NULL ''

--------------------------------------------------------
--  Load Data for Table D_ITEMS
--------------------------------------------------------

\copy D_ITEMS from 'd_items.csv' delimiter ',' csv header NULL ''

--------------------------------------------------------
--  Load Data for Table D_LABITEMS
--------------------------------------------------------

\copy D_LABITEMS from 'd_labitems.csv' delimiter ',' csv header NULL ''

--------------------------------------------------------
--  Load Data for Table ICUSTAYS
--------------------------------------------------------

\copy ICUSTAYS from 'icustays.csv' delimiter ',' csv header NULL ''

--------------------------------------------------------
--  Load Data for Table INPUTEVENTS_CV
--------------------------------------------------------

\copy INPUTEVENTS_CV from 'inputevents_cv.csv' delimiter ',' csv header NULL ''

--------------------------------------------------------
--  Load Data for Table INPUTEVENTS_MV
--------------------------------------------------------

\copy INPUTEVENTS_MV from 'inputevents_mv.csv' delimiter ',' csv header NULL ''

--------------------------------------------------------
--  Load Data for Table LABEVENTS
--------------------------------------------------------

\copy LABEVENTS from 'labevents.csv' delimiter ',' csv header NULL ''

--------------------------------------------------------
--  Load Data for Table MICROBIOLOGYEVENTS
--------------------------------------------------------

\copy MICROBIOLOGYEVENTS from 'microbiologyevents.csv' delimiter ',' csv header NULL ''

--------------------------------------------------------
--  Load Data for Table NOTEEVENTS
--------------------------------------------------------

\copy NOTEEVENTS from 'noteevents.csv' delimiter ',' csv header NULL ''

--------------------------------------------------------
--  Load Data for Table OUTPUTEVENTS
--------------------------------------------------------

\copy OUTPUTEVENTS from 'outputevents.csv' delimiter ',' csv header NULL ''

--------------------------------------------------------
--  Load Data for Table PATIENTS
--------------------------------------------------------

\copy PATIENTS from 'patients.csv' delimiter ',' csv header NULL ''

--------------------------------------------------------
--  Load Data for Table PRESCRIPTIONS
--------------------------------------------------------

\copy PRESCRIPTIONS from 'prescriptions.csv' delimiter ',' csv header NULL ''

--------------------------------------------------------
--  Load Data for Table PROCEDUREEVENTS_MV
--------------------------------------------------------

\copy PROCEDUREEVENTS_MV from 'procedureevents_mv.csv' delimiter ',' csv header NULL ''

--------------------------------------------------------
--  Load Data for Table PROCEDURES_ICD
--------------------------------------------------------

\copy PROCEDURES_ICD from 'procedures_icd.csv' delimiter ',' csv header NULL ''

--------------------------------------------------------
--  Load Data for Table SERVICES
--------------------------------------------------------

\copy SERVICES from 'services.csv' delimiter ',' csv header NULL ''

--------------------------------------------------------
--  Load Data for Table TRANSFERS
--------------------------------------------------------

\copy TRANSFERS from 'transfers.csv' delimiter ',' csv header NULL ''
