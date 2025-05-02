import os
import shutil
import subprocess

def clean_dist():
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("YouTubeMusic.egg-info"):
        shutil.rmtree("YouTubeMusic.egg-info")

def build_package():
    subprocess.run(["python3", "-m", "build"], check=True)

def upload_package():
    subprocess.run(["twine", "upload", "dist/*"], check=True)

if __name__ == "__main__":
    print("📦 Cleaning old builds...")
    clean_dist()

    print("⚙️ Building package...")
    build_package()

    print("🚀 Uploading to PyPI...")
    upload_package()

    print("✅ Done!")
