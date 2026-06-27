import os
import requests
import zipfile
import shutil
import sys
import subprocess

REPO_URL = "https://github.com/yourusername/facimg2custom/archive/refs/heads/main.zip"

class Updater:
    def __init__(self, current_version="0.1"):
        self.current_version = current_version

    def check_for_updates(self):
        """Checks for updates and performs redownload if needed."""
        print("[*] Checking for program updates...")
        # In a real scenario, we'd compare version tags.
        # For now, we simulate an 'always check and prompt' or 'force refresh'
        return True

    def perform_update(self):
        """Downloads the latest main branch and replaces current files."""
        print("[*] Updating program from main branch...")
        update_zip = "update.zip"
        try:
            response = requests.get(REPO_URL, stream=True)
            with open(update_zip, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            extract_dir = "temp_update"
            if os.path.exists(extract_dir): shutil.rmtree(extract_dir)

            with zipfile.ZipFile(update_zip, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)

            # Find the actual root of the extracted files (GitHub zips are nested)
            root_dir = None
            for entry in os.scandir(extract_dir):
                if entry.is_dir():
                    root_dir = entry.path
                    break

            if not root_dir:
                raise Exception("Could not find update root folder")

            # Copy all files from root_dir to current directory
            # We use a batch script on Windows to handle the replacement after exit
            if os.name == 'nt':
                self._create_windows_update_script(root_dir)
                print("[*] Update staged. Restarting...")
                os.remove(update_zip)
                subprocess.Popen(["cmd", "/c", "update.bat"], creationflags=0x00000008)
                sys.exit(0)
            else:
                # Linux/Unix logic
                for item in os.listdir(root_dir):
                    s = os.path.join(root_dir, item)
                    d = os.path.join(os.getcwd(), item)
                    if os.path.isdir(s):
                        if os.path.exists(d): shutil.rmtree(d)
                        shutil.copytree(s, d)
                    else:
                        shutil.copy2(s, d)
                os.remove(update_zip)
                shutil.rmtree(extract_dir)
                return True
        except Exception as e:
            print(f"[!] Update failed: {e}")
            return False

    def _create_windows_update_script(self, source_dir):
        """Creates a batch file to replace files after the python process exits."""
        with open("update.bat", "w") as f:
            f.write("@echo off\n")
            f.write("timeout /t 2 /nobreak > nul\n") # Wait for python to exit
            f.write(f"xcopy /E /Y /H \"{os.path.abspath(source_dir)}\\*\" \"{os.getcwd()}\"\n")
            f.write(f"rd /S /Q \"{os.path.abspath('temp_update')}\"\n")
            f.write("start python launcher.py\n")
            f.write("del \"%~f0\"\n")
