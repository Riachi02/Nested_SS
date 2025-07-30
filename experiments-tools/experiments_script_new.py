import json
import argparse
import requests
import os
import random

data_parser = argparse.ArgumentParser()
data_parser.add_argument("-r", "--resource", help="path to resource", required=True)
data_parser.add_argument("-g", "--group", help="path to group", required=True)
data_parser.add_argument("-t", "--threshold", help="threshold", required=True)
data_parser.add_argument("-n", "--num_shares", help="number of shares", required=True)
data_parser.add_argument("-i", "--iterations", help="number of iterations", required=True)
data_parser.add_argument("-us", "--urls", help="url split", required=True)
data_parser.add_argument("-ur", "--urlr", help="url retrieve", required=True)


args = data_parser.parse_args()

#hl7_files = os.listdir(args.resource)

split_payload = dict()
retrieve_payload = dict()
split_payload["plaintext"] = dict()
split_payload["config"] = dict()
retrieve_payload["config"] = dict()
split_payload["config"]["threshold"] = args.threshold
split_payload["config"]["num_shares"] = args.num_shares
retrieve_payload["config"]["threshold"] = args.threshold
retrieve_payload["config"]["num_shares"] = args.num_shares
split_payload["config"]["resource"]=args.resource.strip("/").split("/")[-1]
retrieve_payload["config"]["resource"]=args.resource.strip("/").split("/")[-1]
print(split_payload["config"]["resource"])
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

options = {
    "norm": []
}

with open(args.group, 'r') as group_file:
    hl7_names = json.load(group_file)
    descriptor_path = os.path.join(args.group[0: args.group.rfind("/")].replace('grouped', 'counted'), hl7_names[0])
    #print(descriptor_path)
    with open(descriptor_path, 'r') as descriptor_file:
        descriptor = json.load(descriptor_file)
        descriptor.pop("id")
        descriptor.pop("resourceType")
        #print(descriptor)
        num_values = 0
        keys = list(descriptor.keys())
        options['100'] = keys.copy()
        #print(keys)
        for key in descriptor:
            #print("I'm considering key: " + key)
            num_values += descriptor[key]['num_values']
            #print(str(num_values) + " values in total")
        reverse_count = num_values
        #print(str(num_values) + " values in total")
        for key in descriptor:
            #print("I'm removing key: " + key)
            keys.remove(key)
            reverse_count -= descriptor[key]['num_values']
            #print(str(reverse_count) + " values left")
            if reverse_count > 0:
                options[str(round(reverse_count / num_values * 100, 2))] = keys.copy()
            """ #print("I'm considering key: " + key)
            if reverse_count > num_values * 3 / 4:
                #print("I'm removing key: " + key)
                keys.remove(key)
                reverse_count -= descriptor[key]['num_values']
                print(str(reverse_count) + " values left")
            elif reverse_count > num_values / 2:
                if options.get('75') is None:
                    print("I'm saving the keys: " + str(keys))
                    options['75'] = keys.copy()
                #print("I'm removing key: " + key)
                keys.remove(key)
                reverse_count -= descriptor[key]['num_values']
                print(str(reverse_count) + " values left")
            elif reverse_count > num_values / 4:
                if options.get('50') is None:
                    print("I'm saving the keys: " + str(keys))
                    options['50'] = keys.copy()
                #print("I'm removing key: " + key)
                keys.remove(key)
                reverse_count -= descriptor[key]['num_values']
                print(str(reverse_count) + " values left")
            elif options.get('25') is None:
                print("I'm saving the keys: " + str(keys))
                options['25'] = keys.copy()
                break """
        
        print(options)

    for option in options:
        split_payload["config"]["keys"] = options[option]
        retrieve_payload["config"]["keys"] = options[option]
        for i in range(int(args.iterations)):
            random_index = random.randint(0, len(hl7_names) - 1)
            hl7_name = hl7_names[random_index]
            hl7_file_path = os.path.join(args.resource, hl7_name)
            #print(hl7_file_path)
            with open(hl7_file_path, 'r') as fr:
                data = json.load(fr)
                id = data.pop("id")
                split_payload["plaintext"]["data"] = data
                split_payload["plaintext"]["id"] = str(i) + "_" + id
                split_payload["config"]["how"] = option
                response = requests.post(args.urls, json=split_payload)
                if response.status_code == 200:
                    print("OK")
                    print(response.text)
                else:
                    print("ERROR")
                    raise Exception(response.text)
                retrieve_payload["id"] = str(i) + "_" + id
                retrieve_payload["config"]["how"] = option
                response = requests.post(args.urlr, json=retrieve_payload)
            if response.status_code == 200:
                print("OK")
                print(response.text)
            else:
                print("ERROR")
                raise Exception(response.text)

""" with open(args.file, 'r') as fr:
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
#        time.sleep(1) """