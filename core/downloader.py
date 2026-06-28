import os
import sys
import platform
import requests
import zipfile
import shutil

# Verified URLs for Windows binaries
SIMG2IMG_WIN_URL = "https://github.com/KinglyWayne/simg2img_win/archive/refs/heads/master.zip"
MAGISKBOOT_URL = "https://github.com/PinNaCode/magiskboot_build/releases/download/last-ci/magiskboot-e159716-release-windows-mingw-w64-ucrt-x86_64-standalone.zip"
LZ4_WIN_ZIP_URL = "https://github.com/lz4/lz4/releases/download/v1.10.0/lz4_win64_v1_10_0.zip"
LPUNPACK_URL = "https://github.com/thka2016/lpunpack_and_lpmake_cmake/releases/download/220922/lpunpack.exe"
CYGWIN_DLL_URL = "https://github.com/thka2016/lpunpack_and_lpmake_cmake/releases/download/220922/cygwin1.dll"

class Downloader:
    def __init__(self, bin_dir):
        self.bin_dir = bin_dir

    def verify_binary(self, filepath):
        """Verifies that the file is a valid Windows executable."""
        if not os.path.exists(filepath): return False
        try:
            with open(filepath, 'rb') as f:
                header = f.read(2)
                return header == b'MZ'
        except: return False

    def download_file(self, url, target_name):
        """Downloads a single file directly."""
        if not os.path.exists(self.bin_dir):
            os.makedirs(self.bin_dir)

        dst = os.path.join(self.bin_dir, target_name)
        print(f"[*] Downloading {target_name} from {url}...")
        try:
            r = requests.get(url, timeout=30, allow_redirects=True)
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
            response = requests.get(url, stream=True, timeout=30, allow_redirects=True)
            response.raise_for_status()

            zip_path = os.path.join(self.bin_dir, f"{target_name}.zip")

            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"[*] Extracting {target_name}...")
            if not zipfile.is_zipfile(zip_path):
                print(f"[!] {target_name} download is not a valid zip file.")
                os.remove(zip_path)
                return False

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
            if not self.verify_binary(os.path.join(self.bin_dir, "magiskboot.exe")):
                 if not self.download_dependency(MAGISKBOOT_URL, "magiskboot_zip"):
                     success = False

            # lz4
            if not self.verify_binary(os.path.join(self.bin_dir, "lz4.exe")):
                if not self.download_dependency(LZ4_WIN_ZIP_URL, "lz4_zip"):
                    success = False

            # lpunpack
            if not self.verify_binary(os.path.join(self.bin_dir, "lpunpack.exe")):
                if not self.download_file(LPUNPACK_URL, "lpunpack.exe"):
                    success = False

            # Cygwin DLL
            if not os.path.exists(os.path.join(self.bin_dir, "cygwin1.dll")):
                if not self.download_file(CYGWIN_DLL_URL, "cygwin1.dll"):
                    success = False

        return success
