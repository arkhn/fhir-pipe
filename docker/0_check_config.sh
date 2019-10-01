#!/bin/bash

echo 'Check downloaded MIMIC data files ... '

EXT='.csv'
ALLTABLES='admissions callout caregivers chartevents cptevents datetimeevents d_cpt diagnoses_icd d_icd_diagnoses d_icd_procedures d_items d_labitems drgcodes icustays inputevents_cv inputevents_mv labevents microbiologyevents noteevents outputevents patients prescriptions procedureevents_mv procedures_icd services transfers'
for TBL in $ALLTABLES; do
    if [ ! -e "/mimic_data/${TBL}$EXT" ];
    then
        echo "Unable to find ${TBL}$EXT in /mimic_data"
        exit 1
    fi
done
echo "Found all tables in /mimic_data - beginning import from $EXT files."
