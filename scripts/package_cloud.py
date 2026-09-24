"""Create a code-only deployment ZIP; never include local history or secrets."""
from pathlib import Path
from datetime import datetime
from zipfile import ZipFile, ZIP_DEFLATED


def deployment_files(root):
    names = ['app.py', 'cloud_app.py', 'requirements.txt', 'packages.txt',
             '.gitignore', 'config/sources.yaml', 'docs/streamlit_cloud_deployment.md',
             'README.md', 'CONTRIBUTING.md', 'SECURITY.md', 'requirements-dev.txt',
             'pyproject.toml', 'docs/architecture.md', 'docs/operations.md',
             'docs/source_tuning_status.md', 'scripts/package_cloud.py',
             'scripts/sync_cloud.py', 'scripts/apply_source_health_stage.py']
    files = [root / name for name in names]
    files.extend(sorted((root / 'src').rglob('*.py')))
    files.extend(sorted((root / 'tests').rglob('*.py')))
    return files


def main():
    root = Path(__file__).resolve().parents[1]
    output = root / 'dist'
    output.mkdir(exist_ok=True)
    archive = output / ('streamlit-cloud-' + datetime.now().strftime('%Y%m%d-%H%M%S') + '.zip')
    with ZipFile(archive, 'x', ZIP_DEFLATED) as bundle:
        for path in deployment_files(root):
            if path.is_symlink():
                raise ValueError('Deployment files must not be symlinks')
            bundle.write(path, path.relative_to(root).as_posix())
    print(archive)


if __name__ == '__main__':
    main()
