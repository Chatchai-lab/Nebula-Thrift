import os
from typing import Optional
from pathlib import Path
# NEU: Diese Libraries brauchen wir für den echten Key Vault Zugriff
try:
    from azure.identity import DefaultAzureCredential
    from azure.keyvault.secrets import SecretClient
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

class ConfigService:
    def __init__(self):
        self._config = {}
        self._load_config()

    def _load_config(self):
        # 1. .env laden (Lokal)
        dotenv_path = Path(__file__).parent.parent.parent / ".env"
        print(f"🔍 Looking for config at: {dotenv_path.absolute()}")
        if dotenv_path.exists():
            from dotenv import load_dotenv
            load_dotenv(dotenv_path)

        # 2. Basis-Umgebungsvariablen laden
        self._load_from_environment()

        # 3. Falls in Azure & Key Vault URL vorhanden -> Secrets aus Vault nachladen
        vault_url = self._config.get("KEY_VAULT_URL")
        if vault_url and AZURE_AVAILABLE:
            self._load_from_key_vault(vault_url)

    def _load_from_environment(self):
        # ... (dein bisheriger Code zum Laden aus os.getenv)
        # GitHub Models
        self._config["GITHUB_TOKEN"] = os.environ.get("GITHUB_TOKEN")
        self._config["GITHUB_MODEL_ENDPOINT"] = os.environ.get("GITHUB_MODEL_ENDPOINT", "https://models.inference.ai.azure.com")
        self._config["GITHUB_MODEL_NAME"] = os.environ.get("GITHUB_MODEL_NAME", "Llama-4-Scout-17B-16E-Instruct")

        # Cosmos DB
        self._config["COSMOS_ENDPOINT"] = os.environ.get("COSMOS_ENDPOINT")
        self._config["COSMOS_KEY"] = os.environ.get("COSMOS_KEY")
        self._config["COSMOS_DATABASE"] = os.environ.get("COSMOS_DATABASE", "nebulathrift")
        self._config["COSMOS_CONTAINER"] = os.environ.get("COSMOS_CONTAINER", "recommendations")

        # AWS
        self._config["AWS_ACCESS_KEY_ID"] = os.environ.get("AWS_ACCESS_KEY_ID")
        self._config["AWS_SECRET_ACCESS_KEY"] = os.environ.get("AWS_SECRET_ACCESS_KEY")
        self._config["AWS_REGION"] = os.environ.get("AWS_REGION", "eu-central-1")

        # Key Vault
        self._config["KEY_VAULT_URL"] = os.environ.get("KEY_VAULT_URL")
        

    def _load_from_key_vault(self, vault_url: str):
        """Versucht, fehlende Secrets aus dem Azure Key Vault zu ziehen."""
        try:
            # DefaultAzureCredential nutzt lokal deine VS Code Anmeldung 
            # und in Azure die "Managed Identity" der Function App.
            credential = DefaultAzureCredential()
            client = SecretClient(vault_url=vault_url, credential=credential)

            # Wir füllen nur auf, was bisher leer ist
            for key in self._config:
                if not self._config[key]:
                    # Key Vault Namen dürfen keine Unterstriche haben, oft nutzt man Bindestriche
                    kv_secret_name = key.replace("_", "-")
                    try:
                        self._config[key] = client.get_secret(kv_secret_name).value
                    except Exception:
                        continue # Falls ein Secret nicht im Vault existiert
        except Exception as e:
            print(f"⚠️ Key Vault Access failed: {e}")

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Holt einen Config-Wert. Falls der Key fehlt, wird erneut 
        aus der Umgebung geladen (Lazy Loading für Azure Functions).
        """
        value = self._config.get(key)
        
        # Falls der Wert fehlt, schauen wir nochmal direkt in os.environ nach
        # Das hilft, falls die Function die Umgebung erst nach Init befüllt hat.
        if not value:
            value = os.environ.get(key)
            if value:
                self._config[key] = value # Für das nächste Mal speichern
                
        return value if value is not None else default

    def get_required(self, key: str) -> str:
        value = self.get(key) # Nutzt die neue get-Logik von oben
        if not value:
            # Zeige zur Hilfe an, was überhaupt geladen wurde
            print(f"DEBUG: Current Config Keys: {list(self._config.keys())}")
            raise ValueError(f"❌ Required config '{key}' not found...")
        return value

    def validate_required(self, keys: list[str]) -> bool:
        """
        Validiert dass alle erforderlichen Keys vorhanden sind.

        Args:
            keys: Liste der erforderlichen Keys

        Returns:
            True falls alle vorhanden, False sonst
        """
        missing = [k for k in keys if not self._config.get(k)]
        if missing:
            print(f"⚠️ Missing config keys: {', '.join(missing)}")
            return False
        return True

    def __repr__(self) -> str:
        """Debug-Ausgabe der geladenen Keys (ohne sensitive Werte)."""
        keys = list(self._config.keys())
        return f"ConfigService(keys={keys})"


# Singleton-Instanz
_config_instance: Optional[ConfigService] = None


def get_config() -> ConfigService:
    """Holt die globale ConfigService-Instanz (Lazy Loading)."""
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigService()
    return _config_instance
