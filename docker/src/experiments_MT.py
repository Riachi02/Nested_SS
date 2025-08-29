import requests
import os
import json
import argparse

def remove_shares(level=None, n=None):
    DATA_PATH = "../shares/"
    count = 0
    if level is None and n is None:
        print("No level or n specified, removing all shares.")
        for dir in os.listdir(DATA_PATH):
            for file in os.listdir(os.path.join(DATA_PATH, dir)):
                with open(os.path.join(DATA_PATH, dir, file), 'r') as f:
                    share = json.load(f)
                    os.remove(os.path.join(DATA_PATH, dir, file))
                    #print(f"Removed share: {share}")
    else:
        for dir in os.listdir(DATA_PATH):
            for file in os.listdir(os.path.join(DATA_PATH, dir)):
                if count >= n:
                    break
                with open(os.path.join(DATA_PATH, dir, file), 'r') as f:
                    share = json.load(f)

                    if share["share_data"]["text"].get('level') == level:
                        os.remove(os.path.join(DATA_PATH, dir, file))
                        #print(f"Removed share: {share}")
                        count += 1

data_parser = argparse.ArgumentParser()
data_parser.add_argument("-l1", "--level_1", help="level 1", required=True)
data_parser.add_argument("-l2", "--level_2", help="level 2")
data_parser.add_argument("-p", "--plaintext", help="path to plaintext file", required=True)
data_parser.add_argument("-r", "--resource", help="type of resource", required=True)

# data_parser.add_argument("-g", "--group", help="path to group", required=True)
# data_parser.add_argument("-us", "--urls", help="url split", required=True)
# data_parser.add_argument("-ur", "--urlr", help="url retrieve", required=True)


args = data_parser.parse_args()

split_payload = dict()
retrieve_payload = dict()
split_payload["plaintext"] = dict()
split_payload["plaintext"]["data"] = dict()
split_payload["config"] = dict()
retrieve_payload["config"] = dict()
split_payload["config"]["levels"] = list()
split_payload["config"]["levels"].append(list(map(int, args.level_1.split(","))))
if args.level_2 is not None:
    split_payload["config"]["levels"].append(list(map(int, args.level_2.split(","))))
split_payload["plaintext"]["id"] = "123"
#retrieve_payload["config"]["levels"] = args.levels
#split_payload["config"]["resource"]=args.resource.strip("/").split("/")[-1]
#retrieve_payload["config"]["resource"]=args.resource.strip("/").split("/")[-1]
split_payload["config"]["endpoints"] = [
    "storage-node-1", "storage-node-2", "storage-node-3", "storage-node-4", 
    "storage-node-5", "storage-node-6", "storage-node-7", "storage-node-8", 
    "storage-node-9", "storage-node-10", "storage-node-11", "storage-node-12",
    "storage-node-13", "storage-node-14", "storage-node-15", "storage-node-16",
    "storage-node-17", "storage-node-18", "storage-node-19", "storage-node-20",
    "storage-node-21", "storage-node-22", "storage-node-23", "storage-node-24",
    "storage-node-25", "storage-node-26", "storage-node-27", "storage-node-28"
]
split_payload["config"]["resource"] = args.resource
retrieve_payload["config"]["resource"] = args.resource
split_payload["config"]["how"] = "manual"
retrieve_payload["config"]["how"] = "manual"
retrieve_payload["config"]["id"] = "123"

# options = {
#     "norm": []
# }

with open(args.plaintext, 'r') as f:
    text = f.read()

split_payload["plaintext"]["data"]["text"] = text
split_payload["config"]["keys"] = list(split_payload["plaintext"]["data"].keys())
retrieve_payload["config"]["keys"] = list(split_payload["plaintext"]["data"].keys())




# plaintext = {
#     "id": "123",
#     "data": {
#         "text": text,
#     }
# }

# config_split = {
#     "levels": [[4, 2, 1], [3, 2, 0]],
#     "endpoints": 
#     [
#         "storage-node-1", "storage-node-2", "storage-node-3", "storage-node-4", 
#         "storage-node-5", "storage-node-6", "storage-node-7", "storage-node-8", 
#         "storage-node-9", "storage-node-10", "storage-node-11", "storage-node-12",
#         "storage-node-13", "storage-node-14", "storage-node-15", "storage-node-16",
#         "storage-node-17", "storage-node-18", "storage-node-19", "storage-node-20",
#         "storage-node-21", "storage-node-22", "storage-node-23", "storage-node-24",
#         "storage-node-25", "storage-node-26", "storage-node-27", "storage-node-28"
#     ],
#     "keys": list(plaintext["data"].keys()),
#     "resource": "test",
#     "how": "manual"
# }

# config_reconstruct = {
#     "keys": list(plaintext["data"].keys()),
#     "resource": "test",
#     "how": "manual"
# }


#print(f"Sending data: {plaintext}, {config_split}.")
for i in range(50):
    try:
        response = requests.post("http://localhost:8000/split", json=split_payload)
        print(response.json())
    except Exception as e:
        print(f"An exception occurred while trying to send data to message broker: {e}.")

    n_shares_to_rm = split_payload["config"]["levels"][0][0] - split_payload["config"]["levels"][0][2] - split_payload["config"]["levels"][0][1] + 1
    remove_shares(0, n_shares_to_rm)

    try:
        response = requests.post("http://localhost:8000/reconstruct", json={"id": "123", "config": retrieve_payload["config"]})
        print(response.json())
    except Exception as e:
        print(f"An exception occurred while trying to send data to message broker: {e}.")

    remove_shares()
