import os
import sys
import platform
import requests
import zipfile
import shutil

SIMG2IMG_WIN_URL = "https://codeload.github.com/KinglyWayne/simg2img_win/zip/refs/heads/master"
MAGISKBOOT_URL = "https://codeload.github.com/svoboda18/magiskboot/zip/refs/heads/master"
# Long URL provided by user for LZ4 Windows binaries
LZ4_WIN_URL = "https://release-assets.githubusercontent.com/github-production-release-asset/18106269/c64d979e-37ce-4736-a9a2-eda2d420f2b0?sp=r&sv=2018-11-09&sr=b&spr=https&se=2026-06-27T19%3A40%3A34Z&rscd=attachment%3B+filename%3Dlz4_win64_v1_10_0.zip&rsct=application%2Foctet-stream&skoid=96c2d410-5711-43a1-aedd-ab1947aa7ab0&sktid=398a6654-997b-47e9-b12b-9515b896b4de&skt=2026-06-27T18%3A39%3A57Z&ske=2026-06-27T19%3A40%3A34Z&sks=b&skv=2018-11-09&sig=0seFgZ2rqFuBi4SPeYY08MiYNAXTHOCrwk6k40p2%2FgE%3D&jwt=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmVsZWFzZS1hc3NldHMuZ2l0aHVidXNlcmNvbnRlbnQuY29tIiwia2V5Ijoia2V5MSIsImV4cCI6MTc4MjU4Njg1NiwibmJmIjoxNzgyNTg2NTU2LCJwYXRoIjoicmVsZWFzZWFzc2V0cHJvZHVjdGlvbi5ibG9iLmNvcmUud2luZG93cy5uZXQifQ.uf8Ebn-OgjxFiiom47Otd0SPOp0WzsVGc9inEuIiYOY&response-content-disposition=attachment%3B%20filename%3Dlz4_win64_v1_10_0.zip&response-content-type=application%2Foctet-stream"
LPUNPACK_URL = "https://github.com/khusika/lpunpack-window/releases/download/v1.0/lpunpack.exe"

class Downloader:
    def __init__(self, bin_dir):
        self.bin_dir = bin_dir

    def download_file(self, url, target_name):
        """Downloads a single file."""
        if not os.path.exists(self.bin_dir):
            os.makedirs(self.bin_dir)

        dst = os.path.join(self.bin_dir, target_name)
        print(f"[*] Downloading {target_name} from {url}...")
        try:
            r = requests.get(url, timeout=15)
            r.raise_for_status()
            with open(dst, 'wb') as f:
                f.write(r.content)
            return True
        except Exception as e:
            print(f"[!] Failed to download {target_name}: {e}")
            return False

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
            simg2img_path = os.path.join(self.bin_dir, "simg2img.exe")
            if not os.path.exists(simg2img_path):
                if not self.download_dependency(SIMG2IMG_WIN_URL, "simg2img_win"):
                    success = False

            # magiskboot
            magiskboot_path = os.path.join(self.bin_dir, "magiskboot.exe")
            if not os.path.exists(magiskboot_path) and not os.path.exists(os.path.join(self.bin_dir, "magiskboot")):
                 if not self.download_dependency(MAGISKBOOT_URL, "magiskboot"):
                     success = False

            # lz4
            lz4_path = os.path.join(self.bin_dir, "lz4.exe")
            if not os.path.exists(lz4_path):
                if not self.download_dependency(LZ4_WIN_URL, "lz4"):
                    success = False

            # lpunpack
            lpunpack_path = os.path.join(self.bin_dir, "lpunpack.exe")
            if not os.path.exists(lpunpack_path):
                if not self.download_file(LPUNPACK_URL, "lpunpack.exe"):
                    success = False

        return success
