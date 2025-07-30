#!/bin/bash
echo "Starting venv"
source ${HOME}/samothrace-pseudonymization/samothrace-env/bin/activate
echo "Venv started"

echo "Running experiments"

echo "Patient t 2 n 3"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script_new.py -r ${HOME}/samothrace-pseudonymization/dataset/extracted/Patient/ -g ${HOME}/samothrace-pseudonymization/dataset/analysis/grouped/Patient/group_0.json -t 2 -n 3 -i 100 -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
echo "Condition t 2 n 3"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script_new.py -r ${HOME}/samothrace-pseudonymization/dataset/extracted/Condition/ -g ${HOME}/samothrace-pseudonymization/dataset/analysis/grouped/Condition/group_0.json -t 2 -n 3 -i 100 -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
echo "DiagnosticReport t 2 n 3"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script_new.py -r ${HOME}/samothrace-pseudonymization/dataset/extracted/DiagnosticReport/ -g ${HOME}/samothrace-pseudonymization/dataset/analysis/grouped/DiagnosticReport/group_0.json -t 2 -n 3 -i 100 -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
echo "Encounter t 2 n 3"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script_new.py -r ${HOME}/samothrace-pseudonymization/dataset/extracted/Encounter/ -g ${HOME}/samothrace-pseudonymization/dataset/analysis/grouped/Encounter/group_0.json -t 2 -n 3 -i 100 -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
echo "Observation t 2 n 3"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script_new.py -r ${HOME}/samothrace-pseudonymization/dataset/extracted/Observation/ -g ${HOME}/samothrace-pseudonymization/dataset/analysis/grouped/Observation/group_0.json -t 2 -n 3 -i 100 -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct

echo "Patient t 3 n 5"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script_new.py -r ${HOME}/samothrace-pseudonymization/dataset/extracted/Patient/ -g ${HOME}/samothrace-pseudonymization/dataset/analysis/grouped/Patient/group_0.json -t 3 -n 5 -i 100 -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
echo "Condition t 3 n 5"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script_new.py -r ${HOME}/samothrace-pseudonymization/dataset/extracted/Condition/ -g ${HOME}/samothrace-pseudonymization/dataset/analysis/grouped/Condition/group_0.json -t 3 -n 5 -i 100 -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
echo "DiagnosticReport t 3 n 5"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script_new.py -r ${HOME}/samothrace-pseudonymization/dataset/extracted/DiagnosticReport/ -g ${HOME}/samothrace-pseudonymization/dataset/analysis/grouped/DiagnosticReport/group_0.json -t 3 -n 5 -i 100 -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
echo "Encounter t 3 n 5"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script_new.py -r ${HOME}/samothrace-pseudonymization/dataset/extracted/Encounter/ -g ${HOME}/samothrace-pseudonymization/dataset/analysis/grouped/Encounter/group_0.json -t 3 -n 5 -i 100 -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
echo "Observation t 3 n 5"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script_new.py -r ${HOME}/samothrace-pseudonymization/dataset/extracted/Observation/ -g ${HOME}/samothrace-pseudonymization/dataset/analysis/grouped/Observation/group_0.json -t 3 -n 5 -i 100 -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct

echo "Patient t 4 n 7"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script_new.py -r ${HOME}/samothrace-pseudonymization/dataset/extracted/Patient/ -g ${HOME}/samothrace-pseudonymization/dataset/analysis/grouped/Patient/group_0.json -t 4 -n 7 -i 100 -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
echo "Condition t 4 n 7"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script_new.py -r ${HOME}/samothrace-pseudonymization/dataset/extracted/Condition/ -g ${HOME}/samothrace-pseudonymization/dataset/analysis/grouped/Condition/group_0.json -t 4 -n 7 -i 100 -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
echo "DiagnosticReport t 4 n 7"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script_new.py -r ${HOME}/samothrace-pseudonymization/dataset/extracted/DiagnosticReport/ -g ${HOME}/samothrace-pseudonymization/dataset/analysis/grouped/DiagnosticReport/group_0.json -t 4 -n 7 -i 100 -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
echo "Encounter t 4 n 7"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script_new.py -r ${HOME}/samothrace-pseudonymization/dataset/extracted/Encounter/ -g ${HOME}/samothrace-pseudonymization/dataset/analysis/grouped/Encounter/group_0.json -t 4 -n 7 -i 100 -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
echo "Observation t 4 n 7"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script_new.py -r ${HOME}/samothrace-pseudonymization/dataset/extracted/Observation/ -g ${HOME}/samothrace-pseudonymization/dataset/analysis/grouped/Observation/group_0.json -t 4 -n 7 -i 100 -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct

echo "Patient t 5 n 9"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script_new.py -r ${HOME}/samothrace-pseudonymization/dataset/extracted/Patient/ -g ${HOME}/samothrace-pseudonymization/dataset/analysis/grouped/Patient/group_0.json -t 5 -n 9 -i 100 -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
echo "Condition t 5 n 9"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script_new.py -r ${HOME}/samothrace-pseudonymization/dataset/extracted/Condition/ -g ${HOME}/samothrace-pseudonymization/dataset/analysis/grouped/Condition/group_0.json -t 5 -n 9 -i 100 -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
echo "DiagnosticReport t 5 n 9"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script_new.py -r ${HOME}/samothrace-pseudonymization/dataset/extracted/DiagnosticReport/ -g ${HOME}/samothrace-pseudonymization/dataset/analysis/grouped/DiagnosticReport/group_0.json -t 5 -n 9 -i 100 -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
echo "Encounter t 5 n 9"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script_new.py -r ${HOME}/samothrace-pseudonymization/dataset/extracted/Encounter/ -g ${HOME}/samothrace-pseudonymization/dataset/analysis/grouped/Encounter/group_0.json -t 5 -n 9 -i 100 -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
echo "Observation t 5 n 9"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script_new.py -r ${HOME}/samothrace-pseudonymization/dataset/extracted/Observation/ -g ${HOME}/samothrace-pseudonymization/dataset/analysis/grouped/Observation/group_0.json -t 5 -n 9 -i 100 -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct


echo "Experiments finished"