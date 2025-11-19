"""Utility functions for handling form-fields.json and reference type conversions."""

import json
import os
from typing import Any, Dict, List, Optional
import requests

SCHEMA = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "form-fields.json"
    )

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
        raise ReferenceTypeError(
            f"Failed to find reference type with id {reference_id}: {e}"
        )
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
    
TYPE_MAP = {
    "journal-article": "article",
    "proceedings-article": "inproceedings",
    "book": "book",
    "book-chapter": "inbook",
    "reference-entry": "misc",
}

import os
import requests
from typing import Any, Dict, Optional

TYPE_MAP = {
    "journal-article": "article",
    "proceedings-article": "inproceedings",
    "book": "book",
    "book-chapter": "inbook",
    "reference-entry": "misc",
}


def detect_type(crossref_type: str) -> str:
    return TYPE_MAP.get(crossref_type, "misc")


def parse_authors(authors: Optional[list]) -> Optional[str]:
    if not authors:
        return None
    return ", ".join(f"{a.get('given','')} {a.get('family','')}".strip() for a in authors)


def clean_values(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove keys with empty or None values."""
    def valid(v):
        if v is None:
            return False
        if isinstance(v, str) and not v.strip():
            return False
        if isinstance(v, (list, tuple)) and not v:
            return False
        return True

    return {k: v for k, v in data.items() if valid(v)}


def parse_doi(doi_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse CrossRef API response data into a structured reference dictionary.
    """
    entry_type = detect_type(doi_data.get("type", "misc"))
    parsed = {"type": entry_type}

    form_fields = load_form_fields()  # Assuming returns dict of type -> fields

    for field in form_fields.get(entry_type, []):
        key = field["key"]

        if key == "author":
            parsed[key] = parse_authors(doi_data.get("author"))

        elif key == "title":
            parsed[key] = doi_data["title"]

        elif key in ("journal", "booktitle"):
            container = doi_data["container-title"]
            parsed[key] = container if container else None

        elif key == "year":
            date_parts = doi_data.get("issued", {}).get("date-parts", [[None]])
            parsed[key] = date_parts[0][0]

        elif key == "month":
            date_parts = doi_data.get("issued", {}).get("date-parts", [[None, None]])
            parsed[key] = date_parts[0][1] if len(date_parts[0]) > 1 else None

        elif key in ("pages", "volume", "number", "publisher", "doi", "url"):
            mapping = {
                "pages": "page",
                "number": "issue",
                "doi": "DOI",
            }
            parsed[key] = doi_data.get(mapping.get(key, key))

        elif key == "issn":
            issn = doi_data.get("ISSN")
            parsed[key] = issn if issn else None

        else:
            parsed[key] = None

    return clean_values(parsed)


def get_doi_data_from_api(doi: str) -> Dict[str, Any]:
    """
    Fetch DOI metadata from CrossRef API and parse it.
    """
    url = f"https://citation.doi.org/metadata?doi={doi}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        doi_data = response.json()
        parsed = parse_doi(doi_data)
        print(f"Fetched and parsed DOI data for {doi}: {parsed}")
        return parsed
    except requests.exceptions.RequestException as e:
        raise UtilError(f"Failed to fetch DOI data: {e}")
