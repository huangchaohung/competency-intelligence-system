"""Source configuration application service."""
from src.models.domain import Source
from src.repositories.source_repository import SourceRepository


class SourceService:
    """Synchronise configured sources into the database."""
    def __init__(self, repository: SourceRepository) -> None:
        self._repository = repository

    def synchronise(self, sources: list[Source]) -> list[Source]:
        """Persist source definitions and return their stored forms."""
        stored = [self._repository.upsert(source) for source in sources]
        self._repository.retire_missing({source.url for source in stored})
        return stored

    def persist(self, source: Source) -> Source:
        """Create a source or update its existing database record."""
        return self._repository.update(source) if source.id is not None else self._repository.upsert(source)

    def persist_catalogue(self, sources: list[Source]) -> list[Source]:
        """Persist a complete validated catalogue, preserving existing identities."""
        stored = [self.persist(source) for source in sources]
        self._repository.retire_missing({source.url for source in stored})
        return stored
