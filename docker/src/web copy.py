from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import utils
import json
import requests
import os

DATA_PATH = "./data/"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

class SplitConfig(BaseModel):
    threshold: int
    num_shares: int
    num_first_level_shares: int
    endpoints: list = []
    keys: list = []
    #dim: str
    resource: str
    how: str

class ReconstructConfig(BaseModel):
    threshold: int
    num_shares: int
    keys: list = []
    #dim: str
    resource: str
    how: str

class SplitInput(BaseModel):
    plaintext: dict
    config: SplitConfig

class ReconstructInput(BaseModel):
    id: str
    config: ReconstructConfig

app = FastAPI()

@app.get("/")
def root():
    return {"available": True}

@app.get("/doc")
def get_doc_by_id(id: str):
    with open(DATA_PATH + id + ".json", 'r') as fr:
        share = json.load(fr)
    return share

@app.post("/save")
def save(data: dict):
    chunk_ref = data.pop('chunk_ref')
    with open(DATA_PATH + chunk_ref + '.json', 'w') as f:
        json.dump(data, f)
    return {"saved": True}

@app.post("/split")
def split(split_input: SplitInput):
    plaintext = split_input.plaintext
    id = plaintext.pop('id')
    config = split_input.config
    #print(plaintext.keys())
    pseudonymize_start = datetime.now()
    pseudonymized_data = utils.pseudonymize(plaintext["data"], config.keys, config.threshold, config.num_shares, config.num_first_level_shares)
    pseudonymize_end = datetime.now()
    pseudonymize_end = datetime.now()
    pseudonymize_time = datetime.timestamp(pseudonymize_end) - datetime.timestamp(pseudonymize_start)
    pseudonymize_start_value = pseudonymize_start.strftime(DATE_FORMAT)
    pseudonymize_end_value = pseudonymize_end.strftime(DATE_FORMAT)
    times = {
        'start': [pseudonymize_start_value],
        'end': [pseudonymize_end_value],
        'elapsed': [pseudonymize_time]
    }
    columns = ['start', 'end', 'elapsed']
    if not os.path.exists('./experiments_MT/t'+str(config.threshold)+'n'+str(config.num_shares)+'/'+config.resource): # IL CONTROLLO È RIPETUTO ANCHE NELLA FUNZIONE utils.save_to_csv
        os.makedirs('./experiments_MT/t'+str(config.threshold)+'n'+str(config.num_shares)+'/'+config.resource)
    utils.save_to_csv(times, './experiments_MT/t'+str(config.threshold)+'n'+str(config.num_shares)+'/'+config.resource+'/split-'+config.how+'.csv', columns)
    #return {"splitted": pseudonymized_data}
    utils.distribute(id, pseudonymized_data, config.endpoints, config.num_first_level_shares)
    return {"splitted": True, "pseudonymized_data": pseudonymized_data}

# @app.post("/reconstruct")
# def reconstruct(reconstruct_input: ReconstructInput):
#     id = reconstruct_input.id
#     config = reconstruct_input.config
#     secret_map = utils.get_secret_map(id,config.threshold)
#     #print(secret_map)
#     ciphered_data = []
#     chunks = secret_map['doc']
#     for chunk_ref in chunks:
#         response = requests.get(chunk_ref, timeout=(5, None))
#         #print(response.status_code)
#         if response.status_code == 200:
#             result = response.json()
#             if 'chunk' in result:
#                 ciphered_data.append(result['chunk'])
#             else:
#                 ciphered_data.append(response.json())
#         if len(ciphered_data) == config.threshold:
#             break
#     #print(ciphered_data)
#     if len(ciphered_data) < config.threshold:
#         raise Exception("Not enough shares to reconstruct")
#     else:
#         reconstruct_start = datetime.now()
#         plaintext = utils.reconstruct(ciphered_data, config.keys)
#         reconstruct_end = datetime.now()
#         reconstruct_time = datetime.timestamp(reconstruct_end) - datetime.timestamp(reconstruct_start)
#         reconstruct_start_value = reconstruct_start.strftime(DATE_FORMAT)
#         reconstruct_end_value = reconstruct_end.strftime(DATE_FORMAT)
#         times = {
#             'start': [reconstruct_start_value],
#             'end': [reconstruct_end_value],
#             'elapsed': [reconstruct_time]
#         }
#         columns = ['start', 'end', 'elapsed']
#         if not os.path.exists('./experiments/t'+str(config.threshold)+'n'+str(config.num_shares)+'/'+config.resource):
#             os.makedirs('./experiments/t'+str(config.threshold)+'n'+str(config.num_shares)+'/'+config.resource)
#         utils.save_to_csv(times, './experiments/t'+str(config.threshold)+'n'+str(config.num_shares)+'/'+config.resource+'/retrieve-'+config.how+'.csv', columns)
#         return {"reconstructed": plaintext}

@app.post("/reconstruct")
def reconstruct(reconstruct_input: ReconstructInput):
    id = reconstruct_input.id
    config = reconstruct_input.config

    # Recupera la mappa con distinzione tra share primari e secondari
    secret_map = utils.get_secret_map(id, config.threshold)

    reconstruct_start = datetime.now()

    # Usa la nuova logica gerarchica di ricostruzione
    plaintext = utils.reconstruct_from_secret_map(secret_map, config.threshold, config.keys)

    reconstruct_end = datetime.now()
    reconstruct_time = datetime.timestamp(reconstruct_end) - datetime.timestamp(reconstruct_start)
    reconstruct_start_value = reconstruct_start.strftime(DATE_FORMAT)
    reconstruct_end_value = reconstruct_end.strftime(DATE_FORMAT)
    times = {
        'start': [reconstruct_start_value],
        'end': [reconstruct_end_value],
        'elapsed': [reconstruct_time]
    }
    columns = ['start', 'end', 'elapsed']

    if not os.path.exists('./experiments/t'+str(config.threshold)+'n'+str(config.num_shares)+'/'+config.resource):
        os.makedirs('./experiments/t'+str(config.threshold)+'n'+str(config.num_shares)+'/'+config.resource)

    #utils.save_to_csv(times, './experiments/t'+str(config.threshold)+'n'+str(config.num_shares)+'/'+config.resource+'/retrieve-'+config.how+'.csv', columns)
    
    return {"reconstructed": plaintext}
