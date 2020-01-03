#!/bin/bash

echo 'Check downloaded MIMIC data files ... '

EXT='.csv'
ALLTABLES='ADMISSIONS CALLOUT CAREGIVERS CHARTEVENTS CPTEVENTS DATETIMEEVENTS D_CPT DIAGNOSES_ICD D_ICD_DIAGNOSES D_ICD_PROCEDURES D_ITEMS D_LABITEMS DRGCODES ICUSTAYS INPUTEVENTS_CV INPUTEVENTS_MV LABEVENTS MICROBIOLOGYEVENTS NOTEEVENTS OUTPUTEVENTS PATIENTS PRESCRIPTIONS PROCEDUREEVENTS_MV PROCEDURES_ICD SERVICES TRANSFERS'
for TBL in $ALLTABLES; do
    if [ ! -e "/mimic_data/${TBL}$EXT" ];
    then
        echo "Unable to find ${TBL}$EXT in /mimic_data"
        exit 1
    fi
done
echo "Found all tables in /mimic_data - beginning import from $EXT files."
