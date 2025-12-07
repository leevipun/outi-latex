"""Integration tests for src/utils/references.py module."""

import pytest

from src.utils.references import (
    DatabaseError,
    add_reference,
    delete_reference_by_bib_key,
    get_all_added_references,
    get_all_references,
    get_reference_by_bib_key,
    get_reference_visibility,
)
from src.utils.users import create_user, link_reference_to_user

from sqlalchemy import text
from src.config import db

@pytest.fixture
def test_user(app, db_session):
    """Create a test user for reference tests."""
    with app.app_context():
        # Tarkista onko käyttäjä jo olemassa
        existing = db.session.execute(
            text("SELECT id, username FROM users WHERE username = :username"),
            {"username": "testuser"}
        ).fetchone()

        if existing:
            return {"id": existing[0], "username": existing[1]}

        # Luo uusi käyttäjä vain jos ei ole olemassa
        user = create_user("testuser", "testpass123")
        return user


class TestGetAllReferences:
    """Tests for get_all_references function."""

    def test_returns_all_reference_types(self, app, db_session):
        """Test that all seeded reference types are returned."""
        with app.app_context():
            result = get_all_references()
            assert len(result) == 3
            names = {ref["name"] for ref in result}
            assert names == {"article", "book", "inproceedings"}

    def test_returns_sorted_by_id(self, app, db_session):
        """Test that reference types are sorted by ID."""
        with app.app_context():
            result = get_all_references()
            ids = [ref["id"] for ref in result]
            assert ids == sorted(ids)

    def test_returns_dict_with_id_and_name(self, app, db_session):
        """Test that each reference type has id and name."""
        with app.app_context():
            result = get_all_references()
            for ref_type in result:
                assert "id" in ref_type
                assert "name" in ref_type
                assert isinstance(ref_type["id"], int)
                assert isinstance(ref_type["name"], str)


class TestAddReference:
    """Tests for add_reference function."""

    def test_add_reference_successfully(self, app, db_session, sample_reference_data, test_user):
        """Test adding a reference successfully."""
        with app.app_context():
            ref_id = add_reference("article", sample_reference_data)
            link_reference_to_user(test_user["id"], ref_id)

            result = get_all_added_references(user_id=test_user["id"])
            assert len(result) == 1
            assert result[0]["bib_key"] == "Smith2020"
            assert result[0]["reference_type"] == "article"

    def test_add_reference_with_all_fields(self, app, db_session, sample_reference_data, test_user):
        """Test that all fields are stored correctly."""
        with app.app_context():
            ref_id = add_reference("article", sample_reference_data)
            link_reference_to_user(test_user["id"], ref_id)

            result = get_all_added_references(user_id=test_user["id"])
            ref = result[0]["fields"]

            assert ref["author"] == "John Smith"
            assert ref["title"] == "A Great Paper"
            assert ref["journal"] == "Journal of Examples"
            assert ref["year"] == "2020"

    def test_add_reference_skips_empty_values(self, app, db_session, test_user):
        """Test that empty values are not stored."""
        with app.app_context():
            data = {
                "bib_key": "Test2020",
                "author": "Test Author",
                "title": "Test Title",
                "journal": None,
                "year": "",
            }
            ref_id = add_reference("article", data)
            link_reference_to_user(test_user["id"], ref_id)

            result = get_all_added_references(user_id=test_user["id"])
            ref = result[0]["fields"]

            assert "author" in ref
            assert "title" in ref
            assert "journal" not in ref
            assert "year" not in ref

    def test_add_reference_unknown_type_raises_error(self, app, db_session, test_user):
        """Test that unknown reference type raises DatabaseError."""
        with app.app_context():
            data = {
                "bib_key": "Test2020",
                "author": "Test Author",
                "title": "Test Title",
            }

            with pytest.raises(DatabaseError) as exc_info:
                add_reference("unknown_type", data)  # ← EI user_id parametria

            assert "Unknown reference type" in str(exc_info.value)

    def test_add_multiple_references(self, app, db_session, sample_reference_data, test_user):
        """Test adding multiple references."""
        with app.app_context():
            ref_id1 = add_reference("article", sample_reference_data)
            link_reference_to_user(test_user["id"], ref_id1)

            data2 = {
                "bib_key": "Johnson2021",
                "author": "Jane Johnson",
                "title": "Another Paper",
                "journal": "Different Journal",
                "year": 2021,
            }
            ref_id2 = add_reference("article", data2)
            link_reference_to_user(test_user["id"], ref_id2)

            result = get_all_added_references(user_id=test_user["id"])
            assert len(result) == 2
            bib_keys = {ref["bib_key"] for ref in result}
            assert bib_keys == {"Smith2020", "Johnson2021"}

    def test_add_references_of_different_types(self, app, db_session, test_user):
        """Test adding references of different types."""
        with app.app_context():
            article_data = {
                "bib_key": "Article2020",
                "author": "Author A",
                "title": "Article Title",
                "journal": "A Journal",
                "year": 2020,
            }

            book_data = {
                "bib_key": "Book2020",
                "author": "Author B",
                "title": "Book Title",
                "publisher": "A Publisher",
                "year": 2020,
            }

            ref_id1 = add_reference("article", article_data)
            link_reference_to_user(test_user["id"], ref_id1)

            ref_id2 = add_reference("book", book_data)
            link_reference_to_user(test_user["id"], ref_id2)

            result = get_all_added_references(user_id=test_user["id"])
            assert len(result) == 2

            types = {ref["reference_type"] for ref in result}
            assert types == {"article", "book"}

    def test_add_reference_with_special_characters(self, app, db_session, test_user):
        """Test adding reference with special characters."""
        with app.app_context():
            data = {
                "bib_key": "Müller2020",
                "author": "Dr. Müller & Co.",
                "title": 'Test\'s "Special" Title',
                "journal": "Journal (International)",
                "year": 2020,
            }

            ref_id = add_reference("article", data)
            link_reference_to_user(test_user["id"], ref_id)

            result = get_all_added_references(user_id=test_user["id"])
            ref = result[0]["fields"]
            assert ref["author"] == "Dr. Müller & Co."
            assert '"Special"' in ref["title"]


class TestGetAllAddedReferences:
    """Tests for get_all_added_references function."""

    def test_returns_empty_list_initially(self, app, db_session, test_user):
        """Test that empty database returns empty list."""
        with app.app_context():
            result = get_all_added_references(user_id=test_user["id"])
            assert result == []

    def test_returns_added_reference(self, app, db_session, sample_reference_data, test_user):
        """Test retrieving added reference."""
        with app.app_context():
            ref_id = add_reference("article", sample_reference_data)
            link_reference_to_user(test_user["id"], ref_id)

            result = get_all_added_references(user_id=test_user["id"])
            assert len(result) == 1
            assert result[0]["bib_key"] == "Smith2020"
            assert result[0]["reference_type"] == "article"
            assert "fields" in result[0]
            assert "created_at" in result[0]

    def test_returns_fields_correctly_grouped(self, app, db_session, sample_reference_data, test_user):
        """Test that fields are grouped correctly per reference."""
        with app.app_context():
            ref_id = add_reference("article", sample_reference_data)
            link_reference_to_user(test_user["id"], ref_id)

            result = get_all_added_references(user_id=test_user["id"])
            fields = result[0]["fields"]

            assert isinstance(fields, dict)
            assert len(fields) > 0
            for key, value in fields.items():
                assert isinstance(key, str)
                assert isinstance(value, str)

    def test_sorted_by_created_at_descending(self, app, db_session, test_user):
        """Test that results are sorted by created_at descending."""
        with app.app_context():
            data1 = {
                "bib_key": "First2020",
                "author": "Author 1",
                "title": "First",
                "journal": "J1",
                "year": 2020,
            }

            data2 = {
                "bib_key": "Second2020",
                "author": "Author 2",
                "title": "Second",
                "journal": "J2",
                "year": 2020,
            }

            ref_id1 = add_reference("article", data1)
            link_reference_to_user(test_user["id"], ref_id1)

            ref_id2 = add_reference("article", data2)
            link_reference_to_user(test_user["id"], ref_id2)

            result = get_all_added_references(user_id=test_user["id"])

            assert result[0]["bib_key"] == "Second2020"
            assert result[1]["bib_key"] == "First2020"

    def test_contains_all_required_fields(self, app, db_session, sample_reference_data, test_user):
        """Test that returned reference has all required fields."""
        with app.app_context():
            ref_id = add_reference("article", sample_reference_data)
            link_reference_to_user(test_user["id"], ref_id)

            result = get_all_added_references(user_id=test_user["id"])
            ref = result[0]

            assert "bib_key" in ref
            assert "reference_type" in ref
            assert "created_at" in ref
            assert "fields" in ref

    def test_created_at_is_datetime(self, app, db_session, sample_reference_data, test_user):
        """Test that created_at is a datetime object."""
        from datetime import datetime

        with app.app_context():
            ref_id = add_reference("article", sample_reference_data)
            link_reference_to_user(test_user["id"], ref_id)

            result = get_all_added_references(user_id=test_user["id"])
            assert isinstance(result[0]["created_at"], datetime)


class TestIntegrationWorkflows:
    """Integration tests combining multiple functions."""

    def test_full_workflow_add_and_retrieve(
        self, app, db_session, sample_reference_data, test_user
    ):
        """Test complete workflow: get types -> add reference -> retrieve all."""
        with app.app_context():
            types = get_all_references()
            assert len(types) > 0

            ref_id = add_reference("article", sample_reference_data)
            link_reference_to_user(test_user["id"], ref_id)

            references = get_all_added_references(user_id=test_user["id"])
            assert len(references) == 1
            assert references[0]["bib_key"] == "Smith2020"

    def test_add_multiple_different_types_workflow(self, app, db_session, test_user):
        """Test workflow with multiple reference types."""
        with app.app_context():
            types = get_all_references()
            type_names = {t["name"] for t in types}
            assert "article" in type_names
            assert "book" in type_names

            article_data = {
                "bib_key": "Art2020",
                "author": "A",
                "title": "Article",
                "journal": "J",
                "year": 2020,
            }
            ref_id1 = add_reference("article", article_data)
            link_reference_to_user(test_user["id"], ref_id1)

            book_data = {
                "bib_key": "Book2020",
                "author": "B",
                "title": "Book",
                "publisher": "P",
                "year": 2020,
            }
            ref_id2 = add_reference("book", book_data)
            link_reference_to_user(test_user["id"], ref_id2)

            refs = get_all_added_references(user_id=test_user["id"])
            assert len(refs) == 2

            ref_types = {r["reference_type"] for r in refs}
            assert ref_types == {"article", "book"}


class TestGetReferenceByBibKey:
    """Tests for get_reference_by_bib_key function."""

    def test_get_existing_reference(self, app, sample_reference_data, test_user):
        """Test retrieving an existing reference by bib_key."""
        with app.app_context():
            ref_id = add_reference("article", sample_reference_data)
            link_reference_to_user(test_user["id"], ref_id)

            ref = get_reference_by_bib_key("Smith2020", user_id=test_user["id"])
            assert ref is not None
            assert ref["bib_key"] == "Smith2020"
            assert ref["reference_type"] == "article"
            assert "fields" in ref
            assert ref["fields"]["author"] == "John Smith"

    def test_get_nonexistent_reference_returns_none(self, app, test_user):
        """Test that retrieving a non-existent bib_key returns None."""
        with app.app_context():
            ref = get_reference_by_bib_key("NonExistentKey", user_id=test_user["id"])
            assert ref is None

    def test_get_reference_after_deletion(self, app, db_session, sample_reference_data, test_user):
        """Test that a reference cannot be retrieved after deletion."""
        with app.app_context():
            ref_id = add_reference("article", sample_reference_data)
            link_reference_to_user(test_user["id"], ref_id)

            ref = get_reference_by_bib_key("Smith2020", user_id=test_user["id"])
            assert ref is not None

            delete_reference_by_bib_key("Smith2020", user_id=test_user["id"])

            ref_after = get_reference_by_bib_key("Smith2020", user_id=test_user["id"])
            assert ref_after is None


class TestDeleteReference:
    """Tests for delete_reference_by_bib_key function."""

    def test_delete_reference_removes_from_db(self, app, db_session, sample_reference_data, test_user):
        """Adding then deleting a reference removes it from DB."""
        with app.app_context():
            ref_id = add_reference("article", sample_reference_data)
            link_reference_to_user(test_user["id"], ref_id)

            ref = get_reference_by_bib_key("Smith2020", user_id=test_user["id"])
            assert ref is not None

            delete_reference_by_bib_key("Smith2020", user_id=test_user["id"])

            ref_after = get_reference_by_bib_key("Smith2020", user_id=test_user["id"])
            assert ref_after is None

            all_refs = get_all_added_references(user_id=test_user["id"])
            assert all_refs == []

    def test_delete_reference_also_deletes_values_via_cascade(self, app, db_session, sample_reference_data, test_user):
        """Deleting from single_reference removes related reference_values (ON DELETE CASCADE)."""
        from sqlalchemy import text
        from src.config import db

        with app.app_context():
            ref_id = add_reference("article", sample_reference_data)
            link_reference_to_user(test_user["id"], ref_id)

            ref = get_reference_by_bib_key("Smith2020", user_id=test_user["id"])
            ref_id = ref["id"]

            count_before = db.session.execute(
                text("SELECT COUNT(*) FROM reference_values WHERE reference_id = :rid"),
                {"rid": ref_id},
            ).scalar()
            assert count_before > 0

            delete_reference_by_bib_key("Smith2020", user_id=test_user["id"])

            count_after = db.session.execute(
                text("SELECT COUNT(*) FROM reference_values WHERE reference_id = :rid"),
                {"rid": ref_id},
            ).scalar()
            assert count_after == 0


class TestPublicPrivateReferences:
    """Tests for public/private reference visibility feature.

    These tests ensure that:
    - References can be marked as public or private
    - Private references don't appear in public listings
    - Visibility can be changed during editing
    - Default visibility is public
    """

    def test_add_public_reference(self, app, db_session, test_user):
        """Test adding a public reference."""
        with app.app_context():
            data = {
                "bib_key": "Public2024",
                "author": "Test Author",
                "title": "Public Paper",
                "year": "2024",
                "journal": "Test Journal",
                "is_public": True,
            }

            ref_id = add_reference("article", data, editing=False)
            link_reference_to_user(test_user["id"], ref_id)

            assert ref_id is not None
            assert get_reference_visibility("Public2024") is True

    def test_add_private_reference(self, app, db_session, test_user):
        """Test adding a private reference."""
        with app.app_context():
            data = {
                "bib_key": "Private2024",
                "author": "Test Author",
                "title": "Private Paper",
                "year": "2024",
                "journal": "Test Journal",
                "is_public": False,
            }

            ref_id = add_reference("article", data, editing=False)
            link_reference_to_user(test_user["id"], ref_id)

            assert ref_id is not None
            assert get_reference_visibility("Private2024") is False

    def test_private_references_not_in_public_listing(self, app, db_session, test_user):
        """Test that private references don't appear in get_all_added_references."""
        with app.app_context():
            public_data = {
                "bib_key": "Public2024",
                "author": "Public Author",
                "title": "Public Paper",
                "year": "2024",
                "journal": "Public Journal",
                "is_public": True,
            }
            ref_id1 = add_reference("article", public_data, editing=False)
            link_reference_to_user(test_user["id"], ref_id1)

            private_data = {
                "bib_key": "Private2024",
                "author": "Private Author",
                "title": "Private Paper",
                "year": "2024",
                "journal": "Private Journal",
                "is_public": False,
            }
            ref_id2 = add_reference("article", private_data, editing=False)
            link_reference_to_user(test_user["id"], ref_id2)

            all_refs = get_all_added_references(user_id=None)
            bib_keys = [ref["bib_key"] for ref in all_refs]

            assert "Public2024" in bib_keys
            assert "Private2024" not in bib_keys

    def test_change_visibility_from_public_to_private(self, app, db_session, test_user):
        """Test changing reference visibility from public to private."""
        with app.app_context():
            data = {
                "bib_key": "EditTest2024",
                "author": "Test Author",
                "title": "Test Paper",
                "year": "2024",
                "journal": "Test Journal",
                "is_public": True,
            }
            ref_id = add_reference("article", data, editing=False)
            link_reference_to_user(test_user["id"], ref_id)

            assert get_reference_visibility("EditTest2024") is True

            data["is_public"] = False
            data["old_bib_key"] = "EditTest2024"
            add_reference("article", data, editing=True)  # ← EI link_reference_to_user (jo linkitetty)

            assert get_reference_visibility("EditTest2024") is False

            all_refs = get_all_added_references(user_id=None)
            bib_keys = [ref["bib_key"] for ref in all_refs]
            assert "EditTest2024" not in bib_keys

    def test_change_visibility_from_private_to_public(self, app, db_session, test_user):
        """Test changing reference visibility from private to public."""
        with app.app_context():
            data = {
                "bib_key": "EditTest2025",
                "author": "Test Author",
                "title": "Test Paper",
                "year": "2025",
                "journal": "Test Journal",
                "is_public": False,
            }
            ref_id = add_reference("article", data, editing=False)
            link_reference_to_user(test_user["id"], ref_id)

            assert get_reference_visibility("EditTest2025") is False

            data["is_public"] = True
            data["old_bib_key"] = "EditTest2025"
            add_reference("article", data, editing=True)  # ← EI link_reference_to_user

            assert get_reference_visibility("EditTest2025") is True

            all_refs = get_all_added_references(user_id=None)
            bib_keys = [ref["bib_key"] for ref in all_refs]
            assert "EditTest2025" in bib_keys

    def test_default_visibility_is_public(self, app, db_session, test_user):
        """Test that default visibility is public when not specified."""
        with app.app_context():
            data = {
                "bib_key": "Default2024",
                "author": "Test Author",
                "title": "Test Paper",
                "year": "2024",
                "journal": "Test Journal",
            }

            ref_id = add_reference("article", data, editing=False)
            link_reference_to_user(test_user["id"], ref_id)

            assert ref_id is not None
            assert get_reference_visibility("Default2024") is True

    def test_private_reference_can_be_retrieved_by_bib_key(self, app, db_session, test_user):
        """Test that private references can still be retrieved by bib_key (for editing)."""
        with app.app_context():
            data = {
                "bib_key": "PrivateEdit2024",
                "author": "Private Author",
                "title": "Private Paper",
                "year": "2024",
                "journal": "Private Journal",
                "is_public": False,
            }
            ref_id = add_reference("article", data, editing=False)
            link_reference_to_user(test_user["id"], ref_id)

            reference = get_reference_by_bib_key("PrivateEdit2024", user_id=test_user["id"])
            assert reference is not None
            assert reference["bib_key"] == "PrivateEdit2024"

            all_refs = get_all_added_references(user_id=None)
            bib_keys = [ref["bib_key"] for ref in all_refs]
            assert "PrivateEdit2024" not in bib_keys

    def test_editing_preserves_visibility_when_not_changed(self, app, db_session, test_user):
        """Test that editing other fields preserves visibility setting."""
        with app.app_context():
            data = {
                "bib_key": "Preserve2024",
                "author": "Original Author",
                "title": "Original Title",
                "year": "2024",
                "journal": "Original Journal",
                "is_public": False,
            }
            ref_id = add_reference("article", data, editing=False)
            link_reference_to_user(test_user["id"], ref_id)

            data["author"] = "Updated Author"
            data["title"] = "Updated Title"
            data["old_bib_key"] = "Preserve2024"
            add_reference("article", data, editing=True)  # ← EI link_reference_to_user

            assert get_reference_visibility("Preserve2024") is False

            reference = get_reference_by_bib_key("Preserve2024", user_id=test_user["id"])
            assert reference["fields"]["author"] == "Updated Author"
            assert reference["fields"]["title"] == "Updated Title"

    def test_multiple_references_mixed_visibility(self, app, db_session, test_user):
        """Test multiple references with different visibility settings."""
        with app.app_context():
            references_data = [
                {
                    "bib_key": "Ref1",
                    "author": "A1",
                    "title": "T1",
                    "year": "2024",
                    "journal": "J1",
                    "is_public": True,
                },
                {
                    "bib_key": "Ref2",
                    "author": "A2",
                    "title": "T2",
                    "year": "2024",
                    "journal": "J2",
                    "is_public": False,
                },
                {
                    "bib_key": "Ref3",
                    "author": "A3",
                    "title": "T3",
                    "year": "2024",
                    "journal": "J3",
                    "is_public": True,
                },
                {
                    "bib_key": "Ref4",
                    "author": "A4",
                    "title": "T4",
                    "year": "2024",
                    "journal": "J4",
                    "is_public": False,
                },
            ]

            for data in references_data:
                ref_id = add_reference("article", data, editing=False)
                link_reference_to_user(test_user["id"], ref_id)

            all_refs = get_all_added_references(user_id=None)
            bib_keys = [ref["bib_key"] for ref in all_refs]

            assert "Ref1" in bib_keys
            assert "Ref2" not in bib_keys
            assert "Ref3" in bib_keys
            assert "Ref4" not in bib_keys
            assert len([k for k in bib_keys if k.startswith("Ref")]) == 2

    def test_delete_private_reference(self, app, db_session, test_user):
        """Test that private references can be deleted."""
        with app.app_context():
            data = {
                "bib_key": "DeletePrivate2024",
                "author": "Test Author",
                "title": "Test Paper",
                "year": "2024",
                "journal": "Test Journal",
                "is_public": False,
            }
            ref_id = add_reference("article", data, editing=False)
            link_reference_to_user(test_user["id"], ref_id)

            assert get_reference_by_bib_key("DeletePrivate2024", user_id=test_user["id"]) is not None

            delete_reference_by_bib_key("DeletePrivate2024", user_id=test_user["id"])

            assert get_reference_by_bib_key("DeletePrivate2024", user_id=test_user["id"]) is None
