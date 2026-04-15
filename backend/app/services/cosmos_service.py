import logging
from azure.cosmos import CosmosClient
from app.models.recommendation import Recommendation
from app.services.config_service import get_config

logger = logging.getLogger(__name__)


class CosmosService:
    """Service für Cosmos DB Operationen — nutzt zentrale ConfigService."""

    def __init__(self):
        """
        Initialisiert den CosmosService mit Secrets aus ConfigService.

        Raises:
            ValueError: Falls erforderliche Config-Keys nicht gesetzt sind
        """
        config = get_config()

        # Lade erforderliche Secrets
        endpoint = config.get_required("COSMOS_ENDPOINT")
        key = config.get_required("COSMOS_KEY")
        db_name = config.get("COSMOS_DATABASE", "nebulathrift")
        container_name = config.get("COSMOS_CONTAINER", "recommendations")

        # Client initialisieren
        self.client = CosmosClient(endpoint, key)
        self.database = self.client.get_database_client(db_name)
        self.container = self.database.get_container_client(container_name)

        logger.info("CosmosService initialized: %s.%s", db_name, container_name)

    async def save_recommendation(self, recommendation: Recommendation):
        """Speichert eine Empfehlung in Cosmos DB."""
        # Umwandlung in Dictionary
        item = recommendation.model_dump()
        
        # Cosmos DB verlangt ein Feld 'id' (String)
        item["id"] = recommendation.recommendation_id
        
        try:
            # upsert_item erstellt das Dokument oder aktualisiert es, falls die ID existiert
            self.container.upsert_item(item)
            logger.info("Empfehlung %s erfolgreich in Cosmos DB gespeichert.", item['id'])
        except Exception as e:
            logger.exception("Cosmos DB Fehler")
            raise e