"""Framework version import and retrieval application service."""
import csv
import io
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from openpyxl import load_workbook
from src.core.exceptions import FrameworkImportError
from src.models.domain import Competency, FrameworkVersion, SubFunctionalArea
from src.repositories.framework_repository import FrameworkRepository

AREA_COLUMN = "sub_functional_area"
CAP_AREA_COLUMN = "cap_area"
COMPETENCY_COLUMN = "competency"
DEFINITION_COLUMN = "definition"


@dataclass(frozen=True)
class FrameworkRow:
    """A validated row in the framework CSV import format."""
    cap_area: str | None
    area_name: str
    area_description: str | None
    competency_name: str
    competency_description: str
    definition: str


class FrameworkService:
    """Import complete framework versions atomically from CSV."""
    def __init__(self, repository: FrameworkRepository) -> None:
        self._repository = repository

    def import_file(self, version: str, filename: str, content: bytes) -> FrameworkVersion:
        """Validate and persist a CSV or XLSX framework version atomically."""
        if not version.strip():
            raise FrameworkImportError("A non-empty framework version is required")
        rows = self._parse_file(filename, content)
        if any(item.version == version for item in self._repository.list_versions()):
            raise FrameworkImportError(f"Framework version already exists: {version}")
        try:
            framework = self._repository.create_version(version.strip(), datetime.now().astimezone())
            areas: dict[str, SubFunctionalArea] = {}
            for row in rows:
                area = areas.get(row.area_name)
                if area is None:
                    area = self._repository.add_area(SubFunctionalArea(None, framework.id or 0, row.cap_area, row.area_name, row.area_description))
                    areas[row.area_name] = area
                self._repository.add_competency(Competency(None, area.id or 0, row.competency_name, row.competency_description))
            self._repository.commit()
            return framework
        except (ValueError, OSError, sqlite3.Error) as error:
            self._repository.rollback()
            raise FrameworkImportError(f"Unable to import framework: {error}") from error

    @staticmethod
    def preview_columns(filename: str, content: bytes) -> list[str]:
        """Return the detected framework columns for a quick import preview."""
        suffix = filename.lower().rsplit(".", maxsplit=1)[-1] if "." in filename else ""
        if suffix == "csv":
            try:
                reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig")))
            except UnicodeDecodeError as error:
                raise FrameworkImportError("Framework CSV must be UTF-8 encoded") from error
            if reader.fieldnames is None:
                raise FrameworkImportError("Framework CSV has no header row")
            return [str(header).strip() for header in reader.fieldnames if header]
        if suffix == "xlsx":
            try:
                worksheet = load_workbook(io.BytesIO(content), read_only=True, data_only=True).active
                headers = next(worksheet.iter_rows(values_only=True), None)
            except (OSError, ValueError, StopIteration) as error:
                raise FrameworkImportError("Unable to read framework XLSX file") from error
            if headers is None:
                raise FrameworkImportError("Framework XLSX has no header row")
            return [str(header).strip() for header in headers if header]
        raise FrameworkImportError("Framework file must be CSV or XLSX")

    def import_csv(self, version: str, content: bytes) -> FrameworkVersion:
        """Import a CSV framework; retained as a stable service interface."""
        return self.import_file(version, "framework.csv", content)

    @staticmethod
    def _parse_file(filename: str, content: bytes) -> list[FrameworkRow]:
        suffix = filename.lower().rsplit(".", maxsplit=1)[-1] if "." in filename else ""
        if suffix == "csv":
            return FrameworkService._parse_csv(content)
        if suffix == "xlsx":
            return FrameworkService._parse_xlsx(content)
        raise FrameworkImportError("Framework file must be CSV or XLSX")

    @staticmethod
    def _parse_csv(content: bytes) -> list[FrameworkRow]:
        try:
            reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig")))
        except UnicodeDecodeError as error:
            raise FrameworkImportError("Framework CSV must be UTF-8 encoded") from error
        if reader.fieldnames is None:
            raise FrameworkImportError("Framework CSV has no header row")
        return FrameworkService._parse_rows(reader.fieldnames, reader)

    @staticmethod
    def _parse_xlsx(content: bytes) -> list[FrameworkRow]:
        try:
            worksheet = load_workbook(io.BytesIO(content), read_only=True, data_only=True).active
            values = worksheet.iter_rows(values_only=True)
            headers = next(values, None)
        except (OSError, ValueError, StopIteration) as error:
            raise FrameworkImportError("Unable to read framework XLSX file") from error
        if headers is None:
            raise FrameworkImportError("Framework XLSX has no header row")
        rows = (dict(zip(headers, row)) for row in values)
        return FrameworkService._parse_rows(headers, rows)

    @staticmethod
    def _parse_rows(headers: object, records: object) -> list[FrameworkRow]:
        header_map = {FrameworkService._normalise_header(str(header)): header for header in headers if header}
        area_header = header_map.get(AREA_COLUMN)
        competency_header = next((original for normalised, original in header_map.items() if normalised.startswith(COMPETENCY_COLUMN)), None)
        cap_area_header = header_map.get(CAP_AREA_COLUMN)
        area_description_header = header_map.get("sub_functional_area_description")
        competency_description_header = header_map.get("competency_description")
        definition_header = header_map.get(DEFINITION_COLUMN)
        if area_header is None or competency_header is None:
            raise FrameworkImportError("Framework headers must include 'Sub-Functional Area' and a 'Competency' column")
        rows: list[FrameworkRow] = []
        for number, item in enumerate(records, start=2):
            area_name = FrameworkService._required_value(item.get(area_header), number, "Sub-Functional Area")
            cap_area = FrameworkService._optional_value(item.get(cap_area_header)) if cap_area_header else None
            competency_name = FrameworkService._required_value(item.get(competency_header), number, "Competency")
            area_description = FrameworkService._optional_value(item.get(area_description_header)) if area_description_header else None
            competency_description = FrameworkService._optional_value(item.get(competency_description_header)) if competency_description_header else ""
            definition = FrameworkService._optional_value(item.get(definition_header)) if definition_header else competency_description
            if not competency_description:
                competency_description = definition
            rows.append(FrameworkRow(cap_area, area_name, area_description, competency_name, competency_description, definition))
        if not rows:
            raise FrameworkImportError("Framework file contains no competency rows")
        area_descriptions: dict[str, str | None] = {}
        area_cap_areas: dict[str, str | None] = {}
        competency_keys: set[tuple[str, str]] = set()
        for row in rows:
            existing_description = area_descriptions.setdefault(row.area_name, row.area_description)
            if existing_description != row.area_description:
                raise FrameworkImportError(f"Area '{row.area_name}' has inconsistent descriptions")
            existing_cap_area = area_cap_areas.setdefault(row.area_name, row.cap_area)
            if existing_cap_area != row.cap_area:
                raise FrameworkImportError(f"Area '{row.area_name}' has inconsistent Cap Area values")
            key = (row.area_name, row.competency_name)
            if key in competency_keys:
                raise FrameworkImportError(f"Duplicate competency '{row.competency_name}' in area '{row.area_name}'")
            competency_keys.add(key)
        return rows

    @staticmethod
    def _normalise_header(value: str) -> str:
        return "".join(character.lower() if character.isalnum() else "_" for character in value).strip("_").replace("__", "_")

    @staticmethod
    def _required_value(value: object, row_number: int, column_name: str) -> str:
        text = FrameworkService._optional_value(value)
        if not text:
            raise FrameworkImportError(f"Row {row_number} has an empty {column_name} value")
        return text

    @staticmethod
    def _optional_value(value: object) -> str:
        return str(value).strip() if value is not None else ""
