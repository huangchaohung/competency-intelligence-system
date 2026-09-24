from src.core.database import connect, initialise
from src.core.exceptions import FrameworkImportError
from src.repositories.framework_repository import FrameworkRepository
from src.services.framework_service import FrameworkService
import pytest
from openpyxl import Workbook


CSV = b"sub_functional_area,sub_functional_area_description,competency,competency_description\nTechnology,Technology capability,Architecture,Design maintainable architectures\nTechnology,Technology capability,Security,Protect systems and information\n"


def test_import_creates_current_framework_hierarchy(tmp_path) -> None:
    """A valid import atomically creates a current framework hierarchy."""
    connection = connect(tmp_path / "test.db")
    initialise(connection)
    repository = FrameworkRepository(connection)
    framework = FrameworkService(repository).import_csv("2026.1", CSV)
    assert repository.get_current() == framework
    areas = repository.list_areas(framework.id or 0)
    assert len(areas) == 1
    assert [item.name for item in repository.list_competencies(areas[0].id or 0)] == ["Architecture", "Security"]


def test_import_rejects_invalid_csv_without_creating_version(tmp_path) -> None:
    """Invalid input leaves no partial framework version behind."""
    connection = connect(tmp_path / "test.db")
    initialise(connection)
    repository = FrameworkRepository(connection)
    with pytest.raises(FrameworkImportError):
        FrameworkService(repository).import_csv("2026.1", b"competency\nArchitecture\n")
    assert repository.list_versions() == []


def test_import_accepts_operational_two_column_xlsx_structure(tmp_path) -> None:
    """The live two-column framework layout imports without descriptions."""
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(["Sub-Functional Area", "Competency (keep to 40 charcs & under for HRPS only)"])
    worksheet.append(["Programme Management", "Programme Planning & Strategy"])
    file_path = tmp_path / "framework.xlsx"
    workbook.save(file_path)
    connection = connect(tmp_path / "test.db")
    initialise(connection)
    repository = FrameworkRepository(connection)
    framework = FrameworkService(repository).import_file("2026.2", file_path.name, file_path.read_bytes())
    areas = repository.list_areas(framework.id or 0)
    assert areas[0].name == "Programme Management"
    assert repository.list_competencies(areas[0].id or 0)[0].name == "Programme Planning & Strategy"


def test_import_accepts_definition_column_xlsx_structure(tmp_path) -> None:
    """The new workbook layout imports competency definitions."""
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append(["Sub-Functional Area", "Competency", "Definition"])
    worksheet.append(["Technology", "Architecture", "Design systems that remain maintainable and scalable."])
    file_path = tmp_path / "framework_definition.xlsx"
    workbook.save(file_path)
    connection = connect(tmp_path / "test.db")
    initialise(connection)
    repository = FrameworkRepository(connection)
    framework = FrameworkService(repository).import_file("2026.3", file_path.name, file_path.read_bytes())
    areas = repository.list_areas(framework.id or 0)
    competency = repository.list_competencies(areas[0].id or 0)[0]
    assert competency.name == "Architecture"
    assert competency.description == "Design systems that remain maintainable and scalable."
