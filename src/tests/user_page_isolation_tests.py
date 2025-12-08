"""Tests for user reference isolation."""

from utils.references import (
    add_reference,
    get_all_added_references,
    get_reference_by_bib_key,
    delete_reference_by_bib_key,
)
from utils.users import create_user, link_reference_to_user


class TestUserIsolation:
    """Tests for user reference isolation."""

    def test_user_sees_only_own_references(self, app, db_session):
        """Test that user can only see their own references on user page."""
        with app.app_context():
            # Luo kaksi käyttäjää
            user1 = create_user("user1", "pass123")
            user2 = create_user("user2", "pass456")

            # User1 lisää viitteen
            data1 = {
                "bib_key": "User1Ref2024",
                "author": "User 1 Author",
                "title": "User 1 Paper",
                "journal": "Journal 1",
                "year": "2024",
                "is_public": True,
            }
            ref_id1 = add_reference("article", data1)
            link_reference_to_user(user1["id"], ref_id1)

            # User2 lisää viitteen
            data2 = {
                "bib_key": "User2Ref2024",
                "author": "User 2 Author",
                "title": "User 2 Paper",
                "journal": "Journal 2",
                "year": "2024",
                "is_public": True,
            }
            ref_id2 = add_reference("article", data2)
            link_reference_to_user(user2["id"], ref_id2)

            # User1 näkee vain omat viitteensä
            user1_refs = get_all_added_references(user_id=user1["id"])
            assert len(user1_refs) == 1
            assert user1_refs[0]["bib_key"] == "User1Ref2024"

            # User2 näkee vain omat viitteensä
            user2_refs = get_all_added_references(user_id=user2["id"])
            assert len(user2_refs) == 1
            assert user2_refs[0]["bib_key"] == "User2Ref2024"

    def test_user_sees_both_public_and_private_own_refs(self, app, db_session):
        """Test that user sees both their public and private references."""
        with app.app_context():
            user = create_user("testuser", "pass123")

            # Lisää julkinen viite
            public_data = {
                "bib_key": "PublicRef2024",
                "author": "Public Author",
                "title": "Public Paper",
                "journal": "Journal",
                "year": "2024",
                "is_public": True,
            }
            public_ref_id = add_reference("article", public_data)
            link_reference_to_user(user["id"], public_ref_id)

            # Lisää yksityinen viite
            private_data = {
                "bib_key": "PrivateRef2024",
                "author": "Private Author",
                "title": "Private Paper",
                "journal": "Journal",
                "year": "2024",
                "is_public": False,
            }
            private_ref_id = add_reference("article", private_data)
            link_reference_to_user(user["id"], private_ref_id)

            # Käyttäjä näkee molemmat
            user_refs = get_all_added_references(user_id=user["id"])
            assert len(user_refs) == 2
            bib_keys = {ref["bib_key"] for ref in user_refs}
            assert bib_keys == {"PublicRef2024", "PrivateRef2024"}

    def test_user_cannot_see_other_users_private_refs_on_all_page(
        self, app, db_session
    ):
        """Test that user cannot see other users' private references on /all page."""
        with app.app_context():
            user1 = create_user("user1", "pass123")
            user2 = create_user("user2", "pass456")

            # User1 lisää yksityisen viitteen
            private_data = {
                "bib_key": "User1Private2024",
                "author": "User 1",
                "title": "Private Paper",
                "journal": "Journal",
                "year": "2024",
                "is_public": False,
            }
            ref_id = add_reference("article", private_data)
            link_reference_to_user(user1["id"], ref_id)

            # User2 ei näe User1:n yksityistä viitettä /all sivulla
            all_public_refs = get_all_added_references(user_id=None)
            bib_keys = [ref["bib_key"] for ref in all_public_refs]
            assert "User1Private2024" not in bib_keys

            # User2 ei näe sitä myöskään omilla sivuillaan
            user2_refs = get_all_added_references(user_id=user2["id"])
            user2_bib_keys = [ref["bib_key"] for ref in user2_refs]
            assert "User1Private2024" not in user2_bib_keys

    def test_user_cannot_edit_other_users_reference(self, app, db_session):
        """Test that user cannot edit another user's reference."""
        with app.app_context():
            user1 = create_user("user1", "pass123")
            user2 = create_user("user2", "pass456")

            # User1 lisää viitteen
            data = {
                "bib_key": "User1Ref2024",
                "author": "User 1",
                "title": "Original Title",
                "journal": "Journal",
                "year": "2024",
                "is_public": True,
            }
            ref_id = add_reference("article", data)
            link_reference_to_user(user1["id"], ref_id)

            # User2 ei voi hakea User1:n viitettä omilla tunnuksilla
            ref = get_reference_by_bib_key("User1Ref2024", user_id=user2["id"])
            assert ref is None

            # User1 voi hakea oman viitteensä
            user1_ref = get_reference_by_bib_key("User1Ref2024", user_id=user1["id"])
            assert user1_ref is not None
            assert user1_ref["bib_key"] == "User1Ref2024"

    def test_user_cannot_delete_other_users_reference(self, app, db_session):
        """Test that user cannot delete another user's reference."""
        with app.app_context():
            user1 = create_user("user1", "pass123")
            user2 = create_user("user2", "pass456")

            # User1 lisää viitteen
            data = {
                "bib_key": "User1Ref2024",
                "author": "User 1",
                "title": "Paper",
                "journal": "Journal",
                "year": "2024",
                "is_public": True,
            }
            ref_id = add_reference("article", data)
            link_reference_to_user(user1["id"], ref_id)

            # User2 yrittää poistaa User1:n viitteen
            delete_reference_by_bib_key("User1Ref2024", user_id=user2["id"])

            # Viite on edelleen olemassa (User1 näkee sen)
            user1_ref = get_reference_by_bib_key("User1Ref2024", user_id=user1["id"])
            assert user1_ref is not None

            # User1 voi poistaa oman viitteensä
            delete_reference_by_bib_key("User1Ref2024", user_id=user1["id"])
            deleted_ref = get_reference_by_bib_key("User1Ref2024", user_id=user1["id"])
            assert deleted_ref is None


class TestUserBibTexExport:
    """Tests for BibTeX export endpoints."""

    def test_export_user_bibtex_requires_login(self, app, client):
        """Test that /export/user_bibtex requires authentication."""
        with app.app_context():
            response = client.get("/export/user_bibtex", follow_redirects=False)
            # Should redirect to login
            assert response.status_code == 302
            assert "/login" in response.location

    def test_export_user_bibtex_with_no_references(self, app, client, db_session):
        """Test that export redirects with message when user has no references."""
        with app.app_context():
            # Luo käyttäjä ja kirjaudu
            user = create_user("testuser", "testpass")

            with client.session_transaction() as sess:
                sess["user_id"] = user["id"]
                sess["username"] = user["username"]

            # Yritä exporttaa tyhjä lista
            response = client.get("/export/user_bibtex", follow_redirects=True)

            assert response.status_code == 200
            assert b"no references" in response.data.lower()

    def test_export_user_bibtex_exports_own_references(self, app, client, db_session):
        """Test that user export contains user's own references."""
        with app.app_context():
            # Luo käyttäjä
            user = create_user("testuser", "testpass")

            # Lisää viite
            data = {
                "bib_key": "TestRef2024",
                "author": "Test Author",
                "title": "Test Title",
                "journal": "Test Journal",
                "year": "2024",
                "is_public": True,
            }
            ref_id = add_reference("article", data)
            link_reference_to_user(user["id"], ref_id)

            # Kirjaudu
            with client.session_transaction() as sess:
                sess["user_id"] = user["id"]
                sess["username"] = user["username"]

            # Exporttaa
            response = client.get("/export/user_bibtex")

            assert response.status_code == 200
            assert b"application/x-bibtex" in response.content_type.encode()
            assert b"@article{TestRef2024," in response.data
            assert b"author = {Test Author}" in response.data
            assert b"title = {Test Title}" in response.data

    def test_export_user_bibtex_includes_private_references(
        self, app, client, db_session
    ):
        """Test that user export includes both public and private references."""
        with app.app_context():
            user = create_user("testuser", "testpass")

            # Lisää julkinen viite
            public_data = {
                "bib_key": "PublicRef2024",
                "author": "Public Author",
                "title": "Public Title",
                "journal": "Journal",
                "year": "2024",
                "is_public": True,
            }
            public_id = add_reference("article", public_data)
            link_reference_to_user(user["id"], public_id)

            # Lisää yksityinen viite
            private_data = {
                "bib_key": "PrivateRef2024",
                "author": "Private Author",
                "title": "Private Title",
                "journal": "Journal",
                "year": "2024",
                "is_public": False,
            }
            private_id = add_reference("article", private_data)
            link_reference_to_user(user["id"], private_id)

            # Kirjaudu
            with client.session_transaction() as sess:
                sess["user_id"] = user["id"]
                sess["username"] = user["username"]

            # Exporttaa
            response = client.get("/export/user_bibtex")

            assert response.status_code == 200
            # Molemmat viitteet mukana
            assert b"PublicRef2024" in response.data
            assert b"PrivateRef2024" in response.data
            assert b"Public Author" in response.data
            assert b"Private Author" in response.data

    def test_export_user_bibtex_does_not_include_other_users_refs(
        self, app, client, db_session
    ):
        """Test that user export does not include other users' references."""
        with app.app_context():
            # Luo kaksi käyttäjää
            user1 = create_user("user1", "pass1")
            user2 = create_user("user2", "pass2")

            # User1 lisää viitteen
            data1 = {
                "bib_key": "User1Ref2024",
                "author": "User 1",
                "title": "User 1 Paper",
                "journal": "Journal",
                "year": "2024",
                "is_public": True,
            }
            ref1_id = add_reference("article", data1)
            link_reference_to_user(user1["id"], ref1_id)

            # User2 lisää viitteen
            data2 = {
                "bib_key": "User2Ref2024",
                "author": "User 2",
                "title": "User 2 Paper",
                "journal": "Journal",
                "year": "2024",
                "is_public": True,
            }
            ref2_id = add_reference("article", data2)
            link_reference_to_user(user2["id"], ref2_id)

            # Kirjaudu User1:nä
            with client.session_transaction() as sess:
                sess["user_id"] = user1["id"]
                sess["username"] = user1["username"]

            # User1 exporttaa
            response = client.get("/export/user_bibtex")

            assert response.status_code == 200
            # User1:n viite mukana
            assert b"User1Ref2024" in response.data
            # User2:n viite EI mukana
            assert b"User2Ref2024" not in response.data

    def test_export_user_bibtex_filename(self, app, client, db_session):
        """Test that export has correct filename."""
        with app.app_context():
            user = create_user("testuser", "testpass")

            # Lisää viite
            data = {
                "bib_key": "TestRef2024",
                "author": "Author",
                "title": "Title",
                "journal": "Journal",
                "year": "2024",
                "is_public": True,
            }
            ref_id = add_reference("article", data)
            link_reference_to_user(user["id"], ref_id)

            # Kirjaudu
            with client.session_transaction() as sess:
                sess["user_id"] = user["id"]
                sess["username"] = user["username"]

            response = client.get("/export/user_bibtex")

            assert response.status_code == 200
            content_disposition = response.headers.get("Content-Disposition")
            assert "my_references.bib" in content_disposition
