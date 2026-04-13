"""Configuration loader for AWS credentials.

Decides based on NEBULA_ENV where to read AWS credentials from:
- "local" (default): uses ~/.aws/credentials via profile name
- "cloud": reads secrets from Azure Key Vault via DefaultAzureCredential
"""

import os

from app.providers.aws import AWSProvider


def get_env() -> str:
    return os.getenv("NEBULA_ENV", "local")


def create_aws_provider(account_id: str | None = None) -> AWSProvider:
    """Create an AWSProvider with credentials from the correct source.

    Args:
        account_id: Required in cloud mode to look up per-account secrets
                    in Key Vault. Ignored in local mode.
    """
    env = get_env()

    if env == "cloud":
        if not account_id:
            raise ValueError("account_id is required in cloud mode")

        from app.services.key_vault import KeyVaultService

        kv = KeyVaultService()
        access_key_id, secret_access_key = kv.get_credentials(account_id)
        return AWSProvider(
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
        )

    # Local: use AWS profile from environment or default
    profile = os.getenv("AWS_PROFILE", "nebula-thrift")
    return AWSProvider(profile_name=profile)
