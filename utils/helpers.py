import os
import sys
import platform
import requests
import zipfile
import shutil

SIMG2IMG_WIN_URL = "https://codeload.github.com/KinglyWayne/simg2img_win/zip/refs/heads/master"
MAGISKBOOT_URL = "https://codeload.github.com/svoboda18/magiskboot/zip/refs/heads/master"

def get_bin_path():
    """Returns the path to the bin directory."""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'bin')

def download_dependency(url, target_name):
    """Downloads a zip dependency and extracts it to the bin folder."""
    bin_dir = get_bin_path()
    if not os.path.exists(bin_dir):
        os.makedirs(bin_dir)

    print(f"[*] Downloading {target_name} from {url}...")
    try:
        response = requests.get(url, stream=True)
        zip_path = os.path.join(bin_dir, f"{target_name}.zip")

        with open(zip_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"[*] Extracting {target_name}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            temp_extract_dir = os.path.join(bin_dir, f"temp_{target_name}")
            zip_ref.extractall(temp_extract_dir)

            for root, dirs, files in os.walk(temp_extract_dir):
                for file in files:
                    if file.endswith(".exe") or file.endswith(".dll") or file == "magiskboot":
                        src = os.path.join(root, file)
                        dst = os.path.join(bin_dir, file)
                        if not os.path.exists(dst):
                            shutil.move(src, dst)

            shutil.rmtree(temp_extract_dir)

        os.remove(zip_path)
        return True
    except Exception as e:
        print(f"[!] Failed to download {target_name}: {e}")
        return False

def check_dependencies():
    """Checks if required binaries are present, downloads them if not."""
    bin_dir = get_bin_path()
    success = True

    if platform.system() == "Windows":
        simg2img_path = os.path.join(bin_dir, "simg2img.exe")
        if not os.path.exists(simg2img_path):
            if not download_dependency(SIMG2IMG_WIN_URL, "simg2img_win"):
                success = False

        magiskboot_path = os.path.join(bin_dir, "magiskboot.exe")
        # magiskboot might not have .exe in the zip name, checking both
        if not os.path.exists(magiskboot_path) and not os.path.exists(os.path.join(bin_dir, "magiskboot")):
             if not download_dependency(MAGISKBOOT_URL, "magiskboot"):
                 success = False
    return success

def find_unified_models(device_tree_path):
    """Searches for subdirectories containing BoardConfig.mk."""
    models = []
    if not device_tree_path or not os.path.exists(device_tree_path):
        return models

    for entry in os.scandir(device_tree_path):
        if entry.is_dir():
            if os.path.exists(os.path.join(entry.path, 'BoardConfig.mk')):
                models.append(entry.name)
    return models
