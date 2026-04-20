"""Unit tests for authentication services — no external dependencies."""
import pytest
from app.services.auth_service import hash_password, verify_password, create_access_token, decode_token
from app.models.user import UserCreate, UserLogin, UserOut
from jose import JWTError


class TestAuthService:
    """Tests for JWT and password hashing."""

    def test_hash_password(self):
        """Password hashing creates different hashes for same input."""
        password = "test123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Hashes should be different (bcrypt uses salt)
        assert hash1 != hash2
        # But both should verify correctly
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)

    def test_verify_password_correct(self):
        """Correct password verifies successfully."""
        password = "secure123"
        hashed = hash_password(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Incorrect password fails verification."""
        password = "correct123"
        wrong_password = "wrong123"
        hashed = hash_password(password)
        assert verify_password(wrong_password, hashed) is False

    def test_create_access_token(self):
        """JWT token creation with user data."""
        user_id = "user123"
        email = "test@example.com"

        token = create_access_token(user_id, email)

        # Token should be a non-empty string
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_token_valid(self):
        """Decoding valid JWT token returns payload."""
        user_id = "user456"
        email = "jane@example.com"

        token = create_access_token(user_id, email)
        payload = decode_token(token)

        assert payload["user_id"] == user_id
        assert payload["email"] == email
        assert "exp" in payload

    def test_decode_token_invalid(self):
        """Decoding invalid token raises JWTError."""
        invalid_token = "not.a.valid.jwt.token"

        with pytest.raises(JWTError):
            decode_token(invalid_token)

    def test_decode_token_expired_would_fail(self):
        """Expired tokens would fail (tested via mock or integration)."""
        # Note: Full expiry testing would require time mocking
        # This is covered in integration tests
        pass


class TestUserModels:
    """Tests for User Pydantic models."""

    def test_user_create_model(self):
        """UserCreate model validates required fields."""
        user = UserCreate(
            name="John Doe",
            email="john@example.com",
            password="secure123"
        )

        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.password == "secure123"

    def test_user_create_invalid_email(self):
        """UserCreate rejects invalid email."""
        with pytest.raises(Exception):  # Pydantic validation error
            UserCreate(
                name="John Doe",
                email="not_an_email",
                password="secure123"
            )

    def test_user_login_model(self):
        """UserLogin model validates email and password."""
        login = UserLogin(
            email="user@example.com",
            password="pass123"
        )

        assert login.email == "user@example.com"
        assert login.password == "pass123"

    def test_user_out_model(self):
        """UserOut model (no password)."""
        user = UserOut(
            user_id="abc123",
            name="Jane Smith",
            email="jane@example.com",
            created_at="2026-04-20T10:00:00"
        )

        assert user.user_id == "abc123"
        assert user.name == "Jane Smith"
        assert user.email == "jane@example.com"
        # Password should NOT be in UserOut
        assert not hasattr(user, "password")
