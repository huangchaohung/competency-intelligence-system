"""Copy only deployment-allowlisted files into the existing clean Git checkout.

Does not commit, push, delete remote files or overwrite runtime source edits.
"""
from pathlib import Path
import shutil
import subprocess
from package_cloud import deployment_files

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / '.cloud-deploy'
REMOTE = 'https://github.com/huangchaohung/competency-intelligence-system.git'


def main():
    actual = subprocess.check_output(['git', '-C', str(TARGET), 'remote', 'get-url', 'origin'], text=True).strip()
    if actual != REMOTE:
        raise ValueError('Unexpected deployment repository; refusing to copy')
    for source in deployment_files(ROOT):
        target = TARGET / source.relative_to(ROOT)
        if source.is_symlink() or target.is_symlink():
            raise ValueError('Symlink rejected')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    subprocess.run(['git', '-C', str(TARGET), 'diff', '--stat'], check=True)


if __name__ == '__main__':
    main()
