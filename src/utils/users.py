"""User management utilities."""

from typing import Optional

from sqlalchemy import text
from werkzeug.security import check_password_hash, generate_password_hash

from src.config import db


class UserError(Exception):
    """Base exception for user operations."""

    pass


class UserExistsError(UserError):
    """Raised when attempting to create a duplicate username."""

    pass


class AuthenticationError(UserError):
    """Raised when username/password authentication fails."""

    pass


def _row_to_user(row) -> Optional[dict]:
    """Convert a SQLAlchemy row mapping to a plain dict."""
    if not row:
        return None
    return {
        "id": row["id"],
        "username": row["username"],
        "password_hash": row["password_hash"],
        "created_at": row["created_at"],
    }


def create_user(username: str, password: str) -> dict:
    """Create a new user with a hashed password."""
    username = (username or "").strip()
    if not username:
        raise UserError("Username is required")
    if not password:
        raise UserError("Password is required")

    # Check for existing username
    existing = get_user_by_username(username)
    if existing:
        raise UserExistsError("Username already exists")

    password_hash = generate_password_hash(password)
    sql = text(
        """
        INSERT INTO users (username, password_hash)
        VALUES (:username, :password_hash)
        RETURNING id, username, password_hash, created_at
        """
    )
    result = db.session.execute(
        sql, {"username": username, "password_hash": password_hash}
    ).mappings()
    db.session.commit()
    return _row_to_user(result.first())


def get_user_by_username(username: str) -> Optional[dict]:
    """Fetch a user by username."""
    sql = text(
        """
        SELECT id, username, password_hash, created_at
        FROM users
        WHERE username = :username
        """
    )
    result = db.session.execute(sql, {"username": username}).mappings().first()
    return _row_to_user(result)


def get_user_by_id(user_id: int) -> Optional[dict]:
    """Fetch a user by id."""
    sql = text(
        """
        SELECT id, username, password_hash, created_at
        FROM users
        WHERE id = :user_id
        """
    )
    result = db.session.execute(sql, {"user_id": user_id}).mappings().first()
    return _row_to_user(result)


def verify_user_credentials(username: str, password: str) -> dict:
    """Validate username/password combo and return the user dict on success."""
    user = get_user_by_username(username)
    if not user:
        raise AuthenticationError("Invalid username or password")
    if not check_password_hash(user["password_hash"], password or ""):
        raise AuthenticationError("Invalid username or password")
    return user


def link_reference_to_user(user_id: int, reference_id: int) -> None:
    """Link an existing reference to a user.
    
    Args:
        user_id: The user ID to link to
        reference_id: The reference ID to link
        
    Raises:
        UserError: If the user doesn't exist in the database
    """
    # Validate that user exists first
    user = get_user_by_id(user_id)
    if not user:
        raise UserError(f"User with ID {user_id} does not exist")
    
    sql = text(
        """
        INSERT INTO user_ref (user_id, reference_id)
        VALUES (:user_id, :reference_id)
        ON CONFLICT DO NOTHING
        """
    )
    db.session.execute(sql, {"user_id": user_id, "reference_id": reference_id})
    db.session.commit()


def unlink_reference_from_user(user_id: int, reference_id: int) -> None:
    """Remove link between user and reference."""
    sql = text(
        """
        DELETE FROM user_ref
        WHERE user_id = :user_id AND reference_id = :reference_id
        """
    )
    db.session.execute(sql, {"user_id": user_id, "reference_id": reference_id})
    db.session.commit()


def ensure_user_tables() -> None:
    """Ensure users and user_ref tables exist (for upgraded databases)."""
    create_users_sql = text(
        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    create_user_ref_sql = text(
        """
        CREATE TABLE IF NOT EXISTS user_ref (
            user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            reference_id INT NOT NULL REFERENCES single_reference(id) ON DELETE CASCADE,
            PRIMARY KEY(user_id, reference_id)
        );
        """
    )

    db.session.execute(create_users_sql)
    db.session.execute(create_user_ref_sql)
    db.session.commit()
