from unittest.mock import patch

import pytest


@pytest.mark.parametrize("reference_type", ["article"])
def test_save_reference_success_redirects_to_all(client, reference_type):
    """Valid POST /save_reference calls add_reference ja redirectaa /all:iin."""
    # Mockataan get_fields_for_type, ettei lueta oikeaa form-fields.json:ia
    fake_fields = [
        {"key": "author", "required": True},
        {"key": "title", "required": True},
        {"key": "journal", "required": False},
    ]

    with (
        patch("src.app.get_fields_for_type", return_value=fake_fields),
        patch("src.app.references.add_reference") as mock_add_ref,
    ):
        form_data = {
            "reference_type": reference_type,
            "cite_key": "TestKey2025",
            "author": "Test Author",
            "title": "Test Title",
            "journal": "Test Journal",
        }

        resp = client.post("/save_reference", data=form_data, follow_redirects=False)

        # 1) pitäisi redirectata /all:iin
        assert resp.status_code == 302
        assert resp.headers["Location"].endswith("/all")

        # 2) add_reference pitäisi olla kutsuttu kerran oikeilla parametreilla
        mock_add_ref.assert_called_once()
        called_type, called_data = mock_add_ref.call_args[0]

        assert called_type == reference_type
        assert called_data["bib_key"] == "TestKey2025"
        assert called_data["author"] == "Test Author"
        assert called_data["title"] == "Test Title"
        assert called_data["journal"] == "Test Journal"


def test_save_reference_missing_cite_key_shows_error_and_redirects_back(client):
    """Jos cite_key puuttuu, ei tallenneta ja redirectataan takaisin /add:iin."""
    with patch("src.app.get_fields_for_type", return_value=[]):
        resp = client.post(
            "/save_reference",
            data={"reference_type": "article"},  # ei cite_key:ä
            follow_redirects=False,
        )

        # 302 redirect takaisin /add?form=article
        assert resp.status_code == 302
        assert "/add?form=article" in resp.headers["Location"]
