"""Public STE evidence collector: no framework or AI services."""
import logging
from pathlib import Path
from src.core.database import connect, initialise
from src.extractor.article_extractor import ArticleExtractor
from src.repositories.scan_repository import ScanRepository
from src.repositories.source_repository import SourceRepository
from src.scanner.web_page_scanner import WebPageScanner
from src.services.configuration_service import ConfigurationService
from src.services.source_service import SourceService
from src.services.operational_logger import OperationalLogger
from src.workflow.scan_workflow import ScanWorkflow
from src.workflow.source_configuration_workflow import SourceConfigurationWorkflow

logging.basicConfig(level=logging.INFO)
ROOT = Path(__file__).resolve().parents[2]


def build_services(root: Path = ROOT) -> dict:
    """Compose collection-only services; preserve legacy storage for later migration."""
    connection = connect(root / "data" / "competency_intelligence.db")
    initialise(connection)
    sources = SourceRepository(connection)
    scans = ScanRepository(connection)
    configuration = ConfigurationService(root / "config" / "sources.yaml")
    service = SourceService(sources)
    service.synchronise(configuration.load_sources())
    logger = OperationalLogger(root / "logs")
    return {"connection": connection, "source_repository": sources,
            "scan_repository": scans, "configuration_service": configuration,
            "source_configuration_workflow": SourceConfigurationWorkflow(configuration, service),
            "scan_workflow": ScanWorkflow(sources, scans, WebPageScanner(), ArticleExtractor(), logger),
            "operational_logger": logger}

