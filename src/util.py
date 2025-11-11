import os
import json
from typing import Dict, List, Any

def load_form_fields() -> Dict[str, List[Dict[str, Any]]]:
    """Lataa form-fields.json"""
    json_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'form-fields.json'
    )
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)