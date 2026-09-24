"""Trial cloud storage and administrator validation, separate from local data."""
import hashlib
import hmac
import shutil
from pathlib import Path


def password_token(password: str) -> str:
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def authorised(password: str, token: str) -> bool:
    return bool(len(password) >= 20 and token and hmac.compare_digest(password_token(password), token))


def initialise_cloud_root(project: Path) -> Path:
    """Call under the cloud app lock. Never copy local databases or logs."""
    root = project / '.cloud_runtime'
    target = root / 'config' / 'sources.yaml'
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        shutil.copyfile(project / 'config' / 'sources.yaml', target)
    # Upgrade an existing cloud catalogue without replacing user-edited URLs.
    import yaml
    from src.services.configuration_service import ConfigurationService
    document = yaml.safe_load(target.read_text(encoding='utf-8')) or {}
    if isinstance(document, dict) and any(any(field in item for field in ('country', 'category', 'evidence_label'))
           for item in document.get('sources', [])):
        backup = target.with_suffix('.pre-schema20.yaml')
        if not backup.exists():
            shutil.copyfile(target, backup)
        configuration = ConfigurationService(target)
        configuration.save_sources(configuration.load_sources())
    return root
