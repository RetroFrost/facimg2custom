import os
import sys
import platform
import requests
import zipfile
import shutil

SIMG2IMG_WIN_URL = "https://codeload.github.com/KinglyWayne/simg2img_win/zip/refs/heads/master"
MAGISKBOOT_URL = "https://codeload.github.com/svoboda18/magiskboot/zip/refs/heads/master"

class Downloader:
    def __init__(self, bin_dir):
        self.bin_dir = bin_dir

    def download_dependency(self, url, target_name):
        """Downloads a zip dependency and extracts it to the bin folder, flattening nested structures."""
        if not os.path.exists(self.bin_dir):
            os.makedirs(self.bin_dir)

        print(f"[*] Downloading {target_name} from {url}...")
        try:
            response = requests.get(url, stream=True, timeout=15)
            response.raise_for_status()

            zip_path = os.path.join(self.bin_dir, f"{target_name}.zip")

            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"[*] Extracting {target_name}...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                temp_extract_dir = os.path.join(self.bin_dir, f"temp_{target_name}")
                if os.path.exists(temp_extract_dir): shutil.rmtree(temp_extract_dir)
                zip_ref.extractall(temp_extract_dir)

                # Flattening: Find all files regardless of nesting
                found_any = False
                for root, dirs, files in os.walk(temp_extract_dir):
                    for file in files:
                        if file.endswith(".exe") or file.endswith(".dll") or file == "magiskboot":
                            src = os.path.join(root, file)
                            dst = os.path.join(self.bin_dir, file)
                            if not os.path.exists(dst):
                                shutil.move(src, dst)
                                print(f"[*] Found and moved: {file}")
                                found_any = True

                shutil.rmtree(temp_extract_dir)
                if not found_any:
                    print(f"[!] Warning: No relevant binaries found in {target_name} zip.")

            os.remove(zip_path)
            return True
        except Exception as e:
            print(f"[!] Failed to download {target_name}: {e}")
            return False

    def check_dependencies(self):
        """Checks if required binaries are present, downloads them if not."""
        success = True

        if platform.system() == "Windows":
            simg2img_path = os.path.join(self.bin_dir, "simg2img.exe")
            if not os.path.exists(simg2img_path):
                if not self.download_dependency(SIMG2IMG_WIN_URL, "simg2img_win"):
                    success = False

            magiskboot_path = os.path.join(self.bin_dir, "magiskboot.exe")
            if not os.path.exists(magiskboot_path) and not os.path.exists(os.path.join(self.bin_dir, "magiskboot")):
                 if not self.download_dependency(MAGISKBOOT_URL, "magiskboot"):
                     success = False
        return success
