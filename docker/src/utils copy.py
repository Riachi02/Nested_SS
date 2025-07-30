from secretsharing import PlaintextToHexSecretSharer
from hashlib import sha256
import json
from copy import deepcopy
import random
from math import ceil
import numpy as np
import requests
from datetime import datetime
import pandas as pd
import numbers
import os

MAX_LENGTH = 192
BATCH_SEPARATOR = '%'
SERVICE_LIST_PATH = "./data/service_list.json"
TRUSTED_FILE_PATH = "./data/trusted.json"
SELF_ENDPOINT = "172.17.7.37"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"
def save_to_csv(data, path, columns):
    if not os.path.exists(path):
        os.makedirs(path)
    try:
        df = pd.read_csv(path)
    except:
        df = pd.DataFrame([],columns=columns)
    to_add = pd.DataFrame(data, columns=columns)
    df = df.merge(to_add, 'outer')
    df.to_csv(path, index=False)
    

def autobatch_split(secret, threshold, num_shares):
    num_batches = ceil(len(secret) / MAX_LENGTH)
    all_shares = []
    for i in range(num_batches):
        batch = secret[i * MAX_LENGTH : (i + 1) * MAX_LENGTH]
        #start_ss = datetime.now()
        shares = PlaintextToHexSecretSharer.split_secret(batch, threshold, num_shares)
        #end_ss = datetime.now()
        #elapsed_ss = datetime.timestamp(end_ss) - datetime.timestamp(start_ss)
        #start_value = start_ss.strftime(DATE_FORMAT)
        #end_value = end_ss.strftime(DATE_FORMAT)
        #times = {
        #    'start': [start_value],
        #    'end': [end_value],
        #    'elapsed': [elapsed_ss],
        #    'batch': [batch],
        #    'len': [len(batch)]
        #}
        #columns = ['start', 'end', 'elapsed', 'batch', 'len']
        #save_to_csv(times,'./experiments/ss_call.csv',columns)
        for j in range(num_shares):
            if i != num_batches - 1:
                shares[j] = shares[j] + BATCH_SEPARATOR
        if i == 0:
            all_shares = shares
        else:
            for j in range(num_shares):
                all_shares[j] = all_shares[j] + shares[j]
    return all_shares

def autobatch_recover(shares):
    #print (shares)
    num_shares = len(shares)
    for i in range(num_shares):
        #print(shares)
        shares[i] = shares[i].split(BATCH_SEPARATOR)
    num_batches = len(shares[0])
    secret = ''
    shares = np.array(shares)
    shares = np.transpose(shares)
    #print(shares)
    for i in range(num_batches):
        secret += PlaintextToHexSecretSharer.recover_secret(shares[i])
    return secret

# def pseudonymize(plaintext, keys=[], threshold=2, num_shares=3):
#     #calls=dict()
#     #for i in range(len(keys)):
#     #    calls['key'+str(i)] = [keys[i]]
#     #columns = list(calls.keys())
#     #print(columns)
#     #save_to_csv(calls,'./experiments/pseudo_call'+ str(random.random())+'.csv',columns)
#     if not keys:
#         plaintext = json.dumps(plaintext)
#         shares = autobatch_split(plaintext, threshold, num_shares)
#         return shares
#     pseudonymized_data = [deepcopy(plaintext) for i in range(num_shares)]
#     if type(plaintext) == dict:
#         for key in plaintext:
#             if key in keys:
#                 if type(plaintext[key]) == dict:
#                     shares = pseudonymize(plaintext[key], list(plaintext[key].keys()), threshold, num_shares)
#                 elif type(plaintext[key]) == list:
#                     shares = pseudonymize(plaintext[key], keys, threshold, num_shares)
#                 elif type(plaintext[key]) == str:
#                     #shares = PlaintextToHexSecretSharer.split_secret(plaintext[key], threshold, num_shares)
#                     shares = autobatch_split(plaintext[key], threshold, num_shares)
#                 elif isinstance(plaintext[key], numbers.Number):
#                     shares = autobatch_split(str(plaintext[key]), threshold, num_shares)
#                 else:
#                     print(str(type(plaintext[key])))
#                     raise ValueError("Unsupported type: " + str(type(plaintext[key])))
#                 for i in range(num_shares):
#                     pseudonymized_data[i][key] = shares[i]
#     elif type(plaintext) == list:
#         for i in range(len(plaintext)):
#             if type(plaintext[i]) == dict:
#                 shares = pseudonymize(plaintext[i], list(plaintext[i].keys()), threshold, num_shares)
#             elif type(plaintext[i]) == list:
#                 shares = pseudonymize(plaintext[i], keys, threshold, num_shares)
#             elif type(plaintext[i]) == str:
#                 #shares = PlaintextToHexSecretSharer.split_secret(plaintext[i], threshold, num_shares)
#                 shares = autobatch_split(plaintext[i], threshold, num_shares)
#             elif isinstance(plaintext[key], numbers.Number):
#                     shares = autobatch_split(str(plaintext[key]), threshold, num_shares)
#             else:
#                 raise ValueError("Unsupported type: " + str(type(plaintext[i])))
#             for j in range(num_shares):
#                 pseudonymized_data[j][i] = shares[j]
#     return pseudonymized_data

def pseudonymize(plaintext, keys=[], threshold=2, num_shares=3, num_first_level_shares=None):
    if num_first_level_shares is None:
        num_first_level_shares = num_shares  # Default behavior: no second-level shares

    num_second_level_shares = num_shares - num_first_level_shares

    # Caso base: nessuna chiave specificata → intero oggetto da pseudonimizzare
    if not keys:
        plaintext = json.dumps(plaintext)
        first_level_total = num_first_level_shares + (1 if num_second_level_shares > 0 else 0)
        shares = autobatch_split(plaintext, threshold, first_level_total)

        if num_second_level_shares > 0:
            second_level_shares = autobatch_split(
                shares[-1], threshold, num_second_level_shares
            )
            shares = shares[:-1] + second_level_shares

        return shares

    # Caso ricorsivo: elaborazione per chiavi specifiche
    pseudonymized_data = [deepcopy(plaintext) for _ in range(num_shares)]

    if isinstance(plaintext, dict):
        for key in plaintext:
            if key in keys:
                value = plaintext[key]

                if isinstance(value, dict):
                    shares = pseudonymize(value, list(value.keys()), threshold, num_shares, num_first_level_shares)
                elif isinstance(value, list):
                    shares = pseudonymize(value, keys, threshold, num_shares, num_first_level_shares)
                elif isinstance(value, str):
                    shares = pseudonymize(value, [], threshold, num_shares, num_first_level_shares)
                elif isinstance(value, numbers.Number):
                    shares = pseudonymize(str(value), [], threshold, num_shares, num_first_level_shares)
                else:
                    raise ValueError("Unsupported type in dict:", type(value))

                for i in range(num_shares):
                    pseudonymized_data[i][key] = shares[i]

    elif isinstance(plaintext, list):
        for i, item in enumerate(plaintext):
            if isinstance(item, dict):
                shares = pseudonymize(item, list(item.keys()), threshold, num_shares, num_first_level_shares)
            elif isinstance(item, list):
                shares = pseudonymize(item, keys, threshold, num_shares, num_first_level_shares)
            elif isinstance(item, str):
                shares = pseudonymize(item, [], threshold, num_shares, num_first_level_shares)
            elif isinstance(item, numbers.Number):
                shares = pseudonymize(str(item), [], threshold, num_shares, num_first_level_shares)
            else:
                raise ValueError("Unsupported type in list:", type(item))

            for j in range(num_shares):
                pseudonymized_data[j][i] = shares[j]

    return pseudonymized_data

def reconstruct(ciphertexts, keys=[]):
    if not keys:
        #for i in range(len(ciphertexts)):
        #    ciphertexts[i] = json.dumps(ciphertexts[i])
        plaintext = autobatch_recover(ciphertexts)
        return json.loads(plaintext)
    plaintext = deepcopy(ciphertexts[0])
    
    if type(ciphertexts[0]) == dict:
        for key in ciphertexts[0]:
            if key in keys:
                if type(ciphertexts[0][key]) == dict:
                    plaintext[key] = reconstruct([ciphertext[key] for ciphertext in ciphertexts], list(ciphertexts[0][key].keys()))
                elif type(ciphertexts[0][key]) == list:
                    plaintext[key] = reconstruct([ciphertext[key] for ciphertext in ciphertexts], keys)
                elif type(ciphertexts[0][key]) == str:                 
                    #plaintext[key] = PlaintextToHexSecretSharer.recover_secret([ciphertext[key] for ciphertext in ciphertexts])
                    plaintext[key] = autobatch_recover([ciphertext[key] for ciphertext in ciphertexts])
                    if plaintext[key].isdigit():
                        plaintext[key] = float(plaintext[key])
                else:
                    raise ValueError("Unsupported type: " + str(type(ciphertexts[0][key])))
    elif type(ciphertexts[0]) == list:
        for i in range(len(ciphertexts[0])):
            if type(ciphertexts[0][i]) == dict:
                plaintext[i] = reconstruct([ciphertext[i] for ciphertext in ciphertexts], list(ciphertexts[0][i].keys()))
            elif type(ciphertexts[0][i]) == list:
                plaintext[i] = reconstruct([ciphertext[i] for ciphertext in ciphertexts], keys)
            elif type(ciphertexts[0][i]) == str:
                #plaintext[i] = PlaintextToHexSecretSharer.recover_secret([ciphertext[i] for ciphertext in ciphertexts])
                plaintext[i] = autobatch_recover([ciphertext[i] for ciphertext in ciphertexts])
                if plaintext[i].isdigit():
                    plaintext[i] = float(plaintext[i])
            else:
                raise ValueError("Unsupported type: " + str(type(ciphertexts[0][i])))
    return plaintext

def reconstruct_from_secret_map(secret_map, threshold, keys=[]):
    all_shares = []
    primary_shares = []
    # print("Starting reconstruction with secret map:", secret_map)
    # Recupero degli share
    for url in secret_map.get('primary_doc', []):
        try:
            response = requests.get(url, timeout=(10, None))
            result = response.json()
            primary_shares.append(result)
        except:
            continue
    seen = set()
    new_l = []
    for d in primary_shares:
        t = tuple(d.items())
        if t not in seen:
            seen.add(t)
            new_l.append(d)    
    primary_shares = new_l[:threshold - 1]  # Limita agli share primari fino al threshold

    print(f"Primary shares retrieved: {primary_shares}")
    for url in secret_map.get('secondary_doc', []):
        try:
            response = requests.get(url, timeout=(10, None))
            result = response.json()
            all_shares.append(result)
        except:
            continue
    
    seen = set()
    new_l = []
    for d in all_shares:
        t = tuple(d.items())
        if t not in seen:
            seen.add(t)
            new_l.append(d)    
    all_shares = new_l
    # Condizione fondamentale: almeno 1 primario
    if len(primary_shares) == 0:
        raise ValueError("No primary shares available. At least one is required.")

    # Combina i primari con i secondari (se servono)
    total_shares = primary_shares.copy()
    if len(total_shares) < threshold:
        print(f"Total primary shares: {len(total_shares)}, Secondary shares available: {len(all_shares)}")
        # total_shares.extend(all_shares[:threshold - len(total_shares)])
        reconstructed_primary = recover_missing_primary_share(all_shares, keys, threshold)

        total_shares.append(reconstructed_primary)
        print(f"Total shares after reconstruction: {len(total_shares)}, {total_shares}")
    if len(total_shares) < threshold:
        raise ValueError("Not enough shares to reconstruct the secret (needed {}, got {})".format(
            threshold, len(total_shares)
        ))

    # Ricostruzione con la logica esistente
    return reconstruct(total_shares, keys)

def recover_missing_primary_share(secondary_shares: list, keys: list, threshold: int):
    if not secondary_shares:
        raise ValueError("No secondary shares provided")

    if len(secondary_shares) < threshold:
        raise ValueError(f"Need at least {threshold} secondary shares, got {len(secondary_shares)}")
    
    return reconstruct(secondary_shares, keys)


# def distribute(id, data, endpoints=[]):
#     num_shares = len(data)
#     if num_shares > len(endpoints):
#         raise ValueError("Not enough available endpoints")
#     else:
#         trusted = dict()
#         trusted['owner'] = SELF_ENDPOINT
#         trusted['segments'] = num_shares
#         trusted['doc'] = []
#         share_num = 1
#         for share in data:
#             endpoint_index = random.randint(0, len(endpoints) - 1)
#             endpoint = endpoints[endpoint_index]
#             url = "http://" + endpoint + ':8000/save'
#             chunk = dict()
#             chunk['chunk_ref'] = sha256((id + str(share_num)).encode()).hexdigest()
#             chunk['uuid_ref'] = sha256(('http://' + endpoint + ':8000/doc?id=' + chunk['chunk_ref']).encode()).hexdigest()
#             if type(share) == str:
#                 share = {'chunk': share}
#             share['chunk_ref'] = chunk['chunk_ref']
#             response = requests.post(url, json=share, timeout=(10, None))
#             result = response.json()
#             if result['saved'] == True:
#                 trusted['doc'].append(chunk)
#                 with open(TRUSTED_FILE_PATH, 'r') as fr:
#                     trusted_file = json.load(fr)
#                 trusted_file[id] = trusted
#                 with open(TRUSTED_FILE_PATH, 'w') as fw:
#                     json.dump(trusted_file, fw)
#                 endpoints.remove(endpoint)
#             else:
#                 raise ValueError("Endpoint " + endpoint + " failed to save data")
#             share_num += 1
#         return True

def distribute(id, data, endpoints=[], num_first_level_shares=None):
    num_shares = len(data)

    if num_first_level_shares is None:
        num_first_level_shares = num_shares  # fallback: tutti sono primari

    if num_shares > len(endpoints):
        raise ValueError("Not enough available endpoints")

    trusted = dict()
    trusted['owner'] = SELF_ENDPOINT
    trusted['segments'] = num_shares
    trusted['doc'] = []

    share_num = 1
    for i, share in enumerate(data):
        endpoint_index = random.randint(0, len(endpoints) - 1)
        endpoint = endpoints[endpoint_index]

        url = "http://" + endpoint + ':8000/save'
        chunk = dict()
        chunk['chunk_ref'] = sha256((id + str(share_num)).encode()).hexdigest()
        chunk['uuid_ref'] = sha256(('http://' + endpoint + ':8000/doc?id=' + chunk['chunk_ref']).encode()).hexdigest()
        chunk['type'] = 'primary' if i < num_first_level_shares else 'secondary'

        if type(share) == str:
            share = {'chunk': share}
        share['chunk_ref'] = chunk['chunk_ref']

        response = requests.post(url, json=share, timeout=(10, None))
        result = response.json()

        if result.get('saved') is True:
            trusted['doc'].append(chunk)
            with open(TRUSTED_FILE_PATH, 'r') as fr:
                trusted_file = json.load(fr)
            trusted_file[id] = trusted
            with open(TRUSTED_FILE_PATH, 'w') as fw:
                json.dump(trusted_file, fw)
            endpoints.remove(endpoint)
        else:
            raise ValueError("Endpoint " + endpoint + " failed to save data")

        share_num += 1

    return True


# def get_secret_map(id,threshold):
#     map_start = datetime.now()
#     with open(TRUSTED_FILE_PATH, 'r') as f:
#         trusted_file = json.load(f)
#     trusted = trusted_file[id] if id in trusted_file else None
#     if trusted == None:
#         raise ValueError("No trusted file for id " + id)
#     with open(SERVICE_LIST_PATH, 'r') as f:
#         service_list = json.load(f)
#     secret_map = dict()
#     secret_map['owner'] = trusted['owner']
#     secret_map['segments'] = trusted['segments']
#     secret_map['doc'] = []
#     for chunk in trusted['doc']:
#         for service in service_list:
#             url = service + '?id=' + chunk['chunk_ref']
#             computed_uuid_ref = sha256(url.encode()).hexdigest()
#             if computed_uuid_ref == chunk['uuid_ref']:
#                 secret_map['doc'].append(url)
#     map_end = datetime.now()
#     map_time = datetime.timestamp(map_end) - datetime.timestamp(map_start)
#     map_start_value = map_start.strftime(DATE_FORMAT)
#     map_end_value = map_end.strftime(DATE_FORMAT)
#     times = {
#         'start': [map_start_value],
#         'end': [map_end_value],
#         'elapsed': [map_time]
#     }
#     columns = ['start', 'end', 'elapsed']
#     save_to_csv(times, './experiments/t'+str(threshold)+'n'+str(secret_map['segments'])+'/map.csv', columns)
#     return secret_map

def get_secret_map(id, threshold):
    map_start = datetime.now()

    with open(TRUSTED_FILE_PATH, 'r') as f:
        trusted_file = json.load(f)

    if id not in trusted_file:
        raise ValueError("No trusted file for id " + id)

    trusted = trusted_file[id]

    with open(SERVICE_LIST_PATH, 'r') as f:
        service_list = json.load(f)

    secret_map = {
        'owner': trusted['owner'],
        'segments': trusted['segments'],
        'primary_doc': [],
        'secondary_doc': []
    }

    for chunk in trusted['doc']:
        for service in service_list:
            url = service + '?id=' + chunk['chunk_ref']
            computed_uuid_ref = sha256(url.encode()).hexdigest()
            # print(f"Computed UUID: {computed_uuid_ref}, Expected UUID: {chunk['uuid_ref']}")
            if computed_uuid_ref == chunk['uuid_ref']:
                if chunk.get('type') == 'primary':
                    secret_map['primary_doc'].append(url)
                else:
                    secret_map['secondary_doc'].append(url)

    map_end = datetime.now()
    map_time = datetime.timestamp(map_end) - datetime.timestamp(map_start)

    times = {
        'start': [map_start.strftime(DATE_FORMAT)],
        'end': [map_end.strftime(DATE_FORMAT)],
        'elapsed': [map_time]
    }
    # if not os.path.exists('./experiments_MT/t'+str(config.threshold)+'n'+str(config.num_shares)+'/'+config.resource):
    #     os.makedirs('./experiments_MT/t'+str(config.threshold)+'n'+str(config.num_shares)+'/'+config.resource)
    # save_to_csv(times, f'./experiments_MT/t{threshold}n{secret_map["segments"]}/map.csv', ['start', 'end', 'elapsed'])

    return secret_map
