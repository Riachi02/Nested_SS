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
    # if not os.path.exists(path):
    #     os.makedirs(path)
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
        shares = PlaintextToHexSecretSharer.split_secret(batch, threshold, num_shares)
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
    num_shares = len(shares)
    for i in range(num_shares):
        shares[i] = shares[i].split(BATCH_SEPARATOR)
    num_batches = len(shares[0])
    secret = ''
    shares = np.array(shares)
    shares = np.transpose(shares)
    for i in range(num_batches):
        secret += PlaintextToHexSecretSharer.recover_secret(shares[i])
    return secret

def validate_levels(levels):
    """Valida i parametri per tutti i livelli"""
    for i, level in enumerate(levels):
        n, t, m = level
        if m >= t:
            raise ValueError(f"Livello {i}: m ({m}) deve essere < t ({t})")
        if m >= n - t:
            raise ValueError(f"Livello {i}: m ({m}) deve essere < n-t ({n-t})")
    return True

def pseudonymize(plaintext, keys=[], levels=None):
    """Pseudonymize ricorsivo con supporto per livelli multipli"""
    if levels is None:
        levels = [[3, 2, 0]]
    
    print(f"[PSEUDONYMIZE] Inizio con levels: {levels}")
    validate_levels(levels)
    
    # Caso base: nessuna chiave specificata → pseudonymizza tutto
    if not keys:
        print("[PSEUDONYMIZE] Nessuna chiave specificata, pseudonymizzazione completa")
        plaintext_str = json.dumps(plaintext)
        shares_metadata = _split_hierarchical(plaintext_str, levels, 0, "ROOT")
        return shares_metadata
    
    # Caso ricorsivo: elaborazione per chiavi specifiche
    n_total_shares = _calculate_total_shares(levels)
    print(f"[PSEUDONYMIZE] Numero totale shares attesi: {n_total_shares}")
    
    # Inizializza la struttura dati dei risultati
    result_shares = []
    
    if isinstance(plaintext, dict):
        for key in plaintext:
            if key in keys:
                print(f"[PSEUDONYMIZE] Processando chiave: {key}")
                value = plaintext[key]
                shares_metadata = _process_value(value, keys, levels, f"KEY_{key}")
                
                # Prima esecuzione: inizializza la struttura
                if not result_shares:
                    result_shares = [{} for _ in range(len(shares_metadata))]
                
                # Distribuisci i share per questa chiave
                for i, share_meta in enumerate(shares_metadata):
                    if i < len(result_shares):
                        result_shares[i][key] = share_meta
                    else:
                        # Estendi se necessario
                        result_shares.append({key: share_meta})
            else:
                # Chiave non da pseudonymizzare, copiala in tutti gli share
                if not result_shares:
                    result_shares = [{} for _ in range(n_total_shares)]
                for i in range(len(result_shares)):
                    result_shares[i][key] = plaintext[key]
    
    elif isinstance(plaintext, list):
        for i, item in enumerate(plaintext):
            print(f"[PSEUDONYMIZE] Processando elemento lista {i}")
            shares_metadata = _process_value(item, keys, levels, f"LIST_{i}")
            
            if not result_shares:
                result_shares = [[] for _ in range(len(shares_metadata))]
            
            for j, share_meta in enumerate(shares_metadata):
                if j < len(result_shares):
                    result_shares[j].append(share_meta)
                else:
                    result_shares.append([share_meta])
    
    print(f"[PSEUDONYMIZE] Risultato finale: {len(result_shares)} share")
    return result_shares

def _process_value(value, keys, levels, debug_prefix):
    """Processa un singolo valore basandosi sul suo tipo"""
    print(f"[{debug_prefix}] Processando valore di tipo {type(value)}")
    
    if isinstance(value, dict):
        return pseudonymize(value, list(value.keys()), levels)
    elif isinstance(value, list):
        return pseudonymize(value, keys, levels)
    elif isinstance(value, (str, numbers.Number)):
        return _split_hierarchical(str(value), levels, 0, debug_prefix)
    else:
        raise ValueError(f"Tipo non supportato: {type(value)}")

def _split_hierarchical(data, levels, current_level, debug_prefix):
    """Esegue il secret sharing gerarchico ricorsivo con metadati"""
    print(f"[{debug_prefix}] Split livello {current_level}: {levels[current_level] if current_level < len(levels) else 'TERMINATO'}")
    
    if current_level >= len(levels):
        print(f"[{debug_prefix}] Livello terminato, ritorno dati")
        return [{
            'data': data,
            'level': current_level,
            'share_type': 'leaf',
            'share_id': f"{debug_prefix}_L{current_level}",
            'parent_id': None
        }]
    
    n, t, m = levels[current_level]
    print(f"[{debug_prefix}] Parametri livello {current_level}: n={n}, t={t}, m={m}")
    
    # Esegui lo split del livello corrente
    shares = autobatch_split(data, t, n)
    print(f"[{debug_prefix}] Generati {len(shares)} share base")
    
    # Se m = 0, questo è l'ultimo livello
    if m == 0:
        print(f"[{debug_prefix}] Ultimo livello, ritorno {len(shares)} share")
        result = []
        for i, share in enumerate(shares):
            result.append({
                'data': share,
                'level': current_level,
                'share_type': 'primary',
                'share_id': f"{debug_prefix}_L{current_level}_P{i}",
                'parent_id': None,
                'share_index': i
            })
        return result
    
    # Seleziona randomicamente m share da splittare ulteriormente
    selected_indices = random.sample(range(n), m)
    print(f"[{debug_prefix}] Share selezionati per split successivo: {selected_indices}")
    
    final_shares = []
    
    for i in range(n):
        if i in selected_indices:
            print(f"[{debug_prefix}] Splittando share {i} nel livello successivo")
            parent_id = f"{debug_prefix}_L{current_level}_P{i}"
            sub_shares = _split_hierarchical(shares[i], levels, current_level + 1, f"{debug_prefix}_SUB{i}")
            
            # Aggiorna i metadati dei sotto-share
            for sub_share in sub_shares:
                sub_share['parent_id'] = parent_id
                sub_share['share_type'] = 'secondary'
            
            final_shares.extend(sub_shares)
            print(f"[{debug_prefix}] Share {i} ha generato {len(sub_shares)} sotto-share")
        else:
            print(f"[{debug_prefix}] Share {i} rimane primario")
            final_shares.append({
                'data': shares[i],
                'level': current_level,
                'share_type': 'primary',
                'share_id': f"{debug_prefix}_L{current_level}_P{i}",
                'parent_id': None,
                'share_index': i
            })
    
    print(f"[{debug_prefix}] Livello {current_level} completato: {len(final_shares)} share finali")
    return final_shares

def _calculate_total_shares(levels):
    """Calcola il numero totale di share finali"""
    if not levels:
        return 0
    
    n, t, m = levels[0]
    
    if m == 0:
        return n
    
    # Share che non vengono splittati + share derivati da quelli splittati
    remaining_shares = n - m
    sub_shares = m * _calculate_total_shares(levels[1:])
    
    total = remaining_shares + sub_shares
    print(f"[CALC] Livello con n={n}, m={m}: {remaining_shares} primari + {sub_shares} secondari = {total}")
    return total

def reconstruct(ciphertexts_metadata, keys=[], levels=None):
    """Ricostruisce i dati da share gerarchici con metadati"""
    if levels is None:
        levels = [[3, 2, 0]]
    
    print(f"[RECONSTRUCT] Inizio ricostruzione con {len(ciphertexts_metadata)} share")
    print(f"[RECONSTRUCT] Levels: {levels}")
    
    if not keys:
        print("[RECONSTRUCT] Nessuna chiave specificata, ricostruzione completa")
        result = _reconstruct_hierarchical(ciphertexts_metadata, levels, 0, "ROOT")
        if isinstance(result, str):
            try:
                return json.loads(result)
            except:
                return result
        return result
    
    # Ricostruzione per chiavi specifiche
    print(f"[RECONSTRUCT] Ricostruzione per chiavi: {keys}")
    plaintext = deepcopy(ciphertexts_metadata[0])
    
    # Rimuovi i metadati per ottenere la struttura originale
    if isinstance(ciphertexts_metadata[0], dict):
        for key in ciphertexts_metadata[0]:
            if key in keys:
                print(f"[RECONSTRUCT] Ricostruendo chiave: {key}")
                key_ciphertexts = [cipher[key] for cipher in ciphertexts_metadata]
                plaintext[key] = _reconstruct_value(key_ciphertexts, keys, levels, f"KEY_{key}")
            else:
                # Chiave non cifrata, prendi il valore dal primo share
                if not isinstance(ciphertexts_metadata[0][key], dict) or 'data' not in ciphertexts_metadata[0][key]:
                    plaintext[key] = ciphertexts_metadata[0][key]
    
    elif isinstance(ciphertexts_metadata[0], list):
        for i in range(len(ciphertexts_metadata[0])):
            print(f"[RECONSTRUCT] Ricostruendo elemento lista {i}")
            item_ciphertexts = [cipher[i] for cipher in ciphertexts_metadata]
            plaintext[i] = _reconstruct_value(item_ciphertexts, keys, levels, f"LIST_{i}")
    
    return plaintext

def _reconstruct_value(ciphertexts_metadata, keys, levels, debug_prefix):
    """Ricostruisce un singolo valore dai metadati"""
    print(f"[{debug_prefix}] Ricostruzione valore")
    
    # Controlla se è un oggetto con metadati
    if isinstance(ciphertexts_metadata[0], dict) and 'data' in ciphertexts_metadata[0]:
        result = _reconstruct_hierarchical(ciphertexts_metadata, levels, 0, debug_prefix)
        print(f"[{debug_prefix}] Risultato ricostruzione: '{result}'")
        
        if isinstance(result, str) and result.replace('.', '').replace('-', '').isdigit():
            try:
                if '.' in result:
                    return float(result)
                else:
                    return int(result)
            except:
                pass
        
        return result
    
    # Struttura dati complessa, ricorsione
    elif isinstance(ciphertexts_metadata[0], dict):
        return reconstruct(ciphertexts_metadata, list(ciphertexts_metadata[0].keys()), levels)
    elif isinstance(ciphertexts_metadata[0], list):
        return reconstruct(ciphertexts_metadata, keys, levels)
    else:
        # Valore non cifrato
        return ciphertexts_metadata[0]

def _reconstruct_hierarchical(shares_metadata, levels, current_level, debug_prefix):
    """Ricostruisce ricorsivamente dai share gerarchici con metadati"""
    print(f"[{debug_prefix}] Ricostruzione livello {current_level}")
    print(f"[{debug_prefix}] Share disponibili: {len(shares_metadata)}")
    
    if current_level >= len(levels):
        print(f"[{debug_prefix}] Livello terminato")
        return shares_metadata[0]['data'] if shares_metadata else None
    
    n, t, m = levels[current_level]
    print(f"[{debug_prefix}] Parametri livello {current_level}: n={n}, t={t}, m={m}")
    
    # Raggruppa gli share per tipo e livello
    primary_shares = []
    secondary_shares = []
    sub_shares = []
    
    for share_meta in shares_metadata:
        if share_meta.get('level') == current_level:
            #if share_meta.get('share_type') == 'primary':
            primary_shares.append(share_meta)
        #elif share_meta.get('share_type') == 'secondary':
        elif share_meta.get('level') == current_level + 1:
            secondary_shares.append(share_meta)
        elif share_meta.get('level') > current_level + 1:
            sub_shares.append(share_meta)
    
    print(f"[{debug_prefix}] Share primari disponibili: {len(primary_shares)}")
    print(f"[{debug_prefix}] Share secondari disponibili: {len(secondary_shares)}")
    
    # Se m = 0, questo è l'ultimo livello
    if m == 0:
        print(f"[{debug_prefix}] Ultimo livello, ricostruzione diretta")
        available_shares = primary_shares[:t] if len(primary_shares) >= t else primary_shares
        if len(available_shares) < t:
            raise ValueError(f"Share insufficienti per livello {current_level}: servono {t}, disponibili {len(available_shares)}")
        
        share_data = [share['data'] for share in available_shares]
        return autobatch_recover(share_data)
    
    # Raccoglie gli share per la ricostruzione
    collected_shares = []
    
    # Aggiungi share primari disponibili
    for share_meta in primary_shares:
        collected_shares.append(share_meta['data'])
    
    # Se non abbiamo abbastanza share primari, ricostruiamo da quelli secondari
    if len(collected_shares) < t:
        print(f"[{debug_prefix}] Share primari insufficienti, ricostruzione da secondari")
        
        other_shares = secondary_shares + sub_shares

        # Raggruppa i share secondari per parent
        secondary_by_parent = {}
        for share_meta in other_shares:
            parent_id = share_meta.get('parent_id')
            if parent_id:
                if parent_id not in secondary_by_parent:
                    secondary_by_parent[parent_id] = []
                secondary_by_parent[parent_id].append(share_meta)
        
        # Ricostruisci i share mancanti
        for parent_id, child_shares in secondary_by_parent.items():
            if len(collected_shares) >= t:
                break
            
            print(f"[{debug_prefix}] Ricostruendo share da parent {parent_id}")
            try:
                reconstructed_share = _reconstruct_hierarchical(
                    child_shares, levels, current_level + 1, f"{debug_prefix}_SUB"
                )
                collected_shares.append(reconstructed_share)
                print(f"[{debug_prefix}] Share ricostruito da {parent_id}")
            except Exception as e:
                print(f"[{debug_prefix}] Errore ricostruzione da {parent_id}: {e}")
                continue
    
    print(f"[{debug_prefix}] Share totali raccolti: {len(collected_shares)}")
    
    if len(collected_shares) >= t:
        print(f"[{debug_prefix}] Ricostruzione finale con {t} share")
        return autobatch_recover(collected_shares[:t])
    else:
        raise ValueError(f"Share insufficienti per livello {current_level}: servono {t}, disponibili {len(collected_shares)}")

def distribute(id, data_with_metadata, endpoints=[], levels=None):
    """Distribuisce gli share agli endpoints con metadati"""
    if levels is None:
        levels = [[3, 2, 0]]
    
    print(f"[DISTRIBUTE] Distribuzione di {len(data_with_metadata)} share")
    print(f"[DISTRIBUTE] Levels: {levels}")
    
    num_shares = len(data_with_metadata)
    
    if num_shares > len(endpoints):
        raise ValueError("Endpoint insufficienti")
    
    trusted = {
        'owner': SELF_ENDPOINT,
        'segments': num_shares,
        'levels': levels,
        'doc': []
    }
    
    # Distribuisci tutti gli share con metadati
    for i, share_data in enumerate(data_with_metadata):
        endpoint = random.choice(endpoints)
        endpoints.remove(endpoint)
        
        url = f"http://{endpoint}:8000/save"
        chunk_ref = sha256((id + str(i)).encode()).hexdigest()
        
        chunk = {
            'chunk_ref': chunk_ref,
            'uuid_ref': sha256(f"http://{endpoint}:8000/doc?id={chunk_ref}".encode()).hexdigest(),
            'type': 'share',
            'index': i,
            'share_metadata': _extract_metadata(share_data) if isinstance(share_data, dict) else None
        }
        
        # Prepara i dati per il salvataggio
        save_data = {
            'chunk_ref': chunk_ref,
            'share_data': share_data
        }
        
        print(f"[DISTRIBUTE] Salvando share {i} su {endpoint}")
        
        response = requests.post(url, json=save_data, timeout=(10, None))
        result = response.json()
        
        if result.get('saved'):
            trusted['doc'].append(chunk)
        else:
            raise ValueError(f"Endpoint {endpoint} ha fallito il salvataggio")
    
    # Salva le informazioni trusted
    with open(TRUSTED_FILE_PATH, 'r') as f:
        trusted_file = json.load(f)
    
    trusted_file[id] = trusted
    
    with open(TRUSTED_FILE_PATH, 'w') as f:
        json.dump(trusted_file, f)
    
    print(f"[DISTRIBUTE] Distribuzione completata")
    return True

def _extract_metadata(share_data):
    """Estrae i metadati da una struttura di share"""
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
                metadata[key] = _extract_metadata(value)
        return metadata
    elif isinstance(share_data, list):
        return [_extract_metadata(item) for item in share_data]
    return None

def get_secret_map(id, threshold=None):
    """Ottiene la mappa dei segreti con metadati"""
    print(f"[SECRET_MAP] Recupero mappa per id: {id}")
    
    with open(TRUSTED_FILE_PATH, 'r') as f:
        trusted_file = json.load(f)
    
    if id not in trusted_file:
        raise ValueError(f"Nessun file trusted per id {id}")
    
    trusted = trusted_file[id]
    print(f"[SECRET_MAP] Informazioni trusted trovate: {trusted}")
    
    with open(SERVICE_LIST_PATH, 'r') as f:
        service_list = json.load(f)
    
    secret_map = {
        'owner': trusted['owner'],
        'segments': trusted['segments'],
        'levels': trusted.get('levels', [[3, 2, 0]]),
        'doc': []
    }
    
    print(f"[SECRET_MAP] Levels recuperati: {secret_map['levels']}")
    
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
    
    print(f"[SECRET_MAP] URLs recuperati: {len(secret_map['doc'])}")
    return secret_map

def reconstruct_from_secret_map(secret_map, threshold=None, keys=[]):
    """Ricostruisce da una mappa di segreti con metadati"""
    levels = secret_map.get('levels', [[3, 2, 0]])
    print(f"[RECONSTRUCT_MAP] Livelli dalla mappa: {levels}")
    
    # Recupera tutti gli share con metadati
    all_shares = []
    
    print(f"[RECONSTRUCT_MAP] Recupero {len(secret_map['doc'])} share")
    for i, doc_info in enumerate(secret_map['doc']):
        try:
            if isinstance(doc_info, dict):
                url = doc_info['url']
            else:
                url = doc_info  # Retrocompatibilità
            
            print(f"[RECONSTRUCT_MAP] Recuperando share {i} da {url}")
            response = requests.get(url, timeout=(10, None))
            share_data = response.json()
            
            # Estrai i dati effettivi dello share
            if 'share_data' in share_data:
                all_shares.append(share_data['share_data'])
            else:
                # Retrocompatibilità
                all_shares.append(share_data)
                
            print(f"[RECONSTRUCT_MAP] Share {i} recuperato con successo")
        except Exception as e:
            print(f"[RECONSTRUCT_MAP] Errore nel recupero share {i}: {e}")
            continue
    
    print(f"[RECONSTRUCT_MAP] Share totali recuperati: {len(all_shares)}")
    
    # Ricostruisci usando la logica gerarchica con metadati
    return reconstruct(all_shares, keys, levels)