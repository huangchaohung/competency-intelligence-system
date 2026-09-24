from pathlib import Path

from scripts.package_cloud import deployment_files


def test_handover_package_contains_docs_and_tests_without_legacy_archive():
    root = Path(__file__).resolve().parents[1]
    files = deployment_files(root)
    paths = {p.relative_to(root).as_posix() for p in files}
    assert all(p.is_file() for p in files)
    assert len(paths) == len(files)
    assert {'README.md', 'CONTRIBUTING.md', 'SECURITY.md',
            'requirements-dev.txt', 'pyproject.toml', 'docs/architecture.md',
            'docs/operations.md', 'tests/test_handover_package.py'} <= paths
    assert 'docs/archive_readme_before_it_handover.md' not in paths
    assert not any(p.startswith(('data/', 'logs/', 'backups/', '.cloud_runtime/')) for p in paths)
