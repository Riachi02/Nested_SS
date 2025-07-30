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
    levels: list  # Lista di [n, t, m] per ogni livello
    endpoints: list = []
    keys: list = []
    resource: str
    how: str

class ReconstructConfig(BaseModel):
    keys: list = []
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
    
    # Valida i parametri dei livelli
    try:
        utils.validate_levels(config.levels)
    except ValueError as e:
        return {"error": str(e)}
    
    pseudonymize_start = datetime.now()
    pseudonymized_data = utils.pseudonymize(
        plaintext["data"], 
        config.keys, 
        config.levels
    )
    pseudonymize_end = datetime.now()
    
    pseudonymize_time = datetime.timestamp(pseudonymize_end) - datetime.timestamp(pseudonymize_start)
    
    # Salva i tempi per analisi
    times = {
        'start': [pseudonymize_start.strftime(DATE_FORMAT)],
        'end': [pseudonymize_end.strftime(DATE_FORMAT)],
        'elapsed': [pseudonymize_time]
    }
    
    # Crea il path per i risultati sperimentali
    levels_str = '_'.join([f"L{i}n{n}t{t}m{m}" for i, (n, t, m) in enumerate(config.levels)])
    experiment_path = f'./experiments_MT/{levels_str}/{config.resource}'
    
    if not os.path.exists(experiment_path):
        os.makedirs(experiment_path)
    
    utils.save_to_csv(
        times, 
        f'{experiment_path}/split-{config.how}.csv', 
        ['start', 'end', 'elapsed']
    )
    
    # Distribuisci gli share
    utils.distribute(id, pseudonymized_data, config.endpoints, config.levels)
    
    return {"splitted": True}

@app.post("/reconstruct")
def reconstruct(reconstruct_input: ReconstructInput):
    id = reconstruct_input.id
    config = reconstruct_input.config
    
    # Recupera la mappa dei segreti
    secret_map = utils.get_secret_map(id)
    
    reconstruct_start = datetime.now()
    
    # Ricostruisci usando la logica gerarchica
    plaintext = utils.reconstruct_from_secret_map(
        secret_map, 
        None,
        config.keys
    )
    
    reconstruct_end = datetime.now()
    reconstruct_time = datetime.timestamp(reconstruct_end) - datetime.timestamp(reconstruct_start)
    
    # Salva i tempi per analisi
    times = {
        'start': [reconstruct_start.strftime(DATE_FORMAT)],
        'end': [reconstruct_end.strftime(DATE_FORMAT)],
        'elapsed': [reconstruct_time]
    }
    
    # Ottieni i livelli dalla mappa per creare il path corretto
    levels = secret_map.get('levels', [[3, 2, 0]])
    levels_str = '_'.join([f"L{i}n{n}t{t}m{m}" for i, (n, t, m) in enumerate(levels)])
    experiment_path = f'./experiments_MT/{levels_str}/{config.resource}'
    
    if not os.path.exists(experiment_path):
        os.makedirs(experiment_path)
    
    utils.save_to_csv(
        times, 
        f'{experiment_path}/retrieve-{config.how}.csv', 
        ['start', 'end', 'elapsed']
    )
    
    return {"reconstructed": plaintext}