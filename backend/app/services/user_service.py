"""User service for managing user data in Cosmos DB."""
import logging
from uuid import uuid4
from datetime import datetime
from azure.cosmos import CosmosClient
from app.services.config_service import get_config

logger = logging.getLogger(__name__)


class UserService:
    """Service für User-Operationen in Cosmos DB."""

    def __init__(self):
        """Initialize UserService with Cosmos DB client."""
        config = get_config()

        # Load required secrets
        endpoint = config.get_required("COSMOS_ENDPOINT")
        key = config.get_required("COSMOS_KEY")
        db_name = config.get("COSMOS_DATABASE", "nebulathrift")

        # Initialize client and get users container
        self.client = CosmosClient(endpoint, key)
        self.database = self.client.get_database_client(db_name)

        # Create users container if it doesn't exist
        try:
            self.container = self.database.get_container_client("users")
        except Exception:
            # Container doesn't exist, create it
            logger.info("Creating 'users' container in Cosmos DB")
            self.container = self.database.create_container(
                id="users",
                partition_key="/user_id",
                offer_throughput=400,
            )

        logger.info("UserService initialized: %s.users", db_name)

    def create(self, name: str, email: str, hashed_password: str) -> dict:
        """Create a new user.

        Args:
            name: User's display name
            email: User's email (unique)
            hashed_password: Bcrypt-hashed password

        Returns:
            User document dict with user_id, name, email, created_at

        Raises:
            ValueError: If email already exists
        """
        # Check if email already exists
        existing = self.get_by_email(email)
        if existing:
            raise ValueError(f"Email {email} already in use")

        user_id = str(uuid4())[:12]
        created_at = datetime.utcnow().isoformat()

        user_doc = {
            "id": user_id,
            "user_id": user_id,
            "name": name,
            "email": email,
            "hashed_password": hashed_password,
            "created_at": created_at,
        }

        try:
            self.container.create_item(user_doc)
            logger.info("User %s (%s) created", user_id, email)
            return {
                "user_id": user_id,
                "name": name,
                "email": email,
                "created_at": created_at,
            }
        except Exception as e:
            logger.exception("Failed to create user")
            raise e

    def get_by_email(self, email: str) -> dict | None:
        """Get a user by email address.

        Args:
            email: The email to search for

        Returns:
            User document dict (including hashed_password), or None if not found
        """
        try:
            query = "SELECT * FROM users u WHERE u.email = @email"
            params = [{"name": "@email", "value": email}]
            results = list(self.container.query_items(query=query, parameters=params))
            return results[0] if results else None
        except Exception as e:
            logger.exception("Failed to get user by email: %s", email)
            raise e

    def get_by_id(self, user_id: str) -> dict | None:
        """Get a user by ID (excludes password).

        Args:
            user_id: The user ID

        Returns:
            User document dict without hashed_password, or None if not found
        """
        try:
            item = self.container.read_item(item=user_id, partition_key=user_id)
            # Remove sensitive data
            item.pop("hashed_password", None)
            return item
        except Exception as e:
            logger.debug("User not found: %s", user_id)
            return None
