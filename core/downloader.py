import os
import sys
import platform
import requests
import zipfile
import tarfile
import shutil

# Verified URLs for binaries
SIMG2IMG_WIN_URL = "https://github.com/KinglyWayne/simg2img_win/archive/refs/heads/master.zip"
MAGISKBOOT_WIN_URL = "https://github.com/PinNaCode/magiskboot_build/releases/download/last-ci/magiskboot-e159716-release-windows-mingw-w64-ucrt-x86_64-standalone.zip"
LZ4_WIN_ZIP_URL = "https://github.com/lz4/lz4/releases/download/v1.10.0/lz4_win64_v1_10_0.zip"
LPUNPACK_WIN_URL = "https://github.com/thka2016/lpunpack_and_lpmake_cmake/releases/download/220922/lpunpack.exe"
CYGWIN_DLL_URL = "https://github.com/thka2016/lpunpack_and_lpmake_cmake/releases/download/220922/cygwin1.dll"

MAGISKBOOT_LINUX_URL = "https://github.com/PinNaCode/magiskboot_build/releases/download/last-ci/magiskboot-e159716-release-linux-x86_64-standalone.zip"
LZ4_LINUX_URL = "https://github.com/lz4/lz4/releases/download/v1.10.0/lz4_linux_v1_10_0.tar.gz"

class Downloader:
    def __init__(self, bin_dir):
        self.bin_dir = bin_dir

    def verify_binary(self, filepath):
        """Verifies that the file is a valid executable (MZ for Win, ELF for Linux)."""
        if not os.path.exists(filepath): return False
        try:
            with open(filepath, 'rb') as f:
                header = f.read(4)
                if platform.system() == "Windows":
                    return header[:2] == b'MZ'
                else:
                    return header == b'\x7fELF'
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
        """Downloads a zip or tar.gz dependency and extracts it to the bin folder, flattening nested structures."""
        if not os.path.exists(self.bin_dir):
            os.makedirs(self.bin_dir)

        is_zip = url.endswith(".zip")
        ext = ".zip" if is_zip else ".tar.gz"
        print(f"[*] Downloading {target_name}{ext} from {url}...")

        try:
            response = requests.get(url, stream=True, timeout=30, allow_redirects=True)
            response.raise_for_status()

            archive_path = os.path.join(self.bin_dir, f"{target_name}{ext}")

            with open(archive_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            print(f"[*] Extracting {target_name}...")
            temp_extract_dir = os.path.join(self.bin_dir, f"temp_{target_name}")
            if os.path.exists(temp_extract_dir): shutil.rmtree(temp_extract_dir)
            os.makedirs(temp_extract_dir)

            if is_zip:
                if not zipfile.is_zipfile(archive_path):
                    print(f"[!] {target_name} download is not a valid zip file.")
                    os.remove(archive_path)
                    return False
                with zipfile.ZipFile(archive_path, 'r') as archive_ref:
                    archive_ref.extractall(temp_extract_dir)
            else:
                try:
                    with tarfile.open(archive_path, 'r:gz') as archive_ref:
                        archive_ref.extractall(temp_extract_dir)
                except Exception as e:
                    print(f"[!] {target_name} extraction failed: {e}")
                    os.remove(archive_path)
                    return False

            # Flattening: Find all files regardless of nesting
            found_any = False
            for root, dirs, files in os.walk(temp_extract_dir):
                for file in files:
                    is_binary = file.endswith(".exe") or file.endswith(".dll") or file in ["magiskboot", "lz4", "simg2img", "lpunpack"]
                    if is_binary:
                        src = os.path.join(root, file)
                        dst = os.path.join(self.bin_dir, file)
                        if not os.path.exists(dst):
                            shutil.move(src, dst)
                            if platform.system() != "Windows" and not file.endswith(".dll"):
                                os.chmod(dst, 0o755)
                            print(f"[*] Found and copied: {file}")
                            found_any = True

            shutil.rmtree(temp_extract_dir)
            if not found_any:
                print(f"[!] Warning: No relevant binaries found in {target_name} archive.")

            os.remove(archive_path)
            return True
        except Exception as e:
            print(f"[!] Failed to download {target_name}: {e}")
            return False

    def check_dependencies(self):
        """Checks if required binaries are present, downloads them if not."""
        success = True
        system = platform.system()

        if system == "Windows":
            # simg2img
            if not os.path.exists(os.path.join(self.bin_dir, "simg2img.exe")):
                if not self.download_dependency(SIMG2IMG_WIN_URL, "simg2img_win"):
                    success = False

            # magiskboot
            if not self.verify_binary(os.path.join(self.bin_dir, "magiskboot.exe")):
                 if not self.download_dependency(MAGISKBOOT_WIN_URL, "magiskboot_zip"):
                     success = False

            # lz4
            if not self.verify_binary(os.path.join(self.bin_dir, "lz4.exe")):
                if not self.download_dependency(LZ4_WIN_ZIP_URL, "lz4_zip"):
                    success = False

            # lpunpack
            if not self.verify_binary(os.path.join(self.bin_dir, "lpunpack.exe")):
                if not self.download_file(LPUNPACK_WIN_URL, "lpunpack.exe"):
                    success = False

            # Cygwin DLL
            if not os.path.exists(os.path.join(self.bin_dir, "cygwin1.dll")):
                if not self.download_file(CYGWIN_DLL_URL, "cygwin1.dll"):
                    success = False

        elif system == "Linux":
            # For Linux, we try to download magiskboot and lz4.
            # simg2img and lpunpack are often in system paths, but we check bin/ too.

            if not self.verify_binary(os.path.join(self.bin_dir, "magiskboot")):
                if not self.download_dependency(MAGISKBOOT_LINUX_URL, "magiskboot_linux"):
                    success = False

            if not self.verify_binary(os.path.join(self.bin_dir, "lz4")):
                if not self.download_dependency(LZ4_LINUX_URL, "lz4_linux"):
                    # Fallback: check if system lz4 exists
                    if not shutil.which("lz4"):
                        success = False

            # For simg2img and lpunpack on Linux, we highly recommend system packages
            # but we will check for them.
            for tool in ["simg2img", "lpunpack"]:
                if not os.path.exists(os.path.join(self.bin_dir, tool)) and not shutil.which(tool):
                    print(f"[!] Warning: {tool} not found. Please install android-sdk-libsparse-utils or equivalent.")
                    # We don't mark success=False here yet because they might be installed via apt/dnf

        return success
