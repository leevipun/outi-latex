"""Utility functions for handling form-fields.json and reference type conversions."""

import os
import json
from typing import Dict, List, Any, Optional


def load_form_fields() -> Dict[str, List[Dict[str, Any]]]:
    """Lataa form-fields.json"""
    json_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "form-fields.json"
    )
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_reference_type_by_id(reference_id: int, reference_types) -> Optional[str]:
    """Muunna tietokannan ID viitetyypin nimeksi

    Args:
        reference_id: Tietokannan viitetyypin ID (1, 2, 3...)
        reference_types: Lista reference_types objekteja/dictionaryja tietokannasta

    Returns:
        Viitetyypin nimi (esim. "article") tai None
    """
    try:
        for ref_type in reference_types:
            if isinstance(ref_type, dict):
                if ref_type.get("id") == reference_id:
                    return ref_type.get("name")
            elif hasattr(ref_type, "id") and ref_type.id == reference_id:
                return ref_type.name
    except (KeyError, AttributeError) as e:
        print(f"Virhe get_reference_type_by_id: {e}")
    return None


def get_fields_for_type(type_name: str) -> List[Dict[str, Any]]:
    """Hae kentät viitetyypille form-fields.json:sta

    Args:
        type_name: Viitetyypin nimi (esim. "article")

    Returns:
        Lista kenttämäärittelyjä tai tyhjä lista
    """
    form_fields = load_form_fields()
    return form_fields.get(type_name, [])
