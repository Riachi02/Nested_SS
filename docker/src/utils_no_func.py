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

def validate_hierarchical_params(levels_config):
    """
    Valida i parametri per il secret sharing gerarchico ricorsivo.
    levels_config: lista di liste [[n1, t1, m1], [n2, t2, m2], ...]
    """
    for i, (n, t, m) in enumerate(levels_config):
        # Validazione base per secret sharing
        if t > n:
            raise ValueError(f"Livello {i}: threshold {t} non può essere maggiore del numero di share {n}")
        if t <= 0 or n <= 0:
            raise ValueError(f"Livello {i}: threshold e numero di share devono essere positivi")
        
        # Validazione per secret sharing gerarchico
        if m < 0:
            raise ValueError(f"Livello {i}: numero di share da splittare {m} non può essere negativo")
        if m > 0:  # Se non è l'ultimo livello
            if m >= t:
                raise ValueError(f"Livello {i}: numero di share da splittare {m} deve essere < threshold {t}")
            if m >= n - t:
                raise ValueError(f"Livello {i}: numero di share da splittare {m} deve essere < n-t ({n-t})")
        
        # Ultimo livello deve avere m = 0
        if i == len(levels_config) - 1 and m != 0:
            raise ValueError(f"Ultimo livello deve avere m = 0, trovato {m}")

def apply_hierarchical_secret_sharing(content, levels_config, level_index=0, parent_id=None):
    """
    Applica il secret sharing gerarchico ricorsivamente.
    
    Args:
        content: contenuto da condividere
        levels_config: configurazione dei livelli [[n1, t1, m1], [n2, t2, m2], ...]
        level_index: indice del livello corrente
        parent_id: ID del share padre (per livelli > 0)
    
    Returns:
        dict con struttura:
        {
            'shares': [lista degli share finali],
            'metadata': {
                'structure': informazioni sulla struttura gerarchica,
                'parent_mapping': mapping share secondari -> share primari
            }
        }
    """
    if level_index >= len(levels_config):
        return {'shares': [content], 'metadata': {'structure': {}, 'parent_mapping': {}}}
    
    n, t, m = levels_config[level_index]
    current_level_id = f"level_{level_index}"
    
    # Converti in stringa se necessario
    if not isinstance(content, str):
        content = json.dumps(content)
    
    # Applica secret sharing per il livello corrente
    shares = autobatch_split(content, t, n)
    
    # Se è l'ultimo livello (m = 0), restituisci tutti gli share
    if m == 0:
        final_shares = []
        for i, share in enumerate(shares):
            share_data = {
                'content': share,
                'level': level_index,
                'share_id': i,
                'parent_id': parent_id,
                'is_final': True
            }
            final_shares.append(share_data)
        
        return {
            'shares': final_shares,
            'metadata': {
                'structure': {current_level_id: {'n': n, 't': t, 'm': m, 'is_final': True}},
                'parent_mapping': {}
            }
        }
    
    # Selezione random di m share da splittare ulteriormente
    selected_indices = random.sample(range(n), m)
    
    all_final_shares = []
    structure_info = {current_level_id: {'n': n, 't': t, 'm': m, 'selected_indices': selected_indices}}
    parent_mapping = {}
    
    for i, share in enumerate(shares):
        if i in selected_indices:
            # Questo share viene ulteriormente splittato
            share_id = f"{current_level_id}_share_{i}"
            recursive_result = apply_hierarchical_secret_sharing(
                share, levels_config, level_index + 1, share_id
            )
            
            # Aggiungi gli share risultanti
            all_final_shares.extend(recursive_result['shares'])
            
            # Aggiorna metadata
            structure_info.update(recursive_result['metadata']['structure'])
            parent_mapping.update(recursive_result['metadata']['parent_mapping'])
            
            # Aggiungi mapping per i nuovi share secondari
            for secondary_share in recursive_result['shares']:
                if secondary_share['parent_id'] == share_id:
                    parent_mapping[f"{secondary_share['level']}_{secondary_share['share_id']}"] = share_id
        else:
            # Questo share rimane come share primario finale
            share_data = {
                'content': share,
                'level': level_index,
                'share_id': i,
                'parent_id': parent_id,
                'is_final': True
            }
            all_final_shares.append(share_data)
    
    return {
        'shares': all_final_shares,
        'metadata': {
            'structure': structure_info,
            'parent_mapping': parent_mapping
        }
    }

def pseudonymize(plaintext, keys=[], levels_config=None):
    """
    Versione ricorsiva del secret sharing gerarchico.
    
    Args:
        plaintext: dati da pseudonimizzare
        keys: chiavi da processare
        levels_config: lista di liste [[n1, t1, m1], [n2, t2, m2], ...]
    
    Returns:
        lista di share pseudonimizzati con metadata
    """
    if levels_config is None:
        raise ValueError("levels_config è richiesto per il secret sharing gerarchico")
    
    # Valida i parametri
    validate_hierarchical_params(levels_config)
    
    # Caso base: nessuna chiave specificata → intero oggetto da pseudonimizzare
    if not keys:
        plaintext_str = json.dumps(plaintext) if not isinstance(plaintext, str) else plaintext
        result = apply_hierarchical_secret_sharing(plaintext_str, levels_config)
        return result['shares'], result['metadata']
    
    # Caso ricorsivo: elaborazione per chiavi specifiche
    num_total_shares = sum(len(result['shares']) for result in [
        apply_hierarchical_secret_sharing("dummy", levels_config)
    ])
    
    pseudonymized_data = [deepcopy(plaintext) for _ in range(num_total_shares)]
    global_metadata = {'structure': {}, 'parent_mapping': {}}
    
    if isinstance(plaintext, dict):
        for key in plaintext:
            if key in keys:
                value = plaintext[key]
                
                if isinstance(value, dict):
                    shares, metadata = pseudonymize(value, list(value.keys()), levels_config)
                elif isinstance(value, list):
                    shares, metadata = pseudonymize(value, keys, levels_config)
                elif isinstance(value, str):
                    shares, metadata = pseudonymize(value, [], levels_config)
                elif isinstance(value, numbers.Number):
                    shares, metadata = pseudonymize(str(value), [], levels_config)
                else:
                    raise ValueError("Unsupported type in dict:", type(value))
                
                # Aggiorna i dati pseudonimizzati
                for i, share_data in enumerate(shares):
                    if i < len(pseudonymized_data):
                        pseudonymized_data[i][key] = share_data
                
                # Aggiorna metadata globale
                global_metadata['structure'].update(metadata['structure'])
                global_metadata['parent_mapping'].update(metadata['parent_mapping'])
    
    elif isinstance(plaintext, list):
        for i, item in enumerate(plaintext):
            if isinstance(item, dict):
                shares, metadata = pseudonymize(item, list(item.keys()), levels_config)
            elif isinstance(item, list):
                shares, metadata = pseudonymize(item, keys, levels_config)
            elif isinstance(item, str):
                shares, metadata = pseudonymize(item, [], levels_config)
            elif isinstance(item, numbers.Number):
                shares, metadata = pseudonymize(str(item), [], levels_config)
            else:
                raise ValueError("Unsupported type in list:", type(item))
            
            # Aggiorna i dati pseudonimizzati
            for j, share_data in enumerate(shares):
                if j < len(pseudonymized_data):
                    pseudonymized_data[j][i] = share_data
            
            # Aggiorna metadata globale
            global_metadata['structure'].update(metadata['structure'])
            global_metadata['parent_mapping'].update(metadata['parent_mapping'])
    
    return pseudonymized_data, global_metadata

def distribute(id, shares_data, metadata, endpoints=[]):
    """
    Distribuisce gli share con informazioni gerarchiche.
    """
    
    num_shares = len(shares_data)
    
    if num_shares > len(endpoints):
        raise ValueError("Not enough available endpoints")
    
    trusted = {
        'owner': SELF_ENDPOINT,
        'segments': num_shares,
        'hierarchical': True,
        'metadata': metadata,
        'doc': []
    }
    
    share_num = 1
    random.shuffle(endpoints)

    for i, share_data in enumerate(shares_data):
        endpoint = endpoints[i]
        
        url = "http://" + endpoint + ':8000/save'
        chunk = {
            'chunk_ref': sha256((id + str(share_num)).encode()).hexdigest(),
            'type': 'hierarchical',
            'level': share_data.get('level', 0),
            'share_id': share_data.get('share_id', i),
            'parent_id': share_data.get('parent_id'),
            'is_final': share_data.get('is_final', True)
        }
        chunk['uuid_ref'] = sha256(('http://' + endpoint + ':8000/doc?id=' + chunk['chunk_ref']).encode()).hexdigest()
        
        # Prepara i dati da salvare
        save_data = {
            'chunk': share_data.get('content', share_data),
            'chunk_ref': chunk['chunk_ref'],
            'metadata': {
                'level': chunk['level'],
                'share_id': chunk['share_id'],
                'parent_id': chunk['parent_id'],
                'is_final': chunk['is_final']
            }
        }
        
        response = requests.post(url, json=save_data, timeout=(10, None))
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

def get_secret_map(id, threshold):
    """
    Recupera la mappa dei segreti con supporto gerarchico.
    """
    map_start = datetime.now()
    
    with open(TRUSTED_FILE_PATH, 'r') as f:
        trusted_file = json.load(f)
    
    if id not in trusted_file:
        raise ValueError("No trusted file for id " + id)
    
    trusted = trusted_file[id]
    
    with open(SERVICE_LIST_PATH, 'r') as f:
        service_list = json.load(f)
    
    # Verifica se è gerarchico
    is_hierarchical = trusted.get('hierarchical', False)
    
    if is_hierarchical:
        secret_map = {
            'owner': trusted['owner'],
            'segments': trusted['segments'],
            'hierarchical': True,
            'metadata': trusted.get('metadata', {}),
            'shares': []
        }
        
        for chunk in trusted['doc']:
            for service in service_list:
                url = service + '?id=' + chunk['chunk_ref']
                computed_uuid_ref = sha256(url.encode()).hexdigest()
                if computed_uuid_ref == chunk['uuid_ref']:
                    chunk_info = {
                        'url': url,
                        'type': chunk.get('type', 'standard'),
                        'level': chunk.get('level', 0),
                        'share_id': chunk.get('share_id'),
                        'parent_id': chunk.get('parent_id'),
                        'is_final': chunk.get('is_final', True)
                    }
                    secret_map['shares'].append(chunk_info)
    else:
        # Versione standard
        secret_map = {
            'owner': trusted['owner'],
            'segments': trusted['segments'],
            'hierarchical': False,
            'primary_doc': [],
            'secondary_doc': []
        }
        
        for chunk in trusted['doc']:
            for service in service_list:
                url = service + '?id=' + chunk['chunk_ref']
                computed_uuid_ref = sha256(url.encode()).hexdigest()
                if computed_uuid_ref == chunk['uuid_ref']:
                    if chunk.get('type') == 'primary':
                        secret_map['primary_doc'].append(url)
                    else:
                        secret_map['secondary_doc'].append(url)
    
    map_end = datetime.now()
    map_time = datetime.timestamp(map_end) - datetime.timestamp(map_start)
    
    return secret_map

def reconstruct_hierarchical_share(share_data_list, levels_config, metadata, target_level=0, target_parent_id=None):
    """
    Ricostruisce uno share specifico o un livello da share secondari usando la struttura gerarchica ricorsivamente.
    """
    if not share_data_list:
        raise ValueError("Lista share vuota")
    
    # Organizza gli share per livello e parent_id
    shares_by_level = {}
    shares_by_parent = {}
    
    for share in share_data_list:
        level = share.get('level', 0)
        parent_id = share.get('parent_id')
        
        if level not in shares_by_level:
            shares_by_level[level] = []
        shares_by_level[level].append(share)
        
        if parent_id:
            if parent_id not in shares_by_parent:
                shares_by_parent[parent_id] = []
            shares_by_parent[parent_id].append(share)
    
    # Funzione interna ricorsiva per ricostruire share di un parent_id a un certo livello
    def recursive_reconstruct(current_level, parent_id):
        if current_level >= len(levels_config):
            return None  # livello troppo profondo
        
        threshold = levels_config[current_level][1]
        
        # Prendi tutti gli share figli per quel parent_id
        child_shares = [s for s in share_data_list if s.get('level') == current_level and s.get('parent_id') == parent_id]
        
        if len(child_shares) >= threshold:
            # Abbastanza share per ricostruzione diretta
            share_contents = [s['content'] for s in child_shares[:threshold]]
            return autobatch_recover(share_contents)
        else:
            # Prova a ricostruire ulteriori share a partire dal livello inferiore
            sub_parent_groups = {}
            for s in share_data_list:
                if s.get('level') == current_level + 1 and s.get('parent_id') in [cs['share_id'] for cs in child_shares]:
                    pid = s.get('parent_id')
                    if pid not in sub_parent_groups:
                        sub_parent_groups[pid] = []
                    sub_parent_groups[pid].append(s)
            
            # Ricostruisci quelli mancanti dal livello più profondo
            for missing_parent_id in set([cs['share_id'] for cs in child_shares]):
                if len(child_shares) >= threshold:
                    break  # già raggiunta soglia
                reconstructed = recursive_reconstruct(current_level + 1, str(missing_parent_id))
                if reconstructed:
                    child_shares.append({
                        'content': reconstructed,
                        'level': current_level,
                        'share_id': missing_parent_id,
                        'parent_id': parent_id,
                        'is_final': True,
                        'reconstructed': True
                    })
            
            # Verifica di nuovo
            if len(child_shares) >= threshold:
                share_contents = [s['content'] for s in child_shares[:threshold]]
                return autobatch_recover(share_contents)
        
        return None  # Impossibile ricostruire
    
    # Se target specifico
    if target_parent_id:
        reconstructed = recursive_reconstruct(target_level + 1, target_parent_id)
        if reconstructed is None:
            raise ValueError(f"Impossibile ricostruire share per parent_id={target_parent_id} a livello {target_level}")
        return reconstructed

    # Ricostruzione generale dal livello massimo fino al target
    max_level = max(shares_by_level.keys())
    for current_level in range(max_level, target_level, -1):
        if current_level not in shares_by_level:
            continue
        
        parent_groups = {}
        for share in shares_by_level[current_level]:
            pid = share.get('parent_id')
            if pid not in parent_groups:
                parent_groups[pid] = []
            parent_groups[pid].append(share)
        
        for parent_id, group in parent_groups.items():
            if len(group) < levels_config[current_level][1]:
                # Prova a ricostruire figli mancanti
                reconstructed = recursive_reconstruct(current_level + 1, str(group[0]['share_id']))
                if reconstructed:
                    group.append({
                        'content': reconstructed,
                        'level': current_level,
                        'share_id': group[0]['share_id'],
                        'parent_id': parent_id,
                        'is_final': True,
                        'reconstructed': True
                    })
            
            if len(group) >= levels_config[current_level][1]:
                share_contents = [s['content'] for s in group[:levels_config[current_level][1]]]
                recovered = autobatch_recover(share_contents)
                reconstructed_share = {
                    'content': recovered,
                    'level': current_level - 1,
                    'share_id': int(parent_id.split('_')[-1]) if '_' in parent_id else 0,
                    'parent_id': None,
                    'is_final': True,
                    'reconstructed': True
                }
                if (current_level - 1) not in shares_by_level:
                    shares_by_level[current_level - 1] = []
                shares_by_level[current_level - 1].append(reconstructed_share)

    # Restituisci tutto il livello target
    if target_level in shares_by_level:
        return shares_by_level[target_level]
    
    raise ValueError(f"Impossibile ricostruire share per il livello {target_level}")


def count_available_shares_by_level(shares_data):
    """
    Conta gli share disponibili per ogni livello.
    
    Args:
        shares_data: lista di share con metadata
        
    Returns:
        dict: {livello: conteggio_share}
    """
    counts = {}
    for share in shares_data:
        level = share.get('level', 0)
        if level not in counts:
            counts[level] = 0
        counts[level] += 1
    return counts

def identify_missing_primary_shares(shares_data, levels_config, threshold):
    """
    Identifica quali share di primo livello mancano e possono essere ricostruiti.
    
    Args:
        shares_data: lista di share con metadata
        levels_config: configurazione dei livelli
        threshold: threshold necessario per la ricostruzione
        
    Returns:
        dict: informazioni sui share mancanti e ricostruibili
    """
    # Separa share per livello
    level_0_shares = [s for s in shares_data if s.get('level', 0) == 0]
    secondary_shares = [s for s in shares_data if s.get('level', 0) > 0]
    
    # Conta share di primo livello disponibili
    available_primary = len(level_0_shares)
    missing_primary = max(0, threshold - available_primary)
    
    # Identifica quali share primari possono essere ricostruiti
    reconstructable = {}
    
    if missing_primary > 0:
        # Raggruppa share secondari per parent_id
        secondary_by_parent = {}
        for share in secondary_shares:
            parent_id = share.get('parent_id')
            if parent_id:
                if parent_id not in secondary_by_parent:
                    secondary_by_parent[parent_id] = []
                secondary_by_parent[parent_id].append(share)
        
        # Verifica quali share primari possono essere ricostruiti
        for parent_id, group_shares in secondary_by_parent.items():
            # Trova il livello di questi share
            if group_shares:
                share_level = group_shares[0].get('level', 0)
                if share_level > 0 and share_level < len(levels_config):
                    required_threshold = levels_config[share_level][1]
                    if len(group_shares) >= required_threshold:
                        reconstructable[parent_id] = {
                            'level': share_level,
                            'available_shares': len(group_shares),
                            'required_threshold': required_threshold,
                            'shares': group_shares
                        }
    
    return {
        'available_primary': available_primary,
        'missing_primary': missing_primary,
        'reconstructable_primary': reconstructable
    }

def reconstruct(ciphertexts, keys=[], levels_config=None, metadata=None):
    """
    Ricostruisce i dati dal secret sharing gerarchico con priorità agli share di primo livello.
    
    Args:
        ciphertexts: lista di share criptati o share gerarchici
        keys: chiavi da ricostruire (per compatibilità)
        levels_config: configurazione dei livelli gerarchici
        metadata: metadata della struttura gerarchica
        
    Returns:
        dati ricostruiti
    """
    # Nuova logica per secret sharing gerarchico con priorità ai share di primo livello
    
    # Verifica se ciphertexts è una lista di share gerarchici
    if isinstance(ciphertexts, list) and len(ciphertexts) > 0:
        # Controlla se sono share gerarchici (hanno metadata di livello)
        if isinstance(ciphertexts[0], dict) and 'level' in ciphertexts[0]:
            # Sono share gerarchici - applica la logica di priorità
            
            # Calcola la threshold necessaria per il livello 0
            threshold = levels_config[0][1]
            
            # Identifica share mancanti e ricostruibili
            missing_info = identify_missing_primary_shares(ciphertexts, levels_config, threshold)
            
            level_0_shares = [s for s in ciphertexts if s.get('level', 0) == 0]
            
            # Se abbiamo abbastanza share di primo livello, usali direttamente
            if len(level_0_shares) >= threshold:
                share_contents = [share['content'] for share in level_0_shares[:threshold]]
                reconstructed_content = autobatch_recover(share_contents)
                
                try:
                    if isinstance(reconstructed_content, str):
                        return json.loads(reconstructed_content)
                    return reconstructed_content
                except json.JSONDecodeError:
                    return reconstructed_content
            
            # Se mancano share di primo livello, ricostruisci solo quelli necessari
            if missing_info['missing_primary'] > 0:
                print(f"Mancano {missing_info['missing_primary']} share di primo livello, tentativo di ricostruzione...")
                
                reconstructed_primary_shares = []
                reconstructed_count = 0
                
                # Ricostruisci share primari uno alla volta fino a raggiungere la threshold
                for parent_id, info in missing_info['reconstructable_primary'].items():
                    if reconstructed_count >= missing_info['missing_primary']:
                        break
                    
                    try:
                        # Ricostruisci questo share primario
                        reconstructed_content = reconstruct_hierarchical_share(
                            info['shares'], 
                            levels_config, 
                            metadata, 
                            target_level=0, 
                            target_parent_id=parent_id
                        )
                        
                        # Crea un share primario ricostruito
                        reconstructed_share = {
                            'content': reconstructed_content,
                            'level': 0,
                            'share_id': len(level_0_shares) + reconstructed_count,
                            'parent_id': None,
                            'is_final': True,
                            'reconstructed': True
                        }
                        
                        reconstructed_primary_shares.append(reconstructed_share)
                        reconstructed_count += 1
                        
                        print(f"Ricostruito share primario da {parent_id}")
                        
                    except Exception as e:
                        print(f"Errore nella ricostruzione di {parent_id}: {e}")
                        continue
                
                # Combina share originali e ricostruiti
                all_primary_shares = level_0_shares + reconstructed_primary_shares
                
                if len(all_primary_shares) >= threshold:
                    share_contents = [share['content'] for share in all_primary_shares[:threshold]]
                    reconstructed_content = autobatch_recover(share_contents)
                    
                    try:
                        if isinstance(reconstructed_content, str):
                            return json.loads(reconstructed_content)
                        return reconstructed_content
                    except json.JSONDecodeError:
                        return reconstructed_content
                else:
                    raise ValueError(f"Impossibile ricostruire: solo {len(all_primary_shares)} share primari disponibili su {threshold} necessari")
            
            # Se arriviamo qui, non abbiamo abbastanza share
            raise ValueError(f"Share insufficienti per la ricostruzione: {len(level_0_shares)} primari disponibili, {threshold} necessari")
    
    # Caso in cui abbiamo dati pseudonimizzati con chiavi specifiche
    if not keys:
        # Ricostruisci l'intero contenuto
        if isinstance(ciphertexts, list) and len(ciphertexts) > 0:
            # Estrai i contenuti se sono share gerarchici
            if isinstance(ciphertexts[0], dict) and 'content' in ciphertexts[0]:
                contents = [share['content'] for share in ciphertexts]
                reconstructed = autobatch_recover(contents)
            else:
                reconstructed = autobatch_recover(ciphertexts)
            
            try:
                return json.loads(reconstructed)
            except:
                return reconstructed
        
        return ciphertexts
    
    # Ricostruzione con chiavi specifiche per dati pseudonimizzati
    if not ciphertexts:
        raise ValueError("Lista ciphertexts vuota")
    
    # Prendi il primo elemento come template
    plaintext = deepcopy(ciphertexts[0])
    
    if isinstance(plaintext, dict):
        for key in plaintext:
            if key in keys:
                # Estrai i valori per questa chiave da tutti i ciphertexts
                key_values = []
                for ciphertext in ciphertexts:
                    if isinstance(ciphertext, dict) and key in ciphertext:
                        key_values.append(ciphertext[key])
                
                if not key_values:
                    continue
                
                # Ricostruisci ricorsivamente
                if isinstance(key_values[0], dict):
                    # Se il valore è un dizionario, ricostruisci con tutte le sue chiavi
                    if 'content' in key_values[0]:
                        # È uno share gerarchico
                        plaintext[key] = reconstruct(key_values, [], levels_config, metadata)
                    else:
                        # È un dizionario normale
                        plaintext[key] = reconstruct(key_values, list(key_values[0].keys()), levels_config, metadata)
                elif isinstance(key_values[0], list):
                    # Se è una lista, ricostruisci ricorsivamente
                    plaintext[key] = reconstruct(key_values, keys, levels_config, metadata)
                elif isinstance(key_values[0], str):
                    # Se è una stringa, usa autobatch_recover
                    plaintext[key] = autobatch_recover(key_values)
                    # Prova a convertire in numero se appropriato
                    if plaintext[key].isdigit():
                        plaintext[key] = float(plaintext[key])
                else:
                    raise ValueError("Unsupported type: " + str(type(key_values[0])))
    
    elif isinstance(plaintext, list):
        for i in range(len(plaintext)):
            # Estrai gli elementi alla posizione i da tutti i ciphertexts
            list_items = []
            for ciphertext in ciphertexts:
                if isinstance(ciphertext, list) and i < len(ciphertext):
                    list_items.append(ciphertext[i])
            
            if not list_items:
                continue
            
            # Ricostruisci ricorsivamente
            if isinstance(list_items[0], dict):
                if 'content' in list_items[0]:
                    # È uno share gerarchico
                    plaintext[i] = reconstruct(list_items, [], levels_config, metadata)
                else:
                    # È un dizionario normale
                    plaintext[i] = reconstruct(list_items, list(list_items[0].keys()), levels_config, metadata)
            elif isinstance(list_items[0], list):
                plaintext[i] = reconstruct(list_items, keys, levels_config, metadata)
            elif isinstance(list_items[0], str):
                plaintext[i] = autobatch_recover(list_items)
                if plaintext[i].isdigit():
                    plaintext[i] = float(plaintext[i])
            else:
                raise ValueError("Unsupported type: " + str(type(list_items[0])))
    
    return plaintext

def reconstruct_from_secret_map(secret_map, threshold, keys=[], levels_config=None):
    """
    Ricostruisce da una mappa di segreti con priorità agli share di primo livello.
    
    Args:
        secret_map: mappa contenente informazioni sui share
        threshold: soglia minima di share necessari
        keys: chiavi specifiche da ricostruire
        levels_config: configurazione dei livelli gerarchici
        
    Returns:
        dati ricostruiti
    """
    if secret_map.get('hierarchical', False):
        # Logica per secret sharing gerarchico con priorità
        metadata = secret_map.get('metadata', {})
        
        # Scarica tutti gli share disponibili
        all_shares = []
        for share_info in secret_map['shares']:
            try:
                response = requests.get(share_info['url'], timeout=(10, None))
                if response.status_code == 200:
                    result = response.json()
                    
                    # Crea la struttura dello share con metadata
                    share_data = {
                        'content': result.get('chunk', result),
                        'level': share_info.get('level', 0),
                        'share_id': share_info.get('share_id'),
                        'parent_id': share_info.get('parent_id'),
                        'is_final': share_info.get('is_final', True)
                    }
                    
                    # Aggiungi anche i metadata se presenti nella risposta
                    if 'metadata' in result:
                        result_metadata = result['metadata']
                        share_data.update({
                            'level': result_metadata.get('level', share_data['level']),
                            'share_id': result_metadata.get('share_id', share_data['share_id']),
                            'parent_id': result_metadata.get('parent_id', share_data['parent_id']),
                            'is_final': result_metadata.get('is_final', share_data['is_final'])
                        })
                    
                    all_shares.append(share_data)
            except Exception as e:
                print(f"Errore nel recupero dello share da {share_info['url']}: {e}")
                continue
        
        if not all_shares:
            raise ValueError("Nessuno share recuperato")
        
        # Conta share disponibili per livello
        level_counts = count_available_shares_by_level(all_shares)
        print(f"Share disponibili per livello: {level_counts}")
        
        # Usa la logica di ricostruzione con priorità
        try:
            return reconstruct(all_shares, keys, levels_config, metadata)
        except Exception as e:
            print(f"Errore nella ricostruzione gerarchica: {e}")
            raise
    
    else:
        # Usa la logica originale per la compatibilità
        all_shares = []
        primary_shares = []
        
        # Scarica share primari
        for url in secret_map.get('primary_doc', []):
            try:
                response = requests.get(url, timeout=(10, None))
                if response.status_code == 200:
                    result = response.json()
                    primary_shares.append(result)
            except:
                continue
        
        # Rimuovi duplicati da primary_shares
        seen = set()
        new_primary = []
        for d in primary_shares:
            t = tuple(d.items()) if isinstance(d, dict) else tuple(d)
            if t not in seen:
                seen.add(t)
                new_primary.append(d)
        primary_shares = new_primary
        
        # Scarica share secondari
        for url in secret_map.get('secondary_doc', []):
            try:
                response = requests.get(url, timeout=(10, None))
                if response.status_code == 200:
                    result = response.json()
                    all_shares.append(result)
            except:
                continue
        
        # Rimuovi duplicati da all_shares
        seen = set()
        new_secondary = []
        for d in all_shares:
            t = tuple(d.items()) if isinstance(d, dict) else tuple(d)
            if t not in seen:
                seen.add(t)
                new_secondary.append(d)
        all_shares = new_secondary
        
        # Priorità agli share primari
        if len(primary_shares) >= threshold:
            # Usa solo share primari
            return reconstruct(primary_shares[:threshold], keys)
        
        elif len(primary_shares) > 0:
            # Usa share primari + ricostruisci quelli mancanti da secondari
            missing = threshold - len(primary_shares)
            if len(all_shares) >= threshold:
                reconstructed_primary = recover_missing_primary_share(all_shares, keys, threshold)
                total_shares = primary_shares + [reconstructed_primary]
                return reconstruct(total_shares[:threshold], keys)
            else:
                raise ValueError("Share insufficienti per ricostruire il segreto")
        
        else:
            # Nessuno share primario, usa solo secondari
            if len(all_shares) >= threshold:
                return reconstruct(all_shares[:threshold], keys)
            else:
                raise ValueError("Share insufficienti per ricostruire il segreto")

def recover_missing_primary_share(secondary_shares, keys, threshold):
    """Recupera uno share primario mancante dai share secondari."""
    if not secondary_shares:
        raise ValueError("No secondary shares provided")
    
    if len(secondary_shares) < threshold:
        raise ValueError(f"Need at least {threshold} secondary shares, got {len(secondary_shares)}")
    
    return reconstruct(secondary_shares[:threshold], keys)