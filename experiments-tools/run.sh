#!/bin/bash
echo "Starting venv"
source ${HOME}/samothrace-pseudonymization/samothrace-env/bin/activate
echo "Venv started"

echo "Running experiments"

#echo "t4 n7 5k"
#python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/5k.json -t 4 -n 7 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
#echo "t4 n7 10k"
#python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/10k.json -t 4 -n 7 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
#echo "t4 n7 15k"
#python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/15k.json -t 4 -n 7 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
#echo "t4 n7 20k"
#python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/20k.json -t 4 -n 7 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
#echo "t4 n7 25k"
#python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/25k.json -t 4 -n 7 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
#echo "t4 n7 30k"
#python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/30k.json -t 4 -n 7 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
echo "t4 n7 40k"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/40k.json -t 4 -n 7 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
echo "t4 n7 50k"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/50k.json -t 4 -n 7 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
echo "t4 n7 60k"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/60k.json -t 4 -n 7 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
echo "t4 n7 70k"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/70k.json -t 4 -n 7 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
echo "t4 n7 80k"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/80k.json -t 4 -n 7 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
echo "t4 n7 90k"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/90k.json -t 4 -n 7 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
echo "t4 n7 100k"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/100k.json -t 4 -n 7 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct

#echo "t2 n3 5k"
#python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/5k.json -t 2 -n 3 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
#echo "t2 n3 10k"
#python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/10k.json -t 2 -n 3 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
#echo "t2 n3 15k"
#python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/15k.json -t 2 -n 3 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
#echo "t2 n3 20k"
#python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/20k.json -t 2 -n 3 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
#echo "t2 n3 25k"
#python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/25k.json -t 2 -n 3 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
#echo "t2 n3 30k"
#python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/30k.json -t 2 -n 3 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
echo "t2 n3 40k"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/40k.json -t 2 -n 3 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
echo "t2 n3 50k"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/50k.json -t 2 -n 3 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
echo "t2 n3 60k"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/60k.json -t 2 -n 3 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
echo "t2 n3 70k"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/70k.json -t 2 -n 3 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
echo "t2 n3 80k"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/80k.json -t 2 -n 3 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
echo "t2 n3 90k"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/90k.json -t 2 -n 3 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
echo "t2 n3 100k"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/100k.json -t 2 -n 3 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct

#echo "t5 n9 5k"
#python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/5k.json -t 5 -n 9 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
#echo "t5 n9 10k"
#python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/10k.json -t 5 -n 9 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
#echo "t5 n9 15k"
#python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/15k.json -t 5 -n 9 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
#echo "t5 n9 20k"
#python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/20k.json -t 5 -n 9 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
#echo "t5 n9 25k"
#python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/25k.json -t 5 -n 9 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
#echo "t5 n9 30k"
#python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/30k.json -t 5 -n 9 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
echo "t5 n9 40k"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/40k.json -t 5 -n 9 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
echo "t5 n9 50k"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/50k.json -t 5 -n 9 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
echo "t5 n9 60k"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/60k.json -t 5 -n 9 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
echo "t5 n9 70k"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/70k.json -t 5 -n 9 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
echo "t5 n9 80k"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/80k.json -t 5 -n 9 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
echo "t5 n9 90k"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/90k.json -t 5 -n 9 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct
echo "t5 n9 100k"
python3 ${HOME}/samothrace-pseudonymization/experiments-tools/experiments_script.py -f ${HOME}/samothrace-pseudonymization/experiments-tools/100k.json -t 5 -n 9 -i 100  -us http://172.17.7.37:8000/split -ur http://172.17.7.37:8000/reconstruct

echo "Experiments finished"