"""Utility functions for handling form-fields.json and reference type conversions."""

import os
import json
from typing import Dict, List, Any, Optional


class UtilError(Exception):
    """Base exception for utility operations."""
    pass


class FormFieldsError(UtilError):
    """Raised when form fields cannot be loaded."""
    pass


class ReferenceTypeError(UtilError):
    """Raised when reference type conversion fails."""
    pass


def load_form_fields() -> Dict[str, List[Dict[str, Any]]]:
    """Lataa form-fields.json
    
    Raises:
        FileNotFoundError: If form-fields.json file is not found.
        json.JSONDecodeError: If form-fields.json contains invalid JSON.
        FormFieldsError: For other errors during loading.
    """
    json_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "form-fields.json"
    )
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Let these exceptions propagate without conversion
        raise
    except Exception as e:
        raise FormFieldsError(f"Failed to load form-fields.json: {e}")


def get_reference_type_by_id(reference_id: int, reference_types) -> Optional[str]:
    """Muunna tietokannan ID viitetyypin nimeksi

    Args:
        reference_id: Tietokannan viitetyypin ID (1, 2, 3...)
        reference_types: Lista reference_types objekteja/dictionaryja tietokannasta

    Returns:
        Viitetyypin nimi (esim. "article") tai None
        
    Raises:
        ReferenceTypeError: If reference type lookup fails.
    """
    try:
        for ref_type in reference_types:
            if isinstance(ref_type, dict):
                if ref_type.get("id") == reference_id:
                    return ref_type.get("name")
            elif hasattr(ref_type, "id") and ref_type.id == reference_id:
                return ref_type.name
    except (KeyError, AttributeError, TypeError) as e:
        raise ReferenceTypeError(f"Failed to find reference type with id {reference_id}: {e}")
    return None


def get_fields_for_type(type_name: str) -> List[Dict[str, Any]]:
    """Hae kentät viitetyypille form-fields.json:sta

    Args:
        type_name: Viitetyypin nimi (esim. "article")

    Returns:
        Lista kenttämäärittelyjä tai tyhjä lista
        
    Raises:
        FormFieldsError: If form fields cannot be loaded.
    """
    try:
        form_fields = load_form_fields()
        return form_fields.get(type_name, [])
    except FormFieldsError:
        raise
    except Exception as e:
        raise FormFieldsError(f"Failed to get fields for type '{type_name}': {e}")
