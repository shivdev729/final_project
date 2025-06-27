import json
import os
from datetime import datetime

class EntryNotFoundError(Exception):
    """Raised when an entry is not found in the metastore."""
    pass

def setup(store_path="metastore.json"):
    if not os.path.exists(store_path):
        with open(store_path, 'w') as f:
            json.dump([], f)

def add_entry(entry,store_path="metastore.json"):
    data = _load_store(store_path)
    data.append(entry)
    _save_store(data, store_path)

def delete_entry_by_hash( file_hash,store_path="metastore.json"):
    data = _load_store(store_path)
    new_data = [entry for entry in data if entry['hash'] != file_hash]
    _save_store(new_data, store_path)
    return len(new_data)<len(data)

def _load_store(store_path="metastore.json"):
    with open(store_path, 'r') as f:
        return json.load(f)

def _save_store(data, store_path="metastore.json"):
    with open(store_path, 'w') as f:
        json.dump(data, f, indent=2)