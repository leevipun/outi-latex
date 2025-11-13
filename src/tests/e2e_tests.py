"""End-to-end tests for Flask application routes."""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock


@pytest.fixture
def client(app):
    """Create a test client for the Flask app."""
    with app.test_client() as client:
        yield client


class TestIndexRoute:
    """E2E tests for the main index route."""

    def test_index_get_returns_html(self, client):
        """Test GET / returns the index page with form."""
        with patch("utils.references.get_all_references") as mock_refs:
            mock_refs.return_value = [
                {"id": 1, "name": "article"},
                {"id": 2, "name": "book"},
            ]
            response = client.get("/")
            assert response.status_code == 200
            assert b"Select Reference Type" in response.data or b"reference" in response.data.lower()

    def test_index_post_with_valid_reference_type(self, client):
        """Test POST / redirects to add page when form is selected."""
        response = client.post("/", data={"form": "article"}, follow_redirects=False)
        assert response.status_code == 302  # Redirect
        assert "/add" in response.location

    def test_index_post_without_form_parameter(self, client):
        """Test POST / without form shows error."""
        with patch("utils.references.get_all_references") as mock_refs:
            mock_refs.return_value = [{"id": 1, "name": "article"}]
            response = client.post("/", data={})
            assert response.status_code == 400

    def test_index_post_with_empty_form(self, client):
        """Test POST / with empty form shows error."""
        with patch("utils.references.get_all_references") as mock_refs:
            mock_refs.return_value = [{"id": 1, "name": "article"}]
            response = client.post("/", data={"form": ""})
            assert response.status_code == 400


class TestAddRoute:
    """E2E tests for the add reference form route."""

    def test_add_without_form_parameter(self, client):
        """Test GET /add without parameter shows empty form."""
        response = client.get("/add")
        assert response.status_code == 200

    def test_add_with_nonexistent_type(self, client):
        """Test GET /add?form=999 with non-existent ID."""
        with patch("utils.references.get_all_references") as mock_refs:
            mock_refs.return_value = [{"id": 1, "name": "article"}]
            response = client.get("/add?form=999")
            assert response.status_code == 200


class TestAllReferencesRoute:
    """E2E tests for viewing all references."""

    def test_all_references_returns_page(self, client):
        """Test GET /all returns references page."""
        with patch("utils.references.get_all_added_references") as mock_refs:
            mock_refs.return_value = []
            response = client.get("/all")
            assert response.status_code == 200

    def test_all_references_with_data(self, client):
        """Test GET /all displays reference data."""
        mock_reference = {
            "id": 1,
            "title": "Test Article",
            "author": "John Doe",
            "created_at": datetime(2025, 11, 13, 10, 30, 0),
            "fields": {"title": "Test Article", "author": "John Doe"},
        }
        with patch("utils.references.get_all_added_references") as mock_refs:
            mock_refs.return_value = [mock_reference]
            response = client.get("/all")
            assert response.status_code == 200


class TestErrorHandling:
    """E2E tests for error handling."""

    def test_nonexistent_route_returns_404(self, client):
        """Test accessing non-existent route returns 404."""
        response = client.get("/nonexistent_route")
        assert response.status_code == 404

    def test_invalid_method_returns_error(self, client):
        """Test invalid HTTP method returns error."""
        response = client.delete("/")
        assert response.status_code in [405, 404]  # Method not allowed or not found


class TestUserJourneys:
    """E2E tests simulating complete user workflows."""

    def test_journey_select_and_view_form(self, client):
        """Test user journey: select reference type and view form."""
        # Step 1: View index page
        with patch("utils.references.get_all_references") as mock_refs:
            mock_refs.return_value = [{"id": 1, "name": "article"}]
            response = client.get("/")
            assert response.status_code == 200

        # Step 2: Submit selection (redirect)
        response = client.post("/", data={"form": "article"}, follow_redirects=False)
        assert response.status_code == 302

    def test_journey_view_all_references(self, client):
        """Test user journey: navigate to and view all references."""
        mock_references = [
            {
                "id": 1,
                "title": "Paper 1",
                "author": "Author 1",
                "created_at": datetime(2025, 11, 13, 10, 0, 0),
                "fields": {"title": "Paper 1"},
            },
            {
                "id": 2,
                "title": "Paper 2",
                "author": "Author 2",
                "created_at": datetime(2025, 11, 13, 11, 0, 0),
                "fields": {"title": "Paper 2"},
            },
        ]

        with patch("utils.references.get_all_added_references") as mock_refs:
            mock_refs.return_value = mock_references
            response = client.get("/all")
            assert response.status_code == 200


class TestResponseTypes:
    """E2E tests for response types and content."""

    def test_index_returns_html_content_type(self, client):
        """Test that index returns HTML content."""
        with patch("utils.references.get_all_references") as mock_refs:
            mock_refs.return_value = []
            response = client.get("/")
            assert "text/html" in response.content_type or response.content_type == "text/html; charset=utf-8"

    def test_add_returns_html_content_type(self, client):
        """Test that add page returns HTML content."""
        response = client.get("/add")
        assert "text/html" in response.content_type or response.content_type == "text/html; charset=utf-8"

    def test_all_returns_html_content_type(self, client):
        """Test that all page returns HTML content."""
        with patch("utils.references.get_all_added_references") as mock_refs:
            mock_refs.return_value = []
            response = client.get("/all")
            assert "text/html" in response.content_type or response.content_type == "text/html; charset=utf-8"


class TestFormSelection:
    """E2E tests for form selection flow."""

    def test_select_article_redirects_to_add(self, client):
        """Test selecting article redirects to add page."""
        response = client.post("/", data={"form": "article"}, follow_redirects=False)
        assert response.status_code == 302
        assert "article" in response.location

    def test_select_book_redirects_to_add(self, client):
        """Test selecting book redirects to add page."""
        response = client.post("/", data={"form": "book"}, follow_redirects=False)
        assert response.status_code == 302
        assert "book" in response.location

    def test_select_inproceedings_redirects_to_add(self, client):
        """Test selecting inproceedings redirects to add page."""
        response = client.post("/", data={"form": "inproceedings"}, follow_redirects=False)
        assert response.status_code == 302
        assert "inproceedings" in response.location
