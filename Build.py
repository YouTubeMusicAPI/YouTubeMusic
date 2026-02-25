import os
import shutil
import subprocess
import sys
import glob

DIST_DIR = "dist"
BUILD_DIR = "build"
EGG_INFO_SUFFIX = ".egg-info"


def clean():
    for path in (DIST_DIR, BUILD_DIR):
        if os.path.exists(path):
            shutil.rmtree(path)
    for item in os.listdir():
        if item.endswith(EGG_INFO_SUFFIX):
            shutil.rmtree(item)


def run_command(command):
    subprocess.run(command, check=True)


def check_tools():
    try:
        import build
        import twine
    except ImportError:
        sys.exit(1)


def build_package():
    run_command([sys.executable, "-m", "build"])


def upload_package(test=False):
    dist_files = glob.glob("dist/*")
    if not dist_files:
        sys.exit(1)

    command = [sys.executable, "-m", "twine", "upload"]
    if test:
        command += ["--repository", "testpypi"]
    command += dist_files

    run_command(command)


def main(upload=False, test=False):
    check_tools()
    clean()
    build_package()
    if upload:
        upload_package(test=test)


if __name__ == "__main__":
    main(
        upload="--upload" in sys.argv,
        test="--test" in sys.argv
    )
