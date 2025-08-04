import requests
import os
import json

def remove_shares(level, n):
    DATA_PATH = "../docker/src/data/"
    count = 0
    for file in os.listdir(DATA_PATH):
        if file != "service_list.json" and file != "trusted.json":
            if count >= n:
                break
            with open(os.path.join(DATA_PATH, file), 'r') as f:
                share = json.load(f)

                if share["share_data"]["nome"].get('level') == level:
                    os.remove(os.path.join(DATA_PATH, file))
                    #print(f"Removed share: {share}")
                    count += 1

# broker.send(target.name(), outputs)
with open("./txts/text_10.txt", 'r') as f:
    text = f.read()

plaintext = {
    "id": "123",
    "data": {
        "nome": "Anna",
        "cognome": "Bianchi",
        "età": 25,
        "altezza": 165,
        "peso": 60,
        "indirizzo": "Via Roma 1",
        "telefono": "1234567890",
    }
}
config_split = {
    "levels": [[5, 3, 1], [4, 2, 1], [3, 2, 0]],
    "endpoints": 
    [
        "storage-node-1", "storage-node-2", "storage-node-3", "storage-node-4", 
        "storage-node-5", "storage-node-6", "storage-node-7", "storage-node-8", 
        "storage-node-9", "storage-node-10", "storage-node-11", "storage-node-12",
        "storage-node-13", "storage-node-14", "storage-node-15", "storage-node-16",
        "storage-node-17", "storage-node-18", "storage-node-19", "storage-node-20",
        "storage-node-21", "storage-node-22", "storage-node-23", "storage-node-24",
        "storage-node-25", "storage-node-26", "storage-node-27", "storage-node-28"
    ],
    "keys": list(plaintext["data"].keys()),
    "resource": "test",
    "how": "manual"
}

config_reconstruct = {
    "keys": list(plaintext["data"].keys()),
    "resource": "test",
    "how": "manual"
}


#print(f"Sending data: {plaintext}, {config_split}.")

#for i in range(100):
try:
    print(f"Sending split request with plaintext: {plaintext} and config: {config_split}")
    response = requests.post("http://ss-node:8000/split", json={"plaintext": plaintext, "config": config_split})
    print(response.json())
except Exception as e:
    print(f"An exception occoued while trying to send data to message broker: {e}.")

# remove_shares(0, 2)
# remove_shares(1, 2)

# try:
#     response = requests.post("http://localhost:8000/reconstruct", json={"id": "123", "config": config_reconstruct})
#     print(response.json())
# except Exception as e:
#     print(f"An exception occoued while trying to send data to message broker: {e}.")