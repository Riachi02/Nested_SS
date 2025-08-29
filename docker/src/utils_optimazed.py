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
from typing import List, Dict, Any, Tuple
from functools import lru_cache
import io

MAX_LENGTH = 192
BATCH_SEPARATOR = '%'
SERVICE_LIST_PATH = "./data/service_list.json"
TRUSTED_FILE_PATH = "./data/trusted.json"
SELF_ENDPOINT = "172.17.7.37"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

def save_to_csv(data, path, columns):
    try:
        df = pd.read_csv(path)
    except:
        df = pd.DataFrame([], columns=columns)
    to_add = pd.DataFrame(data, columns=columns)
    df = df.merge(to_add, 'outer')
    df.to_csv(path, index=False)

def autobatch_split_optimized(secret: str, threshold: int, num_shares: int) -> List[str]:
    """
    Versione ottimizzata del batching che evita concatenazioni O(n²)
    """
    if len(secret) <= MAX_LENGTH:
        # Caso semplice: nessun batching necessario
        return PlaintextToHexSecretSharer.split_secret(secret, threshold, num_shares)
    
    num_batches = ceil(len(secret) / MAX_LENGTH)
    
    # Pre-alloca le liste per evitare concatenazioni ripetute
    all_shares = [[] for _ in range(num_shares)]
    
    # Processa batch per batch
    for i in range(num_batches):
        start_idx = i * MAX_LENGTH
        end_idx = min((i + 1) * MAX_LENGTH, len(secret))
        batch = secret[start_idx:end_idx]
        
        shares = PlaintextToHexSecretSharer.split_secret(batch, threshold, num_shares)
        
        # Aggiungi alla lista invece di concatenare stringhe
        for j in range(num_shares):
            all_shares[j].append(shares[j])
    
    # Unisci una sola volta alla fine
    return [BATCH_SEPARATOR.join(share_parts) for share_parts in all_shares]

def autobatch_recover_optimized(shares: List[str]) -> str:
    """
    Versione ottimizzata del recovery che evita operazioni NumPy ridondanti
    """
    if not shares:
        return ""
    
    # Split una sola volta
    split_shares = [share.split(BATCH_SEPARATOR) for share in shares]
    num_batches = len(split_shares[0])
    
    # Pre-alloca buffer per risultato
    secret_parts = []
    
    # Processa batch per batch senza NumPy
    for batch_idx in range(num_batches):
        batch_shares = [split_shares[share_idx][batch_idx] 
                       for share_idx in range(len(shares))]
        secret_parts.append(PlaintextToHexSecretSharer.recover_secret(batch_shares))
    
    return ''.join(secret_parts)

@lru_cache(maxsize=128)
def _calculate_total_shares_cached(levels_tuple: tuple) -> int:
    """
    Versione cached del calcolo totale share per evitare ricalcoli
    """
    levels = list(levels_tuple)
    if not levels:
        return 0
    
    n, t, m = levels[0]
    
    if m == 0:
        return n
    
    remaining_shares = n - m
    sub_shares = m * _calculate_total_shares_cached(tuple(levels[1:]))
    
    return remaining_shares + sub_shares

def _calculate_total_shares(levels: List[List[int]]) -> int:
    """
    Wrapper per la versione cached
    """
    return _calculate_total_shares_cached(tuple(tuple(level) for level in levels))

def validate_levels(levels: List[List[int]]) -> bool:
    """
    Validazione ottimizzata dei livelli
    """
    for i, level in enumerate(levels):
        if len(level) != 3:
            raise ValueError(f"Livello {i}: deve avere esattamente 3 parametri [n, t, m]")
        
        n, t, m = level
        if m >= t:
            raise ValueError(f"Livello {i}: m ({m}) deve essere < t ({t})")
        if m >= n - t:
            raise ValueError(f"Livello {i}: m ({m}) deve essere < n-t ({n-t})")
    return True

def pseudonymize_optimized(plaintext: Any, keys: List[str] = None, levels: List[List[int]] = None) -> List[Dict]:
    """
    Versione ottimizzata della pseudonymizzazione con gestione memoria migliorata
    """
    if levels is None:
        levels = [[4, 2, 1], [3, 2, 0]]
    
    validate_levels(levels)
    
    # Caso base: nessuna chiave specificata
    if not keys:
        plaintext_str = json.dumps(plaintext, separators=(',', ':'))  # Formato compatto
        shares_metadata = _split_hierarchical_optimized(plaintext_str, levels, 0, "ROOT")
        return shares_metadata
    
    # Caso ricorsivo con pre-allocazione
    n_total_shares = _calculate_total_shares(levels)
    result_shares = [{} for _ in range(n_total_shares)]
    
    if isinstance(plaintext, dict):
        # Processa chiavi in batch per ridurre overhead
        for key in plaintext:
            value = plaintext[key]
            
            if key in keys:
                shares_metadata = _process_value_optimized(value, keys, levels, f"KEY_{key}")
                
                # Distribuzione ottimizzata
                for i, share_meta in enumerate(shares_metadata):
                    if i < len(result_shares):
                        result_shares[i][key] = share_meta
            else:
                # Copia valore non cifrato in tutti gli share (reference sharing quando possibile)
                if _is_immutable(value):
                    for share in result_shares:
                        share[key] = value
                else:
                    # Solo per valori mutabili facciamo deepcopy
                    for share in result_shares:
                        share[key] = deepcopy(value)
    
    elif isinstance(plaintext, list):
        result_shares = [[] for _ in range(n_total_shares)]
        
        for i, item in enumerate(plaintext):
            shares_metadata = _process_value_optimized(item, keys, levels, f"LIST_{i}")
            
            for j, share_meta in enumerate(shares_metadata):
                if j < len(result_shares):
                    result_shares[j].append(share_meta)
    
    return result_shares

def _is_immutable(obj: Any) -> bool:
    """
    Controlla se un oggetto è immutabile per ottimizzare le copie
    """
    return isinstance(obj, (str, int, float, bool, type(None), tuple))

def _process_value_optimized(value: Any, keys: List[str], levels: List[List[int]], debug_prefix: str) -> List[Dict]:
    """
    Versione ottimizzata del processing dei valori
    """
    if isinstance(value, dict):
        return pseudonymize_optimized(value, list(value.keys()), levels)
    elif isinstance(value, list):
        return pseudonymize_optimized(value, keys, levels)
    elif isinstance(value, (str, numbers.Number)):
        return _split_hierarchical_optimized(str(value), levels, 0, debug_prefix)
    else:
        # Serializza oggetti complessi in modo efficiente
        value_str = json.dumps(value, separators=(',', ':'), default=str)
        return _split_hierarchical_optimized(value_str, levels, 0, debug_prefix)

def _split_hierarchical_optimized(data: str, levels: List[List[int]], current_level: int, debug_prefix: str) -> List[Dict]:
    """
    Versione ottimizzata dello splitting gerarchico con stack invece di ricorsione
    """
    # Usa uno stack per evitare ricorsione profonda
    work_stack = [(data, levels, current_level, debug_prefix, None)]
    final_shares = []
    
    while work_stack:
        current_data, current_levels, level, prefix, parent_id = work_stack.pop()
        
        if level >= len(current_levels):
            final_shares.append({
                'data': current_data,
                'level': level,
                'share_type': 'leaf',
                'share_id': f"{prefix}_L{level}",
                'parent_id': parent_id
            })
            continue
        
        n, t, m = current_levels[level]
        
        # Usa la versione ottimizzata del batching
        shares = autobatch_split_optimized(current_data, t, n)
        
        if m == 0:
            # Ultimo livello
            for i, share in enumerate(shares):
                final_shares.append({
                    'data': share,
                    'level': level,
                    'share_type': 'primary',
                    'share_id': f"{prefix}_L{level}_P{i}",
                    'parent_id': parent_id,
                    'share_index': i
                })
        else:
            # Seleziona share da splittare
            selected_indices = random.sample(range(n), m)
            
            for i in range(n):
                if i in selected_indices:
                    # Aggiungi allo stack per processing successivo
                    new_parent_id = f"{prefix}_L{level}_P{i}"
                    work_stack.append((
                        shares[i], 
                        current_levels, 
                        level + 1, 
                        f"{prefix}_SUB{i}", 
                        new_parent_id
                    ))
                else:
                    # Share primario
                    final_shares.append({
                        'data': shares[i],
                        'level': level,
                        'share_type': 'primary',
                        'share_id': f"{prefix}_L{level}_P{i}",
                        'parent_id': parent_id,
                        'share_index': i
                    })
    
    return final_shares

def reconstruct_optimized(ciphertexts_metadata: List[Dict], keys: List[str] = None, levels: List[List[int]] = None) -> Any:
    """
    Versione ottimizzata della ricostruzione
    """
    if levels is None:
        levels = [[3, 2, 0]]
    
    if not keys:
        result = _reconstruct_hierarchical_optimized(ciphertexts_metadata, levels, 0, "ROOT")
        if isinstance(result, str):
            try:
                return json.loads(result)
            except:
                return result
        return result
    
    # Evita deepcopy costoso - crea struttura minimale
    if not ciphertexts_metadata:
        return None
    
    template = ciphertexts_metadata[0]
    
    if isinstance(template, dict):
        plaintext = {}
        for key in template:
            if key in keys:
                key_ciphertexts = [cipher[key] for cipher in ciphertexts_metadata]
                plaintext[key] = _reconstruct_value_optimized(key_ciphertexts, keys, levels, f"KEY_{key}")
            else:
                # Prendi il valore dal primo share (non cifrato)
                plaintext[key] = template[key]
        return plaintext
    
    elif isinstance(template, list):
        plaintext = []
        for i in range(len(template)):
            item_ciphertexts = [cipher[i] for cipher in ciphertexts_metadata]
            plaintext.append(_reconstruct_value_optimized(item_ciphertexts, keys, levels, f"LIST_{i}"))
        return plaintext
    
    return template

def _reconstruct_value_optimized(ciphertexts_metadata: List[Dict], keys: List[str], levels: List[List[int]], debug_prefix: str) -> Any:
    """
    Versione ottimizzata della ricostruzione dei valori
    """
    if not ciphertexts_metadata:
        return None
    
    first_item = ciphertexts_metadata[0]
    
    # Controlla se è un oggetto con metadati
    if isinstance(first_item, dict) and 'data' in first_item:
        result = _reconstruct_hierarchical_optimized(ciphertexts_metadata, levels, 0, debug_prefix)
        
        # Ottimizzazione: parsing numeri più efficiente
        if isinstance(result, str):
            result = result.strip()
            if result.replace('.', '').replace('-', '').replace('+', '').isdigit():
                try:
                    return float(result) if '.' in result else int(result)
                except:
                    pass
        
        return result
    
    # Struttura dati complessa
    elif isinstance(first_item, dict):
        return reconstruct_optimized(ciphertexts_metadata, list(first_item.keys()), levels)
    elif isinstance(first_item, list):
        return reconstruct_optimized(ciphertexts_metadata, keys, levels)
    else:
        return first_item

def _reconstruct_hierarchical_optimized(shares_metadata: List[Dict], levels: List[List[int]], current_level: int, debug_prefix: str) -> str:
    """
    Versione ottimizzata della ricostruzione gerarchica con pre-sorting
    """
    if current_level >= len(levels) or not shares_metadata:
        return shares_metadata[0]['data'] if shares_metadata else ""
    
    n, t, m = levels[current_level]
    
    # Pre-sorting per performance
    shares_by_level = {}
    for share_meta in shares_metadata:
        level = share_meta.get('level', current_level)
        if level not in shares_by_level:
            shares_by_level[level] = []
        shares_by_level[level].append(share_meta)
    
    primary_shares = shares_by_level.get(current_level, [])
    
    if m == 0:
        # Ultimo livello - ricostruzione diretta
        if len(primary_shares) >= t:
            share_data = [share['data'] for share in primary_shares[:t]]
            return autobatch_recover_optimized(share_data)
        else:
            raise ValueError(f"Share insufficienti per livello {current_level}: servono {t}, disponibili {len(primary_shares)}")
    
    # Raccoglie share per ricostruzione
    collected_shares = [share['data'] for share in primary_shares]
    
    # Se non abbiamo abbastanza share primari, ricostruiamo da quelli secondari
    if len(collected_shares) < t:
        secondary_shares = shares_by_level.get(current_level + 1, [])
        other_shares = []
        for level in range(current_level + 2, max(shares_by_level.keys(), default=current_level) + 1):
            other_shares.extend(shares_by_level.get(level, []))
        
        all_secondary = secondary_shares + other_shares
        
        # Raggruppa per parent (ottimizzato)
        secondary_by_parent = {}
        for share_meta in all_secondary:
            parent_id = share_meta.get('parent_id')
            if parent_id:
                if parent_id not in secondary_by_parent:
                    secondary_by_parent[parent_id] = []
                secondary_by_parent[parent_id].append(share_meta)
        
        # Ricostruisci i share mancanti
        for parent_id, child_shares in secondary_by_parent.items():
            if len(collected_shares) >= t:
                break
            
            try:
                reconstructed_share = _reconstruct_hierarchical_optimized(
                    child_shares, levels, current_level + 1, f"{debug_prefix}_SUB"
                )
                collected_shares.append(reconstructed_share)
            except Exception:
                continue
    
    if len(collected_shares) >= t:
        return autobatch_recover_optimized(collected_shares[:t])
    else:
        raise ValueError(f"Share insufficienti per livello {current_level}: servono {t}, disponibili {len(collected_shares)}")

# Le altre funzioni rimangono invariate ma con chiamate alle versioni ottimizzate
def distribute(id, data_with_metadata, endpoints=[], levels=None):
    if levels is None:
        levels = [[3, 2, 0]]
    
    num_shares = len(data_with_metadata)
    
    if num_shares > len(endpoints):
        raise ValueError("Endpoint insufficienti")
    
    trusted = {
        'owner': SELF_ENDPOINT,
        'segments': num_shares,
        'levels': levels,
        'doc': []
    }
    
    # Copia endpoints per non modificare l'originale
    available_endpoints = endpoints.copy()
    
    for i, share_data in enumerate(data_with_metadata):
        endpoint = random.choice(available_endpoints)
        available_endpoints.remove(endpoint)
        
        url = f"http://{endpoint}:8000/save"
        chunk_ref = sha256((id + str(i)).encode()).hexdigest()
        
        chunk = {
            'chunk_ref': chunk_ref,
            'uuid_ref': sha256(f"http://{endpoint}:8000/doc?id={chunk_ref}".encode()).hexdigest(),
            'type': 'share',
            'index': i,
            'share_metadata': _extract_metadata(share_data) if isinstance(share_data, dict) else None
        }
        
        save_data = {
            'chunk_ref': chunk_ref,
            'share_data': share_data
        }
        
        try:
            response = requests.post(url, json=save_data, timeout=(10, None))
            result = response.json()
            
            if result.get('saved'):
                trusted['doc'].append(chunk)
            else:
                raise ValueError(f"Endpoint {endpoint} ha fallito il salvataggio")
        except requests.RequestException as e:
            raise ValueError(f"Errore di connessione con endpoint {endpoint}: {e}")
    
    # Salva le informazioni trusted
    try:
        with open(TRUSTED_FILE_PATH, 'r') as f:
            trusted_file = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        trusted_file = {}
    
    trusted_file[id] = trusted
    
    with open(TRUSTED_FILE_PATH, 'w') as f:
        json.dump(trusted_file, f, separators=(',', ':'))
    
    return True

def _extract_metadata(share_data):
    """
    Estrazione metadati ottimizzata
    """
    if isinstance(share_data, dict):
        metadata = {}
        for key, value in share_data.items():
            if isinstance(value, dict) and 'data' in value:
                metadata[key] = {
                    'level': value.get('level'),
                    'share_type': value.get('share_type'),
                    'share_id': value.get('share_id'),
                    'parent_id': value.get('parent_id')
                }
            elif isinstance(value, (dict, list)):
                sub_metadata = _extract_metadata(value)
                if sub_metadata:  # Solo se c'è qualcosa da salvare
                    metadata[key] = sub_metadata
        return metadata if metadata else None
    elif isinstance(share_data, list):
        metadata = []
        for item in share_data:
            item_metadata = _extract_metadata(item)
            metadata.append(item_metadata)
        return metadata if any(metadata) else None
    return None

def get_secret_map(id, threshold=None):
    try:
        with open(TRUSTED_FILE_PATH, 'r') as f:
            trusted_file = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        raise ValueError(f"File trusted non trovato o corrotto")
    
    if id not in trusted_file:
        raise ValueError(f"Nessun file trusted per id {id}")
    
    trusted = trusted_file[id]
    
    try:
        with open(SERVICE_LIST_PATH, 'r') as f:
            service_list = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        raise ValueError(f"Service list non trovata o corrotta")
    
    secret_map = {
        'owner': trusted['owner'],
        'segments': trusted['segments'],
        'levels': trusted.get('levels', [[3, 2, 0]]),
        'doc': []
    }
    
    for chunk in trusted['doc']:
        for service in service_list:
            url = f"{service}?id={chunk['chunk_ref']}"
            computed_uuid = sha256(url.encode()).hexdigest()
            
            if computed_uuid == chunk['uuid_ref']:
                secret_map['doc'].append({
                    'url': url,
                    'metadata': chunk.get('share_metadata')
                })
                break
    
    return secret_map

def reconstruct_from_secret_map(secret_map, threshold=None, keys=[]):
    """
    Versione ottimizzata con gestione errori migliorata
    """
    levels = secret_map.get('levels', [[3, 2, 0]])
    all_shares = []
    failed_requests = []
    
    for i, doc_info in enumerate(secret_map['doc']):
        try:
            if isinstance(doc_info, dict):
                url = doc_info['url']
            else:
                url = doc_info
            
            response = requests.get(url, timeout=(10, 30))  # Timeout più generoso per download
            response.raise_for_status()  # Alza eccezione per status HTTP di errore
            
            share_data = response.json()
            
            if 'share_data' in share_data:
                all_shares.append(share_data['share_data'])
            else:
                all_shares.append(share_data)
                
        except Exception as e:
            failed_requests.append((i, str(e)))
            continue
    
    if not all_shares:
        raise ValueError(f"Nessuno share recuperato. Errori: {failed_requests}")
    
    if failed_requests:
        print(f"Warning: {len(failed_requests)} share non recuperati: {failed_requests}")
    
    return reconstruct_optimized(all_shares, keys, levels)

# Funzioni di utilità per il wrapper delle vecchie funzioni
def pseudonymize(plaintext, keys=[], levels=None):
    """Wrapper per compatibilità con il codice esistente"""
    return pseudonymize_optimized(plaintext, keys, levels)

def reconstruct(ciphertexts_metadata, keys=[], levels=None):
    """Wrapper per compatibilità con il codice esistente"""
    return reconstruct_optimized(ciphertexts_metadata, keys, levels)

def autobatch_split(secret, threshold, num_shares):
    """Wrapper per compatibilità con il codice esistente"""
    return autobatch_split_optimized(secret, threshold, num_shares)

def autobatch_recover(shares):
    """Wrapper per compatibilità con il codice esistente"""
    return autobatch_recover_optimized(shares)
