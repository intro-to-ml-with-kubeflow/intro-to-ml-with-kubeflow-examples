#!/usr/bin/env bash

wget https://www.fmrib.ox.ac.uk/primers/intro_primer/ExBox14/ExBox14.zip
unzip ExBox14.zip

mv ExBox14/T1_brain.nii.gz src/T1_brain.nii.gz
mv ExBox14/T1_brain_mask.nii.gz src/T1_brain_mask.nii.gz


wget https://nifti.nimh.nih.gov/nifti-1/data/avg152T1_LR_nifti.nii.gz