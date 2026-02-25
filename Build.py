import os
import shutil
import subprocess
import sys


DIST_DIR = "dist"
BUILD_DIR = "build"
EGG_INFO = "YouTubeMusic.egg-info"


def clean():
    for path in (DIST_DIR, BUILD_DIR, EGG_INFO):
        if os.path.exists(path):
            shutil.rmtree(path)


def run_command(command):
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {' '.join(command)}")
        sys.exit(e.returncode)


def build():
    run_command([sys.executable, "-m", "build"])


def upload():
    run_command(["twine", "upload", "dist/*"])


def main(upload_to_pypi: bool = False):
    print("Cleaning previous builds...")
    clean()

    print("Building package...")
    build()

    if upload_to_pypi:
        print("Uploading to PyPI...")
        upload()

    print("Build process completed.")


if __name__ == "__main__":
    upload_flag = "--upload" in sys.argv
    main(upload_to_pypi=upload_flag)
