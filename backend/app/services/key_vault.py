"""Azure Key Vault integration for storing AWS credentials."""
import os
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential


class KeyVaultService:
    """Securely store and retrieve AWS credentials from Azure Key Vault."""

    def __init__(self):
        key_vault_url = os.getenv("AZURE_KEY_VAULT_URL")
        if not key_vault_url:
            raise ValueError("AZURE_KEY_VAULT_URL environment variable not set")

        self.credential = DefaultAzureCredential()
        self.client = SecretClient(vault_url=key_vault_url, credential=self.credential)

    def store_credentials(
        self,
        account_id: str,
        access_key_id: str,
        secret_access_key: str,
    ) -> None:
        """Store AWS credentials in Key Vault."""
        self.client.set_secret(f"aws-{account_id}-access-key-id", access_key_id)
        self.client.set_secret(f"aws-{account_id}-secret-access-key", secret_access_key)

    def get_credentials(self, account_id: str) -> tuple[str, str]:
        """Retrieve AWS credentials from Key Vault.

        Returns:
            (access_key_id, secret_access_key)
        """
        access_key_id = self.client.get_secret(f"aws-{account_id}-access-key-id").value
        secret_access_key = self.client.get_secret(f"aws-{account_id}-secret-access-key").value
        return access_key_id, secret_access_key

    def delete_credentials(self, account_id: str) -> None:
        """Delete AWS credentials from Key Vault."""
        self.client.begin_delete_secret(f"aws-{account_id}-access-key-id")
        self.client.begin_delete_secret(f"aws-{account_id}-secret-access-key")
