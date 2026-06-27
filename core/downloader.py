import os
import sys
import platform
import requests
import zipfile
import shutil

# Stable URLs for Windows binaries
SIMG2IMG_WIN_URL = "https://github.com/KinglyWayne/simg2img_win/archive/refs/heads/master.zip"
MAGISKBOOT_URL = "https://github.com/erdilS/Port-Windows-11-Xiaomi-Pad-5/raw/main/magiskboot.exe"
# LZ4 official releases are in ZIPs
LZ4_WIN_ZIP_URL = "https://github.com/lz4/lz4/releases/download/v1.10.0/lz4_win64_v1_10_0.zip"
LPUNPACK_URL = "https://github.com/thka2016/lpunpack_and_lpmake_cmake/raw/main/lpunpack.exe"
CYGWIN_DLL_URL = "https://github.com/thka2016/lpunpack_and_lpmake_cmake/raw/main/cygwin1.dll"

class Downloader:
    def __init__(self, bin_dir):
        self.bin_dir = bin_dir

    def download_file(self, url, target_name):
        """Downloads a single file directly."""
        if not os.path.exists(self.bin_dir):
            os.makedirs(self.bin_dir)

        dst = os.path.join(self.bin_dir, target_name)
        print(f"[*] Downloading {target_name} from {url}...")
        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            with open(dst, 'wb') as f:
                f.write(r.content)
            print(f"[*] Downloaded {target_name} successfully.")
            return True
        except Exception as e:
            print(f"[!] Failed to download {target_name}: {e}")
            return False

    def download_dependency(self, url, target_name):
        """Downloads a zip dependency and extracts it to the bin folder, flattening nested structures."""
        if not os.path.exists(self.bin_dir):
            os.makedirs(self.bin_dir)

        print(f"[*] Downloading {target_name} zip from {url}...")
        try:
            response = requests.get(url, stream=True, timeout=30)
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
                                shutil.copy2(src, dst)
                                print(f"[*] Found and copied: {file}")
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
            # simg2img
            if not os.path.exists(os.path.join(self.bin_dir, "simg2img.exe")):
                if not self.download_dependency(SIMG2IMG_WIN_URL, "simg2img_win"):
                    success = False

            # magiskboot
            if not os.path.exists(os.path.join(self.bin_dir, "magiskboot.exe")):
                 if not self.download_file(MAGISKBOOT_URL, "magiskboot.exe"):
                     success = False

            # lz4
            if not os.path.exists(os.path.join(self.bin_dir, "lz4.exe")):
                if not self.download_dependency(LZ4_WIN_ZIP_URL, "lz4_zip"):
                    success = False

            # lpunpack
            if not os.path.exists(os.path.join(self.bin_dir, "lpunpack.exe")):
                if not self.download_file(LPUNPACK_URL, "lpunpack.exe"):
                    success = False

            # Cygwin DLL (often required for lpunpack/simg2img)
            if not os.path.exists(os.path.join(self.bin_dir, "cygwin1.dll")):
                if not self.download_file(CYGWIN_DLL_URL, "cygwin1.dll"):
                    success = False

        return success
