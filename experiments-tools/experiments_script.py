import json
import argparse
import requests

data_parser = argparse.ArgumentParser()
data_parser.add_argument("-f", "--file", help="path to file", required=True)
data_parser.add_argument("-t", "--threshold", help="threshold", required=True)
data_parser.add_argument("-n", "--num_shares", help="number of shares", required=True)
data_parser.add_argument("-i", "--iterations", help="number of iterations", required=True)
data_parser.add_argument("-us", "--urls", help="url split", required=True)
data_parser.add_argument("-ur", "--urlr", help="url retrieve", required=True)


args = data_parser.parse_args()

with open(args.file, 'r') as fr:
    data = json.load(fr)

split_payload = dict()
retrieve_payload = dict()
split_payload["plaintext"] = dict()
split_payload["config"] = dict()
retrieve_payload["config"] = dict()
split_payload["config"]["threshold"] = args.threshold
split_payload["config"]["num_shares"] = args.num_shares
retrieve_payload["config"]["threshold"] = args.threshold
retrieve_payload["config"]["num_shares"] = args.num_shares
split_payload["config"]["dim"]=args.file.split(".")[0].split("/")[-1]
retrieve_payload["config"]["dim"]=args.file.split(".")[0].split("/")[-1]
split_payload["config"]["endpoints"] = [
    "172.17.7.37",
    "172.17.1.203",
    "172.17.4.42",
    "172.17.4.75",
    "172.17.4.77",
    "172.17.4.167",
    "172.17.2.141",
    "172.17.2.198",
    "172.17.2.61"
]

split_payload["plaintext"]["data"] = data

options ={
    "norm": [],
    "100":["data1","data2","data3","data4"],
    "75":["data1","data2","data3"],
    "50":["data1","data2"],
    "25":["data1"]
}

for option in options:
    split_payload["config"]["keys"] = options[option]
    retrieve_payload["config"]["keys"] = options[option]
    for i in range(int(args.iterations)):
        split_payload["plaintext"]["id"] = str(i) + "_" + args.file
        split_payload["config"]["how"] = option
        response = requests.post(args.urls, json=split_payload)
        if response.status_code == 200:
            print("OK")
        else:
            print("ERROR")
            raise Exception(response.text)
#        time.sleep(1)
    for i in range(int(args.iterations)):
        retrieve_payload["id"] = str(i) + "_" + args.file
        retrieve_payload["config"]["how"] = option
        response = requests.post(args.urlr, json=retrieve_payload)
        if response.status_code == 200:
            print("OK")
        else:
            print("ERROR")
            raise Exception(response.text)
#        time.sleep(1)