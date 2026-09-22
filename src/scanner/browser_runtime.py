"""Use packaged Linux Chromium on Community Cloud; local Playwright otherwise."""
import shutil
import sys


def launch_chromium(playwright):
    executable = shutil.which('chromium') if sys.platform.startswith('linux') else None
    options = {'headless': True}
    if executable:
        options['executable_path'] = executable
    return playwright.chromium.launch(**options)
